#!/bin/bash
cd /usr/sbin/kplex_monitor.d
#cat /var/tmp/kplex.log.sav | grep HC  |( while read l ; do sleep 1; m="$1"; echo $m;  done )| nc 127.0.0.1 10111
R=""
#cat /var/tmp/kplex.log.sav | grep HC  | sed "s/$/$R/" > /tmp/goo 
cat /var/tmp/mixed  | sed "s/$/$R/"|( while read l ; do sleep 0.05 ; echo $l;  done )| nc 127.0.0.1 10111 



