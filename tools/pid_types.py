import enum


def get_mask_offset(mask):
    count = 0
    while not mask & (1 << count):
        count += 1
    return count


class J1708FlagEnum(enum.IntFlag):
    def __repr__(self):
        return str(self)

    def __str__(self):
        return f'{self.name} ({self.value:X})'

    @classmethod
    def get_flags(cls, value):
        matches = []
        for flag in list(cls):
            if flag & value:
                matches.append(flag)
        return matches


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

    def __and__(self, other):
        # Customize the bitwise-and operator to ensure that mask group enums 
        # only validate the specific section of the value
        if other & self.mask == self.value & self.mask:
            return True
        else:
            return False

    def __str__(self):
        value = self.value & self.mask
        return f'{self.name} ({value:X} & {self.mask:X})'


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

    def __and__(self, other):
        if self.is_value_field:
            # Value fields are always present, but for the purposes of the 
            # bitwise-and operator return false
            return False
        else:
            # Customize the bitwise-and operator to ensure that mask group enums 
            #     only validate the specific section of the value
            if other & self.mask == self.value & self.mask:
                return True
            else:
                return False

    def __str__(self):
        if self.is_value_field:
            return f'{self.name} (& {self.mask:X})'
        else:
            value = self.value & self.mask
            return f'{self.name} ({value:X} & {self.mask:X})'

    @classmethod
    def get_values(cls, value):
        obj = {}
        for field in list(cls):
            if field.is_value_field:
                obj[field.name] = (value & field.mask) >> field._field_offset

        assert 'flags' not in obj
        obj['flags'] = cls.get_flags(value)
        return obj

    @classmethod
    def get_flags(cls, value):
        matches = []
        for flag in list(cls):
            if not flag.is_value_field and flag & value:
                matches.append(flag)
        return matches


class FMI(enum.Enum):
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
    RESERVED                         = 14


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


# PID: 65
class BrakeSwitchStatus(StatusGroupEnum):
    # Use bits that don't matter to ensure that all the "OFF" values are unique
    BRAKE_ERROR         = (0b11111011, 0x0C)
    BRAKE_ON            = (0b11110111, 0x0C)
    BRAKE_OFF           = (0b11110011, 0x0C)
    SERVICE_BRAKE_ERROR = (0b11111110, 0x03)
    SERVICE_BRAKE_ON    = (0b11111101, 0x03)
    SERVICE_BRAKE_OFF   = (0b11111100, 0x03)


# PID: 70
class ParkingBrakeStatus(StatusGroupEnum):
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


# PID: 194
class DTCState(StatusGroupEnumAndValue):
    # The bit range for the "Value" portion of the PID, the value must be an 
    # integer even though it won't be used.
    FMI         = (0, 0x0F, True)

    # As always, use the bits that don't matter in the value fields to ensure 
    # that the "value" for each enum is unique.
    COUNT_INCL  = (0b10000000, 0x80)
    ACTIVE      = (0b01000000, 0x40)
    INACTIVE    = (0b10111111, 0x40)
    STANDARD    = (0b00100000, 0x20)
    EXTENDED    = (0b11011111, 0x20)
    SID_INCL    = (0b00010000, 0x10)
    PID_INCL    = (0b11101111, 0x10)


class DTC(object):
    def __init__(self, low_byte, code, count=None):
        code = DTCState.get_values(code)
        self.code = code

        if DTCState.EXTENDED in code['flags']:
            self.ext = True
            low_byte += 256
        else:
            self.ext = False

        if DTCState.SID_INCL in code['flags']:
            self.pid = None
            self.sid = low_byte
        else:
            self.pid = low_byte
            self.sid = None

        if DTCState.ACTIVE in code['flags']:
            self.active = True
        else:
            self.active = False

        if DTCState.COUNT_INCL in code['flags']:
            self.count = count
        else:
            self.count = None

        self.fmi = FMI(code['FMI'])

    @classmethod
    def make(cls, msg_body):
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
