#!/bin/sh

source nodes.sh

for node in $NODES; do
    echo === Insert driver module to $node ===
    /usr/bin/rsh -l root $node "/sbin/insmod /home/rsharm14/pp/airen-driver.ko"
done