import os
import glob
import time
import re
import json
import argparse
import sys
import RPi.GPIO as GPIO ## Import GPIO Library

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


# pins on the GPIO that are used 
PINS = [32,36,38,40]

# This associates what pin and ultimatelys what LED is associated with each instrument
LEDS = {'gps': 32, 'compass': 36, 'speed': 38, 'unknown': 40}

# This is association between the start of each NMEA sentence and the instrument it is comming from
NMEA = {'$GP': 'gps', '$PG': 'gps', '$SD': 'gps', '$HC': 'compass', '$VW': 'speed'}

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
 

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
host = "127.0.0.1"
port = 10110
s.connect((host,port))


# pick one of the instruments indicators to be off
pin = LEDS.get( "compass" )

try:
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
              # print instr
              # print pin, line
              # turn on the new one
              GPIO.output(int(pin), True)
           else:
              pin = LEDS.get( "unknown" )
              GPIO.output(int(pin), True)
              print "unknown ",line
#        else:
#            print "junk ", line

except KeyboardInterrupt:  
    print "User terminated"  
  
except:  
    # this catches ALL other exceptions including errors.  
    print "Other error or exception occurred!"  
  
finally:  
    GPIO.cleanup() # this ensures a clean exit  
    s.close 

