import argparse

from .. import iface
from .. import log
from .. import rs485util


def main():
    # TODO:
    #   1. Implement ability to Tx PID 195 to request info or clear DTCs
    #   2. change this from purely CLI to ipython interactive
    #   3. Add timestamp support to j1708 firmware so logs have relative 
    #      timestamps in them
    parser = argparse.ArgumentParser()
    parser.add_argument('--no-decode', '-N', action='store_true',
            help='disable J1587 message decoding')
    parser.add_argument('--ignore-checksum', '-i', action='store_true',
            help='ignore checksums when parsing J1708 messages')
    parser.add_argument('--import-from-raw', '-I',
            help='read J1708 messages from an raw serial log')
    parser.add_argument('--reparse-log', '-r',
            help='read J1708 messages from an existing log and re-parse them')
    parser.add_argument('--output-log', '-o',
            help='Save output to a log file')
    args = parser.parse_args()

    if args.reparse_log:
        log.reparse(args.reparse_log, not args.no_decode, args.ignore_checksum, args.output_log)
    elif args.import_from_raw:
        rs485util.parse_file(args.import_from_raw, not args.no_decode, args.ignore_checksum, args.output_log)
    else:
        port = iface.find_device()
        assert port
        dev = iface.Iface(port)
        try:
            dev.run(not args.no_decode, args.ignore_checksum, args.output_log)
        except KeyboardInterrupt:
            # Add a return char to help make the next command prompt look nice
            print('')
