import time
import string
import re
import struct
import json

from . import mids
from . import pids
from .exceptions import *


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


def make_pid_list_string(pid, value, explicit_flags=False, **kwargs):
    if 'raw' in pid:
        prefix_str = f'\n    {pid["raw"].hex().upper()}:'
    else:
        prefix_str = f'\n    '

    if len(value) == 0:
        return f'{prefix_str} NONE'
    else:
        formatted_values = []
        for val in value:
            formatted = format_pid_value(**kwargs, pid=pid, value=val, explicit_flags=explicit_flags)
            if not formatted.endswith('_OFF') or explicit_flags:
                # Remove any leading whitespace from the formatted value
                formatted_values.append(formatted.lstrip())

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


class J1708:
    def __init__(self, msg=None, timestamp=None, mid=None, pids=None, decode=True, ignore_checksum=False, rate=None):
        self.msg = None
        self.checksum = None
        self.mid = None
        self.pids = None
        self.rate = rate

        if timestamp is None:
            self.time = time.time()
        else:
            self.time = timestamp

        if msg is not None:
            self._init_from_msg(msg, ignore_checksum=ignore_checksum)
            if decode:
                self.decode()
        else:
            assert mid is not None
            self.mid = mids.get_mid(mid)

            if not isinstance(pids, list):
                self.pids = [{'pid': pids['pid'], 'value': None}]
            else:
                self.pids = [{'pid': p, 'value': None} for p in pids]

        self._pid_map = {}
        for pid in self.pids:
            self._pid_map[pid['pid']] = pid

    def __getitem__(self, key):
        return self._pid_map[key]['value']

    def __setitem__(self, key, value):
        if key in self._pid_map:
            self._pid_map[key]['value'] = value
        else:
            self._pid_map[key] = {'pid': key, 'value': value}

    @classmethod
    def calc_checksum(cls, msg):
        chksum = 0
        for char in msg:
            chksum = (chksum + char) & 0xFF

        if chksum != 0:
            # Determine what the checksum _should_ be
            chksum = 0x100 - chksum
        return chksum

    def update_checksum(self):
        self.checksum = self.calc_checksum(self.msg)

        # In theory the struck.pack method is the fastest way to convert an 
        # integer to a single byte
        self.msg += self.msg + struct.pack('>B', self.checksum)

    def _init_from_msg(self, data, ignore_checksum=False):
        if all(chr(c) in string.hexdigits for c in data):
            # Convert from printable hex to actual bytes
            if isinstance(data, bytes) or isinstance(data, bytearray):
                msg = bytes.fromhex(data.decode('latin-1'))
            else:
                msg = bytes.fromhex(data)
        else:
            msg = data

        # If the message is valid calculating a checksum over the message and 
        # current checksum will add up to 0.
        if len(msg) >= 2 and self.calc_checksum(msg) == 0:
            self.msg = msg
            self.checksum = msg[-1]
        elif ignore_checksum:
            self.msg = msg
        else:
            raise J1708ChecksumError(f'Invalid checksum {msg[-1]} for msg {msg[:-1].hex()}')

    def is_valid(self):
        return self.checksum is not None

    def decode(self):
        if self.mid is None:
            self.mid, rest = mids.decode(self.msg)
            self.pids = []

            # assume the last byte of the message is the checksum
            body = rest[:-1]
            while body != b'':
                param, body = pids.decode(body)
                if param:
                    self.pids.append(param)
                else:
                    # This message is invalid
                    raise J1708DecodeError(f'WARNING: unable to extract valid PID from {body}')

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
            self.msg = mids.encode(self.mid) + pids.encode(self.pids)
            self.update_checksum()

        elif not self.is_valid():
            self.update_checksum()

        if len(self.msg) > 21:
            # TODO: need to wrap segment this message using PID 192
            raise NotImplementedError(f'encoded msg too long ({len(raw_msg)}): need to implement msg segmentation using PID 192')

        return self.msg

    def __str__(self):
        if self.msg is None:
            self.encode()

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
            'pids': pids.export(self.pids, mid=self.mid),
        }
        return obj

    def json(self):
        return json.dumps(self.export())


__all__ = [
    'J1708',
]
