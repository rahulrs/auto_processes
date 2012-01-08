#!/bin/sh

# Request nodes before use #

source nodes.sh

for node in $NODES; do
    echo === Powering up $node ===
    fsc restart $node
done

echo === Sleep 60 secs for boot controller ===
sleep 60

echo === Select Slot $1 and boot ===
for node in $NODES; do
    echo === Node $node ===
    fsc select $node $1
    fsc boot $node
done

echo === Sleep 60 secs for boot up ===
sleep 60

echo === Done !! ===