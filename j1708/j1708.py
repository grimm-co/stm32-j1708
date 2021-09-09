#!/usr/bin/env python

import sys
import cmd
import readline
import rlcompleter
readline.parse_and_bind("tab: complete")
import os

from j1708 import *



if __name__ == "__main__":
    import argparse

    # Make it easy to find modules in CWD
    sys.path.append('.')

    parser = argparse.ArgumentParser()
    parser.add_argument('-p', '--port', help='eg: /dev/ttyACM0') 
    parser.add_argument('--tx', help='File with J1708 data to transmit')

    ifo = parser.parse_args()

    interface = J1708Interface

    results = interactive(ifo.port, ifo.tx)
    if results == -1:
        print("Error.  Try '-h' from CLI for help.")

