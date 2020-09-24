import argparse
import curses
import enum
import itertools
import os

from .. import iface
from .. import log


class Colors(enum.IntEnum):
    CURRENT_LINE = 1
    UNEXPANDED = 2
    EXPANDED = 3
    STATUS = 4


def _msg_key_str(msg):
    pidlist_str = '_'.join([str(p['pid']) for p in msg.pids])
    return f'{msg.mid["mid"]}:{pidlist_str}'


class Sniffer(object):
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
            #   dark gray (Grey11)   = 234
            curses.init_pair(Colors.CURRENT_LINE, curses.COLOR_CYAN, 234)
            curses.init_pair(Colors.UNEXPANDED, curses.COLOR_CYAN, curses.COLOR_BLACK)
            curses.init_pair(Colors.EXPANDED, curses.COLOR_BLACK, curses.COLOR_CYAN)
            curses.init_pair(Colors.STATUS, curses.COLOR_BLACK, curses.COLOR_WHITE)
        else:
            curses.init_pair(Colors.CURRENT_LINE, curses.COLOR_CYAN, curses.COLOR_BLACK)
            curses.init_pair(Colors.UNEXPANDED, curses.COLOR_CYAN, curses.COLOR_BLACK)
            curses.init_pair(Colors.EXPANDED, curses.COLOR_BLACK, curses.COLOR_CYAN)
            curses.init_pair(Colors.STATUS, curses.COLOR_BLACK, curses.COLOR_WHITE)

        self.height = 0
        self.width = 0
        self.height, self.width = self.scr.getmaxyx()

        self.cursor = {
            'x': 0,
            'msg': 0,
            'expand': False
        }

    @property
    def max_x_pos(self):
        return min(len(self.msgs), self.height - 1)

    def update_status(self):
        statusleft = f' {self.cursor["msg"] + 1} of {len(self.msgs)} |'
        lenl = len(statusleft)
        statusright = f' {self.msgcount} messages received_'
        lenr = len(statusright)

        if self.width > lenl + lenr:
            # Add an extra '|" before the right side status
            middle_padding = ' ' * ((self.width - 1) - lenl - lenr)
            status = statusleft + middle_padding + '|' + statusright
        elif self.width == lenl + lenr:
            status = statusleft + statusright
        else:
            # How many chars need trimmed? We will re-insert the ' |' between 
            # the messages so for now just use the original length of the status 
            # messages.
            trim = (lenl + lenr) - self.width

            # Trim the status bar msgs from the right side first until the left 
            # and right are the same size.  There is more unnecessary characters 
            # on the right status message.
            # Account for the ' |' separator at the end of the left status msg
            if lenr - trim < (lenl - 2):
                # Calculate how much needs trimmed if we have left and right the 
                # same size (with the ' |' separator)
                trim_from_both = ((lenl - 2) * 2) - (self.width - 2)
                trim_left = trim_from_both // 2
                trim_right = trim - (trim_from_both - trim_left)

                trimmedleft = statusleft[:-(trim_left + 2)]
                trimmedright = statusright[:-trim_right]

                status = trimmedleft + ' |' + trimmedright
            else:
                status = statusleft + statusright[:-trim]

        self.scr.attron(curses.color_pair(Colors.STATUS))

        # NOTE: all the examples I see online use addstr() but if I attempt to 
        #       addstr() a character to the lower right character that 
        #       definitely is within the allowed x, y size, curses crashes.  But 
        #       insstr() doesn't do this for mysterious reasons.  Use insnstr() 
        #       to ensure that we won't write beyond the bounds of the window.
        self.scr.insnstr(self.height - 1, 0, status, self.width)

        self.scr.attroff(curses.color_pair(Colors.STATUS))

    def update_msgs(self):
        # If the window was resized the current message/row may now be beyond 
        # the current window size, if this is the case adjust the cursor 'x' 
        # value now
        if self.cursor['x'] >= self.max_x_pos:
            self.cursor['x'] = self.max_x_pos - 1

        # The x position + (num msgs - current msg) indicates how many messages 
        # the slice will extract.  If this is smaller than max_x_pos increase 
        # the x position until the max number of msgs are displayed
        slice_size = self.cursor['x'] + (len(self.msgs) - self.cursor['msg'])

        if slice_size < self.max_x_pos:
            self.cursor['x'] += self.max_x_pos - slice_size

        # Get a slice of messages to display based on the current msg position, 
        # the current X position, and the number of messages to display.
        slice_start = self.cursor['msg'] - self.cursor['x']
        slice_end = slice_start + self.max_x_pos

        msgs_slice = itertools.islice(enumerate(self.msgs.values()), slice_start, slice_end)
        row = 0
        for msg_idx, msg in msgs_slice:
            pidlist = ', '.join([str(p['pid']) for p in msg.pids])
            msgstr = f'{msg.mid["name"]} [{msg.mid["mid"]}]: {pidlist}'

            if msg_idx == self.cursor['msg']:
                self.scr.attron(curses.color_pair(Colors.CURRENT_LINE))
                self.scr.attron(curses.A_BOLD)
            else:
                self.scr.attron(curses.color_pair(Colors.UNEXPANDED))

            self.scr.insnstr(row, 0, msgstr, self.width)

            if msg_idx == self.cursor['msg']:
                self.scr.attroff(curses.A_BOLD)
                self.scr.attroff(curses.color_pair(Colors.CURRENT_LINE))
            else:
                self.scr.attroff(curses.color_pair(Colors.UNEXPANDED))

            row += 1

    def _key_down(self):
        self.cursor['x'] += 1
        self.cursor['msg'] += 1

        # If the number of messages to display is > the height, stop moving when 
        # the height is reached. Otherwise stop moving the "X" position when the 
        # last message is reached.
        if self.cursor['x'] >= self.max_x_pos:
            self.cursor['x'] = self.max_x_pos - 1
        if self.cursor['msg'] >= len(self.msgs):
            self.cursor['msg'] = len(self.msgs) - 1

    def _key_up(self):
        self.cursor['x'] -= 1
        self.cursor['msg'] -= 1

        if self.cursor['x'] < 0:
            self.cursor['x'] = 0
        if self.cursor['msg'] < 0:
            self.cursor['msg'] = 0

    def _key_page_down(self):
        self.cursor['x'] += self.height + 1
        self.cursor['msg'] += self.height + 1

        if self.cursor['x'] >= self.max_x_pos:
            self.cursor['x'] = self.max_x_pos - 1
        if self.cursor['msg'] >= len(self.msgs):
            self.cursor['msg'] = len(self.msgs) - 1

    def _key_page_up(self):
        self.cursor['x'] -= self.height - 1
        self.cursor['msg'] -= self.height - 1

        if self.cursor['x'] < 0:
            self.cursor['x'] = 0
        if self.cursor['msg'] < 0:
            self.cursor['msg'] = 0

    def process_key(self, key):
        if key == curses.KEY_RESIZE:
            self.height, self.width = self.scr.getmaxyx()

        elif key == curses.KEY_DOWN:
            self._key_down()

        elif key == curses.KEY_UP:
            self._key_up()

        elif key == curses.KEY_NPAGE:
            self._key_page_down()

        elif key == curses.KEY_PPAGE:
            self._key_page_up()

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
                    # of the messages.
                    msg = None

                if msg is not None:
                    self.msgcount += 1
                    self.log.logmsg(msg)
                    key = _msg_key_str(msg)
                    self.msgs[key] = msg
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
