#!/usr/bin/env python3

import argparse
import j1708


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--no-decode', '-N', action='store_true',
            help='disable J1587 message decoding')
    args = parser.parse_args()

    port = j1708.find_device()
    assert port
    iface = j1708.Iface(port)
    iface.run(not args.no_decode)


if __name__ == '__main__':
    main()
