 while (( 1 )) ; do cat ALL3.random | grep HC | sort | uniq  |( while read l ; do sleep 1; echo $l ; done )| nc 127.0.0.1 10111 ; done

