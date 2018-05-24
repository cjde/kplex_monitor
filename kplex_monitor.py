#!/usr/bin/python
import os
import glob
import time
import re
import argparse
import sys
import RPi.GPIO as GPIO ## Import GPIO Library
from SevenSeg import SevenSegSetup,update_displays
# from Adafruit_LED_Backpack import SevenSegment
import socket
import errno
from heading_calc import HEADING
from socket import error as socket_error
import RPi.GPIO as GPIO ## Import GPIO Library



## cource change amount that indicates a tack has occured
#TACKANGLE = 40
#
## this is the number of heading samples that constitute a average course
#num_of_heading_in_course_average = 30
#course = [-1 for i in range(num_of_heading_in_course_average)]

def buffered_readLine(socket):
    '''
    This function reads the output of the kplex server one character at a time. Perhaps it should have a non blocking
    socket call but the data is coming in 2-3 messages per second and there is really nothing to do while waiting
    for more data. So as long as the display can be updated ant the compass calculation can be completed in time 
    its ok. Alternatively kplex could be configured to only forward the sentecnces taht we need adn there could 
    be another process attached to kplex that processes other sentences

    :param socket: Open socket attached to the kplex server
    :return: The entire NMEA sentence
    '''
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


def get_heading( line ):
    '''
    Get the compass heading out of a sentence if it is a heading

    Compas heading sentence looks like this 
    $HCHDM,238,M<CR><LF>
           = 238 degreees magnetic
    '''
    p = re.compile( '\$HCHDM,(\d+)[,.]' )

    m = p.search( line )

    # 1) compass reading
    if m:
       heading = m.group(1)
    else:
       heading = -1
    return int( heading ) 


def getgpstime ( line ):
    '''
    Set the time if we get a "RMC Recommended Minimum Navigation Information"
    it returns False whin it has set the time and no longer needs the time from the GPS 

    This is the date /time sentence
                                                            MMDDYY
    $GPRMC,031010.000,A,2805.8247,N,08227.8609,W,0.00,44.80,101017,,,D*7E
    $GPRMC,171547.000,A,2805.8296,N,08227.8598,W,0.00,99.54,121117,,,D*45
    '''

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


def set_error_status( stat, pins):
    '''
    Puts an error code to the LEDs number of lit LED s indicate the error code
    Currently only four status codes are output 
    Error code    Description
         1        Primary LED backpack at address 70 is not detected, others if detected will have thier addresses on them
         2        KPLES is sick 
         3        Primary display is disconnected 
         4
    :param stat: error code ( number of LEDS to turn on )
    :param pins: list of pins that have LEDs attached
    :return
    '''
    if stat >= 1:
        GPIO.output(pins[0], True)
    if stat >= 2:
        GPIO.output(pins[1], True)
    if stat >= 3:
        GPIO.output(pins[2], True)
    if stat >= 4:
        GPIO.output(pins[3], True)


#----- MAIN -----
def main(argv):
    '''
    Theoretically there could be three displays connected, current heading,  average track and
    how far off the average track the current headin is. Of course the second display could show lift or heading
    value to but that is not what it is doing right now
    ''' 

    SEVSEG = [0, 0, 0]

    # pins on the GPIO that are used
    PINS = [32,36,38,40]

    # Error codes
    NO_PRIMARY_DISPLAY = 1
    NO_KPLEXSERVER = 2
    PRIMARY_DISPLAY_OFFLINE = 3

    # This associates what pin and ultimatelys what LED is associated with each instrument
    LEDS = {'gps': 32, 'compass': 36, 'speed': 38, 'unknown': 40}

    # This is association between the start of each NMEA sentence and the instrument it is comming from
    NMEA = {'$GP': 'gps', '$PG': 'gps', '$SD': 'gps', '$HC': 'compass', '$VW': 'speed'}

    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BOARD) ## Use BOARD pin numbering

    # turn it all off 
    for pin  in PINS:
        GPIO.setup(int(pin), GPIO.OUT)
        GPIO.output(int(pin), False)

    # set all the indicators to output
    for pin  in PINS:
        print pin
        GPIO.output(int(pin), True)
        time.sleep(.50)
        GPIO.output(int(pin), False)
        time.sleep(.10)
        GPIO.output(int(pin), True)
        time.sleep(.50)
        GPIO.output(int(pin), False)
        time.sleep(.10)

    # if the primary seven segment display is plugged in then we will use it
    # otherwize output the error code ands exit
    if  SevenSegSetup(SEVSEG) != 1:
        print "Primary LED display not detected"
        set_error_status( NO_PRIMARY_DISPLAY, PINS )
        exit

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    host = "127.0.0.1"
    port = 10110
    try:
        s.connect((host, port))
    except socket_error as serr:
        if serr.errno == errno.ECONNREFUSED:
            print "Kplex sever not running "
            set_error_status( NO_KPLEXSERVER, PINS )
        raise serr

    # pick one of the instruments indicators to be off
    pin = LEDS.get( "compass" )

    # Get the time from the GPS only once
    needtime = True
    
    try:
        while True:
            # turn off the last one
            GPIO.output(int(pin), False)
            # get the next sentence
            line = buffered_readLine(s)

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
                    h = HEADING( heading )
                    h.add_to_headings()

                    # calculate the avg heading 
                    track = h.get_track()
                    if not ( update_displays(SEVSEG, heading, track) ):
                       print "Lost connection to display" 
                       set_error_status( PRIMARY_DISPLAY_OFFLINE, PINS )
                       exit 
            else:
                print "junk ", line

    except KeyboardInterrupt:
        print "User terminated"


if __name__ == "__main__":
    main(sys.argv[1:])



