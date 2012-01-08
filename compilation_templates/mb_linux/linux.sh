#!/bin/sh

export ARCH=microblaze
export CROSS_COMPILE=microblazeel-unknown-linux-gnu-

make -j 8 simpleImage.ml605_mb_trace

