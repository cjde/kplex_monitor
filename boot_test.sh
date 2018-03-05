#!/bin/bash
cd /usr/sbin/kplex_moniror.d
cat boot_test.txt |( while read l ; do sleep 1; echo $l ; done )| nc 127.0.0.1 10111

