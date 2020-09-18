import time
import string
import re
import struct

from . import mids
from . import pids
from .sid_consts import *
from .pid_types import *


def make_pid_dict_string(value, explicit_flags=False, **kwargs):
    flags = values.pop('flags')

    pid_str = ''
    for field, value in values:
        pid_str += f'\n    {field}: {value}'

    if flags:
        flag_str_list = []
        for flag in flags:
            flag_str = str(f)
            # unless explicit_flags is true, don't include "OFF" values
            if not flag_str.endswith('_OFF') or explicit_flags:
                flag_str_list.append(flag_str)

        if flag_str_list:
            flag_str = ', '.join(flag_str_list)
            pid_str += f'\n    flags: {flag_str}'
        else:
            pid_str += f'\n    flags: NONE'
    return pid_str


_whitespace_pat = re.compile(r'^\s+')
def make_pid_list_string(pid, value, explicit_flags=False, **kwargs):
    if len(value) == 0:
        return f'\n    {pid["raw"].hex().upper()}: NONE'
    else:
        prefix_str = f'\n    {pid["raw"].hex().upper()}:'
        formatted_values = []
        for val in value:
            formatted = format_pid_value(**kwargs, pid=pid, value=val, explicit_flags=explicit_flags)
            if not formatted.endswith('_OFF') or explicit_flags:
                # Remove any leading whitespace from the formatted value
                formatted_values.append(_whitespace_pat.sub('', formatted))

        if formatted_values:
            all_one_line = prefix_str + ' ' + ', '.join(formatted_values)
            if len(all_one_line) < 60:
                return all_one_line
            else:
                # If the value on one line is > 60 chars place each formatted value 
                # into it's own line
                return prefix_str + '\n      ' + '\n      '.join(formatted_values)
        else:
            return prefix_str + ' NONE'


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
    elif isinstance(value, bytes) or isinstance(value, bytearray):
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
        if all(chr(c) in string.hexdigits for c in data):
            # Convert from printable hex to actual bytes
            if isinstance(value, bytes) or isinstance(value, bytearray):
                msg = bytes.fromhex(data.decode('latin-1'))
            else:
                msg = bytes.fromhex(data)
        else:
            msg = data

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

    def format_for_log(self, explicit_flags=False):
        self.decode()
        out = f'{self.mid["name"]} ({self.mid["mid"]}): {self}'
        for pid in self.pids:
            out += f'\n  {pid["pid"]}: {pid["name"]}'
            out += format_pid_value(mid=self.mid, pid=pid, value=pid['value'], explicit_flags=explicit_flags)
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
