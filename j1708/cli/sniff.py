import argparse
import curses
import enum
import itertools
import os

from .. import iface
from .. import log


class Colors(enum.IntEnum):
    CURRENT_LINE = 1
    UNEXPANDED   = 2
    EXPANDED     = 3
    MESSAGE      = 4
    STATUS       = 5


class Sniffer:
    def __init__(self, stdscr, reparse_log=None, log_filename=None):
        self.scr = stdscr

        self.log = log.Log(log_filename=log_filename, stdout=False)

        if reparse_log is not None:
            # Because we can iterate through messages from the interface the 
            # same way we can iterate through a list, store the reparsed 
            # messages in the iface attr.

            self.iface = log.read_msgs(reparse_log, realtime=True)
        else:
            port = iface.find_device()
            self.iface = iface.Iface(port, timeout=0)

        self.msgs = {}
        self.msgcount = 0

        # Prepare the screen
        self.scr.nodelay(1)
        curses.curs_set(0)
        self.scr.clear()
        self.scr.refresh()

        curses.start_color()
        # xterm colors: https://jonasjacek.github.io/colors/
        if '256' in os.getenv('TERM'):
            # extended xterm colors:
            #   light blue (DodgerBlue1) = 33
            #   dark gray  (Grey11)      = 234
            curses.init_pair(Colors.CURRENT_LINE, curses.COLOR_CYAN, 234)
            curses.init_pair(Colors.UNEXPANDED, curses.COLOR_CYAN, curses.COLOR_BLACK)
            curses.init_pair(Colors.EXPANDED, curses.COLOR_BLACK, curses.COLOR_CYAN)
            curses.init_pair(Colors.MESSAGE, 33, curses.COLOR_BLACK)
            curses.init_pair(Colors.STATUS, curses.COLOR_BLACK, curses.COLOR_WHITE)
        else:
            curses.init_pair(Colors.CURRENT_LINE, curses.COLOR_CYAN, curses.COLOR_BLACK)
            curses.init_pair(Colors.UNEXPANDED, curses.COLOR_CYAN, curses.COLOR_BLACK)
            curses.init_pair(Colors.EXPANDED, curses.COLOR_BLACK, curses.COLOR_CYAN)
            curses.init_pair(Colors.MESSAGE, curses.COLOR_CYAN, curses.COLOR_BLACK)
            curses.init_pair(Colors.STATUS, curses.COLOR_BLACK, curses.COLOR_WHITE)

        self.height = 0
        self.width = 0
        self.height, self.width = self.scr.getmaxyx()

        self.cursor = {
            'x': 0,
            'mid': 0,
            'msg': None,
        }

    def get_mid(self, mid_idx=None):
        if mid_idx is None:
            mid_idx = self.cursor['mid']
        return itertools.islice(self.msgs.values()), mid_idx, mid_idx)[0]

    def get_msg(self, mid_idx=None, msg_idx=None):
        if mid_idx is None:
            mid_idx = self.cursor['mid']
        mid = self.get_mid(mid_idx)

        if msg_idx is None
            msg_idx = self.cursor['msg']
        return itertools.islice(mid['msgs'].values()), msg_idx, msg_idx)[0]

    @property
    def num_lines(self):
        """
        Returns the number of text lines to be displayed.  This is the number
        of mids captured plus the number of messages in each mid that is
        expanded.
        """
        lines = len(self.msgs)
        lines += sum(len(m['msgs']) for m in self.msgs.values() if m['expand'])
        return lines

    @property
    def cur_line(self):
        """
        Returns the current virtual line the cursor is on.
        """
        line = 0
        for mid_idx, mid in enumerate(self.msgs.values()):
            if mid_idx == self.cursor['mid']:
                if mid['expand'] and self.cursor['msg'] is not None:
                    # The current virtual line is the count up until now +1 for 
                    # the MID row + the msg index
                    return line + 1 + self.cursor['msg']
                else:
                    # The current virtual line is the current count
                    return line
            elif mid['expand']:
                # Add the number of msgs in this mid +1 for the MID row
                lines += 1 + len(mid['msgs'])
            else:
                # The mid is not expanded, just +1 or the MID row and move on
                lines += 1

    @property
    def msg_win_height(self):
        return self.height - 1

    @property
    def max_x_pos(self):
        return min(self.num_lines, self.msg_win_height)

    def update_status(self):
        left = f' MID {self.cursor["mid"] + 1} of {len(self.msgs)} |'

        # The middle status field is only shown when the cursor has selected 
        # a message in an expanded MID
        if self.cursor['msg'] is not None:
            msgs_in_mid = len(self.msgs[self.cursor['mid']])
            middle = f' MSG {self.cursor["msg"] + 1} of {msgs_in_mid} |'
        else:
            middle = ''

        right = f' {self.msgcount} messages received '

        if self.width > (len(left) + len(middle) + len(right)):
            # Add an extra '|" between the middle and right side status msgs
            middle_padding = ' ' * (self.width - len(left) - len(middle) - len(right))
            status = left + middle + middle_padding + '|' + right
        else:
            # The msgs will get truncated as the window width shrinks, but it's 
            # too much trouble to make them shrink relative to each other when 
            # there are more than 2 fields in the status bar.
            status = left + middle + right

        self.scr.attron(curses.color_pair(Colors.STATUS))

        # NOTE: all the examples I see online use addstr() but if I attempt to 
        #       addstr() a character to the lower right character that 
        #       definitely is within the allowed x, y size, curses crashes.  But 
        #       insstr() doesn't do this for mysterious reasons.  Use insnstr() 
        #       to ensure that we won't write beyond the bounds of the window.
        self.scr.insnstr(self.msg_win_height, 0, status, self.width)

        self.scr.attroff(curses.color_pair(Colors.STATUS))

    def update_msgs(self):
        # TODO: This would require less processing if a curses pad was used and 
        #       lines weren't re-written unless necessary. Not sure it's worth 
        #       the time to implement that.

        # If the window was resized the current message/row may now be beyond 
        # the current window size, if this is the case adjust the cursor 'x' 
        # value now
        if self.cursor['x'] >= self.max_x_pos:
            self.cursor['x'] = self.max_x_pos - 1

        # The x position + (num msgs - current msg) indicates how many messages 
        # the slice will extract.  If this is smaller than max_x_pos increase 
        # the x position until the max number of msgs are displayed
        slice_size = self.cursor['x'] + (self.num_lines - self.cur_line)

        if slice_size < self.max_x_pos:
            self.cursor['x'] += self.max_x_pos - slice_size

        # Get a slice of messages to display based on the current msg position, 
        # the current X position, and the number of messages to display.
        slice_start = self.cur_line - self.cursor['x']
        slice_end = slice_start + self.max_x_pos

        msgs_slice = itertools.islice(enumerate(self.msgs.values()), slice_start, slice_end)
        row = 0
        for msg_idx, msg in msgs_slice:
            pidlist = ', '.join([str(p.pid) for p in msg.pids])
            msgstr = f'{msg.src} [{msg.mid}]: {pidlist}'

            if msg_idx == self.cursor['mid']:
                self.scr.attron(curses.color_pair(Colors.CURRENT_LINE))
                self.scr.attron(curses.A_BOLD)
            else:
                self.scr.attron(curses.color_pair(Colors.UNEXPANDED))

            self.scr.insnstr(row, 0, msgstr, self.width)

            if msg_idx == self.cursor['mid']:
                self.scr.attroff(curses.A_BOLD)
                self.scr.attroff(curses.color_pair(Colors.CURRENT_LINE))
            else:
                self.scr.attroff(curses.color_pair(Colors.UNEXPANDED))

            row += 1

    def _key_down(self, lines):
        self.cursor['x'] += lines
        self.cursor['mid'] += lines

        # If the number of messages to display is > the height, stop moving when 
        # the height is reached. Otherwise stop moving the "X" position when the 
        # last message is reached.
        if self.cursor['x'] >= self.max_x_pos:
            self.cursor['x'] = self.max_x_pos - 1

        # If the current mid is expanded, increment the msg index
        if self.cursor['mid'] 
        if self.cursor['mid'] >= len(self.msgs):
            self.cursor['mid'] = len(self.msgs) - 1

    def _key_up(self, lines):
        self.cursor['x'] -= lines
        self.cursor['mid'] -= lines

        if self.cursor['x'] < 0:
            self.cursor['x'] = 0
        if self.cursor['mid'] < 0:
            self.cursor['mid'] = 0

    def process_key(self, key):
        if key == curses.KEY_RESIZE:
            self.height, self.width = self.scr.getmaxyx()

        elif key == curses.KEY_DOWN:
            self._key_down(1)

        elif key == curses.KEY_UP:
            self._key_up(1)

        elif key == curses.KEY_NPAGE:
            self._key_down(self.msg_win_height)

        elif key == curses.KEY_PPAGE:
            self._key_page_up(self.msg_win_height)

    def run(self):
        ch = -1
        msgs_updated = False
        input_rcvd = False
        try:
            while ch != ord('q'):
                try:
                    # Will return None if there has been no new complete message
                    msg = next(self.iface)
                except StopIteration:
                    # The exception raised when parsed log has reached the end 
                    # of the messages. When this happens, to lower processor 
                    # usage but still remain responsive disable no-delay mode
                    self.scr.nodelay(0)
                    msg = None

                if msg is not None:
                    self.msgcount += 1
                    self.log.logmsg(msg)

                    mid_key = msg.mid.mid
                    msg_key = tuple(p.pid for p in msg.pids)

                    if mid_key not in self.msgs:
                        self.msgs[mid_key] = {'expand': False, 'msgs': {}}

                    if msg_key not in self.msgs[mid_key]:
                        self.msgs[mid_key]['msgs'][msg_key] = [msg]

                    msgs_updated = True

                if ch != -1:
                    self.process_key(ch)

                if ch != -1 or msgs_updated:
                    self.scr.clear()
                    self.update_msgs()
                    self.update_status()
                    self.scr.refresh()

                ch = self.scr.getch()
                msgs_updated = False

        except KeyboardInterrupt:
            pass


def run(stdscr, reparse_log=None, log_filename=None):
    sniffer = Sniffer(stdscr, reparse_log=reparse_log, log_filename=log_filename)
    sniffer.run()


def main():
    # TODO:
    #   1. Implement ability to Tx PID 195 to request info or clear DTCs
    #   2. Implement the ability to send commands/messages
    #   3. Support importing a raw 485 log?
    parser = argparse.ArgumentParser()
    parser.add_argument('--reparse-log', '-r',
            help='read J1708 messages from an existing log and re-parse them')
    parser.add_argument('--output-log', '-o',
            help='Save output to a log file')
    args = parser.parse_args()

    curses.wrapper(run, reparse_log=args.reparse_log, log_filename=args.output_log)
