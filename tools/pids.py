from fractions import Fraction

from pid_consts import *
from pid_types import *


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


def extract(data):
    if len(data) >= 4 and data[:3] == b'\xff\xff\xff':
        pid_char = data[3]
        pid = 768 + pid_char
        start = 4
    elif len(data) >= 4 and data[:2] == b'\xff\xff':
        pid_char = data[2]
        pid = 512 + pid_char
        start = 3
    elif len(data) >= 4 and data[:1] == b'\xff':
        pid_char = data[1]
        pid = 256 + pid_char
        start = 2
    elif len(data) >= 1 and data[:1] != b'\xff':
        pid_char = data[0]
        pid = pid_char
        start = 1
    else:
        # Invalid
        return (None, rest)

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
    value = None
    pid_info = get_pid_info(pid)
    if val_bytes == b'\xff' * data_len:
        value = f'{val_bytes.hex().upper()}: Not Available'
    elif 'resolution' in pid_info:
        if isinstance(pid_info['resolution'], Fraction) and \
                val_bytes != b'\xff' * data_len:
            # First byte swap the data (it's in little endian) and then multiply 
            # by the resolution
            res = pid_info['resolution']
            le_val = int.from_bytes(val_bytes, 'little')
            fractional_val = le_val * res

            if 'units' in pid_info:
                value = f'{float(fractional_val)} {pid_info["units"]} ({val_bytes.hex().upper()})'
            else:
                value = f'{float(fractional_val)} ({val_bytes.hex().upper()})'

        elif hasattr(pid_info['type'], 'get_values'):
            le_val = int.from_bytes(val_bytes, 'little')
            value = f'        {le_val:X}:\n'
            values = pid_info['type'].get_values(le_val).items()
            flags = values.pop('flags')
            for field, value in values:
                value += f'        {field}: {value}\n'
            flag_str = "|".join(str(f) for f in flags)
            value += f'        flags: {flag_str}'

        elif hasattr(pid_info['type'], 'get_flags'):
            le_val = int.from_bytes(val_bytes, 'little')
            flags = pid_info['type'].get_flags(le_val)
            flag_str = "|".join(str(f) for f in flags)
            value = f'{le_val:X}: {flag_str}'

        elif callable(pid_info['type']):
            # Any further special parsing will be done by the top-level message 
            # parser
            value = pid_info['type'](val_bytes)

    if value is None:
        value = val_bytes.hex().upper()

    # Return a dictionary representing the PID and then the rest of the message
    obj = {
        'pid': pid,
        'name': get_pid_name(pid),
        'data': value,
        'raw': data[:end],
    }
    rest = data[end:]

    return (obj, rest)
