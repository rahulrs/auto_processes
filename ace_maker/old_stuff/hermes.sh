#!/bin/sh

rm -rf ace
mkdir ace
make init_bram
cp implementation/download.bit ./ace
cp app/executable.elf ./ace
cd ace
xmd -tcl $XILINX_EDK/data/xmd/genace.tcl -jprog -hw download.bit -ace sw_hw_ace.ace -board ml410
chmod 777 *.ace
md5sum *.ace
cd ..
echo "***** Done !! *****"