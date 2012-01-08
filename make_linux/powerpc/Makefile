# General purpose cross-compiling Makefile for linux & base system
#
# Drop this file in the level you find this:
# project
# |-- hw/
# `-- linux-2.6-xlnx/
#

PROJECT=$(PWD)
HW=$(PROJECT)/hw/
LINUX_DIR=$(PROJECT)/linux-2.6-xlnx/

ARCH=powerpc
PREFIX=powerpc-405-linux-gnu-
HACK=-j 4
DEF=40x/virtex4_defconfig

ACE0=virtex405-ml405-basic


def:
	cd $(LINUX_DIR); make $(HACK) ARCH=$(ARCH) CROSS_COMPILE=$(PREFIX) $(DEF)

config:
	cd $(LINUX_DIR); make $(HACK) ARCH=$(ARCH) CROSS_COMPILE=$(PREFIX) menuconfig

linux:
	cd $(LINUX_DIR); make $(HACK) ARCH=$(ARCH) CROSS_COMPILE=$(PREFIX) simpleImage.$(ACE0)





