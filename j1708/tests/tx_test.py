#!/usr/bin/env python3

import time
import j1708


def main():
    port = j1708.find_device()
    iface = j1708.Iface(port)

    # choosing a MID to send as: 142 "Vehicle Management System" (0x8E)
    # Fuel Level: PID 96 (0x60)
    # fuel level data is 0.5% per count
    #   50% * 2 = 100 (0x64)
    test_msg = bytes.fromhex('ea6064')
    while True:
        iface.send(test_msg)
        time.sleep(1.0)


if __name__ == '__main__':
    main()
