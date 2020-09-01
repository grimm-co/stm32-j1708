import enum
import functools
import struct

from mids import get_mid_name
from pid_name import get_pid_name
from sid_consts import get_sid_string


def get_mask_offset(mask):
    count = 0
    while not mask & (1 << count):
        count += 1
    return count


class J1708FlagEnum(enum.IntFlag):
    def __repr__(self):
        return str(self)

    def __str__(self):
        #return f'{self.name} ({self.value:X})'
        return f'{self.name}'

    def __in__(self, other):
        if self.value & other == self.value:
            return True
        else:
            return False

    def format(self, **kwargs):
        return '\n    ' + str(self)

    @classmethod
    def _get_flags(cls, value):
        flags = []
        for flag in list(cls):
            #if flag in value:
            if flag.__in__(value):
                flags.append(flag)
        return flags

    @classmethod
    def decode(cls, value):
        if isinstance(value, bytes):
            value = int.from_bytes(value, 'little')
        return cls._get_flags(value)

    @classmethod
    def encode(cls, *flags):
        return functools.reduce(lambda x, y: x | y, flags)


class StatusGroupEnum(J1708FlagEnum):
    # TODO: move to a fully unique class.  The way that the Enum class "steals" 
    # values based on value makes it difficult to define bitmask groups.
    def __new__(cls, value, mask):
        # Method to ensure that the mask value is not treated as part of the 
        # value
        obj = super().__new__(cls, value)
        obj.mask = mask

        # The value & mask combination must be unique
        for field in list(cls):
            field_val = field.value & field.mask
            val = value & mask
            if field.mask == mask and field_val == val:
                errmsg = 'fields must be unique:\n' \
                        f'{field.name}: {field_val:b} ({field.value:b} & {field.mask:b}) == ' \
                        f'{val:b} ({value:b} & {mask:b})'
                raise ValueError(errmsg)
        return obj

    def __in__(self, other):
        # Customize the "in" operator to ensure that mask group enums only 
        # validate the specific section of the value.
        if other & self.mask == self.value & self.mask:
            return True
        else:
            return False

    def __and__(self, other):
        # Customize the and operator to ensure that mask group enums only 
        # validate the specific section of the value. Only return valid data if 
        # the field when masked exactly matches the value of this flag.
        if other & self.mask == self.value & self.mask:
            return (other & self.value) & self.mask
        else:
            return 0

    def __or__(self, other):
        # Customize the bitwise-or operator to ensure that or-ing a status group 
        # to another value will result in the group mask being cleared correctly
        value = other

        # Clear the group mask region for this field
        value &= ~self.mask

        # Set the bits for this field
        value |= self.value & self.mask
        return value

    def __str__(self):
        if hasattr(self, 'mask'):
            value = self.value & self.mask
            #return f'{self.name} ({value:X} & {self.mask:X})'
            return f'{self.name}'
        else:
            return super().__str__()

    @classmethod
    def encode(cls, *flags):
        # Sort the flags by mask and ensure there are no duplicate masks
        value = {}
        for flag in flags:
            if flag.mask not in value:
                value[flag.mask] = flag.value & flag.mask
            else:
                errmsg = f'Cannot set multiple values in the same group:\n  {flags}'
                raise ValueError(errmsg)
        return functools.reduce(lambda x, y: x | y, value.values())


