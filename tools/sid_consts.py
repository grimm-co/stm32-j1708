from utils import RangeDict


common_sids = RangeDict({
    151: 'System Diagnostic Code #1',
    152: 'System Diagnostic Code #2',
    153: 'System Diagnostic Code #3',
    154: 'System Diagnostic Code #4',
    155: 'System Diagnostic Code #5',
    range(156, 202): 'Reserved',
    203: 'Door Switch',
    204: 'Diagnostics Data Available Through Alternate Reporting Method',
    205: 'J1939 Network #3',
    206: 'J1939 Network #2',
    207: 'Battery #1 Temperature',
    208: 'Battery #2 Temperature',
    209: 'Start Enable Device #2',
    210: 'Oil Temperature Sensor',
    211: 'Sensor Supply Voltage #2 (+5V DC)',
    212: 'Sensor Supply Voltage #1 (+5V DC)',
    213: 'PLC Data Link',
    214: 'ECU Backup Battery',
    215: 'Cab Interior Temperature Thermostat',
    216: 'Other ECUs Have Reported Fault Codes Affecting Operation',
    217: 'Anti-theft Start Inhibit (Password Valid Indicator)',
    218: 'ECM Main Relay',
    219: 'Start Signal Indicator',
    220: 'Electronic Tractor/Trailer Interface (ISO 11992)',
    221: 'Internal Sensor Voltage Supply',
    222: 'Protect Lamp',
    223: 'Ambient Light Sensor',
    224: 'Audible Alarm',
    225: 'Green Lamp',
    226: 'Transmission Neutral Switch',
    227: 'Auxiliary Analog Input #1',
    228: 'High Side Refrigerant Pressure Switch',
    229: 'Kickdown Switch',
    230: 'Idle Validation Switch',
    231: 'SAE J1939 Data Link',
    232: '5 Volts DC Supply',
    233: 'Controller #2',
    234: 'Parking Brake On Actuator',
    235: 'Parking Brake Off Actuator',
    236: 'Power Connect Device',
    237: 'Start Enable Device',
    238: 'Diagnostic Lamp—Red',
    239: 'Diagnostic Light—Amber',
    240: 'Program Memory',
    241: 'Set aside for Systems Diagnostics',
    242: 'Cruise Control Resume Switch',
    243: 'Cruise Control Set Switch',
    244: 'Cruise Control Enable Switch',
    245: 'Clutch Pedal Switch #1',
    246: 'Brake Pedal Switch #1',
    247: 'Brake Pedal Switch #2',
    248: 'Proprietary Data Link',
    249: 'SAE J1922 Data Link',
    250: 'SAE J1708 (SAE J1587) Data Link',
    251: 'Power Supply',
    252: 'Calibration Module',
    253: 'Calibration Memory',
    254: 'Controller #1',
    255: 'Reserved',
})


