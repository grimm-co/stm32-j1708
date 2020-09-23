import struct
import serial
import serial.tools.list_ports

from .msg import J1708


def find_device():
    """
    Identifies if there are any USB devices that match the VID:PID and device
    strings expected for the J1708 tool.
    """
    for p in serial.tools.list_ports.grep('0483:5740'): 
        if 'j1708' in p.manufacturer.lower():
            return p.device
    return None


def _print_and_log(msg, log=None):
    if log:
        log.write(msg)
    print(msg)


def decode_and_print(raw_msg, decode=True, explicit_flags=False, ignore_checksums=False, log=None):
    try:
        j1708_msg = J1708(raw_msg, ignore_checksums)
        if j1708_msg is not None and j1708_msg.is_valid():
                if decode:
                    logmsg = j1708_msg.format_for_log(explicit_flags=explicit_flags)
                    _print_and_log(logmsg, log=log)
                else:
                    _print_and_log(str(j1708_msg), log=log)
        else:
            _print_and_log(f'INVALID CHECKSUM: {j1708_msg}', log=log)
        return j1708_msg
    except ValueError:
        _print_and_log(f'INVALID MSG: {raw_msg.hex()}', log=log)
        return None


class Iface(object):
    def __init__(self, port=None, speed=115200, som=None, eom=None):
        self.port = port
        self.speed = speed

        if som is None:
            self._som = b'$'
        if eom is None:
            self._eom = b'*'

        self.serial = None
        self.open()

    def __del__(self):
        self.close()

    def open(self):
        if self.port is not None and self.serial is None:
            self.serial = serial.Serial(port=self.port, baudrate=self.speed)

    def close(self):
        if self.serial is not None:
            self.serial.close()
            self.serial = None

    def send(self, msg):
        # In theory the struck.pack method is the fastest way to convert an 
        # integer to a single byte
        msg_bytes = msg + struct.pack('>B', J1708.calc_checksum(msg))

        # Convert the message into printable hex, then that string back to 
        # bytes, then wrap that in the msg delimiters and send it
        data = self._som + msg_bytes.hex().encode() + self._eom

        self.serial.write(data)
        self.serial.flush()

    def read(self):
        read_bytes = self.serial.in_waiting
        return self.serial.read(read_bytes)

    def run(self, decode=True, ignore_checksums=False, log_filename=None):
        if log_filename:
            log = open(log_filename, 'w')
        else:
            log = None

        msg = b''
        incoming = False
        while True:
            char = self.serial.read()
            if not incoming and char == self._som:
                incoming = True
            elif incoming and char != self._eom:
                msg += char
            elif incoming and char == self._eom:
                decode_and_print(msg, decode=decode, ignore_checksums=ignore_checksums, log=log)

                # Clear the message
                msg = b''
                incoming = False

    def read_from_file(self, filename, decode=True, ignore_checksums=False, log_filename=None):
        if log_filename:
            log = open(log_filename, 'w')
        else:
            log = None

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

                    decode_and_print(msg, decode=decode, ignore_checksums=ignore_checksums, log=log)

                    # Clear the message
                    msg = b''
                    incoming = False

    def reparse_log(self, filename, decode=True, ignore_checksums=False, log_filename=None):
        if log_filename:
            log = open(log_filename, 'w')
        else:
            log = None

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

                    decode_and_print(msg, decode=decode, ignore_checksums=ignore_checksums, log=log)

                    # Clear the message
                    msg = b''
                    incoming = False


__all__ = [
    'find_device',
    'decode_and_print',
    'Iface',
]
