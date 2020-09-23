import sys

from .msg import J1708


class Log(object):
    def __init__(self, decode=True, explicit_flags=False, ignore_checksums=False, log_filename=None, stdout=True):
        # Save the format/decode settings
        self._decode = decode
        self._explicit_flags = explicit_flags
        self._ignore_checksums = ignore_checksums

        # Open the output files
        self._filename = log_filename
        self._logs = []
        if log_filename:
            self._fds.append(open(log_filename, 'w'))
        if stdout:
            self._fds.append(sys.stdout)

    def __del__(self):
        for fd in self._fds:
            if fd != sys.stdout:
                fd.close()
        self._fds = []

    def write(self, msg, end='\n'):
        # Force the message to be a string
        if not isinstance(msg, str):
            msg = str(msg)

        # Check for the end char
        if end is not None and msg[-1] != end:
            msg += end

        for fd in self._fds:
            fd.write(msg)

    def logmsg(self, msg):
        if isinstance(msg, str):
            # If this is a string, log it
            self.write(msg)
        else:
            if isinstance(msg, bytes):
                # decode this as a J1708 message
                j1708_msg = J1708(msg, self._ignore_checksums)
            else:
                # Assume it already is a J1708 message
                j1708_msg = msg

            if j1708_msg is not None and j1708_msg.is_valid():
                if self._decode:
                    logmsg = j1708_msg.format_for_log(explicit_flags=explicit_flags)
                    self.write(logmsg)
                else:
                    self.write(j1708_msg)
            else:
                self.write(f'INVALID CHECKSUM: {j1708_msg}')


def read_msgs(filename):
    msg_pat = re.compile(r'^[^ ].*\([0-9]+\): ([0-9A-Fa-f]+) \(([0-9A-Fa-f]+)\)')
    with open(filename, 'r') as logfile:
        for line in logfile:
            match = msg_pat.match(line)
            if match:
                msgbody, msgchksum = match.groups()
                if len(msgchksum) < 2:
                    msg = msgbody + '0' + msgchksum
                else:
                    msg = msgbody + msgchksum
                yield msg

                # Clear the message
                msg = b''
                incoming = False


def reparse(filename, decode=True, ignore_checksums=False, log_filename=None):
    log = Log(decode=decode, ignore_checksums=ignore_checksums, log_filename=log_filename)
    for msg in read_msgs(filename):
        log.logmsg(msg)


__all__ = [
    'read_msgs',
    'reparse',
    'Log',
]