# Engine SIDs (MID = 128, 175, 183, 184, 185, 186)
engine_sids = RangeDict({
    0: 'Reserved',
    1: 'Injector Cylinder #1',
    2: 'Injector Cylinder #2',
    3: 'Injector Cylinder #3',
    4: 'Injector Cylinder #4',
    5: 'Injector Cylinder #5',
    6: 'Injector Cylinder #6',
    7: 'Injector Cylinder #7',
    8: 'Injector Cylinder #8',
    9: 'Injector Cylinder #9',
    10: 'Injector Cylinder #10',
    11: 'Injector Cylinder #11',
    12: 'Injector Cylinder #12',
    13: 'Injector Cylinder #13',
    14: 'Injector Cylinder #14',
    15: 'Injector Cylinder #15',
    16: 'Injector Cylinder #16',
    17: 'Fuel Shutoff Valve #1',
    18: 'Fuel Control Valve',
    19: 'Throttle Bypass Valve',
    20: 'Timing Actuator',
    21: 'Engine Position Sensor',
    22: 'Timing Sensor',
    23: 'Rack Actuator',
    24: 'Rack Position Sensor',
    25: 'External Engine Protection Input #1',
    26: 'Auxiliary Output Device Driver #1',
    27: 'Variable Geometry Turbocharger Actuator #1',
    28: 'Variable Geometry Turbocharger Actuator #2',
    29: 'External Fuel Command Input',
    30: 'External Speed Command Input',
    31: 'Tachometer Signal Output',
    32: 'Turbocharger #1 Wastegate Drive',
    33: 'Fan Clutch Output Device Driver',
    34: 'Exhaust Back Pressure Sensor',
    35: 'Exhaust Back Pressure Regulator Solenoid',
    36: 'Glow Plug Lamp',
    37: 'Electronic Drive Unit Power Relay',
    38: 'Glow Plug Relay',
    39: 'Engine Starter Motor Relay',
    40: 'Auxiliary Output Device Driver #2',
    41: 'ECM 8 Volts DC Supply',
    42: 'Injection Control Pressure Regulator',
    43: 'Autoshift High Gear Actuator',
    44: 'Autoshift Low Gear Actuator',
    45: 'Autoshift Neutral Actuator',
    46: 'Autoshift Common Low Side (Return)',
    47: 'Injector Cylinder #17',
    48: 'Injector Cylinder #18',
    49: 'Injector Cylinder #19',
    50: 'Injector Cylinder #20',
    51: 'Auxiliary Output Device Driver #3',
    52: 'Auxiliary Output Device Driver #4',
    53: 'Auxiliary Output Device Driver #5',
    54: 'Auxiliary Output Device Driver #6',
    55: 'Auxiliary Output Device Driver #7',
    56: 'Auxiliary Output Device Driver #8',
    57: 'Auxiliary PWM Driver #1',
    58: 'Auxiliary PWM Driver #2',
    59: 'Auxiliary PWM Driver #3',
    60: 'Auxiliary PWM Driver #4',
    61: 'Variable Swirl System Valve',
    62: 'Prestroke Sensor',
    63: 'Prestroke Actuator',
    64: 'Engine Speed Sensor #2',
    65: 'Heated Oxygen Sensor',
    66: 'Ignition Control Mode Signal',
    67: 'Ignition Control Timing Signal',
    68: 'Secondary Turbo Inlet Pressure',
    69: 'After Cooler-Oil Cooler Coolant Temperature',
    70: 'Inlet Air Heater Driver #1',
    71: 'Inlet Air Heater Driver #2',
    72: 'Injector Cylinder #21',
    73: 'Injector Cylinder #22',
    74: 'Injector Cylinder #23',
    75: 'Injector Cylinder #24',
    76: 'Knock Sensor',
    77: 'Gas Metering Valve',
    78: 'Fuel Supply Pump Actuator',
    79: 'Engine (Compression) Brake Output #1',
    80: 'Engine (Compression) Brake Output #2',
    81: 'Engine (Exhaust) Brake Output',
    82: 'Engine (Compression) Brake Output #3',
    83: 'Fuel Control Valve #2',
    84: 'Timing Actuator #2',
    85: 'Engine Oil Burn Valve',
    86: 'Engine Oil Replacement Valve',
    87: 'Idle Shutdown Vehicle Accessories Relay Driver',
    88: 'Turbocharger #2 Wastegate Drive',
    89: 'Air Compressor Actuator Circuit',
    90: 'Engine Cylinder #1 Knock Sensor',
    91: 'Engine Cylinder #2 Knock Sensor',
    92: 'Engine Cylinder #3 Knock Sensor',
    93: 'Engine Cylinder #4 Knock Sensor',
    94: 'Engine Cylinder #5 Knock Sensor',
    95: 'Engine Cylinder #6 Knock Sensor',
    96: 'Engine Cylinder #7 Knock Sensor',
    97: 'Engine Cylinder #8 Knock Sensor',
    98: 'Engine Cylinder #9 Knock Sensor',
    99: 'Engine Cylinder #10 Knock Sensor',
    100: 'Engine Cylinder #11 Knock Sensor',
    101: 'Engine Cylinder #12 Knock Sensor',
    102: 'Engine Cylinder #13 Knock Sensor',
    103: 'Engine Cylinder #14 Knock Sensor',
    104: 'Engine Cylinder #15 Knock Sensor',
    105: 'Engine Cylinder #16 Knock Sensor',
    106: 'Engine Cylinder #17 Knock Sensor',
    107: 'Engine Cylinder #18 Knock Sensor',
    108: 'Engine Cylinder #19 Knock Sensor',
    109: 'Engine Cylinder #20 Knock Sensor',
    110: 'Engine Cylinder #21 Knock Sensor',
    111: 'Engine Cylinder #22 Knock Sensor',
    112: 'Engine Cylinder #23 Knock Sensor',
    113: 'Engine Cylinder #24 Knock Sensor',
    114: 'Multiple Unit Synchronization Switch',
    115: 'Engine Oil Change Interval',
    116: 'Engine was Shut Down Hot',
    117: 'Engine has been Shut Down from Data Link Information',
    118: 'Injector Needle Lift Sensor #1',
    119: 'Injector Needle Lift Sensor #2',
    120: 'Coolant System Thermostat',
    121: 'Engine Automatic Start Alarm',
    122: 'Engine Automatic Start Lamp',
    123: 'Engine Automatic Start Safety Interlock Circuit',
    124: 'Engine Automatic Start Failed (Engine)',
    125: 'Fuel Heater Driver Signal',
    126: 'Fuel Pump Pressurizing Assembly #1',
    127: 'Fuel Pump Pressurizing Assembly #2',
    128: 'Starter Solenoid Lockout Relay Driver Circuit',
    129: 'Cylinder #1 Exhaust Gas Port Temperature',
    130: 'Cylinder #2 Exhaust Gas Port Temperature',
    131: 'Cylinder #3 Exhaust Gas Port Temperature',
    132: 'Cylinder #4 Exhaust Gas Port Temperature',
    133: 'Cylinder #5 Exhaust Gas Port Temperature',
    134: 'Cylinder #6 Exhaust Gas Port Temperature',
    135: 'Cylinder #7 Exhaust Gas Port Temperature',
    136: 'Cylinder #8 Exhaust Gas Port Temperature',
    137: 'Cylinder #9 Exhaust Gas Port Temperature',
    138: 'Cylinder #10 Exhaust Gas Port Temperature',
    139: 'Cylinder #11 Exhaust Gas Port Temperature',
    140: 'Cylinder #12 Exhaust Gas Port Temperature',
    141: 'Cylinder #13 Exhaust Gas Port Temperature',
    142: 'Cylinder #14 Exhaust Gas Port Temperature',
    143: 'Cylinder #15 Exhaust Gas Port Temperature',
    144: 'Cylinder #16 Exhaust Gas Port Temperature',
    145: 'Adaptive Cruise Control Mode',
    146: 'Exhaust Gas Recirculation (EGR) Valve #1 Mechanism',
    147: 'Variable Nozzle Turbocharger (VNT) Mechanism',
    148: 'Engine (Compression) Brake Output #4',
    149: 'Engine (Compression) Brake Output #5',
    255: 'Engine (Compression) Brake Output #6',
    256: 'Reserved',
    257: 'Auxiliary output device driver # 9',
    258: 'Auxiliary output device driver # 10',
    259: 'Auxiliary output device driver # 11',
    260: 'Auxiliary output device driver # 12',
    261: 'Auxiliary output device driver # 13',
    262: 'Auxiliary output device driver # 14',
    263: 'Auxiliary output device driver # 15',
    264: 'Auxiliary output device driver # 16',
    265: 'Auxiliary output device driver # 17',
    266: 'Exhaust Gas Recirculation (EGR) Valve #2 Mechanism',
    267: 'Auxiliary PWM Driver #5',
    268: 'Auxiliary PWM Driver #6',
    269: 'Turbocharger Nozzle Position Sensor',
    270: 'Turbocharger Compressor Discharge Temperature Sensor',
    271: 'Charge Air Cooler Bypass Control',
    272: 'Charge Air Cooler Air Outlet Temperature Sensor',
    273: 'Charge Air Cooler Air Outlet Pressure Sensor',
    274: 'Combustion Air Humidity Sensor',
    275: 'Auxiliary Engine Cooling System Control Output',
    276: 'Inlet Air Pre-Cleaner Control Output',
    277: 'Exhaust Gas Recirculation (EGR) Mass Flow Sensor',
    278: 'Fuel Shutoff Valve #2',
    279: 'Fuel Leakage Sensor #1',
    280: 'Fuel Leakage Sensor #2',
    281: 'Exhaust Gas Recirculation (EGR) Check Valve(s)',
    282: 'Exhaust Gas Recirculation (EGR) Cooler',
    283: 'Intake Valve Actuation System Oil Pressure Control Valve',
    284: 'Engine Coolant Diverter Valve',
    285: 'Intake Valve Actuator #1',
    286: 'Intake Valve Actuator #2',
    287: 'Intake Valve Actuator #3',
    288: 'Intake Valve Actuator #4',
    289: 'Intake Valve Actuator #5',
    290: 'Intake Valve Actuator #6',
    291: 'Intake Valve Actuator #7',
    292: 'Intake Valve Actuator #8',
    293: 'Intake Valve Actuator #9',
    294: 'Intake Valve Actuator #10',
    295: 'Intake Valve Actuator #11',
    296: 'Intake Valve Actuator #12',
    297: 'Intake Valve Actuator #13',
    298: 'Intake Valve Actuator #14',
    299: 'Intake Valve Actuator #15',
    300: 'Intake Valve Actuator #16',
    301: 'Intake Valve Actuator #17',
    302: 'Intake Valve Actuator #18',
    303: 'Intake Valve Actuator #19',
    304: 'Intake Valve Actuator #20',
    305: 'Gas Control Valve # 1 Outlet Pressure (Natural Gas)',
    306: 'Engine Coolant # 2 Pressure #1',
    307: 'Mixer Inlet Relative Humidity',
    308: 'Fuel Rack Position # 2',
    309: 'Turbocharger Compressor Outlet # 1 Pressure',
    310: 'Waste Engine Oil Reservoir Level',
    311: 'Engine Oil Level # 2 Remote Reservoir',
    312: 'Coolant Level # 2',
    313: 'Injector Cylinder, Multiple',
    314: 'Turbocharger #1 Compressor Inlet Pressure (absolute)',
    315: 'External Engine Protection Input #2',
    316: 'Service Indication Lamp',
    317: 'Injector Supply Voltage',
    318: 'Particulate Trap Intake Gas Temperature Bank 1',
    319: 'Particulate Trap Intake Gas Temperature Bank 2',
    320: 'Particulate Trap Outlet Gas Temperature Bank 1',
    321: 'Particulate Trap Outlet Gas Temperature Bank 2',
    322: 'Particulate Trap Intermediate Gas Temperature Bank 1',
    323: 'Particulate Trap Intermediate Gas Temperature Bank 2',
    324: 'Particulate Trap Differential Pressure Bank 1',
    325: 'Particulate Trap Differential Pressure Bank 2',
    326: 'Exhaust Gas Temperature 1',
    327: 'Exhaust Gas Temperature 2',
    328: 'Exhaust Gas Temperature 3',
    329: 'Exhaust Gas Temperature 1 Bank 2',
    330: 'Exhaust Gas Temperature 2 Bank 2',
    331: 'Exhaust Gas Temperature 3 Bank 2',
    332: 'Aftertreatment #1 Fuel Pressure',
    333: 'Aftertreatment #1 Fuel Pressure Control Actuator',
    334: 'Aftertreatment #1 Fuel Enable Actuator',
    335: 'Aftertreatment #1 Ignition',
    336: 'Aftertreatment #2 Fuel Pressure',
    337: 'Aftertreatment #2 Fuel Pressure Control Actuator',
    338: 'Aftertreatment #2 Fuel Enable Actuator',
    339: 'Aftertreatment #2 Ignition',
    340: 'Aftertreatment #1 Air Enable Actuator',
    341: 'Aftertreatment #1 Purge Air Actuator',
    342: 'Aftertreatment #1 Atomization Air Actuator',
    343: 'Aftertreatment #1 Air System Relay',
    344: 'Aftertreatment #2 Air Enable Actuator',
    345: 'Aftertreatment #2 Purge Air Actuator',
    346: 'Aftertreatment #2 Atomization Air Actuator',
    347: 'Aftertreatment #2 Air System Relay',
    348: 'Aftertreatment #1 Supply Air Pressure',
    349: 'Aftertreatment #1 Purge Air Pressure',
    350: 'Aftertreatment #1 Air Pressure Control Actuator',
    351: 'Aftertreatment #1 Air Pressure Actuator Position',
    352: 'Aftertreatment #2 Supply Air Pressure',
    353: 'Aftertreatment #2 Purge Air Pressure',
    354: 'Aftertreatment #2 Air Pressure Control Actuator',
    355: 'Aftertreatment #2 Air Pressure Actuator Position',
    356: 'Aftertreatment #1 Failed to Ignite',
    357: 'Aftertreatment #1 Loss of Ignition',
    358: 'Aftertreatment #2 Failed to Ignite',
    359: 'Aftertreatment #2 Loss of Ignition',
    360: 'Aftertreatment #1 Regeneration Manually Disabled',
    361: 'Aftertreatment #2 Regeneration Manually Disabled',
    362: 'Injector Cylinder #1, Actuator #2',
    363: 'Injector Cylinder #2, Actuator #2',
    364: 'Injector Cylinder #3, Actuator #2',
    365: 'Injector Cylinder #4, Actuator #2',
    366: 'Injector Cylinder #5, Actuator #2',
    367: 'Injector Cylinder #6, Actuator #2',
    368: 'Injector Cylinder #7, Actuator #2',
    369: 'Injector Cylinder #8, Actuator #2',
    370: 'Aftertreatment #1 Particulate Trap Intake Pressure',
    371: 'Aftertreatment #1 Particulate Trap Outlet Pressure',
    372: 'Ambient Air Density',
    373: 'Aftertreatment #1 Secondary Air Differential Pressure',
    374: 'Aftertreatment #2 Secondary Air Differential Pressure',
    375: 'Aftertreatment #1 Secondary Air Temperature',
    376: 'Aftertreatment #2 Secondary Air Temperature',
    377: 'Aftertreatment #1 Secondary Air Pressure',
    378: 'Aftertreatment #2 Secondary Air Pressure',
    379: 'Oil Scavenge Pump',
    380: 'Catalyst 1 System Monitor',
    381: 'Aftertreatment 1 Fuel Drain Actuator',
    382: 'Aftertreatment 1 Fuel Injector 1',
    383: 'Particulate Matter Trap Monitor',
    384: 'Engine Turbocharger 1 Turbine Inlet Temperature',
    385: 'Accelerator Pedal #1 Channel 2',
    386: 'Aftertreatment #1 Purge Air Pressure',
    387: 'Aftertreatment #1 Secondary Air Mass Flow',
    388: 'Particulate Trap Active Regeneration Inhibited Due to Permanent System Lockout',
    389: 'Aftertreatment 1 Fuel Rate',
    390: 'Particulate Trap Active Regeneration Inhibited Status',
    391: 'Engine Exhaust Gas Recirculation (EGR) System Monitor',
    392: 'Engine Injector Bank 1',
    393: 'Particulate Trap Active Regeneration Inhibited Due to Inhibit Switch',
    394: 'Particulate Trap Active Regeneration Inhibited Due to Temporary System Lockout',
    395: 'Engine Air Shutoff Command Status',
    396: 'Aftertreatment 1 Ignition Transformer Secondary Output',
range(397, 511): 'Reserved',
})


