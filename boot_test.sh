#!/bin/bash
#
# this test script reads from a file the nmea sentence es and stuffs them into the kplex socket
# 


usage() { 
    echo "Usage: $0 "
    echo "   [-w  <wait this long before sending data >]"
    echo "   [-f <input file of nema seneences>]"
    echo "   [-i < time interval between sending sentencses> ]" 
    echo "   [-m < append a ^M to the NMEA sentence( usefull when readingthe logged data )> ]" 
    exit 1
}


# Default wait time to start sending data 
wait=10

# Default file name 
file=boot_test.txt

# Interval default 1 sec 
interval=1

# by default dont add a ^M to the imput line 
addcr=""

while getopts ":w:f:i:m" o; do
    case "${o}" in
        w)
            wait=${OPTARG}
            ;;
        f)
            file=${OPTARG}
            ;;
        i)
            interval=${OPTARG}
            ;;
        m)
            addcr=""
            ;;
        *)
            usage
            ;;
    esac
done
shift $((OPTIND-1))

sleep $wait 
#cd /usr/sbin/kplex_monitor.d
cd /home/pi/kplex_monitor
cat $file |( while read l ; do sleep $interval; echo "${l}${addcr}" ; done )| nc 127.0.0.1 10111