class StatusGroupEnumAndValue(StatusGroupEnum):
    def __new__(cls, value, mask, is_value_field=False):
        # Method to ensure that the mask value is not treated as part of the 
        # value
        obj = super().__new__(cls, value)
        obj.mask = mask
        obj.is_value_field = is_value_field

        if is_value_field:
            obj._field_offset = get_mask_offset(mask)
            # Also ensure that there are no other fields that have masks that 
            # overlap this one.
            for field in list(cls):
                if field.mask == mask:
                    errmsg = 'value field masks must be unique:\n' \
                            f'{mask:b} == {field.name}: {field.mask:b}'
                    raise ValueError(errmsg)
        else:
            # The value & mask combination must be unique for each mask group
            for field in list(cls):
                field_val = field.value & field.mask
                val = value & mask
                if not field.is_value_field and field.mask == mask and field_val == val:
                    errmsg = 'fields must be unique:\n' \
                            f'{field.name}: {field_val:b} ({field.value:b} & {field.mask:X}) == ' \
                            f'{val:b} ({value:b} & {mask:X})'
                    raise ValueError(errmsg)
        return obj

    def __in__(self, other):
        if self.is_value_field:
            # Value fields are always present, but for the purposes of the "in" 
            # operator return false
            return False
        else:
            return super().__in__(other)

    def __and__(self, other):
        if self.is_value_field:
            # for the bitwise-and operator just mask out the field from the 
            # value specified
            return value & self.mask
        else:
            return super().__and__(other)

    def __str__(self):
        if hasattr(self, 'is_value_field') and self.is_value_field:
            #return f'{self.name} (& {self.mask:X})'
            return f'{self.name}'
        elif hasattr(self, 'mask'):
            #value = self.value & self.mask
            #return f'{self.name} ({value:X} & {self.mask:X})'
            return f'{self.name}'
        else:
            return super().__str__()

    @classmethod
    def _get_flags(cls, value):
        matches = []
        for flag in list(cls):
            #if not flag.is_value_field and flag in value:
            if not flag.is_value_field and flag.__in__(value):
                matches.append(flag)
        return matches

    @classmethod
    def decode(cls, value):
        if isinstance(value, bytes):
            value = int.from_bytes(val_bytes, 'little')

        obj = {}
        for field in list(cls):
            if field.is_value_field:
                obj[field.name] = (value & field.mask) >> field._field_offset

        assert 'flags' not in obj
        obj['flags'] = cls._get_flags(value)
        return obj

    @classmethod
    def encode(cls, *flags, **kwargs):
        # the flags could also be supplied as a dictionary to allow setting 
        # a non-status field explicitly
        if isinstance(flags[0], dict):
            assert not kwargs
            kwargs = flags[0]
            flags = flags[1:]

        value = {}
        # Set any fields specified
        for name in kwargs:
            field = cls[kwargs[name]]
            if flag.mask not in value:
                value[field.mask] = (kwargs[name] << field._field_offset) & field.mask
            else:
                errmsg = f'Cannot set multiple values in the same group:\n  {flags}'
                raise ValueError(errmsg)

        # Set all the flags specified
        for flag in flags:
            if flag.mask not in value:
                value[flag.mask] = flag.value & flag.mask
            else:
                errmsg = f'Cannot set multiple values in the same group:\n  {flags}'
                raise ValueError(errmsg)

        return functools.reduce(lambda x, y: x | y, value.values())


class FMI(enum.IntEnum):
    VALID_ABOVE_NORMAL               = 0
    VALID_BELOW_NORMAL               = 1
    ERRATIC_OR_INCORRECT             = 2
    VOLTAGE_HIGH_OR_SHORTED_HIGH     = 3
    VOLTAGE_LOW_OR_SHORTED_LOW       = 4
    CURRENT__OR_OPEN_CIRCUIT         = 5
    CURRENT_HIGH_OR_GROUNDED_CIRCUIT = 6
    MECHANICAL_SYSTEM_NOT_RESPONDING = 7
    ABNORMAL_FREQ_PWM_OR_PERIOD      = 8
    ABNORMAL_UPDATE_RATE             = 9
    ABNORMAL_RATE_OF_CHANGE          = 10
    UNKNOWN_FAILURE_MODE             = 11
    BAD_INTELLIGENT_DEVICE           = 12
    OUT_OF_CALIBRATION               = 13
    SPECIAL_INSTRUCTIONS             = 14
    RESERVED                         = 15


# PID: 8
class BrakeSystemAirPressureLowWarningSwitchStatus(StatusGroupEnum):
    # Use bits that don't matter to ensure that all the "OFF" values are unique
    TRAILER_EMERGENCY_SUPPLY_ERROR  = (0b10111111, 0xC0)
    TRAILER_EMERGENCY_SUPPLY_ON     = (0b01111111, 0xC0)
    TRAILER_EMERGENCY_SUPPLY_OFF    = (0b00111111, 0xC0)
    TRAILER_SERVICE_SUPPLY_ERROR    = (0b11101111, 0x30)
    TRAILER_SERVICE_SUPPLY_ON       = (0b11011111, 0x30)
    TRAILER_SERVICE_SUPPLY_OFF      = (0b11001111, 0x30)
    TRACTOR_SECONDARY_SUPPLY_ERROR  = (0b11111011, 0x0C)
    TRACTOR_SECONDARY_SUPPLY_ON     = (0b11110111, 0x0C)
    TRACTOR_SECONDARY_SUPPLY_OFF    = (0b11110011, 0x0C)
    TRACTOR_PRIMARY_SUPPLY_ERROR    = (0b11111110, 0x03)
    TRACTOR_PRIMARY_SUPPLY_ON       = (0b11111101, 0x03)
    TRACTOR_PRIMARY_SUPPLY_OFF      = (0b11111100, 0x03)


