from fractions import Fraction

from .pid_types import *
from . import pid_name
from . import pid_info
from .exceptions import *


def genBitMask(bits):
    return ~((-1) << bits)


_bit_masks = {
    1: genBitMask(1),
    2: genBitMask(2),
    3: genBitMask(3),
    4: genBitMask(4),
    5: genBitMask(5),
    6: genBitMask(6),
    7: genBitMask(7),
    8: genBitMask(8),
    9: genBitMask(9),
    10: genBitMask(10),
    11: genBitMask(11),
    12: genBitMask(12),
    13: genBitMask(13),
    14: genBitMask(14),
    15: genBitMask(15),
    16: genBitMask(16),
    17: genBitMask(17),
    18: genBitMask(18),
    19: genBitMask(19),
    20: genBitMask(20),
    21: genBitMask(21),
    22: genBitMask(22),
    23: genBitMask(23),
    24: genBitMask(24),
    25: genBitMask(25),
    26: genBitMask(26),
    27: genBitMask(27),
    28: genBitMask(28),
    29: genBitMask(29),
    30: genBitMask(30),
    31: genBitMask(31),
    32: genBitMask(32),
    33: genBitMask(33),
    34: genBitMask(34),
    35: genBitMask(35),
    36: genBitMask(36),
    37: genBitMask(37),
    38: genBitMask(38),
    39: genBitMask(39),
    40: genBitMask(40),
    41: genBitMask(41),
    42: genBitMask(42),
    43: genBitMask(43),
    44: genBitMask(44),
    45: genBitMask(45),
    46: genBitMask(46),
    47: genBitMask(47),
    48: genBitMask(48),
    49: genBitMask(49),
    50: genBitMask(50),
    51: genBitMask(51),
    52: genBitMask(52),
    53: genBitMask(53),
    54: genBitMask(54),
    55: genBitMask(55),
    56: genBitMask(56),
    57: genBitMask(57),
    58: genBitMask(58),
    59: genBitMask(59),
    60: genBitMask(60),
    61: genBitMask(61),
    62: genBitMask(62),
    63: genBitMask(63),
    64: genBitMask(64),
}


def get_bit_mask(bits):
    if bits in _bit_masks:
        return _bit_masks[bits]
    else:
        return None


def decode(data):
    if len(data) >= 4 and data[:3] == b'\xff\xff\xff':
        pid_char = data[3]
        pid = 768 + pid_char
        start = 4
    elif len(data) >= 3 and data[:2] == b'\xff\xff':
        pid_char = data[2]
        pid = 512 + pid_char
        start = 3
    elif len(data) >= 2 and data[:1] == b'\xff':
        pid_char = data[1]
        pid = 256 + pid_char
        start = 2
    elif len(data) >= 1 and data[:1] != b'\xff':
        pid_char = data[0]
        pid = pid_char
        start = 1
    else:
        # Invalid
        return (None, data)

    if pid_char in range(0, 128):
        data_len = 1
        end = start + data_len
    elif pid_char in range(128, 192):
        data_len = 2
        end = start + data_len
    elif pid_char == 254:
        # The rest of the message is the data
        end = -1
        data_len = len(data[start:])
    else:
        # Variable length, the first data char is the length
        data_len = data[start]
        start += 1
        end = start + data_len

    val_bytes = data[start:end]

    # Ensure that the bytes extracted is the expected size
    assert len(val_bytes) == data_len

    value = None
    info = pid_info.get_pid_info(pid)

    if val_bytes == b'\xff' * data_len:
        value = f'{val_bytes.hex().upper()}: Not Available'

    elif 'resolution' in info:
        if isinstance(info['resolution'], Fraction) and \
                val_bytes != b'\xff' * data_len:
            # First byte swap the data (it's in little endian) and then multiply 
            # by the resolution
            if data_len == 1:
                if info['type'].startswith('signed'):
                    le_val = struct.unpack('<b', val_bytes)
                else:
                    le_val = struct.unpack('<B', val_bytes)
            elif data_len == 2:
                if info['type'].startswith('signed'):
                    le_val = struct.unpack('<h', val_bytes)
                else:
                    le_val = struct.unpack('<H', val_bytes)
            elif data_len == 4:
                if info['type'].startswith('signed'):
                    le_val = struct.unpack('<l', val_bytes)
                else:
                    le_val = struct.unpack('<L', val_bytes)
            elif data_len == 8:
                if info['type'].startswith('signed'):
                    le_val = struct.unpack('<q', val_bytes)
                else:
                    le_val = struct.unpack('<Q', val_bytes)
            else:
                raise J1708DecodeError(f'Bad size {size} for encoding PID {pid} = {value} ({info})')

            fractional_val = float(le_val[0] * info['resolution'])

            if 'units' in info:
                value = f'{fractional_val} {info["units"]} ({val_bytes.hex().upper()})'
            else:
                value = f'{fractional_val} ({val_bytes.hex().upper()})'

        elif hasattr(info['type'], 'decode'):
            value = info['type'].decode(val_bytes)

        else:
            value = val_bytes

    if value is None:
        value = val_bytes.hex().upper()

    # Return a dictionary representing the PID and then the rest of the message
    obj = {
        'pid': pid,
        'name': pid_name.get_pid_name(pid),
        'value': value,
        #'raw': data[:end],
        'raw': val_bytes,
    }
    rest = data[end:]

    return (obj, rest)


