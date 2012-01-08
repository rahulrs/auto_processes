#!/bin/sh

# Script to fix coregen NGC version mismatch
# Does a batch compile of all *.xco to current version

for xco_file in *.xco
do
  coregen -b $xco_file
done