# PID: 9
class AxleLiftStatus(StatusGroupEnum):
    # Use bits that don't matter to ensure that all the "OFF" values are unique
    POSITION_ERROR  = (0b11111011, 0x0C)
    UP              = (0b11110111, 0x0C)
    DOWN            = (0b11110011, 0x0C)
    SWITCH_ERROR    = (0b11111110, 0x03)
    ON              = (0b11111101, 0x03)
    OFF             = (0b11111100, 0x03)


# PID: 10
class AxleSliderStatus(StatusGroupEnum):
    # Use bits that don't matter to ensure that all the "OFF" values are unique
    SLIDER_LOCK_ERROR       = (0b11111011, 0x0C)
    LOCKED                  = (0b11110111, 0x0C)
    UNLOCKED                = (0b11110011, 0x0C)
    SLIDER_LOCKSWITCH_ERROR = (0b11111110, 0x03)
    ON                      = (0b11111101, 0x03)
    OFF                     = (0b11111100, 0x03)


# PID: 11
class CargoSecurement(StatusGroupEnumAndValue):
    # The bit range for the "Value" portion of the PID, the value must be an 
    # integer even though it won't be used.
    CARGO_SECTOR_NUM = (0, 0xF0, True)

    # Use bits that don't matter to ensure that all the "OFF" values are unique
    ERROR            = (0b11111110, 0x03)
    LOOSE            = (0b11111101, 0x03)
    SECURE           = (0b11111100, 0x03)


# PID: 44
class IndicatorLampStatus(StatusGroupEnum):
    # Use bits that don't matter to ensure that all the "OFF" values are unique
    PROTECT_ERROR = (0b11101111, 0x30)
    PROTECT_ON    = (0b11011111, 0x30)
    PROTECT_OFF   = (0b11001111, 0x30)
    AMBER_ERROR   = (0b11111011, 0x0C)
    AMBER_ON      = (0b11110111, 0x0C)
    AMBER_OFF     = (0b11110011, 0x0C)
    RED_ERROR     = (0b11111110, 0x03)
    RED_ON        = (0b11111101, 0x03)
    RED_OFF       = (0b11111100, 0x03)


# PID: 49
class ABSControlStatus(StatusGroupEnum):
    # Use bits that don't matter to ensure that all the "OFF" values are unique
    OFF_ROAD_ERROR      = (0b10111111, 0xC0)
    OFF_ROAD_ON         = (0b01111111, 0xC0)
    OFF_ROAD_OFF        = (0b00111111, 0xC0)
    RETARDER_ERROR      = (0b11101111, 0x30)
    RETARDER_ON         = (0b11011111, 0x30)
    RETARDER_OFF        = (0b11001111, 0x30)
    BRAKE_CONTROL_ERROR = (0b11111011, 0x0C)
    BRAKE_CONTROL_ON    = (0b11110111, 0x0C)
    BRAKE_CONTROL_OFF   = (0b11110011, 0x0C)
    WARNING_LAMP_ERROR  = (0b11111110, 0x03)
    WARNING_LAMP_ON     = (0b11111101, 0x03)
    WARNING_LAMP_OFF    = (0b11111100, 0x03)


# PID: 65
class BrakeSwitchStatus(StatusGroupEnum):
    # Use bits that don't matter to ensure that all the "OFF" values are unique
    ERROR      = (0b11111011, 0x0C)
    ON         = (0b11110111, 0x0C)
    OFF        = (0b11110011, 0x0C)
    LAMP_ERROR = (0b11111110, 0x03)
    LAMP_ON    = (0b11111101, 0x03)
    LAMP_OFF   = (0b11111100, 0x03)


# PID: 70
class ParkingBrakeStatus(StatusGroupEnum):
    ON  = (0b10000000, 0x80)
    OFF = (0b00000000, 0x80)


# PID: 71
class IdleShutdownTimer(J1708FlagEnum):
    SHUTDOWN_TIMER_ACTIVE  = (1 << 7)
    SHUTDOWN_TIMER_ENABLED = (1 << 3)
    OVERRIDE_ACTIVE        = (1 << 2)
    ENGINE_IS_SHUTDOWN     = (1 << 1)
    DRIVER_ALERT_ACTIVE    = (1 << 0)


