# Automated Linux compile generator... Start it and go for some soccer ;-)
# Author: Rahul 
##########################################################################
#
# SPEND SOME TIME AND CHECK THE PROJECT SETTINGS
#
# Uses the XPS project and Linux compilation to create the ace file
# Create this tree
# |--linux-2.6-xlnx	 => Copy from ~/storage/linux_26
# |--xps_project	 => Create the linux worthy xps project and synthesize download.bit
# |--mkrootfs		 => Script will create a fresh ramdisk
# `--ace		 => Leave it empty
#
# Use the above names or prepare to cry
# Run in SCREEN window... keeps processes indestructible
#

# XPS project path - enter here or modify
PROJECT = $(shell pwd)

# XPS project name
XPS =  $(PROJECT)/xps_project
XPS_LIB = ppc405_0/libsrc/linux_2_6_*/linux/arch/ppc/platforms/4xx/xparameters

# Linux paths here
LINUX = $(PROJECT)/linux-2.6-xlnx
LINUX_XPAR = arch/ppc/platforms/4xx/xparameters
IMAGE = arch/ppc/boot/images

# Board settings here - change ace file name if needed
ACE = hw_linux.ace
BOARD = ml410
ARCH = ppc
TRIPLET = powerpc-405-linux-gnu-

# Make sure you have a download.bit ready in xps_project
all:
	make ramdisk
	cd $(XPS); make -f system.make libs
	cp $(XPS)/$(XPS_LIB)/xparameters_ml40x.h $(LINUX)/$(LINUX_XPAR)/xparameters_ml403.h
	cp $(XPS)/$(XPS_LIB)/xparameters_ml40x.h $(LINUX)/$(LINUX_XPAR)/xparameters_ml41x.h
	cp $(PROJECT)/mkrootfs/ramdisk.image.gz $(LINUX)/$(IMAGE)/.	
	cd $(LINUX); make ARCH=$(ARCH) CROSS_COMPILE=$(TRIPLET) ml403_defconfig
	cp ~/Dropbox/auto_processes/make_linux/linux_config_nfs $(LINUX)/.config
	cd $(LINUX); make ARCH=$(ARCH) CROSS_COMPILE=$(TRIPLET)
	cd $(LINUX); make ARCH=$(ARCH) CROSS_COMPILE=$(TRIPLET) zImage
	rm -rf $(PROJECT)/ace/*
	cp $(XPS)/implementation/download.bit $(PROJECT)/ace
	cp $(LINUX)/$(IMAGE)/zImage.elf $(PROJECT)/ace
	cd $(PROJECT)/ace; xmd -tcl $(XILINX_EDK)/data/xmd/genace.tcl -jprog -hw download.bit -elf zImage.elf -ace $(ACE) -board $(BOARD)
	chmod 777 ace/$(ACE)
	md5sum $(PROJECT)/ace/$(ACE)
	cp $(PROJECT)/ace/$(ACE) ~/compilation.ace
	@echo "************* Done !! ***************"
	cd $(PROJECT)

ramdisk:
	rm -rf mkrootfs/*
	cp -r /home/rsharm14/storage/mkrootfs_tools/* ./mkrootfs
	cd mkrootfs; tar xjvf *.bz2; tar xzvf *.gz; rm *.tar.*; . mkfhs.sh; cd busybox*;cp ../busybox_config .config; \
		make ARCH=$(ARCH) CROSS_COMPILE=$(TRIPLET) defconfig; \
	 	make ARCH=$(ARCH) CROSS_COMPILE=$(TRIPLET);  make ARCH=$(ARCH) CROSS_COMPILE=$(TRIPLET) install; cd ..; \
		cp My.makefile ./inetutils*; cd inetutils*; make -f My.makefile; cd ..; sh mkext2.sh

clean:
	cd $(LINUX); make ARCH=$(ARCH) CROSS_COMPILE=$(TRIPLET) clean
#	cd $(XPS); make -f system.make clean
	rm -rf mkrootfs/*
	rm -rf ace/*
