#!/usr/bin/env python

import serial
import time
import threading

class J1708Interface(object):
    '''
    This is the J1708 object. The following methods can be used to 
    interact with the J1708 bus. Run the command j.methodName? for more
    information about any particular method (e.g, j.tx_from_file?)

    j.printMsgs
    j.getMsgCount
    j.send 
    j.txFromFile

    '''
    def __init__(self, port='/dev/ttyACM0'):
        self.msgs = []
        self.partial_msg = b''
        self.port = port
        self.io = serial.Serial(port)

        self.startRxThread()

    # Serial RX/TX Thread
    def rxtx(self):
        while True:
            if(self.io.in_waiting > 0):
                ser_data = self.io.read(self.io.in_waiting)

                unproc_msgs = ser_data.split(b'$')
                if(len(unproc_msgs[0]) == 0):
                    unproc_msgs = unproc_msgs[1:]

                # Check to see if the first byte is a start of message "$". If not, then append it with the previous
                # partial message if one was received
                if (ser_data[0] != ord('$')): # First message is not complete
                    if(len(self.partial_msg) > 0):
                        self.partial_msg = self.partial_msg + unproc_msgs[0]

                        # Check if the partial message is now complete
                        if(self.partial_msg[-1] == b'*'):
                            self.msgs.append(bytes.fromhex(self.partial_msg[0:-1].decode('utf-8')))
                            self.partial_msg = b''
                    unproc_msgs = unproc_msgs[1:]

                # Process all messages except the first one if it was not a SOM (handled above) and the
                # last one in case it is a partial
                for i in range(0, len(unproc_msgs) - 1):
                    self.msgs.append(bytes.fromhex(unproc_msgs[i][0:-1].decode('utf-8')))

                # Process the last message as long as more than one message was received, if only one message
                # was received this case is handled above
                if (len(unproc_msgs) > 0):
                    if(unproc_msgs[-1][-1] != ord('*')):
                        self.partial_msg = unproc_msgs[-1]
                    else:
                        self.msgs.append(bytes.fromhex(unproc_msgs[-1][0:-1].decode('utf-8')))
            time.sleep(0.1)

    def startRxThread(self):
        self.commsthread = threading.Thread(target=self.rxtx)
        self.commsthread.setDaemon(True)
        self.commsthread.start()


    def printMsgs(self, verbose=False, mids=[], bytematch=[]):
        '''
        Print received J1708 messages

        Setting verbose=True prints more verbose message information

        The mids paramter takes an array of mids to print

        The bytematch paramter takes an array of tuples, where the first element
        of the tuple is the index (0-based, and index 0 is the MID) and the second 
        element is the byte value to match. If the message is shorter than the defined
        index that message will always be ignored.
        '''
        for i in self.msgs:
            if(len(mids) > 0):
                mid = i[0]
                if not mid in mids:
                    continue

            if(len(bytematch) > 0):
                skip = False
                for b in bytematch:
                    if b[0] >= len(i):
                        skip = True
                        break
                    if i[b[0]] != b[1]:
                        skip = True
                        break
                if(skip):
                    continue

            if(verbose):
                print("MID:  " + hex(i[0]))
                print("DATA: " + i[1:-1].hex())
                print("CKSM: " + hex(i[-1]))
                print("---------------------------------------------")
            else:
                print(i.hex())

    def getMsgCount(self):
        '''
        Prints the number of messages received
        '''
        print(len(self.msgs))

    def send(self, mid, data):
        '''
        Transmits the data using the specified mid. mid is expected to be an integer
        value and data is a hex string, e.g, "5588A7" to send the values 0x55, 0x88 and 0xA7.
        The checksum is calculated automatically.
        '''
        data = bytes.fromhex(data)
        chksm = self.j1708_checksum(mid, data)
        fullmsg = "${:02x}".format(mid)
        for i in data:
            fullmsg = fullmsg + "{:02x}".format(i)
        fullmsg = fullmsg + "{:02x}*".format(chksm)
        print(bytes(fullmsg, 'utf-8'))
        self.io.write(bytes(fullmsg, 'utf-8'))

    def j1708_checksum(self, mid, data):
        '''
        Calculate the J1708 checksum for mid and data. mid is an integer and
        data is a byte array
        '''
        chksum = 0
        chksum = mid & 0xFF
        for char in data:
            chksum = (chksum + char) & 0xFF
 
        if chksum != 0:
            # Determine what the checksum _should_ be
            chksum = 0x100 - chksum
        return chksum
        
    def txFromFile(self, filename, timing=0.5, mid=None):
        '''
        Transmits the data in the specified file. Data should be encoded
        as hexadecimal strings (e.g, 55AA74 will send the bytes 0x55, 0xAA, 0x74).
        Checksums are calculated automatically, the data in the file should not include
        the checksum.

        If mid is None, the first byte of the data in the file is assumed to be the MID.
        If mis is specified that mid will be used. Timing is the amount of time to wait between
        transmissions.
        '''
        # Transmit the specified file if it exists
        file = open(filename, 'r')
        lines = file.readlines()
        file.close()
        for i in lines:
            if mid is None:
                self.send(int(i[0:2], 16), i[2:])
            else:
                self.send(mid, i)
            time.sleep(timing)


def interactive(port=None):
    global j
    import atexit
    intro = 'J1708 Shell\n\nType j? and press enter for help.'
    print(intro)

    j = J1708Interface(port=port)

    gbls = globals()
    lcls = locals()

    try:
        import IPython.Shell
        ipsh = IPython.Shell.IPShell(argv=[''], user_ns=lcls, user_global_ns=gbls)
        ipsh.mainloop(intro)

    except ImportError as e:
        try:
            from IPython.terminal.interactiveshell import TerminalInteractiveShell
            ipsh = TerminalInteractiveShell()
            ipsh.user_global_ns.update(gbls)
            ipsh.user_global_ns.update(lcls)
            ipsh.autocall = 2       # don't require parenthesis around *everything*.  be smart!
            ipsh.mainloop(intro)
        except ImportError as e:
            try:
                from IPython.frontend.terminal.interactiveshell import TerminalInteractiveShell
                ipsh = TerminalInteractiveShell()
                ipsh.user_global_ns.update(gbls)
                ipsh.user_global_ns.update(lcls)
                ipsh.autocall = 2       # don't require parenthesis around *everything*.  be smart!
                ipsh.mainloop(intro)
            except ImportError as e:
                print(e)
                shell = code.InteractiveConsole(gbls)
                shell.interact(intro)

