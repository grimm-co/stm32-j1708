import sys
import re
import time

from .msg import J1708
from .exceptions import *


class ReplayMsgList:
    def __init__(self, msgs, realtime=False):
        self.msgs = msgs
        self._realtime = realtime

        self._idx = 0
        self._prev_time = None
        self._prev_msg_time = None

    def __iter__(self):
        self._idx = 0
        self._prev_time = None
        self._prev_msg_time = None
        return self

    def __next__(self):
        if self._idx >= len(self.msgs):
            raise StopIteration

        # If the realtime flag is set attempt to duplicate the time messages 
        # were received at previously.
        if self._realtime and self._prev_time is not None:
            # If the previous message did not have a timestamp, use a standard 
            # wait time of 10 msec
            if self._prev_msg_time is None:
                time.sleep(0.01)
            else:
                passed = time.time() - self._prev_time
                wait = self._prev_msg_time - passed
                if wait >= 0:
                    time.sleep(wait)

        self._prev_time = time.time()
        msg = self.msgs[self._idx]
        self._idx += 1

        if hasattr(msg, 'timestamp'):
            self._prev_msg_time = msg.timestamp
        else:
            self._prev_msg_time = None

        return msg

    def __getitem__(self, idx):
        return self.msgs[idx]


class Log:
    def __init__(self, decode=True, explicit_flags=False, ignore_checksums=False, log_filename=None, stdout=True):
        # Save the format/decode settings
        self._decode = decode
        self._explicit_flags = explicit_flags
        self._ignore_checksums = ignore_checksums

        # Open the output files
        self._filename = log_filename
        self._fds = []
        if log_filename:
            self._fds.append(open(log_filename, 'w'))
        if stdout:
            self._fds.append(sys.stdout)

    def __del__(self):
        for fd in self._fds:
            if fd != sys.stdout:
                fd.close()
        self._fds = []

    def write(self, *args, end='\n'):
        if len(args) != 1 or not isinstance(args[0], str):
            # Force the message to be a string
            msg = str(args)
        else:
            msg = args[0]

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
                    logmsg = j1708_msg.format_for_log(explicit_flags=self._explicit_flags)
                    self.write(logmsg)
                else:
                    self.write(j1708_msg)
            else:
                self.write(f'INVALID CHECKSUM: {j1708_msg}')


def read_msgs(filename, realtime=False):
    msgs = []
    msg_pat = re.compile(r'^[^ ].*\([0-9]+\): ([0-9A-Fa-f]+) \(([0-9A-Fa-f]+)\)')
    with open(filename, 'r') as logfile:
        for line in logfile:
            match = msg_pat.match(line)
            if match:
                msgbody, msgchksum = match.groups()

                # The older log style did not include the checksum byte in the 
                # raw message body, but the newer log style does, if the 
                # checksum value matches the last byte of the message assume 
                # this is the newer style.  If a checksum error occurs turning 
                # this into a J1708 message the older style format will be used
                msg_bytes = bytes.fromhex(msgbody)

                try:
                    j1708_msg = J1708(msg_bytes)
                except J1708ChecksumError:
                    # Attempt to use the older log style
                    if len(msgchksum) < 2:
                        msg = msgbody + '0' + msgchksum
                    else:
                        msg = msgbody + msgchksum
                    msg_bytes = bytes.fromhex(msg)

                    try:
                        j1708_msg = J1708(msg_bytes)
                    except J1708ChecksumError:
                        errmsg = f'Unable to decode valid msg from log line "{line}"'
                        raise J1708LogParseError(errmsg)

                #yield j1708_msg
                msgs.append(j1708_msg)

                # Clear the message
                msg = b''
                incoming = False

    return ReplayMsgList(msgs, realtime=realtime)


def reparse(filename, decode=True, ignore_checksums=False, log_filename=None):
    log = Log(decode=decode, ignore_checksums=ignore_checksums, log_filename=log_filename)
    for msg in read_msgs(filename):
        log.logmsg(msg)


__all__ = [
    'read_msgs',
    'reparse',
    'Log',
]
