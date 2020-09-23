import argparse
import serial.tools.list_ports

from .iface import Iface, decode_and_print
from .msg import J1708
from . import rs485util


def find_device():
    """
    Identifies if there are any USB devices that match the VID:PID and device
    strings expected for the J1708 tool.
    """
    for p in serial.tools.list_ports.grep('0483:5740'): 
        if 'j1708' in p.manufacturer.lower():
            return p.device
    return None


__all__ = [
    'J1708',
    'Iface',
    'find_device',
    'decode_and_print',
]


def main():
    # TODO:
    #   1. Implement ability to Tx PID 195 to request info or clear DTCs
    #   2. change this from purely CLI to ipython interactive
    parser = argparse.ArgumentParser()
    parser.add_argument('--no-decode', '-N', action='store_true',
            help='disable J1587 message decoding')
    parser.add_argument('--ignore-checksums', '-i', action='store_true',
            help='ignore checksums when parsing J1708 messages')
    parser.add_argument('--import-from-raw', '-I',
            help='read J1708 messages from an raw serial log')
    parser.add_argument('--reparse-log', '-r',
            help='read J1708 messages from an existing log and re-parse them')
    parser.add_argument('--output-log', '-o',
            help='Save output to a log file')
    args = parser.parse_args()

    if args.reparse_log:
        iface = Iface()
        iface.reparse_log(args.reparse_log, not args.no_decode, args.ignore_checksums, args.output_log)
    elif args.import_from_raw:
        rs485util.parse_file(args.import_from_raw, not args.no_decode, args.ignore_checksums, args.output_log)
    else:
        port = find_device()
        assert port
        iface = Iface(port)
        try:
            iface.run(not args.no_decode, args.ignore_checksums, args.output_log)
        except KeyboardInterrupt:
            # Add a return char to help make the next command prompt look nice
            print('')
