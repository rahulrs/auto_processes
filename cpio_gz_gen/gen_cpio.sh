#!/bin/sh

find . \( ! -name gen_cpio.sh \) -print0 | cpio --null -ov --format=newc | gzip -9 > ../initramfs.cpio.gz
