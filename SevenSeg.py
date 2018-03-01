#!/usr/bin/python
import os
import re
import argparse
import sys
from Adafruit_LED_Backpack import SevenSegment

def SevenSegSetup(SevSeg):
    '''
    This checks if the seven segment desplay is on I2C bus address
    and return true if it was able to set it up. if hte i2cdetect is not available or
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
        #cmdout = str(p.communicate())

        # look for the addresses of the displays
        for i in range(0,9):
            line = str(p.stdout.readline())

            for match in re.finditer(" 70 ", line):
                SevSeg[0] = SevenSegment.SevenSegment(address=0x70,busnum=1)
                SevSeg[0].begin()
                SevSeg[0].clear()
                SevSeg[0].print_float(70, decimal_digits=0 )
                SevSeg[0].write_display()
                got_display = True

            for match in re.finditer(" 71 ", line):
                SevSeg[1] = SevenSegment.SevenSegment(address=0x71,busnum=1)
                SevSeg[1].begin()
                SevSeg[1].clear()
                SevSeg[1].print_float(71, decimal_digits=0 )
                SevSeg[1].write_display()

            for match in re.finditer(" 72 ", line):
                SevSeg[2] = SevenSegment.SevenSegment(address=0x72,busnum=1)
                SevSeg[2].begin()
                SevSeg[2].clear()
                SevSeg[2].print_float(72, decimal_digits=0 )
                SevSeg[2].write_display()

    return got_display




def update_displays(SevSeg, heading, tacks ):
    '''
    This takes updates the displays with the heading and if they are connected,
    the headings from the previous two tacks

    :param heading: Compas heading to put on the primary display
    :param tacks: List of tacks if there are no previous tacs tod display the lithe up all segments
    :return:
    '''
   
    print "heading: ", heading 

    if SevSeg[0]:
        SevSeg[0].clear()
        if heading < 0 :
            SevSeg[0].print_hex(0x8888)
        else:
            SevSeg[0].print_float(heading, decimal_digits=0, justify_right=True)
        SevSeg[0].write_display()

    # when the other displays are available we can display them here 
    # this is the display for the previous tack 
    if SevSeg[1]:
        SevSeg[1].clear()
        if tacks[1] < 0 :
            SevSeg[1].print_hex(0x00)
        else:
            SevSeg[1].print_float(tacks[1], decimal_digits=0, justify_right=True)
        SevSeg[1].write_display()

        
    # if this display is connected then this would hold the tack from 2 tack agoa 
    if SevSeg[2]:
        SevSeg[2].clear()
        if tacks[1] < 0 :
            SevSeg[2].print_hex(0x00)
        else:
            SevSeg[2].print_float(tacks[2], decimal_digits=0, justify_right=True)
        SevSeg[2].write_display()

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
        SEVSEG[0].print_hex('8888')
        tacks = [90,180,270]
        heading = 135 
        time.sleep(.75)
        update_displays( SEVSEG, heading, tacks ) 
        tacks = [heading] + tacks[:-1]
        time.sleep(.75)
        update_displays( SEVSEG, tacks[2], tacks ) 
   else: 
        print "Primary LED display not detected"
        exit    
