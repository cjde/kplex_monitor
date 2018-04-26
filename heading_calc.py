#!/usr/bin/python
import os
import glob
import time
import re
from math import cos, sin, atan2, pi, radians, degrees
import sys

# heading -> headings[] -avg-> track -> tracks[]
tracks = []
headings = []
headings_in_track = 50
tracks_in_route = 50

class HEADING:
    # Couple definitions
    #
    # Heading:
    # This is where my nose points relative to North.
    #
    # Course:
    # This is my INTENDED path of travel that I have calculated taking into consideration winds, variation and declination.
    #
    # Track:
    # This is my ACTUAL path traveled over ground - just like a set of tracks I would leave behind in the snow or sand, relative to North
    #
    # Bearing:
    # This is the angle between the location of an object, machine or destination and either:
    #
    # In this case A heading is collected every M seconds when ever a the compass emits one.
    # A heading consists of the compass angle and the angle transformed into a geometric angle, radians of that angle
    # the sin and cos of that angle. These are saved so that we dont need to calculate them again
    #
    #    {"compass": 270, "angle": 180, "radians": 3.141592654 "cos": -1.000000000, "sin": 0.00000 },
    #    {"compass": 270, "angle": 180, "radians": 3.141592654 "cos": -1.000000000, "sin": 0.00000 },
    #    {"compass": 271, "angle": 179, "radians": 3.124139361 "cos": -0.999847695, "sin": 0.01745 },
    #    {"compass": 272, "angle": 178, "radians": 3.106686069 "cos": -0.999390827, "sin": 0.03490 },
    #    {"compass": 269, "angle": 181, "radians": 3.159045946 "cos": -0.999847695, "sin": -0.01745 },
    #    {"compass": 268, "angle": 182, "radians": 3.176499239 "cos": -0.999390827, "sin": -0.03490 }

    #
    # headings are a ordered list of several headings up to a maximum number,
    # Headings are added to the front and removed from  the back and removed at the end
    #  [h1,h2,h3,h4,...hn ]
    ### headings = []

    # track is the compass angle averaged over the last N headings
    track  = 0

    # tracks are the set of track that have occurred over the route. A new entry is added when ever the average course changes by the tack angle
    # or if the rate of  heading change is greater than something ?
    #  [t1,t2,t3,...tn]
    ### tracks = []

    def __init__( self, c ):
        """
        This is the constructor for the heading it takes the compass reading and computes the sin and cos
        :param c: degrees in the compass domain
        :return:
        """

        self.compass = c
        self.angle = (450-c) % 360
        self.radians = radians( self.angle )
        self.cos = cos( self.radians )
        self.sin = sin( self.radians )

    def add_heading(self, h1 ):
        """
        This adds two headings together without using the vector components
        For example if the course is 90 degreens ( east) and you  your tack angle is 35 degrees
        then this should output 125 degrees. Of course if your heading is 350 then the resultant
        should be 350+35-360=25
        """
        c = self.compass + h2.compass
        if c > 360:
            c = c - 360
        return c

    def sub_heading(self, h1 ):
        """
        This subtracts two headings together without using the vector components
        For example if the course is 90 degrees ( east ) and you  your tack angle is 35 degrees
        then this should output 55 degrees.  of course if your heading is 25 then tne resultant
        should be 25-35=-10 or 350
        """
        c = self.compass - h1.compass
        if c < 360:
            c = c + 360
        return c

    def get_track( self ):
        """
        This computes the average track by using the headings cos and sin values.
        they are summed and then used in atan2 to come up with the compass angle of the
        resulting track

        :return: avg compass heading
        """
        
        global headings

        avg_cos = 0.0
        avg_sin = 0.0

        for h in headings:
            avg_cos += h.cos
            avg_sin += h.sin

        avg_rad = atan2( avg_sin, avg_cos)
        angle = degrees( avg_rad )
        # untwist the geometric angle back into a compass angle
        compass = (450-angle) %  360
        return compass

    def add_to_headings( self ):
        """
        Add the heading to the list of headings so that we can compute the average track, and remove the last one from the list if we have added
        the maximum to the list

        :param h: heading to add to the track
        return:

        """
        global headings
        global headings_in_track
        
        headings.insert( 0, self )
        if len(headings) >= headings_in_track:
           del ( headings[ headings_in_track] )

#### 
"""

    def do_heading_calc( self, heading, course, tacks ):
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
        :param course: list of the past several minutes of headings
        :param tack: list of the last 10 tacks
        :return: true if a tack has just occured
        '''


        tacked = False
        # wait until we have all the complete sample of headings ( the list is fully initialized)
        if course[-1] == -1:

            # if the current heading is +/- the tack angle degree
            # from the average over the past minute then we have tacked !
            # interesting thing about the average course is what if the headingh is close to north
            # then the hwading will be 350- to 10 degrees so we goa take that into acccount

            avg_course = sum(course) / float(len(course))
            if ( heading > course_and_angle( avg_course, TACKANGLE )) :
               tacked = True
            elif ( heading < course_and_angle( avg_course, -TACKANGLE )):
                tacked = True

            if tacked:
                # drop off the last tack and shift them all down
                # set the last tack to be the average course, just before that tack occurred
                # This average course is likely to have a couple readings of the wind header
                # that was occurring so the average course will be slightly lower with these
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
"""
#
# ----------- test function -----------
#

if __name__ == "__main__":
    T = [270,270,271,271,269,269,272,272,268,268]
    for heading in T:
        h = HEADING(heading)
        h.add_to_headings()
        track = h.get_track()
        print(heading, track)
