import struct
import serial
import serial.tools.list_ports

import mids
import pids


def find_device():
    """
    Identifies if there are any USB devices that match the VID:PID and device
    strings expected for the J1708 tool.
    """
    for p in serial.tools.list_ports.grep('0483:5740'): 
        if 'j1708' in p.manufacturer.lower():
            return p.device
    return None


class J1708(object):
    def __init__(self, msg, checksum=None):
        self.msg = msg
        self.checksum = checksum

        self.mid = None
        self.body = None
        self.pids = None

    @classmethod
    def calc_checksum(cls, msg):
        chksum = 0
        for char in msg:
            chksum = (chksum + char) & 0xFF

        if chksum != 0:
            # Determine what the checksum _should_ be
            chksum = 0x100 - chksum
        return chksum

    @classmethod
    def make(cls, data):
        # Convert from printable hex to actual bytes
        if isinstance(data, bytes):
            msg = bytes.fromhex(data.decode('latin-1'))
        else:
            msg = bytes.fromhex(data)

        # If the message is valid calculating a checksum over the message and 
        # current checksum will add up to 0.
        if cls.calc_checksum(msg) == 0:
            return cls(msg[:-1], msg[-1])
        else:
            # The message is invalid, but may be useful for debugging purposes
            return cls(msg=msg, checksum=None)

    def is_valid(self):
        return self.checksum is not None

    def decode(self):
        if self.mid is None:
            self.mid, self.body = mids.extract(self.msg)
            self.pids = []
            body = self.body
            while body != b'':
                param, body = pids.extract(body)
                self.pids.append(param)

        print(f'\n{self.mid["name"]} ({self.mid["mid"]}): {self}')
        for pid in self.pids:
            print(f'  {pid["pid"]}: {pid["name"]}\n    {pid["data"]}')

    def __str__(self):
        if self.checksum is not None:
            return f'{self.msg.hex()} ({hex(self.checksum)})'
        else:
            return f'{self.msg.hex()} ({self.checksum})'


class Iface(object):
    def __init__(self, port, speed=115200, som=None, eom=None):
        self.port = port
        self.speed = speed

        assert self.port
        self.serial = serial.Serial(port=self.port, baudrate=self.speed)

        if som is None:
            self._som = b'$'
        if eom is None:
            self._eom = b'*'

    def __del__(self):
        if self.serial:
            self.serial.close()
            self.serial = None

    def send(self, msg):
        # In theory the struck.pack method is the fastest way to convert an 
        # integer to a single byte
        chksum = struct.pack('>B', J1708.calc_checksum(msg))
        data = self._som + msg + chksum + self._eom

        self.serial.write(data)
        self.serial.flush()

    def read(self):
        read_bytes = self.serial.in_waiting
        return self.serial.read(read_bytes)

    def run(self, decode=True):
        msg = b''
        incoming = False
        while True:
            char = self.serial.read()
            if not incoming and char == self._som:
                incoming = True
            elif incoming and char != self._eom:
                msg += char
            elif incoming and char == self._eom:
                j1708_msg = J1708.make(msg)
                if j1708_msg.is_valid():
                    if decode:
                        j1708_msg.decode()
                    else:
                        print(j1708_msg)
                else:
                    print(f'INVALID: {j1708_msg}')

                # Clear the message
                msg = b''
                incoming = False

