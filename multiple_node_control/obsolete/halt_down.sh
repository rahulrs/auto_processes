#!/bin/sh

source nodes.sh

for node in $NODES; do
    echo === Halting $node ===
    /usr/bin/rsh -l root $node /sbin/halt
done

sleep 5

for node in $NODES; do
    fsc down $node
done
