#!/usr/bin/env python3

import argparse
import serial.tools.list_ports
import j1708

def find_device():
    for p in serial.tools.list_ports.grep('0483:5740'): 
        if 'j1708' in p.manufacturer:
            return p.device


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--no-decode', '-N', action='store_true',
            help='disable J1587 message decoding')
    args = parser.parse_args()

    port = find_device()
    iface = j1708.Iface(port)
    iface.run(not args.no_decode)


if __name__ == '__main__':
    main()
