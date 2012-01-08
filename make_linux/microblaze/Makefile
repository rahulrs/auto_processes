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

ARCH=microblaze
PREFIX=mb-linux-
HACK=-j 4

ACE0=ml605_mb_v1


mmu:
	cd $(LINUX_DIR); make $(HACK) ARCH=$(ARCH) CROSS_COMPILE=$(PREFIX) xilinx_mmu_defconfig

config:
	cd $(LINUX_DIR); make $(HACK) ARCH=$(ARCH) CROSS_COMPILE=$(PREFIX) menuconfig

linux:
	cd $(LINUX_DIR); make $(HACK) ARCH=$(ARCH) CROSS_COMPILE=$(PREFIX) simpleImage.$(ACE0)

init_bram:
	cd $(HW); make -f system.make init_bram



