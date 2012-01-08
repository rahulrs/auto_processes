#!/bin/sh

##########################################################################
#### . loader.sh <Node> <Slot>                                        ####
#### Enter parameters in this format                  		      ####
#### You are expected to request the board in before using the script ####
##########################################################################

echo "==== Displaying loading parameters ===="
echo Node No. : $1
echo Slot No. : $2
echo File     : $3
echo "FSC session will begin in 2 seconds"
sleep 2

echo "==== Restarting the board ===="
fsc down $1
sleep 3
fsc up $1
md5sum $3

echo "==== Waiting for boot up ===="
sleep 60
fsc upload $1 $2 $3 "$(date)"

echo "==== Waiting for sync ===="
sleep 20
echo fsc select $1 $2
fsc select $1 $2

echo "==== Boot up will begin now ===="
sleep 5
echo fsc boot $1
fsc boot $1

echo "==== Script ended... The board is all yours !! ===="


