import struct
import serial
import serial.tools.list_ports

from .msg import J1708
from .log import Log


def find_device():
    """
    Identifies if there are any USB devices that match the VID:PID and device
    strings expected for the J1708 tool.
    """
    for p in serial.tools.list_ports.grep('0483:5740'): 
        if 'j1708' in p.manufacturer.lower():
            return p.device
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
        """
        nonblocking read pending characters
        """
        read_bytes = self.serial.in_waiting
        return self.serial.read(read_bytes)

    def readmsg(self):
        """
        blocking read and return an entire message 
        """
        msg = b''
        incoming = False
        while True:
            char = self.serial.read()
            if not incoming and char == self._som:
                incoming = True
            elif incoming and char != self._eom:
                msg += char
            elif incoming and char == self._eom:
                return msg

    def __iter__(self):
        """
        Nothing special to do to prepare this object to be an iterator
        """
        return self

    def __next__(self):
        """
        Blocks until a message is received.  Never stops.
        """
        return self.readmsg()

    def run(self, decode=True, ignore_checksums=False, log_filename=None):
        """
        Dump and decode J1708 messages until interrupted.
        """
        log = Log(decode=decode, ignore_checksums=ignore_checksums, log_filename=log_filename)
        try:
            for msg in self:
                log.logmsg(msg)
        except KeyboardInterrupt:
            # Add a return char to help make the next command prompt look nice
            print('')


__all__ = [
    'find_device',
    'Iface',
]