# Transmission SIDs(MID = 130, 176, 223)
transmission_sids = {}


# Brake SIDs (MIDs = 136, 137, 138, 139, 246, 247)
brake_sids = {}


# Instrument Panel SIDs (MID = 140, 234)
instrument_panel_sids = {}


# Vehicle Management SIDs (MID = 142, 187, 188)
vehicle_management_sids = {}


# Fuel System SIDs (MID = 143)
fuel_system_sids = {}


# Cab Climate Control SIDs (MID = 146, 200)
cab_climate_control_sids = {}


# Suspension SIDs (MID = 150, 151)
suspension_sids = {}


# Park Brake Controller SIDs (MID = 157)
park_brake_controller_sids = {}


# Vehicle Navigation SIDs (MID = 162, 191)
vehicle_navigation_sids = {}


# Vehicle Security SIDs (MID = 163)
vehicle_security_sids = {}


# Tire SIDs (MID = 166, 168, 169, 186)
tire_sids = {}


# Particulate Trap SIDs (MID = 177)
particulate_trap_sids = {}


# Vehicle Sensors to Data Converter SIDs (MID = 178)
vehicle_sensors_to_data_converter_sids = {}


# Refrigerant Management Systems SIDs (MID = 190)
refrigerant_management_systems_sids = {}


# Tractor/Trailer Bridge SIDs (MID = 217, 218)
tractor_trailer_bridge_sids = {}


# Collision Avoidance Systems SIDs (MID = 219)
collision_avoidance_systems_sids = {}


# Safety Restraint System SIDs (MID = 232, 254)
safety_restraint_system_sids = {}


# Forward Road Image Processor SIDs (MID = 248)
forward_road_image_processor_sids = {}


# Brake Stroke Alert Monitor, Tractor SIDs (MID = 253)
brake_stroke_alert_monitor_tractor_sids = {}

