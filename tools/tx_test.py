#!/usr/bin/env python3

import time
import serial.tools.list_ports
import j1708

def find_device():
    for p in serial.tools.list_ports.grep('0483:5740'): 
        if 'j1708' in p.manufacturer:
            return p.device


def main():
    port = find_device()
    iface = j1708.Iface(port)

    # choosing a MID to send as: 142 "Vehicle Management System" (0x8E)
    # Fuel Level: PID 96 (0x60)
    # fuel level data is 0.5% per count
    #   50% * 2 = 100 (0x64)
    test_msg = bytes.fromhex('8e6064')
    while True:
        iface.send(test_msg)
        time.sleep(0.5)


if __name__ == '__main__':
    main()
