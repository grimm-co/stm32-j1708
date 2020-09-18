import time
import re
import struct
import serial
import serial.tools.list_ports

from . import mids
from . import pids
from .sid_consts import *
from .pid_types import *


def find_device():
    """
    Identifies if there are any USB devices that match the VID:PID and device
    strings expected for the J1708 tool.
    """
    for p in serial.tools.list_ports.grep('0483:5740'): 
        if 'j1708' in p.manufacturer.lower():
            return p.device
    return None


def make_pid_dict_string(value, **kwargs):
    flags = values.pop('flags')

    pid_str = ''
    for field, value in values:
        pid_str += f'\n    {field}: {value}'

    if flags:
        #if all(f.name.endswith('_OFF') for f in flags):
        #    pid_str += '\n    flags: NONE'
        #else:
        flag_str = ', '.join(str(f) for f in flags)
        pid_str += f'\n    flags: {flag_str}'
    return pid_str


_whitespace_pat = re.compile(r'^\s+')
def make_pid_list_string(pid, value, **kwargs):
    if len(value) == 0:
        return f'\n    {pid["raw"].hex().upper()}: NONE'
    else:
        # Special case: If this is a list of flags, and all of the flags end in 
        # '_OFF' just display the flag values as "NONE"
        #try:
        #    if all(f.name.endswith('_OFF') for f in value):
        #        return f'    {pid["raw"].hex().upper()}: NONE'
        #except AttributeError:
        #    pass

        prefix_str = f'    {pid["raw"].hex().upper()}: '
        formatted_values = []
        for val in value:
            formattedstr = format_pid_value(**kwargs, pid=pid, value=val)
            # Drop the leading spaces from the formatted value
            formatted_values.append(_whitespace_pat.sub('', formattedstr))

        #space_prefix = ' ' * len(prefix_str)
        #pid_strs = ['\n' + prefix_str + formatted_values[0]]
        #pid_strs.extend(space_prefix + entry for entry in formatted_values[1:])
        #return '\n'.join(pid_strs)
        return '\n' + prefix_str + ', '.join(formatted_values)


def make_pid_bytes_string(value, **kwargs):
    return f'\n    {value.hex().upper()}'


def make_pid_string(value, **kwargs):
    return f'\n    {value}'


def format_pid_value(value, **kwargs):
    if hasattr(value, 'format'):
        return '\n    ' + value.format(**kwargs)
    elif isinstance(value, dict):
        return make_pid_dict_string(**kwargs, value=value)
    elif isinstance(value, list):
        return make_pid_list_string(**kwargs, value=value)
    elif isinstance(value, bytes):
        return make_pid_bytes_string(**kwargs, value=value)
    else:
        return make_pid_string(**kwargs, value=value)


class J1708(object):
    def __init__(self, msg, checksum=None, timestamp=None):
        self.msg = msg
        self.checksum = checksum

        self.mid = None
        self.body = None
        self.pids = None

        if timestamp is None:
            self.time = time.time()
        else:
            self.time = timestamp

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
    def make(cls, data, ignore_checksum=False):
        # Convert from printable hex to actual bytes
        if isinstance(data, bytes):
            msg = bytes.fromhex(data.decode('latin-1'))
        else:
            msg = bytes.fromhex(data)

        # If the message is valid calculating a checksum over the message and 
        # current checksum will add up to 0.
        if len(msg) >= 2 and cls.calc_checksum(msg) == 0 and not ignore_checksum:
            return cls(msg[:-1], msg[-1])
        elif len(msg) >= 2 and cls.calc_checksum(msg) != 0 and ignore_checksum:
            return cls(msg, None)
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
                if param:
                    self.pids.append(param)
                else:
                    # This message is invalid
                    raise ValueError(f'WARNING: unable to extract valid PID from {body}')

    def format_for_log(self):
        self.decode()
        out = f'\n{self.mid["name"]} ({self.mid["mid"]}): {self}\n'
        for pid in self.pids:
            out += f'  {pid["pid"]}: {pid["name"]}'
            out += format_pid_value(mid=self.mid, pid=pid, value=pid['value'])
        return out

    def encode(self):
        # If there is no message defined yet, encode the mid and pids into 
        # a message
        if self.msg is None:
            raise NotImplementedError

        # If this message is not valid, update the checksum now and then append 
        # it to the message bytes
        if not self.is_valid():
            self.update_checksum()

        # In theory the struck.pack method is the fastest way to convert an 
        # integer to a single byte
        return self.msg + struct.pack('>B', self.checksum)

    def __str__(self):
        if self.checksum is not None:
            return f'{self.msg.hex().upper()} ({self.checksum:X})'
        else:
            return f'{self.msg.hex().upper()} ({self.checksum})'

    def export(self):
        self.decode()
        obj = {
            'time': self.time,
            'mid': self.mid['mid'],
            'checksum': self.checksum,
            'pids': self.pids,
        }
        return obj

    def json(self):
        return json.dumps(self.export())


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