def _export_pid_value(value, mid=None):
    if hasattr(value, 'format'):
        return value.format(mid=mid)
    elif isinstance(value, dict):
        return dict((k, _export_pid_value(v, mid=mid)) for k, v in value.items)
    elif isinstance(value, list):
        return list(_export_pid_value(v, mid=mid) for v in value)
    elif isinstance(value, bytes) or isinstance(value, bytearray):
        # Format bytes as a string
        return value.hex()
    elif isinstance(value, str):
        return value.strip()
    else:
        return value


def export(pids, mid):
    # Don't include the PID name or raw bytes in a JSON exportable object
    exported_pids = []
    for obj in pids:
        exported_pids.append({
            'pid': obj['pid'],
            'name': obj['name'],
            'value': _export_pid_value(obj['value'], mid=mid)
        })
    return exported_pids


def _encode_value(pid, value, size):
    info = pid_info.get_pid_info(pid)
    if isinstance(value, bytes):
        if size is not None:
            assert len(value) == size
        return value

    elif hasattr(info['type'], 'encode') and hasattr(info['type'], 'decode'):
        if isinstance(value, dict):
            data = info['type'].encode(**value)
        elif isinstance(value, list):
            data = info['type'].encode(*value)
        else:
            data = info['type'].encode(value)

        if size is not None:
            assert len(data) == size
        return data

    elif size is not None and value is None:
        return b'\xff' * size

    elif size is not None and \
            'resolution' in info and \
            isinstance(info['resolution'], Fraction):

        # convert the value to an integer
        le_val = int(value / info['resolution'])

        # Then turn it into bytes here, because PID values are encoded 
        # little-endian, but the placement of the values in the message are in 
        # big-endian order.
        if size == 1:
            if info['type'].startswith('signed'):
                return struct.pack('<b', le_val)
            else:
                return struct.pack('<B', le_val)
        elif size == 2:
            if info['type'].startswith('signed'):
                return struct.pack('<h', le_val)
            else:
                return struct.pack('<H', le_val)
        elif size == 4:
            if info['type'].startswith('signed'):
                return struct.pack('<l', le_val)
            else:
                return struct.pack('<L', le_val)
        elif size == 8:
            if info['type'].startswith('signed'):
                return struct.pack('<q', le_val)
            else:
                return struct.pack('<Q', le_val)
        else:
            raise J1708EncodeError(f'Bad size {size} for encoding PID {pid} = {value} ({info})')

    else:
        # All other types must have an explicit size to be able to be encoded
        raise J1708EncodeError(f'Cannot encode PID {pid} = {value} ({info})')


def _encode_pid(pid, value):
    try:
        pid_val = pid['pid']
    except TypeError:
        pid_val = pid
    pid_char = pid_val % 256

    # Individual fields and types in J1708 are little-endian encoded
    if pid_val <= 256:
        msg = b''
    elif pid_val <= 512:
        msg = b'\xFF'
    elif pid_val <= 512:
        msg = b'\xFF\xFF'
    elif pid_val <= 768:
        msg = b'\xFF\xFF\xFF'
    else:
        raise J1708EncodeError(f'Cannot encode invalid PID value {pid_val}')
    msg += struct.pack('<B', pid_char)

    if pid_char in range(0, 128):
        # 1-byte PID value
        msg += _encode_value(pid_val, value, 1)

    elif pid_char in range(128, 192):
        # 2-byte PID value
        msg += _encode_value(pid_val, value, 2)

    elif pid_char == 254:
        # PID 254 is variable length with no length field
        msg += _encode_value(pid_val, value, None)

    else:
        # All other values are variable length
        encoded_value = _encode_value(pid_val, value, None)
        msg += struct.pack('<B', len(encoded_value)) + encoded_value

    return msg


def encode(pids):
    if not isinstance(pids, list):
        pids = [pids]

    # PID 254's length is "the rest of the message" so ensure that if PID 254 is 
    # in the list that it is the last pid
    if any(p['pid'] == 254 for p in pids) and pids[-1]['pid'] != 254:
        pidlist = [p['pid'] for p in pids]
        errmsg = f'PID 254 must be last: {pidlist}'
        raise J1708EncodeError(errmsg)

    # Integer data fields in J1708 are little-endian, but the message fields are 
    # extracted from the message in big-endian order (WTF people)
    msg = b''
    for pid in pids:
        msg += _encode_pid(pid['pid'], pid['value'])

    return msg


def PID(obj):
    # Function that will eventually be turned into a standalone class
    try:
        if 'pid' in obj:
            pid = {'pid': obj['pid'], 'value': None}
    except TypeError:
        if isinstance(obj, int):
            # This is all the data that was provided so just return now
            return {'pid': obj, 'value': None}
        else:
            raise TypeError(f'Not a valid PID: {obj}')

    if 'value' in obj:
        pid['value'] = obj['value']

    return pid


__all__ = [
    'decode',
    'export',
    'encode',
    'PID',
]