"""
Reserved for future assignment by SAE
0
1
2
3
4
5
6
7
8
9
10
11
12
13
14
15
16
17
18
19
20
21
22
23
24
25

Reserved
C1 Solenoid Valve
C2 Solenoid Valve
C3 Solenoid Valve
C4 Solenoid Valve
C5 Solenoid Valve
C6 Solenoid Valve
Lockup Solenoid Valve
Forward Solenoid Valve
Low Signal Solenoid Valve
Retarder Enable Solenoid Valve
Retarder Modulation Solenoid Valve
Retarder Response Solenoid Valve
Differential Lock Solenoid Valve
Engine/Transmission Match
Retarder Modulation Request Sensor
Neutral Start Output
Turbine Speed Sensor
Primary Shift Selector
Secondary Shift Selector
Special Function Inputs
C1 Clutch Pressure Indicator
C2 Clutch Pressure Indicator
C3 Clutch Pressure Indicator
C4 Clutch Pressure Indicator
C5 Clutch Pressure Indicator
SAE
 J1587 Revised JUL2008
 - 33 -
TABLE 7 - SUBSYSTEM26
27
28
29
30
31
32
33
34
35
36
37
38
39
40
41
42
43
44
45
46
47
48
49
50
51
52
53
54
55
56
57
58
59
60
61
62
63
64
65–150
IDENTIFICATION (SID) ASSIGNMENT LIST (CONTINUED)
C6 Clutch Pressure Indicator
Lockup Clutch Pressure Indicator
Forward Range Pressure Indicator
Neutral Range Pressure Indicator
Reverse Range Pressure Indicator
Retarder Response System Pressure Indicator
Differential Lock Clutch Pressure Indicator
Multiple Pressure Indicators
Reverse Switch
Range High Actuator
Range Low Actuator
Splitter Direct Actuator
Splitter Indirect Actuator
Shift Finger Rail Actuator 1
Shift Finger Gear Actuator 1
Upshift Request Switch
Downshift Request Switch
Torque Converter Interrupt Actuator
Torque Converter Lockup Actuator
Range High Indicator
Range Low Indicator
Shift Finger Neutral Indicator
Shift Finger Engagement Indicator
Shift Finger Center Rail Indicator
Shift Finger Rail Actuator 2
Shift Finger Gear Actuator 2
Hydraulic System
Defuel Actuator
Inertia Brake Actuator
Clutch Actuator
Auxiliary Range Mechanical System
Shift Console Data Link
Main Box Shift Engagement System
Main Box Rail Selection System
Main Box Shift Neutralization System
Auxiliary Splitter Mechanical System
Transmission Controller Power Relay
Output Shaft Speed Sensor
Throttle Position Device
Reserved for future assignment by SAE
Brake SIDs (MIDs = 136, 137, 138, 139, 246, 247)
0
 Reserved
1
 Wheel Sensor ABS Axle 1 Left
2
 Wheel Sensor ABS Axle 1 Right
3
 Wheel Sensor ABS Axle 2 Left
4
 Wheel Sensor ABS Axle 2 Right
5
 Wheel Sensor ABS Axle 3 Left
6
 Wheel Sensor ABS Axle 3 Right
SAE
TABLE 7 - SUBSYSTEM7
8
9
10
11
12
13
14
15
16
17
18
19
20
21
22
23
24
25
26
27
28
29
30
31
32
33
34
35
36
37
38
39
40
41
42
43
44
45
46
47
48
49
50
51
52
53
54
55
J1587 Revised JUL2008
 - 34 -
IDENTIFICATION (SID) ASSIGNMENT LIST (CONTINUED)
Pressure Modulation Valve ABS Axle 1 Left
Pressure Modulation Valve ABS Axle 1 Right
Pressure Modulation Valve ABS Axle 2 Left
Pressure Modulation Valve ABS Axle 2 Right
Pressure Modulation Valve ABS Axle 3 Left
Pressure Modulation Valve ABS Axle 3 Right
Retarder Control Relay
Relay Diagonal 1
Relay Diagonal 2
Mode Switch ABS
Mode Switch ASR
DIF 1—ASR Valve
DIF 2—ASR Valve
Pneumatic Engine Control
Electronic Engine Control (Servomotor)
Speed Signal Input
Tractor ABS Warning Light Bulb
ASR Light Bulb
Wheel Sensor, ABS Axle 1 Average
Wheel Sensor, ABS Axle 2 Average
Wheel Sensor, ABS Axle 3 Average
Pressure Modulator, Drive Axle Relay Valve
Pressure Transducer, Drive Axle Relay Valve
Master Control Relay
Trailer Brake Slack Out of Adjustment Forward Axle Left
Trailer Brake Slack Out of Adjustment Forward axle Right
Trailer Brake Slack Out of Adjustment Rear Axle Left
Trailer Brake Slack Out of Adjustment Rear Axle Right
Tractor Brake Slack Out of Adjustment Axle 1 Left
Tractor Brake Slack Out of Adjustment Axle 1 Right
Tractor Brake Slack Out of Adjustment Axle 2 Left
Tractor Brake Slack Out of Adjustment Axle 2 Right
Tractor Brake Slack Out of Adjustment Axle 3 Left
Tractor Brake Slack Out of Adjustment Axle 3 Right
Ride Height Relay
Hold Modulator Valve Solenoid Axle 1 Left
Hold Modulator Valve Solenoid Axle 1 Right
Hold Modulator Valve Solenoid Axle 2 Left
Hold Modulator Valve Solenoid Axle 2 Right
Hold Modulator Valve Solenoid Axle 3 Left
Hold Modulator Valve Solenoid Axle 3 Right
Dump Modulator Valve Solenoid Axle 1 Left
Dump Modulator Valve Solenoid Axle 1 Right
Dump Modulator Valve Solenoid Axle 2 Left
Dump Modulator Valve Solenoid Axle 2 Right
Dump Modulator Valve Solenoid Axle 3 Left
Dump Modulator Valve Solenoid Axle 3 Right
Hydraulic Pump Motor
Brake Light Switch 1
SAE
TABLE 7 - SUBSYSTEM56
57
58
59
60
61
62
63
64
65
66
67
68
69
70
71
72
73
74
75
76
77
78
79
80
81
82
83
84
85
86
87
88
89
90
91
92
93
94
95
96
97
98
99
100
101
102
103
104
J1587 Revised JUL2008
 - 35 -
IDENTIFICATION (SID) ASSIGNMENT LIST (CONTINUED)
Brake Light Switch 2
Electronic Pressure Control, Axle 1
Pneumatic Back-up Pressure Control, Axle 1
Brake Pressure Sensing, Axle 1
Electronic Pressure Control, Axle 2
Pneumatic Back-up Pressure Control, Axle 2
Brake Pressure Sensing, Axle 2
Electronic Pressure Control, Axle 3
Pneumatic Back-up Pressure Control, Axle 3
Brake Pressure Sensing, Axle 3
Electronic Pressure Control, Trailer Control
Pneumatic Back-up Pressure Control, Trailer Control
Brake Pressure Sensing, Trailer Control
Axle Load Sensor
Lining Wear Sensor, Axle 1 Left
Lining Wear Sensor, Axle 1 Right
Lining Wear Sensor, Axle 2 Left
Lining Wear Sensor, Axle 2 Right
Lining Wear Sensor, Axle 3 Left
Lining Wear Sensor, Axle 3 Right
Brake Signal Transmitter
Brake Signal Sensor 1
Brake Signal Sensor 2
Tire Dimension Supervision
Vehicle Deceleration Control
Trailer ABS Warning Light Bulb
Brake Torque Output Axle 1 Left
Brake Torque Output Axle 1 Right
Brake Torque Output Axle 2 Left
Brake Torque Output Axle 2 Right
Brake Torque Output Axle 3 Left
Brake Torque Output Axle 3 Right
Vehicle Dynamic Stability Control System (VDC)
Steering Angle Sensor
Voltage Supply for Stability Control System
Brake Lining Display
Pressure Limitation Valve
Auxiliary Valve
Hill holder System
Voltage Supply, Lining Wear Sensors, Axle 1
Voltage Supply, Lining Wear Sensors, Axle 2
Voltage Supply, Lining Wear Sensors, Axle 3
Reference Ground Connection
Lateral Accelerometer
Brake Light Relay
Brake Warning Light Bulb
Differential Lock control output (transfer case)
Yaw Rate Sensor
Service Odometer
SAE
 J1587 Revised JUL2008
 - 36 -
TABLE 7 - SUBSYSTEM IDENTIFICATION (SID) ASSIGNMENT LIST (CONTINUED)
105–150
 Reserved for future assignment by SAE
Instrument Panel SIDs
0
1
2
3
4
5
6
7
8
9
10
11
12
13
14
16
15
17
18
19
20
21
22
23
24
25–150
VehicleManagement0
1
2
3
4
5
6
7
8
9
10
11
12
13
14
15
16
17
(MID = 140, 234)
Reserved
Left Fuel Level Sensor
Right Fuel Level Sensor
Fuel Feed Rate Sensor
Fuel Return Rate Sensor
Tachometer Gauge Coil
Speedometer Gauge Coil
Turbocharger Air Pressure Gauge Coil
Fuel Pressure Gauge Coil
Fuel Level Gauge Coil
Second Fuel Level Gauge Coil
Engine Oil Pressure Gauge Coil
Engine Oil Temperature Gauge Coil
Engine Coolant Temperature Gauge Coil
Pyrometer Gauge Coil
Transmission Oil Pressure Gauge Coil
Transmission Oil Temperature Gauge Coil
Forward Rear Axle Temperature Gauge Coil
Rear Rear Axle Temperature Gauge Coil
Voltmeter Gauge Coil
Primary Air Pressure Gauge Coil
Secondary Air Pressure Gauge Coil
Ammeter Gauge Coil
Air Application Gauge Coil
Air Restriction Gauge Coil
Reserved for future assignment by SAE
SIDs (MID = 142, 187, 188)
Reserved
Timing Sensor
Timing Actuator
Fuel Rack Position Sensor
Fuel Rack Actuator
Oil Level Indicator Output
Tachometer Drive Output
Speedometer Drive Output
PWM Input (ABS/ASR)
PWM Output
Auxiliary Output #1
Auxiliary Output #2
Auxiliary Output #3
Auxiliary Output #4
Auxiliary Output #5
Power Relay Control Output
“Neutral” Power Relay Control Output
Starter Relay Control Output
SAE
 J1587 Revised JUL2008
 - 37 -
TABLE 7 - SUBSYSTEM IDENTIFICATION (SID) ASSIGNMENT LIST (CONTINUED)
18
19
20
21
22
23
24
25
26
27
28
29
30
31
32
33
34
35
36
37
38
39
40–150
Transmission Shift Control Valve #1 Output
Transmission Shift Control Valve #2 Output
Differential Lock Control Valve #1 Output
Differential Lock Control Valve #2 Output
Windshield Wiper ON Relay Control Output
Windshield Wiper Speed Select Output
Mirror Heat Control Output
Driver Door “Lock” Output
Driver Door “Unlock” Output
Switch Diagnostic Output
Horn Control Output
“Wake Up” Output
Interior Lamps Output
Fan Override Indicator Lamp Output
Low Air Pressure Indicator Relay Output
Maintenance Lamp Output
Battery Monitor Load #1 Control Output
Battery Monitor Load #2 Control Output
Headlamp Low Beam Left #1 Output
Headlamp Low Beam Left #2 Output
Headlamp Low Beam Right #1 Output
Headlamp Low Beam Right #2 Output
Reserved for future assignment by SAE
Fuel System SIDs0
1
2
3
4
5
6
7
8
9
10
11
12
13
14
15
16
17
18
19
20
21
22
23
(MID = 143)
Reserved
Injector Cylinder #1
Injector Cylinder #2
Injector Cylinder #3
Injector Cylinder #4
Injector Cylinder #5
Injector Cylinder #6
Injector Cylinder #7
Injector Cylinder #8
Injector Cylinder #9
Injector Cylinder #10
Injector Cylinder #11
Injector Cylinder #12
Injector Cylinder #13
Injector Cylinder #14
Injector Cylinder #15
Injector Cylinder #16
Fuel Shutoff Valve
Fuel Control Valve
Throttle Bypass Valve
Timing Actuator
Engine Position Sensor
Timing Sensor
Rack Actuator
SAE
 J1587 Revised JUL2008
 - 38 -
TABLE 7 - SUBSYSTEM IDENTIFICATION (SID) ASSIGNMENT LIST (CONTINUED)
24
25
26
27
28
29
30
31
32
33–150
Rack Position Sensor
External Engine Protection Input
Auxiliary Output Device Driver
Cooling Fan Drive Output
Engine (Compression) Brake Output #1
Engine (Compression) Brake Output #2
Engine (Exhaust) Brake Output
Pressure Control Valve #1
Pressure Control Valve #2
Reserved for future assignment by SAE
Cab Climate Control1
2
3
4
5
6
7
8
9
10
11
12
13
14
15
16
17
18
19
20
21
22
23
24
25
26
27
28
29
30
31-150
SIDs (MID = 146, 200)
HVAC Unit Discharge Temperature Sensor
Evaporator Temperature Sensor
Solar Load Sensor #1
Solar Load Sensor #2
Fresh/Recirculation Air Intake Door Actuator
Mode Door #1 Actuator
Mode Door #2 Actuator
Mode Door #3 Actuator
Blend Door Actuator
Blower Motor
A/C Clutch Relay
Water Valve
Heater Exchanger Temperature Sensor
In Cabin Temperature Sensor Blower
Blower Clutch
Stepper Motor Phase 1
Stepper Motor Phase 2
Stepper Motor Phase 3
Stepper Motor Phase 4
Refrigerant Evaporator Inlet Temperature Sensor
Refrigerant Evaporator Outlet Temperature Sensor
Refrigerant Evaporator Inlet Pressure Sensor
Refrigerant Evaporator Outlet Pressure Sensor
Refrigerant Compressor Inlet Temperature Sensor
Refrigerant Compressor Outlet Temperature Sensor
Refrigerant Compressor Inlet Pressure Sensor
Refrigerant Compressor Outlet Pressure Sensor
Refrigerant Condenser Outlet Temperature Sensor
Refrigerant Condenser Outlet Pressure Sensor
Climate Control Air Filter Differential Pressure Sensor
Reserved for future assignment by SAE
Suspension SIDs (MID = 150, 151)
0
 Reserved
1
 Solenoid Valve Axle 1 Right
2
 Solenoid Valve Axle 1 Left
3
 Solenoid Valve Axle 2 Right
SAE
TABLE 7 - SUBSYSTEM4
5
6
7
8
9
10
11
12
13
14
15
16
17
18
19
20
21
22
23
24
25
26
27
28
29
30
31
32
33
34
35
36
37
38
39
40
41
42
43
44
45
46
47
48
49
50
51
52
J1587 Revised JUL2008
 - 39 -
IDENTIFICATION (SID) ASSIGNMENT LIST (CONTINUED)
Solenoid Valve Axle 2 Left
Solenoid Valve Axle 3 Right
Solenoid Valve Axle 3 Left
Solenoid Valve Central (Lowering/Lifting Control)
Solenoid Valve for Lifting the Lifting/Trailing Axle
Solenoid Valve for Lowering the Lifting/Trailing Axle
Solenoid Valve for Control of the Lift Bellow
Solenoid Valve for Starting Lock
Solenoid Valve for Door Release
Solenoid Valve for Mainflow Throttle
Solenoid Valve for Transverse Lock/Throttle
Solenoid Valve for Automatic Load-Dependent Brake-Power Balance
Height Sensor Axle 1 Right
Height Sensor Axle 1 Left
Height Sensor Axle 2 Right
Height Sensor Axle 2 Left
Height Sensor Axle 3 Right
Height Sensor Axle 3 Left
Pressure Sensor Axle 1 Right
Pressure Sensor Axle 1 Left
Pressure Sensor Axle 2 Right
Pressure Sensor Axle 2 Left
Pressure Sensor Axle 3 Right
Pressure Sensor Axle 3 Left
Pressure Sensor Lift Bellow
Sidewalk Detector Sensor
Switch for Maximum Permanent Permissible Pressure
Switch for Maximum Temporary Permissible Pressure
Speed Signal Input
Remote Control Unit #1
Central Valve Relay
Auxiliary Tank Control
Exterior Kneel (warning lamp and audible alarm)
Wheel Chair Lift Inhibit
Checksum ECU Specific Data
Checksum Parameter Data
Checksum Calibration Data Level Sensors
Checksum Calibration Data Pressure Sensors
Checksum Maximum Axle Load Data
Central 3/2 Solenoid Valve Axle 3
Central 3/2 Solenoid Valve Front Axle
Pressure Sensor Brake Pressure
Power Supply for Pressure Sensors
Power Supply for Remote Controls
Remote Control #1 Data Line
Remote Control #1 Clock Line
Remote Control #2 Data Line
Remote Control #2 Clock Line
Remote Control Unit #2
SAE
 J1587 Revised JUL2008
TABLE 7 - SUBSYSTEM IDENTIFICATION (SID) ASSIGNMENT LIST (CONTINUED)
53
54
55
56
57
58
59
60–150
Power Supply for Solenoid Valves
Proportional Valve Front Axle Left
Proportional Valve Front Axle Right
Proportional Valve Drive Axle Left
Proportional Valve Drive Axle Right
Proportional Valve Axle 3 Left
Proportional Valve Axle 3 Right
Reserved for future assignment by SAE
Park Brake Controller0
1
2
3
4
5
6
7
8
9
10
11
12
13
14
15
16
17
18
19
20
21
22
23
24
25
26
27
28
29
30
31
32
33
34
35
36
37
38
SIDs (MID = 157)
Reserved
Pressure Sender #1
Pressure Sender #2
Solenoid Control #1
Solenoid Control #2
Solenoid Control #3
Solenoid Control #4
Operator Control Switch #1 (input)
Operator Control Switch #2 (input)
Operator Station
Passenger Station
Interior Station
Exterior Station
Light Sequence Control
Warning light #1
Warning light #2
Speed Sense Comparator
Series Latch Monitor
Expansion ECU Station
Aux Switch Input #1
Aux Switch Input #2
Diagnostic Input
Aux Data Link (I2C)
Solenoid Supply #1
Solenoid Supply #2
Solenoid Supply #3
Solenoid Supply #4
Operator Control Switch #1 (output)
Operator Control Switch #2 (output)
Operator Control Switch Aux
Aux Output #1
Aux Output # 2
Aux Output # 3
Aux Output # 4
Aux Output # 5
Aux Output # 6
Aux Output # 7
Diagnostic Output
Pressure Control Modulator
- 40 -
SAE
 J1587 Revised JUL2008
 - 41 -
TABLE 7 - SUBSYSTEM IDENTIFICATION (SID) ASSIGNMENT LIST (CONTINUED)
39
 Series Latch Control
40
 Brownout Voltage Sequence Control
41-150
 Reserved for future assignment by SAE
Vehicle Navigation SIDs (MID = 162, 191)
0
 Reserved
1
 Dead Reckoning Unit
2
 Loran Receiver
3
 Global Positioning System (GPS)
4
 Integrated Navigation Unit
5–150
 Reserved for future assignment by SAE
Vehicle Security SIDs (MID = 163)
0
 Reserved
1
 Transceiver Antenna
2
 Security Transponder
3–150
 Reserved for future assignment by SAE
Tire SIDs (MID = 166,0
1
2
3
4
5
6
7
8
9
10
11
12
13
14
15
16
17
18
19
20
21
22
23
24
25
26
27
28
29
167, 168, 169, 186)
Reserved
Operator Control Panel (OCP)
Pneumatic Control Unit (PCU)
PCU Steer Solenoid
PCU Drive Solenoid
PCU Solenoid Trailer #1, Tag #1, or Push #1
PCU Supply Solenoid
PCU Control Solenoid
PCU Deflate Solenoid
Pneumatic—Steer Channel
Pneumatic—Drive Channel
Pneumatic—Trailer #1, Tag #1, or Push #1 Channel
Drive Axle Manifold Deflation Solenoid
Steer Axle Manifold Deflation Solenoid
PCU Solenoid Trailer #2, Tag #2, or Push #2
Brake Priority Pressure Switch
Pneumatic-Trailer #2, Tag #2, or Push #2 Channel
Wiring Harness
Tire Pressure Sensor - # 1
Tire Pressure Sensor - # 2
Tire Pressure Sensor - # 3
Tire Pressure Sensor - # 4
Tire Pressure Sensor - # 5
Tire Pressure Sensor - # 6
Tire Pressure Sensor - # 7
Tire Pressure Sensor - # 8
Tire Pressure Sensor - # 9
Tire Pressure Sensor - # 10
Tire Pressure Sensor - # 11
Tire Pressure Sensor - # 12
SAE
 J1587 Revised JUL2008
 - 42 -
TABLE 7 - SUBSYSTEM30
31
32
33
34
35
36
37
38
39
40
41
42
43
44
45
46
47
48
49
50
51
52
53
54
55
56
57
58
59
60
61
62
63
64
65
66–150
IDENTIFICATION (SID) ASSIGNMENT LIST (CONTINUED)
Tire Pressure Sensor - # 13
Tire Pressure Sensor - # 14
Tire Pressure Sensor - # 15
Tire Pressure Sensor - # 16
Tire Temperature Sensor - # 1
Tire Temperature Sensor - # 2
Tire Temperature Sensor - # 3
Tire Temperature Sensor - # 4
Tire Temperature Sensor - # 5
Tire Temperature Sensor - # 6
Tire Temperature Sensor - # 7
Tire Temperature Sensor - # 8
Tire Temperature Sensor - # 9
Tire Temperature Sensor - # 10
Tire Temperature Sensor - # 11
Tire Temperature Sensor - # 12
Tire Temperature Sensor - # 13
Tire Temperature Sensor - # 14
Tire Temperature Sensor - # 15
Tire Temperature Sensor - # 16
Tire Sensor Voltage - # 1
Tire Sensor Voltage - # 2
Tire Sensor Voltage - # 3
Tire Sensor Voltage - # 4
Tire Sensor Voltage - # 5
Tire Sensor Voltage - # 6
Tire Sensor Voltage - # 7
Tire Sensor Voltage - # 8
Tire Sensor Voltage - # 9
Tire Sensor Voltage - # 10
Tire Sensor Voltage - # 11
Tire Sensor Voltage - # 12
Tire Sensor Voltage - # 13
Tire Sensor Voltage - # 14
Tire Sensor Voltage - # 15
Tire Sensor Voltage - # 16
Reserved for future assignment by SAE
Particulate Trap SIDs related to (MID = 177)
0
 Reserved
1
 Particulate Trap Intake Gas Temperature Bank 1
2
 Particulate Trap Intake Gas Temperature Bank 2
3
 Particulate Trap Outlet Gas Temperature Bank 1
4
 Particulate Trap Outlet Gas Temperature Bank 2
5
 Particulate Trap Intermediate Gas Temperature Bank 1
6
 Particulate Trap Intermediate Gas Temperature Bank 2
7
 Particulate Trap Differential Pressure Bank 1
8
 Particulate Trap Differential Pressure Bank 2
9
 Exhaust Gas Temperature 1
SAE
TABLE 7 - SUBSYSTEM10
11
12
13
14
15
16
17
18
19
20
21
22
23
24
25
26
27
28
29
30
31
32
33
34
35
36
37
38
39
40
41
42
43
44
45
46
47
48
49
50
51
52
53
54
55
56
57
J1587 Revised JUL2008
 - 43 -
IDENTIFICATION (SID) ASSIGNMENT LIST (CONTINUED)
Exhaust Gas Temperature 2
Exhaust Gas Temperature 3
Exhaust Gas Temperature 1 Bank 2
Exhaust Gas Temperature 2 Bank 2
Exhaust Gas Temperature 3 Bank 2
Aftertreatment #1 Fuel Pressure
Aftertreatment #1 Fuel Pressure Control Actuator
Aftertreatment #1 Fuel Enable Actuator
Aftertreatment #1 Ignition
Aftertreatment #2 Fuel Pressure
Aftertreatment #2 Fuel Pressure Control Actuator
Aftertreatment #2 Fuel Enable Actuator
Aftertreatment #2 Ignition
Aftertreatment #1 Air Enable Actuator
Aftertreatment #1 Purge Air Actuator
Aftertreatment #1 Atomization Air Actuator
Aftertreatment #1 Air System Relay
Aftertreatment #2 Air Enable Actuator
Aftertreatment #2 Purge Air Actuator
Aftertreatment #2 Atomization Air Actuator
Aftertreatment #2 Air System Relay
Aftertreatment #1 Supply Air Pressure
Aftertreatment #1 Purge Air Pressure
Aftertreatment #1 Air Pressure Control Actuator
Aftertreatment #1 Air Pressure Actuator Position
Aftertreatment #2 Supply Air Pressure
Aftertreatment #2 Purge Air Pressure
Aftertreatment #2 Air Pressure Control Actuator
Aftertreatment #2 Air Pressure Actuator Position
Aftertreatment #1 Failed to Ignite
Aftertreatment #1 Loss of Ignition
Aftertreatment #2 Failed to Ignite
Aftertreatment #2 Loss of Ignition
Aftertreatment #1 Regeneration Manually Disabled
Aftertreatment #2 Regeneration Manually Disabled
Aftertreatment #1 Particulate Trap Intake Pressure
Aftertreatment #1 Particulate Trap Outlet Pressure
Oil Scavenge Pump
Catalyst 1 System Monitor
Aftertreatment 1 Fuel Drain Actuator
Aftertreatment 1 Fuel Injector 1
Particulate Matter Trap Monitor
Aftertreatment #1 Purge Air Pressure
Aftertreatment #1 Secondary Air Mass Flow
Particulate Trap Active Regeneration Inhibited Due to Permanent System
Lockout
Aftertreatment 1 Fuel Rate
Particulate Trap Active Regeneration Inhibited Status
Particulate Trap Active Regeneration Inhibited Due to Inhibit Switch
SAE
 J1587 Revised JUL2008
 - 44 -
TABLE 7 - SUBSYSTEM IDENTIFICATION (SID) ASSIGNMENT LIST (CONTINUED)
58
59-150
Particulate Trap Active Regeneration Inhibited Due to Temporary System
Lockout
Reserved for future assignment by SAE
Vehicle Sensors to0
1
2
3
4
5
6
7
8
9
10
11
12
13
14
15
16
17
18
19
20
21
22
23
24
25
26
27
28
29
30
31-150
Data Converter SIDs (MID = 178)
Reserved
Battery Positive Input
Battery Negative Input
Current Shunt (-) Input
Current Shunt (+) Input
Starter Negative Input
Alternator Negative Input
Transducer +5V Excitation
Starter Positive Input
Starter Solenoid Input
Alternator Positive Input
Alternator Field Input
Fuel Solenoid Positive Input
User Probe Input
Fuel Supply Sender Input
Air Cleaner Delta P Sender Input
Fuel Filter Delta P Sender Input
Oil Filter Inlet Sender Input
Fuel Return Sender Input
Oil Filter Outlet Sender Input
Fuel Vacuum Sender Input
Battery Negative Input Circuit
Battery Positive Input Circuit
Starter Positive Input Circuit
Starter Negative Input Circuit
Starter Solenoid Input Circuit
Alternator Field Input Circuit
Alternator Positive Input Circuit
Alternator Negative Input Circuit
Current Sensor Discharge Circuit
Current Sensor Charge Circuit
Reserved for future assignment by SAE
Refrigerant Management Systems SIDs (MID = 190)
0
 Reserved
1
 Refrigerant Charge
2
 Refrigerant Moisture Level
3
 Non-condensable Gas in Refrigerant
4
 Refrigerant Flow Control Solenoid
5
 Low Side Refrigerant Pressure Switch
6
 Compressor Clutch Circuit
7
 Evaporator Thermostat Circuit
8
 Refrigerant Flow
9
 Climate Control Air Filter Differential Pressure Sensor
10–150
 Reserved for future assignment by SAE
SAE
 J1587 Revised JUL2008
TABLE 7 - SUBSYSTEM IDENTIFICATION (SID) ASSIGNMENT LIST (CONTINUED)
Tractor/Trailer Bridge SIDs (MID = 217, 218)
0
 Reserved
1
 Auxiliary input #1
2
 Auxiliary input #2
3
 Auxiliary input #3
4
 Auxiliary input #4
5
 Auxiliary input #5
6
 Auxiliary input #6
7
 Auxiliary input #7
8
 Auxiliary input #8
9
 Clearance, side marker, identification lamp circuit (Black)
10
 Left turn lamp circuit (Yellow)
11
 Stop lamp circuit (Red)
12
 Right turn lamp circuit (Green)
13
 Tail lamp/license plate lamp circuit (Brown)
14
 Auxiliary lamp circuit (Blue)
15
 Tractor mounted rear axle slider control unit
16
 Trailer mounted rear axle slider control unit
17–150
 Reserved for future assignment by SAE
Collision Avoidance Systems SIDs (MID = 219)
0
1
2
3
4
5
6
7
8
9
10
11
12
13–150
Reserved
Forward Antenna
Antenna Electronics
Brake Input Monitor
Speaker Monitor
Steering Sensor Monitor
Speedometer Monitor
Right Turn Signal Monitor
Left Turn Signal Monitor
Control Display Unit
Right Side Sensor
Left Side Sensor
Rear Sensor
Reserved for future assignment by SAE
Driveline Retarder SIDs (MID = 222)
0
 Reserved
1
 Retarder Enable Solenoid Valve
2
 Retarder Modulation Solenoid Valve
3
 Retarder Response Solenoid Valve
4
 Retarder Modulation Request Sensor
5
 Retarder Response System Pressure Indicator
6–150
 Reserved for future assignment by SAE
- 45 -
SAE
 J1587 Revised JUL2008
 - 46 -
TABLE 7 - SUBSYSTEM IDENTIFICATION (SID) ASSIGNMENT LIST (CONTINUED)
Safety Restraint System SIDs (MID = 232, 254)
0
 Reserved
1
 Driver Air Bag Ignitor Loop
2
 Passenger Air Bag Ignitor Loop
3
 Left Belt Tensioner Ignitor Loop
4
 Right Belt Tensioner Ignitor Loop
5
 Safety Restraint System (SRS) Lamp—directly controlled by the ECU
6
 Automotive Seat Occupancy Sensor (AOS)—Passenger Side
7
 Side Collision Detector (SDC)—Left
8
 Side Bag Ignitor Loop 1—Left
9
 Side Bag Ignitor Loop 2—Left
10
 Side Collision Detector—Right
11
 Side Bag Ignitor Loop 1—Right
12
 Side Bag Ignitor Loop 2—Right
13
 Rollover Sensor
14
 Driver Air Bag Stage 2 Igniter Loop
15
 Passenger Air Bag Stage 2 Igniter Loop
16–150
 Reserved for future assignment by SAE
Forward Road Image Processor SIDs (MID = 248)
0
 Reserved
1
 Forward View Imager System
2-150
 Reserved for future assignment by SAE
Brake Stroke Alert0
1
2
3
4
5
6
7
8
9
10
11
12
13
14
15
16
17
18
19
20
21
22
23
Monitor, Tractor SIDs (MID = 253)
Reserved
Tractor Brake Stroke Axle 1 Left
Tractor Brake Stroke, Axle 1 Right
Tractor Brake Stroke, Axle 2 Left
Tractor Brake Stroke, Axle 2 Right
Tractor Brake Stroke, Axle 3 Left
Tractor Brake Stroke, Axle 3 Right
Tractor Brake Stroke, Axle 4 Left
Tractor Brake Stroke, Axle 4 Right
Tractor Brake Stroke Alert Monitor
Trailer #1 Brake Stroke, Axle 1 Left
Trailer #1 Brake Stroke, Axle 1 Right
Trailer #1 Brake Stroke, Axle 2 Left
Trailer #1 Brake Stroke, Axle 2 Right
Trailer #1 Brake Stroke, Axle 3 Left
Trailer #1 Brake Stroke, Axle 3 Right
Trailer #1 Brake Stroke, Axle 4 Left
Trailer #1 Brake Stroke, Axle 4 Right
Trailer #1 Brake Stroke, Alert Monitor
Trailer #2 Brake Stroke, Axle 1 Left
Trailer #2 Brake Stroke, Axle 1 Right
Trailer #2 Brake Stroke, Axle 2 Left
Trailer #2 Brake Stroke, Axle 2 Right
Trailer #2 Brake Stroke, Axle 3 Left
SAE
 J1587 Revised JUL2008
 - 47 -
TABLE 7 - SUBSYSTEM IDENTIFICATION (SID) ASSIGNMENT LIST (CONTINUED)
24
25
26
27
28
29
30
31
32
33
34
35
36
37
38
39
40
41
42
43
44
45
46-150
1. Superseded by SIDsTrailer #2 Brake Stroke, Axle 3 Right
Trailer #2 Brake Stroke, Axle 4 Left
Trailer #2 Brake Stroke Axle 4 Right
Trailer #2 Brake Stroke Alert Monitor
Trailer #3 Brake Stroke, Axle 1 Left
Trailer #3 Brake Stroke, Axle 1 Right
Trailer #3 Brake Stroke, Axle 2 Left
Trailer #3 Brake Stroke, Axle 2 Right
Trailer #3 Brake Stroke, Axle 3 Left
Trailer #3 Brake Stroke, Axle 3 Right
Trailer #3 Brake Stroke, Axle 4 Left
Trailer #3 Brake Stroke Axle 4 Right
Trailer #3 Brake Stroke Alert Monitor
Trailer Brake Stroke, Axle 1 Left
Trailer Brake Stroke, Axle 1 Right
Trailer Brake Stroke, Axle 2 Left
Trailer Brake Stroke, Axle 2 Right
Trailer Brake Stroke, Axle 3 Left
Trailer Brake Stroke, Axle 3 Right
Trailer Brake Stroke, Axle 4 Left
Trailer Brake Stroke, Axle 4 Right
Trailer Brake Stroke Alert Monitor
Reserved for future assignment by SAE
151–155
"""


