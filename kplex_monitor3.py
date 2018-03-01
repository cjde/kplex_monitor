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
from socket import error as socket_error
import RPi.GPIO as GPIO ## Import GPIO Library



# cource change amount that indicates a tack has occured
TACKANGLE = 40

# this is the number of heading samples that constitute a average course
num_of_heading_in_course_average = 30
course = [-1 for i in range(num_of_heading_in_course_average)]

def buffered_readLine(socket):
    '''
    This function reads the output of the kplex server one character at a time. Perhaps it should have a non blocking
    socket call but the data is coming in 2-3 messages per second and there is really nothing to do while waiting
    for more data. So as long as the display can be updated ant the compas calcs be completed its ok. Alternatively
    kplex could be configured to only forward the sentecnces taht we need adn there could be another process attached
    to kplex that processes other sentences

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
    get the compass heading out of a sentence if it is a heading

    Compas heading sentence
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
    set the time if we get a "RMC Recommended Minimum Navigation Information"

    this is the date /time sentence
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
    Error code    Description
         1        Primary LED backpack at address 70 is not detected, others if detected will have thier addresses on them
         2
         3
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


def course_and_angle ( course, tackangle ):
    '''
    This returns the normalize course after adding the tack angle
    If the sum is > 360 returns 360 - sum
    if  sum is < 0 returns 360 + sum

    :param course: current average course
    :param tackangle: change in course angle that indicates a tack has ocured
    :return: normalized course degree ( 0 ... 360 )
    '''

    if course + tackangle > 360 :
        return  360 - ( course + tackangle)
    elif course + tackangle < 0 :
        return  360 + ( course + tackangle)



def do_heading_calc( heading, tacks ):
    '''
    This function keeps track of the current average course and the previous N course changes.
    The course consists of the average of the past M compass readings ( 30 sec ?)
        If it takes more that that long to tack then this average will be polluted by the heading as
        it goes thru the tack

    A course change is when the heading differs by TACKANGLE degrees greater or less than the average course
    Once a tack has occurred we must collect several readings before we can determine the average course again

    Tack [1] and tack[2] are the average course just before the previous two tacks, it is planned to have
    them displayed under the heading reading

    *Note* with the heading and the average course, we can determine if we are lifted or headed


    :param heading: latest reading from the compass
    :param tack: list of the last 10 tacks
    :return: true if a tack has just occured
    '''
    global course


    tacked = False
    # wait until we have all the complete sample of headings
    if course[-1] == -1:

        # if the current heading is +/- the tack angle degree
        # from the average over the past minute then we have tacked !
        avg_course = sum(course) / float(len(course))
        if ( heading > course_and_angle( avg_course, TACKANGLE )) :
           tacked = True
        elif ( heading < course_and_angle( avg_course, -TACKANGLE )):
            tacked = True

        if tacked:
            # drop off the last tack and shift them all down
            # set the last tack to be the average course, just before that tack occurred
            # This average course is likely to have a couple readings of the wind header
            # that was occurring so the average course will be slightly lower with these:w
            # values computed into the course
            tacks = [avg_course] + tacks[:-1]

            # remove all the headings  from the course list
            # Once we have a complete set we can we can compute a reasonable average course
            course =  [-1 for i in range(len(course))]
            course[0] = heading
        else:
            # we have not tacked and we been on this course for several readings
            tacks[0] = avg_course
    else:
        # just collect headings until we can form an average course
        # drop off the last heading and add this heading to the list
        course = [heading] + course[:-1]
    return tacked

#----- MAIN -----
def main(argv):


    # theoretically there could be three displays connected, current heading, last tack and
    # the tack heading from befor that. Of course the second display could show lift or heading
    # value to but that is not what it is doing rignt now
    SEVSEG = [0, 0, 0]

    # This will hold the last N number of tacks
    num_of_tacks = 10
    tacks = [-1 for i in range(num_of_tacks)]

    # pins on the GPIO that are used
    PINS = [32,36,38,40]

    # Error codes
    NO_PRIMARY_DISPLAY = 1

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

    # if the seven segment display is plugged in then we will use it
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
               print line
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
                  # do_heading_calc( heading, tacks )
                  update_displays(SEVSEG, heading, tacks)
                  tacks[1] = heading


            else:
               print "junk ", line

    except KeyboardInterrupt:
        print "User terminated"

#    except:
#       # this catches ALL other exceptions including errors.
#       print "Other error or exception occurred!"

    finally:
        GPIO.cleanup() # this ensures a clean exit
        s.close


if __name__ == "__main__":
    main(sys.argv[1:])




