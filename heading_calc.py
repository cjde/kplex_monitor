#!/usr/bin/python
import os
import glob
import time
import re
from math import cos, sin, atan2, pi, radians, degrees
import sys

# heading -> headings[] -avg-> track -> tracks[]
# Couple definitions
#
# Heading:
# This is where my nose points relative to North.
#
# Course:
# This is my INTENDED path of travel that I have calculated taking into consideration winds, 
# variation and declination.
#
# Track:
# This is my ACTUAL path traveled over ground - just like a set of tracks I would leave behind in the snow or sand, 
# relative to North
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
headings = []
headings_in_track = 60 

# tracks are the set of track that have occurred over the route. A new entry is added when ever the average course 
# changes by the tack angle
# or if the rate of  heading change is greater than something ?
#  [t1,t2,t3,...tn]
tracks = []
tracks_in_route = 60

# tacks  contain the last 10 track changes, these are ( potentially ) displayed
tacks = []
tacks_in_race = 10

class HEADING:
    # track is the compass angle averaged over the last N headings
    # track = 0

    def clear_headings(self):
        """
        This clears the list of headings that are collected and averaged to generate the track.
        When a tack occurs this is cleared so that the new average reflecte the new heading
        """
        global headings
        del headings[:]

       
    def __init__(self, c):
        """
        This is the constructor for the heading it takes the compass reading and computes the sin and cos
        :param c: degrees in the compass domain
        :return:
        """

        self.compass = c
        self.angle = (450 - c) % 360
        self.radians = radians(self.angle)
        self.cos = cos(self.radians)
        self.sin = sin(self.radians)

    def add_heading(self, h1):
        """
        This adds two headings together without using the vector components
        For example if the course is 90 degreens ( east) and you  your tack angle is 35 degrees
        then this should output 125 degrees. Of course if your heading is 350 then the resultant
        should be 350+35-360=25
        """
        c = self.compass + h1.compass
        if c > 360:
            c = c - 360
        return c

    def sub_heading(self, h1):
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

    def get_track(self):
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

        avg_rad = atan2(avg_sin, avg_cos)
        angle = degrees(avg_rad)
        # untwist the geometric angle back into a compass angle
        compass = (450 - angle) % 360
        return compass

    def tack_check(self, track, tackangle):
        """
        Computes the minimum and maximum headings on the current track given the tackangle.
        Checks if the current heading is between these two headings and if not then that
        indicates that we have tacked
        :param track:       Compass course of current track
        :param tackangle:   Angle the boat must traverse to go from one beat to another. Basicly 2x the angle
                            we can sail off the wind ( for a J27 thats 60 degrees)
        :return: true if a tack is detected, false otherwize
        """

        # to avoid any complications by going to a negitave angle just add 360 to everything
        h360 = self.compass + 360
        t360 = track + 360

        # minimum and maximum heading off the track,
        # so long as the heading is between these two angele we have not tacked
        lower = t360 - tackangle/2
        upper = t360 + tackangle/2

        # print "check if heading",h360," is between ",lower," and ", upper

        if h360 > lower and h360 < upper :
            # still in between the tabs on the wind vane!
            just_tacked = False
        else:
            # when the tack  occurs the track is reset so the average converges faster to the new heading
            just_tacked = True
            self.clear_headings()

        return just_tacked

    def add_to_headings(self):
        """
        Add the heading to the list of headings so that we can compute the average track,
        and remove the last one from the list if we have added
        the maximum to the list

        :param h: heading to add to the track
        return:

        """
        global headings
        global headings_in_track

        headings.insert(0, self)
        if len(headings) >= headings_in_track + 1:
            del (headings[headings_in_track])

    def add_track_to_tacks(self, track ):
        """
        Add the track (which is the previous tack) to the list of tacks
        Remove the last one from the list if we have added the maximum to the list

        :param track: average over the last collection interval ( in degrees)
        return:
        """
        global tacks
        global tacks_in_race

        tacks.insert(0, track)
        if len(tacks) >= tacks_in_race + 1:
            del (tacks[tacks_in_race])



#
# ----------- test function -----------
#

if __name__ == "__main__":

    # test 1 - result should be 1/2 of headings_in_track 
    degree = HEADING( 1 ) 
    degree.clear_headings()
    c = 1
    for i in range( 1,headings_in_track ):
        h = HEADING( c )
        h.add_to_headings( )
        c = h.add_heading( degree )
  
    track = h.get_track()
    print (  " this should be twice size",  c,  track )

    # test 2- result should be zero 
    degree = HEADING( 1 ) 
    degree.clear_headings()
    c =   360 - (headings_in_track/2 -1 )  
    for i in range( 1,headings_in_track ):
        h = HEADING( c )
        h.add_to_headings( )
        c = h.add_heading( degree )
  
    track = h.get_track()
    print ( "should be 1/2 of ", headings_in_track," and zero", c,  track )


    # test 3- result should be Zero using negitave compass value 
    degree = HEADING( 1 ) 
    degree.clear_headings()
    c =  - (headings_in_track/2 - 1)  
    for i in range( 1,headings_in_track ):
        h = HEADING( c )
        h.add_to_headings( )
        c = h.add_heading( degree )
  
    track = h.get_track()
    print ( "should be 1/2 of ", headings_in_track," and zero", c,  track )



    # test 3- result should be 180 
    degree = HEADING( 1 ) 
    degree.clear_headings()
    c =  180 - (headings_in_track/2 - 1)  
    for i in range( 1,headings_in_track ):
        h = HEADING( c )
        h.add_to_headings( )
        c = h.add_heading( degree )
  
    track = h.get_track()
    print ( "should be ", headings_in_track/2, " + 180 and 180", c,  track )