mid_to_sid_map = {
    128: engine_sids,
    130: transmission_sids,
    136: brake_sids,
    137: brake_sids,
    138: brake_sids,
    139: brake_sids,
    140: instrument_panel_sids,
    142: vehicle_management_sids,
    142: fuel_system_sids,
    146: cab_climate_control_sids,
    150: suspension_sids,
    151: suspension_sids,
    157: park_brake_controller_sids,
    162: vehicle_navigation_sids,
    162: vehicle_security_sids,
    166: tire_sids,
    168: tire_sids,
    169: tire_sids,
    175: engine_sids,
    176: transmission_sids,
    176: particulate_trap_sids,
    178: vehicle_sensors_to_data_converter_sids,
    183: engine_sids,
    184: engine_sids,
    185: engine_sids,
    186: (engine_sids, tire_sids),
    187: vehicle_management_sids,
    188: vehicle_management_sids,
    190: refrigerant_management_systems_sids,
    191: vehicle_navigation_sids,
    200: cab_climate_control_sids,
    217: tractor_trailer_bridge_sids,
    218: tractor_trailer_bridge_sids,
    219: collision_avoidance_systems_sids,
    223: transmission_sids,
    232: safety_restraint_system_sids,
    234: instrument_panel_sids,
    246: brake_sids,
    247: brake_sids,
    248: forward_road_image_processor_sids,
    253: brake_stroke_alert_monitor_tractor_sids,
    254: safety_restraint_system_sids,
}


def get_sid_string(mid, sid):
    sid_table = mid_to_sid_map.get(mid, common_sids)

    if isinstance(sid_table, tuple):
        for table in sid_table:
            try:
                return table[sid]
            except KeyError:
                pass
        return f'Unknown SID {sid} for MID {mid}'
    else:
        try:
            return sid_table[sid]
        except KeyError:
            return f'Unknown SID {sid} for MID {mid}'


__all__ = [
    'get_sid_string',
]
