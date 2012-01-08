#!/bin/sh
# source this file for a cross-compiler built for Linux 2.4 kernel
# may work for 2.6...
#PATH=${PATH}:/opt/crosstool/gcc-3.4.5-glibc-2.3.6/powerpc-405-linux-gnu/bin/

# AGS: Changed to use the RIGHT gcc cross compiler
PATH=${PATH}:/opt/crosstool/gcc-4.2.1-glibc-2.3.6/powerpc-405-linux-gnu/bin/:/opt/crosstool/openmpi-1.2.6/powerpc-405-linux-gnu/bin
