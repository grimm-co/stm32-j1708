import inspect
import re
import struct
import serial
import serial.tools.list_ports

import mids
import pids
from sid_consts import *
from pid_consts import *
from pid_types import *


def find_device():
    """
    Identifies if there are any USB devices that match the VID:PID and device
    strings expected for the J1708 tool.
    """
    for p in serial.tools.list_ports.grep('0483:5740'): 
        if 'j1708' in p.manufacturer.lower():
            return p.device
    return None


def make_dtc_string(mid, value, **kwargs):
    dtc = value
    if dtc.active:
        value_str = 'ACTIVE    '
    else:
        value_str = 'INACTIVE  '

    if dtc.sid is not None:
        sid_str = get_sid_string(mid, dtc.sid)
        value_str += f'SID {dtc.sid} ({sid_str}): '
    else:
        pid_str = get_pid_name(dtc.pid)
        value_str += f'PID {dtc.pid} ({pid_str}): '

    value_str += dtc.fmi.name

    if dtc.count is not None:
        value_str += f' ({dtc.count})'

    return value_str


def make_dtc_req_string(mid, value, **kwargs):
    req = value
    if req.type == DTC_REQ_TYPE.CLEAR_ALL_DTCS:
        return f'{self.type.name} {mid["name"]} ({mid["mid"]})'
    else:
        if dtcreq.sid is not None:
            return f'{self.type.name} {mid["name"]} ({mid["mid"]}): SID {req.sid}'
        else:
            return f'{self.type.name} {mid["name"]} ({mid["mid"]}): PID {req.pid}'


def make_pid_dict_string(value, **kwargs):
    flags = values.pop('flags')
    pid_str = ''
    for field, value in values:
        pid_str += f'\n    {field}: {value}'

    flag_str = "|".join(str(f) for f in flags)
    pid_str += f'\n    flags: {flag_str}'
    return pid_str


_whitespace_pat = re.compile(r'^\s+')
def make_pid_list_string(pid, value, **kwargs):
    if len(value) == 0:
        return '\n    NONE'
    else:
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
        return '\n' + prefix_str + '|'.join(formatted_values)


def make_pid_bytes_string(value, **kwargs):
    return f'\n    {value.hex().upper()}'


pid_formatter_map = {
    DTC: make_dtc_string,
    DTCRequest: make_dtc_req_string,
    dict: make_pid_dict_string,
    list: make_pid_list_string,
    bytes: make_pid_bytes_string,
}


def make_flag_string(value, **kwargs):
    return '\n    ' + str(value)


def make_pid_string(value, **kwargs):
    return f'\n    {value}'


def format_pid_value(mid, value, **kwargs):
    # Some enum types get weird about how they report their type, if the value 
    # has the mro attribute, get the first value in the list and use that
    try:
        mro = inspect.getmro(value)
        value_type = mro[0]
    except AttributeError:
        value_type = type(value)

    # Default to the make_pid_string() to convert pid data
    try:
        formatter = pid_formatter_map[value_type]
    except KeyError:
        if isinstance(value, J1708FlagEnum):
            formatter = make_flag_string
        else:
            formatter = make_pid_string
    return formatter(**kwargs, mid=mid, value=value)


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
                    print(f'WARNING: unable to extract valid PID from {body}')
                    break

        print(f'\n{self.mid["name"]} ({self.mid["mid"]}): {self}')
        for pid in self.pids:
            pid_str = f'  {pid["pid"]}: {pid["name"]}'
            pid_str += format_pid_value(mid=self.mid, pid=pid, value=pid['value'])
            print(pid_str)

    def __str__(self):
        if self.checksum is not None:
            return f'{self.msg.hex().upper()} ({self.checksum:X})'
        else:
            return f'{self.msg.hex().upper()} ({self.checksum})'


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
                j1708_msg = J1708.make(msg, ignore_checksums)
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

    def reparse_log(self, filename, decode=True, ignore_checksums=False):
        msg_pat = re.compile(r'^[^ ].*\([0-9]+\): ([0-9A-Fa-f]+) \(0x([0-9A-Fa-f]+)\)')
        with open(filename, 'r') as logfile:
            for line in logfile:
                match = msg_pat.match(line)
                if match:
                    msgbody, msgchksum = match.groups()
                    if len(msgchksum) < 2:
                        msg = msgbody + '0' + msgchksum
                    else:
                        msg = msgbody + msgchksum

                    j1708_msg = J1708.make(msg, ignore_checksums)
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

