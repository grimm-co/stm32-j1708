import enum


class J1708FlagEnum(enum.IntFlag):
    def __str__(self):
        return f'{self.name} ({self.value:#x})'


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


class StatusGroupEnum(enum.IntFlag):
    #_ignore_ = '_MASKS'
    def __new__(cls, value, mask=None):
        #if mask:
        #    try:
        #        cur_masks = getattr(cls, '_MASKS')
        #    except AttributeError:
        #        cur_masks = []

        #    setattr(cls, '_MASKS', list(set(cur_masks + [mask])))
        obj = super().__new__(cls, value)
        obj.mask = mask
        return obj

    def __and__(self, other):
        value = self.value & self.mask
        if other.value & self.mask == value:
            return True
        #for group, mask in [(self.value & m, m) for m in self._MASKS]:
        #    if group and other.value & mask == group:
        #        return True
        return False

    def __str__(self):
        value = self.value & self.mask
        return f'{self.name} (& {self.mask:#x} = {value:#x})'


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
