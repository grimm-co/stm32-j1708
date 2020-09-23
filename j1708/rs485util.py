# TODO:
#   1. Possible to merge this 485 reparseing function with iface.run?

import argparse

from .msg import J1708
from . import mids
from .log import Log


def parse_file(filename, decode=True, ignore_checksums=False, log_filename=None):
    """
    Attempt to identify valid messages in an RS485 log.

    This is challenging because a raw RS485 log does not have clear indications
    of when a message is complete or not. This function will attempt to sort
    messages into the smallest valid messages possible.
    """
    log = Log(decode=decode, ignore_checksums=ignore_checksums, log_filename=log_filename)

    with open(filename, 'rb') as f:
        data = f.read()

    found_msgs = []

    # Clear the message. use bytearray to hold the message we are constructing 
    # because it will behave just like a bytes object but is mutable.
    raw_msg = bytearray()
    incoming = False

    offset = 0
    end_offset = 0
    while offset < len(data):
        if not incoming and mids.is_valid(data[offset]):
            incoming = True
            raw_msg.append(data[offset])

            # If the end offset is not == offset, print how much was skipped
            if end_offset != offset:
                log.write(f'[{end_offset:08X}] SKIPPED {data[end_offset:offset].hex()}')

            offset += 1

        elif incoming:
            raw_msg.append(data[offset])
            offset += 1

            if len(raw_msg) >= 4:
                try:
                    # Technically 2 bytes is a valid message, but it seems 
                    # unlikely we will see that so to make it easier to "guess" 
                    # what a valid message is don't start checking for a valid 
                    # checksum/end of message until the message size reaches 
                    # 4 bytes
                    j1708_msg = J1708(raw_msg)
                    if j1708_msg is not None and j1708_msg.is_valid():

                        # Attempt to decode the message before we really 
                        # consider it valid
                        j1708_msg.decode()
                        found_msgs.append(j1708_msg)

                        # Record the end offset
                        end_offset = offset

                        # Prefix the message with the offset it was found at
                        start_offset = offset - len(raw_msg)
                        if decode:
                            log.write(f'[{start_offset:08X}] {j1708_msg.format_for_log()}')
                        else:
                            log.write(f'[{start_offset:08X}] {j1708_msg}')

                        # Clear the message
                        raw_msg = bytearray()
                        incoming = False
                except ValueError:
                    pass

            if len(raw_msg) >= 21:
                # max msg length is 21 bytes, if we've reached this length and 
                # still don't have a valid message, clear the current message, 
                # move the offset to 1 > the last offset this message started 
                # with, and try again
                prev_offset = offset - len(raw_msg)
                offset = prev_offset + 1

                # Clear the message
                raw_msg = bytearray()
                incoming = False

        else:
            offset += 1

    if end_offset != offset:
        log.write_print_and_loi(f'[{end_offset:08X}] SKIPPED {data[end_offset:offset].hex()}')
