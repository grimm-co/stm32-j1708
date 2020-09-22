from .utils import RangeDict

msgs = RangeDict({
    range(0, 7): 'J1708: Engine',
    range(8, 9): 'J1708: Brakes, Tractor',
    10: 'Trailer ABS Indicator Lamp ON',        # SAE J2497/PLC
    11: 'Trailer ABS Indicator Lamp OFF',       # SAE J2497/PLC
    range(12, 13): 'J1708: Tires, Tractor',
    range(14, 15): 'J1708: Tires, Trailer',
    range(16, 17): 'J1708: Suspension, Tractor',
    range(18, 19): 'J1708: Suspension, Trailer',
    range(20, 27): 'J1708: Transmission',
    range(28, 29): 'J1708: Electrical Charging System',
    range(30, 32): 'J1708: Electrical',
    range(33, 35): 'J1708: Cargo Refrigeration/Heating',
    range(36, 40): 'J1708: Instrument Cluster',
    range(41, 45): 'J1708: Driver Information Center',
    range(46, 47): 'J1708: Cab Climate Control',
    range(48, 55): 'J1708: Diagnostic Systems',
    range(56, 61): 'J1708: Trip Recorder',
    range(62, 63): 'J1708: Turbocharger',
    range(64, 68): 'J1708: Off-Board Diagnostics',
    range(69, 86): 'J1922',
    87: 'Trailer ABS Active',                   # SAE J2497/PLC
    range(88, 110): 'J1708: Dynamic MID Assignment',
    111: 'J1708: Factory Electronic Module Tester (Off Vehicle)',
    range(112, 127): 'J1708: Unassigned - Available For Use',

    # 128-255: SAE J1587
    128: 'Engine #1',
    129: 'Turbocharger',
    130: 'Transmission',
    131: 'Power Takeoff',
    132: 'Axle, Power Unit',
    133: 'Axle, Trailer',
    range(134, 135): '(Reclaimed)',
    136: 'Brakes, Power Unit',
    137: 'Brakes, Trailer #1',
    138: 'Brakes, Trailer #2',
    139: 'Brakes, Trailer #3',
    140: 'Instrument Cluster',
    141: 'Trip Recorder',
    142: 'Vehicle Management System',
    143: 'Fuel System',
    144: 'Cruise Control',
    145: 'Road Speed Indicator',
    146: 'Cab Climate Control',
    147: 'Cargo Refrigeration / Heating, Trailer',
    range(148, 149): '(Reclaimed)',
    150: 'Suspension, Power Unit',
    151: 'Suspension, Trailer',
    range(152, 153): '(Reclaimed)',
    154: 'Diagnostic Systems, Power Unit',
    155: 'Diagnostic Systems, Trailer',
    156: '(Reclaimed)',
    157: 'Park Brake Controller',
    158: 'Electrical Charging System',
    159: 'Proximity Detector, Front',
    160: 'Proximity Detector, Rear',
    161: 'Aerodynamic Control Unit',
    162: 'Vehicle Navigation Unit',
    163: 'Vehicle Security',
    164: 'Multiplex',
    165: 'Communication Unit-Ground',
    166: 'Tires, Power Unit',
    167: 'Tires, Trailer',
    168: 'Tires, Trailer #2',
    169: 'Tires, Trailer #3',
    170: 'Electrical',
    171: 'Driver Information Center #1',
    172: 'Off-board Diagnostics #1',
    173: 'Engine Retarder',
    174: 'Cranking/Starting System',
    175: 'Engine #2',
    176: 'Transmission, Additional/Hybrid Control Module',
    177: 'Particulate Trap System',
    178: 'Vehicle Sensors to Data Converter',
    179: 'Data Logging Computer',
    180: 'Off-board Diagnostics #2',
    181: 'Communication Unit-Satellite',
    182: 'Off-board Programming Station',
    183: 'Engine #3',
    184: 'Rear Axle Steering Controller',
    185: 'Pneumatic System Controller',
    186: 'Tires Control Unit',
    187: 'Vehicle Management System #2',
    188: 'Vehicle Management System #3',
    189: 'Vehicle Head Signs',
    190: 'Refrigerant Management Protection and Diagnostics',
    191: 'Vehicle Location Unit-Differential Correction',
    192: 'Front Door (Door #1) Status Unit',
    193: 'Middle Door (Door #2) Status Unit',
    194: 'Rear Door (Door #3) Status Unit',
    195: 'Annunciator Unit',
    196: 'Fare Collection Unit',
    197: 'Passenger Counter Unit #1',
    198: 'Schedule Adherence Unit',
    199: 'Route Adherence Unit',
    200: 'Environment Monitor Unit / Auxiliary Cab Climate Control',
    201: ' Vehicle Status Points Monitor Unit',
    202: 'High Speed Communications Unit',
    203: 'Mobile Data Terminal Unit',
    204: 'Vehicle Proximity, Right Side',
    205: 'Vehicle Proximity, Left Side',
    206: 'Base Unit (Radio Gateway to Fixed End)',
    207: 'Bridge from SAE J1708 Drivetrain Link',
    208: 'Maintenance Printer',
    209: 'Fifth Wheel Hitch Monitoring Device',
    210: 'Bus Chassis Identification Unit',
    211: 'Smart Card Terminal',
    212: 'Mobile Data Terminal',
    213: 'Vehicle Control Head Touch Screen',
    214: 'Silent Alarm Unit',
    215: 'Surveillance Microphone',
    216: 'Lighting Control Administrator Unit',
    217: 'Tractor/Trailer Gateway, Tractor Mounted',
    218: 'Tractor/Trailer Gateway, Trailer Mounted',
    219: 'Collision Avoidance Systems',
    220: 'Tachograph',
    221: 'Driver Information Center #2',
    222: 'Driveline Retarder',
    223: 'Transmission Shift Console-Primary',
    224: 'Parking Heater',
    225: 'Weighing System, Axle Group #1 / Vehicle',
    226: 'Weighing System, Axle Group #2',
    227: 'Weighing System, Axle Group #3',
    228: 'Weighing System, Axle Group #4',
    229: 'Weighing System, Axle Group #5',
    230: 'Weighing System, Axle Group #6',
    231: 'Communication Unit-Cellular',
    232: 'Safety Restraint System #1',
    233: 'Intersection Preemption Emitter',
    234: 'Instrument Cluster #2',
    235: 'Engine Oil Control System',
    236: 'Entry Assist Control #1',
    237: 'Entry Assist Control #2',
    238: 'Idle Adjust System',
    239: 'Passenger Counter Unit #2',
    240: 'Passenger Counter Unit #3',
    241: 'Fuel Tank Monitor',
    242: 'Door # 4 Status Unit',
    243: 'Door # 5 Status Unit',
    244: 'Door # 6 Status Unit',
    245: 'Weighing System Display / Door # 7 Status Unit',
    246: 'Brakes, Trailer #4 / Door # 8 Status Unit',
    247: 'Brakes, Trailer #5',
    248: 'Forward Road Image Processor',
    249: 'Body Controller',
    250: 'Steering Column Unit',
    range(251, 255): '(Reclaimed)',
    253: 'Brake Stroke Alert Monitor, Tractor',
    254: 'Safety Restraint System #2',
    255: 'Reserved',
})


def is_valid(mid):
    try:
        mid_name = msgs[mid]
    except KeyError:
        return False

    if mid_name not in ('Reserved', '(Reclaimed)'):
        return True
    else:
        return False


def get_mid_name(mid):
    try:
        return msgs[mid]
    except KeyError:
        return f'Unknown MID {mid}'

def get_mid(mid):
    return {'mid': mid, 'name': get_mid_name(mid)}


def decode(data):
    return (get_mid(data[0]), data[1:])


def encode(mid):
    if isinstance(mid, int):
        mid_num = mid
    elif hasattr(mid, 'mid'):
        mid_num = mid['mid']
    return struct.pack('>B', mid_num)


__all__ = [
    'decode',
    'encode',
    'get_mid_name',
    'is_valid',
]
