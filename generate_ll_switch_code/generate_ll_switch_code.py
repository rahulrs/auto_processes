########################################################################
# Local Link compliant Switch code generator [ALPHA state]             #
# Author: Rahul                                                        #
#                                                                      #
# DATE : 30th June 2010                                                #
#                                                                      #
# DESCRIPTION:                                                         #
# The locallink compliant switch is code heavy and very wordy. Using   #
# 'generate' is not an option since there are layers of logic that do  #
# not recognise the 'generate' statements (MHS, MPD, etc). The aim of  #
# this script is to generate addenda VHDL code for the IPIC and        #
# user_logic VHDL, and MPD and MHS files. It must reduce the tedium of #
# copy-pasting and renaming VHDL signals (which is painful and gets    #
# punished with cryptic error messages).                               #
#                                                                      #
# USAGE: python generate_ll_switch_code.py <no_of_ports>               #
#                                                                      #
# OUTPUT: Produces the repetitive switch code for IPIC-VHDL and MPD    #
########################################################################

import re, os, commands, sys

# user_logic_vhd_addenda.txt - user_logic code
def user_logic_vhd():
    ul_handle = open("user_logic_vhd_addenda.txt","w")
    
    ul_handle.close()


### Function to generate IPIC code
def ipic_vhd():
    # ipic_vhd_addenda.txt - IPIC code
    ipic_handle = open("ipic_vhd_addenda.txt","w")

    # Entity 
    ipic_handle.write("-- Add the following lines before the PLB signal declarations inside entity\n\n")
    temp_string = open("template_ipic_entity.dat","r").read()
    for iter in range(0,num_ports):
        ipic_handle.write(temp_string.replace("$NUM", str(iter)))

    # Arch
    ipic_handle.write("\n\n------------------------------------------------------------------------\n\n")
    ipic_handle.write("-- Add the following code in the architecture block\n\n")
    temp_string = open("template_ipic_arch.dat","r").read()
    for iter in range(0,num_ports):
        ipic_handle.write(temp_string.replace("$NUM", str(iter)))
    ipic_handle.close()


### Function to generate code for MPD file 
def mpd():
    # mpd_addenda.txt
    mpd_handle = open("mpd_addenda.txt", "w")

    # Bus declarations
    mpd_handle.write("## Add the following lines just below the bus in\n\n")
    temp_string = open("template_mpd_bus.dat","r").read()
    for iter in range(0,num_ports):
        mpd_handle.write(temp_string.replace("$NUM", str(iter)))

    # Port Declarations
    mpd_handle.write("\n\n############################################################################\n\n")
    mpd_handle.write("## Add the following code in the ports declaration\n\n")
    mpd_handle.write("# Router rst and clk\n")
    mpd_handle.write("PORT router_clk = "", DIR = I\n")
    mpd_handle.write("PORT router_rst = "", DIR = O\n\n")
    temp_string = open("template_mpd_ports.dat","r").read()
    for iter in range(0,num_ports):
        mpd_handle.write(temp_string.replace("$NUM", str(iter)))
    

##### MAIN : record number of ports #####
if (len(sys.argv)>1):
    num_ports = int(sys.argv[1])
    print
    print "Number of ports = ", num_ports
    print
else:
    print
    print "Usage: python generate_ll_switch_code.py <no_of_ports>"
    print
    sys.exit(0)

# Delete old generated txt files
os.system("/bin/rm *.txt")

ipic_vhd()
mpd()
