#!/bin/sh

source nodes.sh

for node in $NODES; do
    echo === Removing module from $node ===
    /usr/bin/rsh -l root $node "/sbin/rmmod /home/rsharm14/pp/airen-driver.ko"
done