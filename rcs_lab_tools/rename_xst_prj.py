#!/usr/bin/python
import os,getopt,sys,re

#****************************************************************************
#* File:    rename_xst_prj.py
#* Author:  Andy Schmidt
#* Purpose: Rename an XST Synthesis Project which includes the
#*          .PRJ, .SCR, .VHD and Makefile
#*          I did this because I use XST to verify synthesizability of my
#*          components and it was getting annoying to create these or modify
#*          these xst_synthesis directories from the VHDL Template.
#*
#*          Now all I need to do is copy the VHDL_TEMPLATE from my home
#*          directory or an existing project and run this script, yay!
#* Usage:   ./rename_xst_prj.py old_project new_project
#* History: 01/03/2010 - AGS: File Created
#*****************************************************************************

##############################################################################
# Function: find_replace
# Purose:   Find and Replace all Strings and File Names
##############################################################################
def find_replace(old_file_name, new_file_name, old_string, new_string):
    old_fd = open(old_file_name, 'r+')
    new_fd = open(new_file_name, 'w+')    
    old_string_UPPER = old_string.upper()

    for line in old_fd:
        # Look for Exact Match (case sensitive)
        if (old_string in line):
            new_line = line.replace(old_string,new_string)
            new_fd.write(new_line)
        # Look for Upper Case match (MPD File has one line where this matters)
        elif (old_string_UPPER in line):
            new_line = line.replace(old_string_UPPER,new_string)            
            new_fd.write(new_line)
        # String Not Found so ignore
        else:
            new_fd.write(line)
    old_fd.close
    new_fd.close
    # Remove the Old File Name and keep the New File Name
    os.system("rm " + old_file_name)
    

##############################################################################
# Function: rename_project
# Purose:   Renames the XST Synthesis Project Files
##############################################################################
def rename_project(old_prj, new_prj):
    ## Rename PRJ File
    old_file_name = old_prj + ".prj"
    new_file_name = new_prj + ".prj"
    if (os.path.isfile(old_prj + ".prj")):
        find_replace(old_file_name, new_file_name, old_prj, new_prj)
    else:
        print "\tERROR - Unable to find: " + old_file_name

    ## Rename SCR File
    old_file_name = old_prj + ".scr"
    new_file_name = new_prj + ".scr"
    if (os.path.isfile(old_prj + ".scr")):
        find_replace(old_file_name, new_file_name, old_prj, new_prj)
    else:
        print "\tERROR - Unable to find: " + old_file_name

    ## Rename VHDL File
    old_file_name = old_prj + ".vhd"
    new_file_name = new_prj + ".vhd"
    if (os.path.isfile(old_prj + ".vhd")):
        find_replace(old_file_name, new_file_name, old_prj, new_prj)
    else:
        print "\tERROR - Unable to find: " + old_file_name        
        
    ## Update Makefile
    if (os.path.isfile("Makefile")):
        find_replace("Makefile", "Makefile_new", old_prj, new_prj)
        os.system("mv Makefile_new Makefile")
    else:
        print "\tERROR - Unable to find: Makefile"
        
    #os.system("mv " + old_bbd_file + " " + new_bbd_file);
    # Move data/mpd to new File name


##############################################################################
# Main Program Begins here...
##############################################################################
def main():
    try:
        opts, args = getopt.getopt(sys.argv[1:], "h", ["help"])
    except getopt.error, msg:
        print msg
        print "for help use --help"
        sys.exit(2)
    # process options
    for o, a in opts:
        if o in ("-h", "--help"):
            print "Usage: rename_xst_prj.py <old_prj> <new_prj>"
            sys.exit(0)
    # process arguments
    if (len(args) == 2):
        rename_project(sys.argv[1], sys.argv[2])
    else:
        print "Usage: rename_xst_prj.py <old_prj> <new_prj>"
        sys.exit(0)

###############################################################################
## Main Call
###############################################################################
main()
