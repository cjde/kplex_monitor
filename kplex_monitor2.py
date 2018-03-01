#!/usr/bin/python
import os
import glob
import time
import re
import argparse
import sys
import RPi.GPIO as GPIO ## Import GPIO Library
from Adafruit_LED_Backpack import SevenSegment



import socket

#read one line from the socket one character atr a time
def buffered_readLine(socket):
    line = ""
    while True:
        part = socket.recv(1)
        if part != "\n":
            line+=part
        elif part == "\n":
            break
    return line

#  get the headdin out of a sentence if it is a heading 
# 
def get_heading( line ): 
    # Compas heading sentence 
    # $HCHDM,238,M<CR><LF> 
    #        = 238 degreees magnetic 
    p = re.compile( '\$HCHDM,(\d+),M' ) 

    m = p.search( line )

    # 1) compass reading 
    if m: 
       heading = m.group(1) 
    else: 
       heading = -1    
    return heading 

# set the time if we get a "RMC Recommended Minimum Navigation Information" 
# 
def getgpstime ( line ): 
    # this is the date /time sentence   
    #                                                         MMDDYY 
    # $GPRMC,031010.000,A,2805.8247,N,08227.8609,W,0.00,44.80,101017,,,D*7E
    # $GPRMC,171547.000,A,2805.8296,N,08227.8598,W,0.00,99.54,121117,,,D*45


    # and the pattern to get the date and time 
    p = re.compile('\$GPRMC,(\d\d\d\d)(\d\d).\d+,A,(\d+).(\d+),([NS]),(\d+).(\d+),([EW]),\d+.\d+,\d+.\d+.(\d\d\d\d)(\d\d)')

    m = p.search( line )

    #  1) Time: hhmm (UTC)
    #  2) Time: ss
    #  3) Latitude: degreesminutes or degreesfraction 
    #  4) Latitude:  fraction 
    #  5) N or S 
    #  6) Latitude:  degreesminutes or degreesfraction 
    #  7) Latitude:  fraction
    #  8) E or W
    #  9) Date: ddmm
    # 10) Date: yy 
    
    if m: 
       hhmm = m.group(1)
       ss = m.group(2)
       mmdd = m.group(9)
       yy  = m.group(10)

       # set the date wih a system call 
       # date [-u|--utc|--universal] [MMDDhhmm[[CC]YY][.ss]]

       datecmd = "/bin/date -u " + str(mmdd) + str(hhmm) + "20" + str(yy) + "." + str(ss)
       print datecmd

       os.system(datecmd)
       needtime = False 
    else:
       needtime = True

    return needtime 

def SevenSegSetup()
    ''' 
    this checks if the seven sebment desplay is on I2C bus address  70 
    and return true if it was able to set it up  
    '''

    import subprocess
    import os.path
    from pathlib import Path

    # if we find the command and we have a device with address on it ... 
    its_good = True

    i2c_cmd = Path("/usr/sbin/i2cdetect")
    if i2c_cmd.is_file():
        # file exists see if we have a device address 70 on it 
        p = subprocess.Popen(['i2cdetect', '-y','1'],stdout=subprocess.PIPE,)
        # should get back somethin like this :
        # 70: 70 -- -- -- -- -- -- --
        #cmdout = str(p.communicate())

        for i in range(0,9):
            line = str(p.stdout.readline())
            
            for match in re.finditer("70: 70", line):
                print (match.group()
                its_good = True
 
    if its_good:
       display = SevenSegment.SevenSegment()
       display.begin()

    return its_good
#        0  1  2  3  4  5  6  7  8  9  
tack = [-1,-1,-1,-1,-1,-1,-1,-1,-1,-1 ] 
def do_heading_calc( heading, tack ) 
'''````dd




# pins on the GPIO that are used
PINS = [32,36,38,40]

# This associates what pin and ultimatelys what LED is associated with each instrument
LEDS = {'gps': 32, 'compass': 36, 'speed': 38, 'unknown': 40}

# This is association between the start of each NMEA sentence and the instrument it is comming from
NMEA = {'$GP': 'gps', '$PG': 'gps', '$SD': 'gps', '$HC': 'compass', '$VW': 'speed'}

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BOARD) ## Use BOARD pin numbering

# set all the indicators to output

for pin  in PINS:
    print pin
    GPIO.setup(int(pin), GPIO.OUT)
    GPIO.output(int(pin), True)
    time.sleep(.75)
    GPIO.output(int(pin), False)
    time.sleep(.25)
    GPIO.output(int(pin), True)
    time.sleep(.75)
    GPIO.output(int(pin), False)
    time.sleep(.25)

# if the seven segment display is plugged in then we will use it 
SevSeg = SevenSegSetup()

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
host = "127.0.0.1"
port = 10110
s.connect((host,port))

# pick one of the instruments indicators to be off
pin = LEDS.get( "compass" )

# Get the time from the GPS only once 
needtime = True

try:
    print "1" 
    while True:
        # get the next sentence
        line = buffered_readLine(s)
        # turn off the last one
        GPIO.output(int(pin), False)

        # check if the first two characters are not trash
        if ( line[0] == '$') and ( line[1].isalpha()) and ( line[2].isalpha()):
           # print line
           # What is this sentense
           instr =  NMEA.get(line[0:3])
           if instr != None:
              pin = LEDS.get( instr )
              # print instr, pin, line
            
           else:
              instr = "unknown"
              pin = LEDS.get( "unknown" )
              print "unknown ",line

           # turn on the selected led
           GPIO.output(int(pin), True)
           
           # see if this is a time sentence and the set the date, only once 
           if ( needtime ): 
              needtime = getgpstime( line ) 

           # get a heading if this is a headiing sentence 
           heading =  get_heading( line ) 
           # returns the headign or -1 if not a heading 
           if heading >= 0: 
              # calculate the avg heading and the heading for the last two tacks 
              do_heading_calc( heading, tack ) 
              if SevSeg : 
                 display.clear()
                 display.print_float(tack, decimal_digits=0, justify_right=True)
                 display.set_colon(colon)
                 display.write_display()

        else:
           print "junk ", line

except KeyboardInterrupt:
    print "User terminated"

except:
    # this catches ALL other exceptions including errors.
    print "Other error or exception occurred!"

finally:
    GPIO.cleanup() # this ensures a clean exit

    s.close

