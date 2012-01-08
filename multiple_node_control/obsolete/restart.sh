#!/bin/sh

source nodes.sh

for node in $NODES; do
    fsc restart $node
done