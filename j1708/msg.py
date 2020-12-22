import time
import string
import re
import struct
import json

from . import mids as j1708_mids
from . import pids as j1708_pids
from j1708.exceptions import *


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
    if pid.raw is not None:
        prefix_str = f'\n    {pid.raw.hex().upper()}:'
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
    def __init__(self, msg=None, timestamp=None, mid=None, pids=None, decode=True, ignore_checksum=False, rate=None, pid=None):
        # Save msg if it was provided
        self._raw = msg
        self.msg = None
        self.checksum = None
        self._mid = None
        self._pids = {}
        self.rate = rate

        if timestamp is None:
            self.time = time.time()
        else:
            self.time = timestamp

        # the "pid" param can make it easier to use interactively when sending 
        # a single PID
        if pids is None and pid is not None:
            pids = [pid]

        if mid is not None and pids is not None:
            self._mid = j1708_mids.J1708MID(mid)

            if isinstance(pids, dict):
                # If the any of the values in this dict are simple types like 
                # int and str assume this is a single-PID dict rather than 
                # a dict of multiple PIDs.
                if any(isinstance(v, (int, str)) for v in pids.values()):
                    self._init_pids([pids])
                else:
                    self._init_pids(pids.values())
            elif isinstance(pids, list):
                self._init_pids(pids)
            else:
                self._init_pids([pids])

        elif msg is not None:
            self._init_from_msg(msg, ignore_checksum=ignore_checksum)
            if decode:
                self.decode()

        else:
            raise J1708Error('Must supply "msg" or "mid" and "pids" params to create {self.__class__.__name__} object')

    def _init_pids(self, pid_list):
        for value in pid_list:
            pid = j1708_pids.J1708PID(value)
            self._pids[pid.pid] = pid

    @property
    def pids(self):
        # return a list of pids from the _pids
        return self._pids.values()

    @property
    def mid(self):
        return self._mid.mid

    @property
    def src(self):
        return self._mid.name

    def __repr__(self):
        if self.msg is None:
            repr_msg = self._raw
        else:
            repr_msg = self.msg

        return f'{self.__class__.__name__}(msg={repr(repr_msg)}, timestamp={repr(self.time)}, mid={self.mid}, pids={repr(list(self.pids))})'

    def __iter__(self):
        return self._pids.__iter__()

    def __contains__(self, key):
        return key in self._pids

    def __getitem__(self, key):
        return self._pids[key].value

    def __setitem__(self, key, value):
        if key in self._pids:
            self._pids[key].value = value
        else:
            self._pids[key] = J1708PID(pid=key, value=value)

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
        self.msg += struct.pack('>B', self.checksum)

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
        if self._mid is None:
            self._mid, rest = j1708_mids.decode(self.msg)

            # assume the last byte of the message is the checksum
            body = rest[:-1]
            self._pids.update(j1708_pids.decode_msg(body))

    @property
    def is_multisection(self):
        if 192 in self._pids or 448 in self._pids:
            if len(self._pids) != 1:
                errmsg = f'Multisection msgs should only have 1 PID ({repr(self)})'
                raise J1708MultisectionError(errmsg)

            # Last sanity check, ensure that the pid type is correct
            param_id = 192 if 192 in self._pids else 448
            if not isinstance(self._pids[param_id].value, j1708_pids.MultisectionParam):
                errmsg = f'Incorrect multisection msg PID type ({repr(self)})'
                raise J1708MultisectionError(errmsg)

            return True
        else:
            return False

    @property
    def section(self):
        if self.is_multisection:
            param_id = 192 if 192 in self._pids else 448
            return self._pids[param_id].value
        return None

    def format_for_log(self, explicit_flags=False):
        self.decode()
        out = f'{self._mid.name} ({self._mid.mid}): {self}'
        for pid in self._pids.values():
            out += f'\n  {pid.pid}: {pid.name}'
            out += format_pid_value(mid=self.mid, pid=pid, value=pid.value, explicit_flags=explicit_flags)
        return out

    def encode(self):
        # If there is no message defined yet, encode the mid and pids into 
        # a message
        if self.msg is None:
            self.msg = j1708_mids.encode(self.mid)
            self.msg += b''.join(j1708_pids.encode(p) for p in self._pids.values())
            self.update_checksum()

        elif not self.is_valid():
            self.update_checksum()

        if len(self.msg) > 21:
            # TODO: need to wrap segment this message using PID 192
            raise NotImplementedError(f'encoded msg too long ({len(raw_msg)}): need to implement msg segmentation using PID 192')

        return self.msg

    def __str__(self):
        if self.msg is not None:
            msg = self.msg.hex()
        elif self._raw is not None:
            msg = self._raw
        else:
            # Need to encode this msg before we can display it
            self.encode()

        if self.checksum is not None:
            return f'{msg.upper()} ({self.checksum:X})'
        else:
            return f'{msg.upper()} ({self.checksum})'

    def export(self):
        self.decode()
        obj = {
            'time': self.time,
            'mid': self.mid,
            'src': self.src,
            'checksum': self.checksum,
            'pids': [p.export(mid=self._mid) for p in self._pids.values()],
        }

        if self.msg is not None:
            msg = self.msg
        elif self._raw is not None:
            # If no encoded msg is created use the raw message data if available
            msg = self._raw

        # Turn the message into something that can be easily serialized by the
        # json module
        if isinstance(msg, str):
            # String instances are already strings of hex chars, and don't need 
            # to be modified.
            obj['data'] = msg
        elif isinstance(msg, bytes):
            obj['data'] = msg.hex()
        elif isinstance(msg, tuple) and isinstance(msg[0], str):
            obj['data'] = [m for m in msg]
        elif isinstance(msg, tuple) and isinstance(msg[0], bytes):
            obj['data'] = [m.hex() for m in msg]

        return obj

    def json(self):
        return json.dumps(self.export())