# PID: 83
class RoadSpeedLimitStatus(StatusGroupEnum):
    ON  = (0b10000000, 0x80)
    OFF = (0b00000000, 0x80)


# PID: 85
class CruiseControlStatus(J1708FlagEnum):
    ACTIVE = (1 << 7)
    CLUTCH = (1 << 6)
    BRAKE  = (1 << 5)
    ACCEL  = (1 << 4)
    RESUME = (1 << 3)
    COAST  = (1 << 2)
    SET    = (1 << 1)
    ON     = (1 << 0)
    OFF    = 0


# PID: 89
class PowerTakeoffStatus(J1708FlagEnum):
    PTO_ACTIVE    = (1 << 7)
    CLUTCH        = (1 << 6)
    BRAKE         = (1 << 5)
    ACCEL         = (1 << 4)
    RESUME        = (1 << 3)
    COAST         = (1 << 2)
    SET           = (1 << 1)
    PTO_SWITCH_ON = (1 << 0)


# PID: 128
class ParamRequest(object):
    def __init__(self, pid, mid):
        self.pid = pid
        self.mid = mid

    def format(self, **kwargs):
        mid_str = get_mid_name(self.mid)
        pid_str = get_pid_name(self.pid)
        return f'PID {self.pid} ({pid_str}) FROM {self.mid} ({mid_str})'

    @classmethod
    def decode(cls, msg_body):
        return cls(msg_body[0], msg_body[1])

    @classmethod
    def encode(cls, *args, **kwargs):
        return struct.pack('>BB', self.pid, self.mid)


# PID: 151
class ATCControlStatus(StatusGroupEnum):
    SPINOUT_ERROR         = (0b1011111111111111, 0xC000)
    SPINOUT_ACTIVE        = (0b0111111111111111, 0xC000)
    SPINOUT_INACTIVE      = (0b0011111111111111, 0xC000)
    ATC_ENGINE_CTRL_ERROR = (0b0010111111111111, 0x3000)
    ATC_ENGINE_CTRL_ON    = (0b0001111111111111, 0x3000)
    ATC_ENGINE_CTRL_OFF   = (0b0000111111111111, 0x3000)
    ATC_BRAKES_CTRL_ERROR = (0b0000101111111111, 0x0C00)
    ATC_BRAKES_CTRL_ON    = (0b0000011111111111, 0x0C00)
    ATC_BRAKES_CTRL_OFF   = (0b0000001111111111, 0x0C00)
    LAMP_ERROR            = (0b0000001011111111, 0x0300)
    LAMP_ON               = (0b0000000111111111, 0x0300)
    LAMP_OFF              = (0b0000000011111111, 0x0300)
    VDC_ENGINE_CTRL_ERROR = (0b0000000000101111, 0x0030)
    VDC_ENGINE_CTRL_ON    = (0b0000000000011111, 0x0030)
    VDC_ENGINE_CTRL_OFF   = (0b0000000000001111, 0x0030)
    VDC_BRAKES_CTRL_ERROR = (0b0000000000001011, 0x000C)
    VDC_BRAKES_CTRL_ON    = (0b0000000000000111, 0x000C)
    VDC_BRAKES_CTRL_OFF   = (0b0000000000000011, 0x000C)
    ATC_MUD_SNOW_ERROR    = (0b0000000000000010, 0x0003)
    ATC_MUD_SNOW_ON       = (0b0000000000000001, 0x0003)
    ATC_MUD_SNOW_OFF      = (0b0000000000000000, 0x0003)


# PID: 183
class EngineRetarderStatus(StatusGroupEnum):
    ON          = (0b10000000, 0x80)
    OFF         = (0b00000000, 0x80)
    CYL8_ACTIVE = (0b00010000, 0x10)
    CYL6_ACTIVE = (0b00001000, 0x08)
    CYL4_ACTIVE = (0b00000100, 0x04)
    CYL3_ACTIVE = (0b00000010, 0x02)
    CYL2_ACTIVE = (0b00000001, 0x01)


