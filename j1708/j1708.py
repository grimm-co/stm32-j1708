import struct
import serial

from .msg import J1708


def decode_and_print(raw_msg, decode=True, ignore_checksums=False):
    j1708_msg = J1708.make(raw_msg, ignore_checksums)

    if j1708_msg.is_valid():
        try:
            if decode:
                print(j1708_msg.format_for_log())
            else:
                print(j1708_msg)
        except ValueError:
            print(f'INVALID MSG: {j1708_msg}')
    else:
        print(f'INVALID CHECKSUM: {j1708_msg}')

    return j1708_msg


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

    def run(self, decode=True, ignore_checksums=False):
        msg = b''
        incoming = False
        while True:
            char = self.serial.read()
            if not incoming and char == self._som:
                incoming = True
            elif incoming and char != self._eom:
                msg += char
            elif incoming and char == self._eom:
                decode_and_print(msg, decode=decode, ignore_checksums=ignore_checksums)

                # Clear the message
                msg = b''
                incoming = False

    def reparse_log(self, filename, decode=True, ignore_checksums=False):
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

                    decode_and_print(msg, ignore_checksums)

                    # Clear the message
                    msg = b''
                    incoming = False

