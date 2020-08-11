#!/usr/bin/env python3

import serial.tools.list_ports
import j1708

def find_device():
    for p in serial.tools.list_ports.grep('0483:5740'): 
        if 'j1708' in p.manufacturer:
            return p.device


def main():
    port = find_device()
    iface = j1708.Iface(port)
    iface.run()


if __name__ == '__main__':
    main()
