#!/usr/bin/env python3

import argparse
import j1708


def main():
    # TODO:
    #   1. Implement ability to Tx PID 195 to request info or clear DTCs
    #   2. change this from purely CLI to ipython interactive
    parser = argparse.ArgumentParser()
    parser.add_argument('--no-decode', '-N', action='store_true',
            help='disable J1587 message decoding')
    parser.add_argument('--ignore-checksums', '-i', action='store_true',
            help='ignore checksums when parsing J1708 messages')
    parser.add_argument('--reparse-log', '-r',
            help='read J1708 messages from an existing log and re-parse them')
    args = parser.parse_args()

    if args.reparse_log:
        iface = j1708.Iface()
        iface.reparse_log(args.reparse_log, not args.no_decode, args.ignore_checksums)
    else:
        port = j1708.find_device()
        assert port
        iface = j1708.Iface(port)
        iface.run(not args.no_decode, args.ignore_checksums)


if __name__ == '__main__':
    main()
