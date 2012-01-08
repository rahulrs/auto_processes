#######################################################
# VHDL dependency check                               #
# Author : Rahul                                      #
#######################################################
# Checks for VHDL dependency modules and alerts if    #
# a file is missing                                   #
#######################################################

import re, os, commands, sys, string

print "VHDL Dependency check..."

# PWD fix
pwd = commands.getoutput('pwd')
print "PWD =", pwd

# Create a directory of vhdl files in the directory
vhdl_dir = pwd + "/vhdl_listing.temp"
os.system("ls *.vhd > " + vhdl_dir)
vhdl_listing_handle = open(vhdl_dir,"r")

# For every file in the list, read file and check if the component name is in directory, if not report it !!
vhdl_dir_lines = vhdl_listing_handle.readlines()

print "-----------------------------------------------------------------"
# Open each file in directory listing
for line in vhdl_dir_lines:
    current_vhdl = (pwd + '/' + line).replace('\n','')
    # Open each VHDL file in the listing (read mode)
    current_vhdl_handle = open(current_vhdl,"r")
    print "Checking",str(line).replace('\n','')
    
    # Read file
    open_vhdl_contents = current_vhdl_handle.readlines()

    i=1;
    # Parse file line by line
    for line_in_file in open_vhdl_contents:
        reading_line = (str(line_in_file).strip()).replace('\n','')        
        if reading_line.startswith("component") == True:
            # Find the name of the component
            component_name = (reading_line.replace("component"," ")).strip()            
            print "Found component:", component_name
            search_target = component_name + '.vhd\n'
            if search_target not in vhdl_dir_lines:
                print "#####", component_name, "has not been found ! #####" 

    print "-----------------------------------------------------------------"
    # Close the VHDL file
    current_vhdl_handle.close()
    

# Remove tmp files
os.system('rm ' + vhdl_dir)
print "This program is just a heads up to missing modules... not a complete sanity check !"
print "Fin !"
