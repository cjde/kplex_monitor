#!/usr/bin/python
import os
import glob
import time
import re
import argparse
import sys
import errno
from socket import error as socket_error
import RPi.GPIO as GPIO ## Import GPIO Library

import socket

#read one line from the socket one character atr a time
def buffered_readLine(socket):
    line = ""
    while True:
        try:
            part = socket.recv(1)
        except socket_error as serr: 
             #if serr.errno == errno.ECONNREFUSED:
             print "servershutdown" 

        if part != "\n":
            line+=part
        elif part == "":
            raise RuntimeError("kplex server has shutdown.. exiting monitor  ")
        elif part == "\n":
            break

    return line

# set the time if we get a "RMC Recommended Minimum Navigation Information" 
# 
def get_heading( line ):
    '''
    get the compass heading out of a sentence if it is a heading

    Compas heading sentence
    $HCHDM,130.0,M*2B
    $HCHDM,130,M*2B
           = 130 degreees magnetic
    '''
    p = re.compile( '\$HCHDM,(\d+)[.,]' )

    m = p.search( line )
    
    # 1) compass reading
    if m:
       heading = m.group(1)
    else:
       heading = -1
    return heading


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
    time.sleep(.50)
    GPIO.output(int(pin), False)
    time.sleep(.10)
    GPIO.output(int(pin), True)
    time.sleep(.50)
    GPIO.output(int(pin), False)
    time.sleep(.10)


s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
host = "127.0.0.1"
port = 10110
try:
    s.connect((host,port))
except socket_error as serr: 
    if serr.errno == errno.ECONNREFUSED:
       print "Kplex sever not running " 
    raise serr    

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
           # returns the heading or -1 if not a heading
           if heading >= 0:
               print "heading: ", heading 

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

