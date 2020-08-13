import serial
import mids
import pids

class J1708(object):
    def __init__(self, msg, checksum=None):
        self.msg = msg
        if checksum is None:
            self.checksum = self.calc_checksum()
        else:
            self.checksum = checksum

        self.mid = None
        self.body = None
        self.pids = None

    @classmethod
    def calc_checksum(cls, msg):
        chksum = 0
        for char in msg:
            chksum += char
            chksum &= 0xFF
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

    def decode(self):
        if self.mid is None:
            self.mid, self.body = mids.extract(self.msg)
            self.pids = []
            body = self.body
            while body != b'':
                param, body = pids.extract(body)
                self.pids.append(param)

        print(f'{self.mid["name"]} ({self.mid["mid"]}): {self}')
        for pid in self.pids:
            print(f'  {pid["pid"]}: {pid["name"]}\n    {pid["data"].hex()}')

    def __str__(self):
        return f'{self.msg.hex()} ({hex(self.checksum)})'


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
        data = self._som + msg + J1708.calc_checksum(msg).to_bytes(1, 'big') + self._eom
        self.serial.write(data)
        self.serial.flush()

    def read(self):
        read_bytes = self.serial.in_waiting
        return self.serial.read(read_bytes)

    def run(self):
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
                if j1708_msg is not None:
                    #print(j1708_msg)
                    j1708_msg.decode()
                else:
                    print(f'INVALID: {msg}')

                # Clear the message
                msg = b''
                incoming = False

