##############################################################
# Multiple node control
# Author: Rahul
#
##############################################################
#
# Control multiple nodes using this script
# Usage: python ~/multiple_node_control.py <command> <config>
# You must supply a config file of the following format
# NODE = <node numbers separated by a space>
# SLOT = <slot number>
# ACE  = <ACE file path>
#
##############################################################

import os, re, sys, commands, time

# Parse file and obtain required info
def parse_file():
    # Identify settings
    if os.path.isfile(config_file) == True:
        for config_line in open(config_file, "r"):
            if (int(str(config_line).find("NODE")) > -1):
                node_list = config_line
                node_list = node_list.replace("NODE","").strip()
                node_list = node_list.replace("=","").strip()
            if (int(str(config_line).find("SLOT")) > -1):
                slot = config_line
                slot = slot.replace("SLOT","").strip()
                slot = slot.replace("=","").strip()
            if (int(str(config_line).find("ACE")) > -1):
                ace_file = config_line
                ace_file = ace_file.replace("ACE","").strip()
                ace_file = ace_file.replace("=","").strip()
        if (node_list == "") or (slot == "") or (ace_file == ""):
            print "Check the config file... something is not right !!\n"
            sys.exit()
        return node_list, slot, ace_file
    else:
        print "Config file path does not exist !! Exiting !! \n\n"
        sys.exit()


#######################################################        
# Start nodes in the list
def up_nodes():
    for node in node_list:
        print "Powering up " + node
        os.system("fsc up " + node)


#######################################################
# Down nodes
def down_nodes():
    for node in node_list:
        print "Powering down " + node
        os.system("fsc down " + node)


#######################################################
# Upload ace files
def flash_nodes():
    for node in node_list:
        print "Flashing " + node 
        os.system("fsc upload " + node + " " + slot + " " + ace_file + " '" + timestamp + "'")


#######################################################
# Select slot
def select_slot_and_boot():
    for node in node_list:
        os.system("fsc select " + node + " " + slot)
        os.system("fsc boot " + node)

        
################ PROGRAM BEGINS HERE ##################
# Check input arguments
if (len(sys.argv) == 3):
    command = str(sys.argv[1])
    config_file = str(sys.argv[2]) 
else:
    print "Usage: python ~/multiple_node_control.py <command> <config_file>\n"
    sys.exit()

# Parse input file and generate info
parsed_list = parse_file()
node_list = parsed_list[0].split()
slot      = parsed_list[1] + " "
ace_file  = parsed_list[2] + " "

# Sanity check FSC - chosen from loader.py
# Check if everything is fine before running FSC
if commands.getoutput('uname -n') != "marge":
    print "FSC cannot be run here !!\n"
    sys.exit(0)
username = commands.getoutput('echo $USER')
timestamp = commands.getoutput('date')

for node in node_list:
    if int(commands.getoutput('fsc list|grep ' + node).find(username)) > -1:
        continue
    else:
        print node, "has not been requested by", username, "...exiting !!\n"
        sys.exit()

### Start operation ###
# Declare config
print "Nodes to operate  = ",node_list
print "Slot to flash     = ",slot
print "ACE file to flash = ",ace_file

# Command selection
if command == "flash":
    down_nodes()
    time.sleep(5)
    up_nodes()
    time.sleep(60)
    flash_nodes()
    time.sleep(2)
    select_slot_and_boot()
elif command == "boot":
    down_nodes()
    time.sleep(5)
    up_nodes(60)
    select_slot_and_boot()
elif command == "down":
    down_nodes()
else:
    print "Commands available are..."
    print "flash = Flash nodes with ACE file"
    print "boot  = Boot into a slot"
    print "down  = Power down nodes"
