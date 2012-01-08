########################################################################
# Script for changing the MAC address on the DTS file.
# Author : Rahul
#
# The device tree method for compiling a linux kernel leaves the
# problem of i2c not reading the board eeprom and setting up the NFS
# mount correctly. Until a more elegant solution is found, this script
# will fix that problem by fixing the MAC address directly in the DTS
# file.
#
# Working: Hunt down the DTS file generated by "make libs" of XPS,
# find and replace the mac-addr section. Depending on what node number
# is entered in the argument the appropriate line will be read in the
# 'ethers' file and the required MAC address will be put in the DTS
# file
#
# Usage: python change_mac_dts.py <node_number> <dts_file_path>
#
########################################################################

import os, re, sys, commands

# Accept inputs, else exit
if (len(sys.argv)==3):
    node_number = str(sys.argv[1])
    dts_file_path = str(sys.argv[2])
    print "Node number   = ",node_number
    print "DTS file path = ",dts_file_path
else:
    print "Usage: python change_mac_dts.py <node_number> <dts_file_path>\n"
    sys.exit()


# Check if the dts file exists, else exit
if os.path.isfile(dts_file_path) == True:
    dts_bak_file_path = dts_file_path + ".bak"
    os.system("cp " + dts_file_path + " " + dts_bak_file_path)
    print "DTS file backed up !!"
else:
    print "DTS file not found at ",dts_file_path
    sys.exit()


# Use node number and hunt it down in 'ethers'
## Find the required line
for line in open("/home/rsharm14/auto_processes/change_mac_dts/ethers","r"):
    if(int(str(line).find(node_number)) > -1):
        target_line = str(line)
        break


## Tokenize target_line and obtain the ip address and mac 
ether_tokens = target_line.split(' ')
req_mac_address = str(ether_tokens[1]).replace(":"," ")
req_ip_address =  ether_tokens[2]
print "local-mac-address in DTS will be replaced with [",req_mac_address,"]"


# Search for specific line in DTS file and replace it with the new mac address
dts_temp_handle = open("dts.tmp","w")
for dts_line in open(dts_file_path,"r"):
    if int(dts_line.find("local-mac-address")) > -1:
        dts_temp_handle.write("\t\t\t\tlocal-mac-address = [ " + req_mac_address + " ];\n")
    else:
        dts_temp_handle.write(str(dts_line))

# Replace the DTS file
os.system("mv dts.tmp " + dts_file_path)

print "Job done !!\n"
