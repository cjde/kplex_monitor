#!/usr/bin/python
import os
import re
import argparse
import sys
from Adafruit_LED_Backpack import SevenSegment

# this is the device to display mapping table
# this say what LED dispaly has what address and what pattern to look for in the I2C output
device=[
 {'disp': 0, 'pat': ' 70 ', 'addr': 0x70},
 {'disp': 1, 'pat': ' 71 ', 'addr': 0x71},
 {'disp': 2, 'pat': ' 72 ', 'addr': 0x72}
]

def SevenSegSetup(SevSeg):
    '''
    This checks if the seven segment desplay is on I2C bus address
    and return true if it was able to set it up. If the i2cdetect is not available or
    address 70 is not detected then return false
    '''

    import subprocess

    # if we find the command and we have a device with address on it ...
    got_display = False

    # detection binary
    i2c_cmd = "/usr/sbin/i2cdetect"
    if ( os.path.isfile(i2c_cmd) ):
        # file exists see if we have a device address 70 on it
        p = subprocess.Popen([i2c_cmd, '-y','1'],stdout=subprocess.PIPE,)

        # should get back something like this if there are three LCD backpacks:
        '''
             0  1  2  3  4  5  6  7  8  9  a  b  c  d  e  f
        00:          -- -- -- -- -- -- -- -- -- -- -- -- --
        10: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
        20: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
        30: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
        40: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
        50: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
        60: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
        70: 70 71 72 -- -- -- -- --
        '''
        # cmdout = str(p.communicate())

        # look for the addresses of the displays and put the address (in hex ) on the LED
        # nine line of output ....
        for i in range(0,9):
            line = str(p.stdout.readline())

            # look for the pattern in each line
            for i in range(0,len(device)-1):
                # need the LED display number, the hex address of the I2C bus and
                # the pattern to find in the i2c output that says it is there
                disp = device[i]['disp']
                addr = device[i]['addr']
                pat  = device[i]['pat']

                # look for the devices in the i2cdetect output
                for match in re.finditer(pat, line):
                    SevSeg[disp] = SevenSegment.SevenSegment(address=addr,busnum=1)
                    SevSeg[disp].begin()
                    SevSeg[disp].clear()
                    SevSeg[disp].print_hex(addr )
                    SevSeg[disp].write_display()
                    #SevSeg[disp].set_brightness(15)
                    SevSeg[disp].set_brightness(1)
                    got_display = True

    return got_display


def update_displays(SevSeg, d1, d2 , d3):
    '''
    This takes updates the displays with the heading and if they are connected,
    the headings from the previous two tacks

    :rtype: object
    :param d1: Compas value on the first display
    :param d2: compas value on the second display
    :param d3: previous track value on the third display


    :return:
    '''

    # if the display has come loose, or there is a brown out , we may need to reset the bus
    success = True
    # print "headings: ", d1, d2, d3

    # this display is for the current heading
    if SevSeg[0]:
        SevSeg[0].clear()
        SevSeg[0].print_number_str(d1, justify_right=True)

        try:
            SevSeg[0].write_display()
        except:
            success = False
            print "Display 0 is disconnected"

    # when the other displays are available we can display them here
    # this is the display for the  average track
    if SevSeg[1]:
        SevSeg[1].clear()
        SevSeg[1].print_number_str(d2, justify_right=True)

        try:
            SevSeg[1].write_display()
        except:
            success = False
            print "Display 1 is disconnected"


    # if this display is connected then this would hold the heading from the last tack
    if SevSeg[2]:
        SevSeg[2].clear()
        SevSeg[2].print_number_str(d3, justify_right=True)

        try:
            SevSeg[2].write_display()
        except:
            success = False
            print "Display 2 is disconnected"

    return  success

#
# ----------- test function -----------
#

if __name__ == "__main__":
   import time
   # theoretically there could be three displays connected, current heading, last tack and
   # the tack heading from befor that. Of course the second display could show lift or heading
   # value to but that is not what it is doing rignt now
   SEVSEG = [0, 0, 0]

   if SevenSegSetup(SEVSEG):
        time.sleep(.75)
        SEVSEG[0].set_brightness(1)
        SEVSEG[0].print_hex('8888')
        SEVSEG[0].write_display()
        SEVSEG[1].set_brightness(1)
        SEVSEG[1].print_hex('8888')
        SEVSEG[1].write_display()
        time.sleep(.75)

        heading1 = '-100'
        heading2 = '200'
        heading3 = '300'
        if not ( update_displays( SEVSEG, heading1, heading2, heading3 )):
            print "Lost connection to display"
        time.sleep(.75)

        heading1 = '150'
        heading2 = '250'
        heading3 = '350'
        if not ( update_displays( SEVSEG, heading1, heading2, heading3 )):
            print "Lost connection to display"
        time.sleep(.75)

        heading1 = '135 '
        heading2 = '210'
        heading3 = '330'
        if not ( update_displays( SEVSEG, heading1, heading2, heading3 )):
            print "Lost connection to display"
        time.sleep(.75)

        blank = '----'
        if not ( update_displays( SEVSEG, heading1, heading2, heading3 )):
            print "Lost connection to display"
        time.sleep(.75)
        if not ( update_displays( SEVSEG, heading1, heading2, heading3 )):
            print "Lost connection to display"
        time.sleep(.75)
        if not ( update_displays( SEVSEG, heading1, heading2, heading3 )):
            print "Lost connection to display"

   else:
        print "Primary LED display not detected"
        exit
