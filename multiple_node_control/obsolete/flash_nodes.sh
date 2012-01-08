#!/bin/sh

source nodes.sh

for node in $NODES; do
  echo === Powering up $node ===
  fsc restart $node
done

echo === Sleeping 60 secs ===
sleep 60

for node in $NODES; do
  fsc upload $node 3 <ace> "Rahul's test"
done

echo === Wait 60 secs for sync ===
sleep 60

for node in $NODES; do
  fsc select $node 3
  fsc boot $node
done

sleep 30

echo === Done !! ===