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
        if 'j1708 tool' in p.description.lower():
            return p.device
    return None


# TODO: Add an easy way to track multi-section "conversations"


class Iface:
    def __init__(self, port=None, speed=115200, som=None, eom=None, timeout=None):
        self.port = port
        self.speed = speed
        self.timeout = timeout

        if som is None:
            self._som = b'$'
        if eom is None:
            self._eom = b'*'

        # Used to track incoming messages.  If a timeout is specified then 
        # readmsg() may not be able to read a full message and any bytes 
        # received need to be saved for the next read attempt.
        self.msg = b''
        self.incoming = False

        self.serial = None
        self.open()

    def __del__(self):
        self.close()

    def open(self):
        if self.port is not None and self.serial is None:
            self.serial = serial.Serial(port=self.port, baudrate=self.speed, timeout=self.timeout)

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

    def readmsg(self, timeout=None):
        """
        blocking read and return an entire message
        """
        # If a timeout is specified, override the initialization value for this 
        # port
        if timeout is not None:
            self.serial.timeout = timeout

        while True:
            char = self.serial.read()

            if char is None:
                # Timeout occurred
                if timeout is not None:
                    self.serial.timeout = self.timeout
                return None

            if not self.incoming and char == self._som:
                self.incoming = True
            elif self.incoming and char != self._eom:
                self.msg += char
            elif self.incoming and char == self._eom:
                msg = self.msg

                # Clear the in-progress message values before returning
                self.msg = b''
                self.incoming = False

                if timeout is not None:
                    self.serial.timeout = self.timeout
                return msg

    def __iter__(self):
        """
        Nothing special to do to prepare this object to be an iterator
        """
        return self

    def __next__(self, timeout=None):
        """
        Blocks until a message is received.  Never stops.  If a timeout occurs
        will return None.
        """
        return self.readmsg(timeout=timeout)

    def run(self, decode=True, ignore_checksum=False, log_filename=None):
        """
        Dump and decode J1708 messages until interrupted.
        """
        log = Log(decode=decode, ignore_checksum=ignore_checksum, log_filename=log_filename)
        try:
            for msg in self:
                if msg is not None:
                    log.logmsg(msg)
        except KeyboardInterrupt:
            # Add a return char to help make the next command prompt look nice
            print('')


__all__ = [
    'find_device',
    'Iface',
]
