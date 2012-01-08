#!/bin/sh

source nodes.sh

for node in $NODES; do
  echo === Releasing $node ===
  fsc release $node
done