# PID: 194
class DTCCode(StatusGroupEnumAndValue):
    # The bit range for the "Value" portion of the PID, the value must be an 
    # integer even though it won't be used.
    FMI         = (0, 0x0F, True)

    # As always, use the bits that don't matter in the value fields to ensure 
    # that the "value" for each enum is unique.
    COUNT_INCL  = (0b10000000, 0x80)
    INACTIVE    = (0b01000000, 0x40)
    ACTIVE      = (0b10111111, 0x40)
    STANDARD    = (0b00100000, 0x20)
    EXTENDED    = (0b11011111, 0x20)
    SID_INCL    = (0b00010000, 0x10)
    PID_INCL    = (0b11101111, 0x10)


class DTC(object):
    def __init__(self, pid_sid_byte, code, count=None):
        self.code = DTCCode.decode(code)

        if DTCCode.EXTENDED in self.code['flags']:
            self.ext = True
            pid_sid_byte += 256
        else:
            self.ext = False

        if DTCCode.SID_INCL in self.code['flags']:
            self.pid = None
            self.sid = pid_sid_byte
        else:
            self.pid = pid_sid_byte
            self.sid = None

        if DTCCode.ACTIVE in self.code['flags']:
            self.active = True
        else:
            self.active = False

        if DTCCode.COUNT_INCL in self.code['flags']:
            self.count = count
        else:
            self.count = None

        self.fmi = FMI(self.code['FMI'])

    def format(self, mid, **kwargs):
        if self.active:
            value_str = 'ACTIVE    '
        else:
            value_str = 'INACTIVE  '
        if self.sid is not None:
            sid_str = get_sid_string(mid, self.sid)
            value_str += f'SID {self.sid} ({sid_str}): '
        else:
            pid_str = get_pid_name(self.pid)
            value_str += f'PID {self.pid} ({pid_str}): '
        value_str += self.fmi.name
        if self.count is not None:
            value_str += f' ({self.count})'
        return value_str

    @classmethod
    def decode(cls, msg_body):
        dtcs = []
        rest = msg_body
        while rest:
            new_dtc = cls(rest[0], rest[1], rest[2])
            if new_dtc.count is None:
                rest = rest[2:]
            else:
                rest = rest[3:]
            dtcs.append(new_dtc)
        return dtcs

    @classmethod
    def encode(cls, *args, **kwargs):
        raise NotImplementedError


# PID: 195
class DTC_REQ_TYPE(enum.IntEnum):
    ASCII_DESCRIPTION     = 0
    CLEAR_SPECIFIC_DTC    = 1
    CLEAR_ALL_DTCS        = 2
    MANUFACURER_DIAG_INFO = 3


class DTCRequestCode(StatusGroupEnumAndValue):
    # The bit range for the "Value" portion of the PID, the value must be an 
    # integer even though it won't be used.
    FMI          = (0, 0x0F, True)
    DTC_REQ_TYPE = (1, 0xC0, True)

    # As always, use the bits that don't matter in the value fields to ensure 
    # that the "value" for each enum is unique.
    STANDARD                   = (0b00111111, 0x20)
    EXTENDED                   = (0b00011111, 0x20)
    SID_INCL                   = (0b11110000, 0x10)
    PID_INCL                   = (0b11100000, 0x10)


class DTCRequest(object):
    def __init__(self, mid, pid_sid_byte, code):
        self.mid = mid
        self.code = DTCRequestCode.decode(code)

        if DTCRequestCode.EXTENDED in self.code['flags']:
            self.ext = True
            pid_sid_byte += 256
        else:
            self.ext = False

        if DTCRequestCode.SID_INCL in self.code['flags']:
            self.pid = None
            self.sid = pid_sid_byte
        else:
            self.pid = pid_sid_byte
            self.sid = None

        self.fmi = FMI(self.code['FMI'])
        self.type = DTC_REQ_TYPE(self.code['DTC_REQ_TYPE'])

    def format(self, **kwargs):
        mid_str = get_mid_name(self.mid)
        if self.type == DTC_REQ_TYPE.CLEAR_ALL_DTCS:
            return f'{self.type.name} {mid_str} ({self.mid})'
        else:
            if self.sid is not None:
                sid_str = get_sid_string(mid, self.sid)
                return f'{self.type.name} {mid_str} ({self.mid}): SID {self.sid} ({sid_str})'
            else:
                pid_str = get_pid_name(self.pid)
                return f'{self.type.name} {mid_str} ({self.mid}): PID {self.pid} ({pid_str})'

    @classmethod
    def decode(cls, msg_body):
        return cls(msg_body[0], msg_body[1], msg_body[2])

    @classmethod
    def encode(cls, *args, **kwargs):
        raise NotImplementedError