class J1708MultisectionMsg:
    def __init__(self, first, msgs=None):
        if not first.is_multisection:
            errmsg = f'Cannot initialize multisection msg with non-multisection initial msg {repr(first)}'
            raise J1708MultisectionError(errmsg)
        if first.section.cur != 0:
            errmsg = f'Cannot initialize multisection msg with non-first msg section {repr(first)}'
            raise J1708MultisectionError(errmsg)

        self._first = first
        self._msgs = {first.section.cur: first}

        # If messages were provided add them now
        if msgs is not None:
            if isinstance(msgs, msgs):
                msgs = [m for m in msgs.values() if m is not first]
            elif isinstance(msgs, (list, tuple)):
                msgs = [m for m in msgs if m is not first]
            else:
                if msgs is not first:
                    msgs = [msgs]
                else:
                    msgs = []

            for msg in msgs:
                self.append(msg)

    def __repr__(self):
        msgs = [m for m in self._msgs.values() if m is not self._first]
        return f'{self.__class__.__name__}(first={repr(self._first)}, msgs={repr(msgs)})'

    def match(self, msg):
        return msg.is_multisection and\
                self._first.mid == msg.mid and \
                self._first.section.pid == msg.section.pid

    def append(self, msg):
        # Ensure this new message appears to be a valid section of this 
        # multisection message
        if not msg.is_multisection:
            errmsg = f'Cannot append non-multisection msg: {repr(msg)}'
            raise J1708MultisectionError(errmsg)
        if self._first.mid != msg.mid:
            errmsg = f'Cannot append msg with MID mismatch: {repr(self._first)} != {repr(msg)}'
            raise J1708MultisectionError(errmsg)
        if self._first.section.pid != msg.section.pid:
            errmsg = f'Cannot append msg with PID mismatch: {repr(self._first)} != {repr(msg)}'
            raise J1708MultisectionError(errmsg)
        if self._first.section.last != msg.section.last:
            errmsg = f'Cannot append msg with section count mismatch: {repr(self._first)} != {repr(msg)}'
            raise J1708MultisectionError(errmsg)

        # Don't check if the msg's section is already in the received messages, 
        # just overwrite the old msg.
        self._msgs[msg.section.cur] = msg

    @property
    def complete(self):
        # The section numbers start at 0, so the length should be last + 1
        return self._first.section.last in self._msgs and \
                len(self._msgs) == (self._first.section.last + 1)

    def merge(self):
        if not self.complete:
            errmsg = f'Cannot merge, section(s) missing: {repr(self._msgs)}'
            raise J1708MultisectionError(errmsg)

        sections = [m.section for m in self._msgs.values()]
        merged = b''.join(s.data for s in sections)

        if len(merged) != self._first.section.size:
            errmsg = f'Merged msg size does not match initial message (first: {repr(self._first)}, len: {len(merged)}, merged: {repr(merged)})'
            raise J1708MultisectionError(errmsg)

        # Set the timestamp to be the timestamp of the last msg
        last_msg = self._msgs[self._first.section.last]

        # To decode correctly prefix the merged message with the length 
        # specified in the first section
        merged = struct.pack('<B', self._first.section.size) + merged

        # Now decode
        decoded_pid, rest = j1708_pids.decode(merged, pid=self._first.section.pid)

        # There should not be any leftover msg data
        if rest:
            errmsg = f'Multisection msg decoding incomplete: rest={rest.hex()}, pid={repr(decoded_pid)}, msg={merged.hex()}'
            raise J1708MultisectionError(errmsg)

        args = {
            'mid': self._first.mid,
            'pids': decoded_pid,
            'timestamp': last_msg.time,

            # Pass raw message sections to the object being created
            'msg': tuple(m.msg for m in self._msgs.values()),
        }
        return J1708(**args)


__all__ = [
    'J1708',
    'J1708MultisectionMsg',
]
