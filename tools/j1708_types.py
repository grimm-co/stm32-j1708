import enum


class J1708FlagEnum(enum.IntFlag):
    def __repr__(self):
        return str(self)

    def __str__(self):
        return f'{self.name} ({self.value:X})'

    @classmethod
    def get_set_flags(cls, value):
        matches = []
        for flag in list(cls):
            if flag & value:
                matches.append(flag)
        return matches


class StatusGroupEnum(J1708FlagEnum):
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
        #return f'{self.name} (& {self.mask:X} = {value:X})'
        return f'{self.name} ({value:X} & {self.mask:X})'


class StatusGroupEnumAndValue(enum.IntFlag):
    def __new__(cls, value, mask, is_value_field=False):
        # Method to ensure that the mask value is not treated as part of the 
        # value
        obj = super().__new__(cls, value)
        obj.mask = mask
        obj.is_value_field = is_value_field

        if is_value_field:
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
                            f'{field.name}: {field_val:b} ({field.value:b} & {field.mask:b}) == ' \
                            f'{val:b} ({value:b} & {mask:b})'
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

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        if self.is_value_field:
            return f'{self.name}: {self.value}'
        else:
            value = self.value & self.mask
            #return f'{self.name} (& {self.mask:X} = {value:X})'
            return f'{self.name} ({value:X} & {self.mask:X})'

    @classmethod
    def get_set_flags(cls, value):
        value_matches = []
        for field in list(cls):
            if field.is_value_field:
                val = cls._missing_(value * field.mask)
                val._name_ = field._name_
                value_matches.append(val)

        flag_matches = []
        for field in list(cls):
            if field & value:
                flag_matches.append(field)
        return (value_matches, flag_matches)

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


class J1708CruiseControlStatus(J1708FlagEnum):
    ACTIVE = (1 << 7)
    CLUTCH = (1 << 6)
    BRAKE  = (1 << 5)
    ACCEL  = (1 << 4)
    RESUME = (1 << 3)
    COAST  = (1 << 2)
    SET    = (1 << 1)
    ON     = (1 << 0)
    OFF    = 0


class J1708IndicatorLampStatus(StatusGroupEnum):
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


class J1708BrakeSwitchStatus(StatusGroupEnum):
    # Use bits that don't matter to ensure that all the "OFF" values are unique
    BRAKE_ERROR         = (0b11111011, 0x0C)
    BRAKE_ON            = (0b11110111, 0x0C)
    BRAKE_OFF           = (0b11110011, 0x0C)
    SERVICE_BRAKE_ERROR = (0b11111110, 0x03)
    SERVICE_BRAKE_ON    = (0b11111101, 0x03)
    SERVICE_BRAKE_OFF   = (0b11111100, 0x03)


class J1708ParkingBrakeStatus(StatusGroupEnum):
    ON  = (0b1 << 7, 0x80)
    OFF = (0b0 << 7, 0x80)

