#!/usr/bin/python
import os,getopt,sys,re

#****************************************************************************
#* File:    rename_pcore.py
#* Author:  Andy Schmidt
#* Purpose: Rename an existing Hardware PCore with a New Name
#*          Often I want to rename a pcore (or make a copy) when the
#*          functionality changes, so this script should help speed up the
#*          processs.  It just Copies the pcore (don't want to delete it)
#*
#* Usage:   ./rename_pcore.py <old_pcore_directory> <new_pcore_directory>
#*             For Exampe:
#*                  ./rename_pcore.py test_core_v1_00_a awesome_core_v1_00_a
#*
#* Info:    The Process does the following
#*          1. Copies the existing PCORE (I don't delete it, it is up to you)
#*          2. Renames the data/*.mpd, *.pao, *.bbd (if there is one)
#*          3. Updates the mpd, pao files with the new core name
#*          4. Renames the hdl/vhd/*.vhd (not user_logic) the high level VHD
#*          5. Updates the vhd with the new core name
#*          6. Updates synthesis_xst directory if one exists
#*
#* History: 12/26/2008 - AGS: File Created
#*          11/09/2009 - AGS: Updated to handle copying synthesis_dir
#*                            and to change version numbers
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
# Function: rename_pcore
# Purose:   Copies the existing pcore and renames it to its new name
##############################################################################
def rename_pcore(old_dir, new_dir):
    # Check if Path Exists
    if not (os.path.isdir(old_dir)):
        print "\tError: Directory " + old_dir + " Does Not Exist!"
        sys.exit(0)
    # Strip off the version (I.E. v1_00_a)
    # 8 is the number of letters in "_v1_00_a"
    old_pcore_len = len(old_dir) - 8
    new_pcore_len = len(new_dir) - 8
    # Set the actual pcore_name based on directory - 8
    old_pcore_name = old_dir[:old_pcore_len]
    old_pcore_ver = old_dir[old_pcore_len:]
    new_pcore_name = new_dir[:new_pcore_len]
    new_pcore_ver = new_dir[new_pcore_len:]
    # Move Directory    
    os.system("cp -a " + old_dir + " " + new_dir)
    # Move data/bbd to new File name
    old_bbd_file = new_dir + "/data/" + old_pcore_name + "_v2_1_0.bbd"
    new_bbd_file = new_dir + "/data/" + new_pcore_name + "_v2_1_0.bbd"
    os.system("mv " + old_bbd_file + " " + new_bbd_file);
    # Move data/mpd to new File name
    old_mpd_file = new_dir + "/data/" + old_pcore_name + "_v2_1_0.mpd"
    new_mpd_file = new_dir + "/data/" + new_pcore_name + "_v2_1_0.mpd"
    find_replace(old_mpd_file, new_mpd_file, old_pcore_name, new_pcore_name)
    # Move data/pao to new File name
    old_pao_file = new_dir + "/data/" + old_pcore_name + "_v2_1_0.pao"
    new_pao_file = new_dir + "/data/" + new_pcore_name + "_v2_1_0.pao"
    find_replace(old_pao_file, new_pao_file+"_tmp", old_pcore_name, new_pcore_name)
    # Update the new PAO to match the new version number
    find_replace(new_pao_file+"_tmp", new_pao_file, new_pcore_name+old_pcore_ver, new_pcore_name+new_pcore_ver)
    # Move Main VHD File
    old_vhd_file = new_dir + "/hdl/vhdl/" + old_pcore_name + ".vhd"
    new_vhd_file = new_dir + "/hdl/vhdl/" + new_pcore_name + ".vhd"
    find_replace(old_vhd_file, new_vhd_file, old_pcore_name, new_pcore_name)
    # Rename Synthesis Directory
    update_synthesis_xst(old_dir, old_pcore_name, old_pcore_ver, new_dir, new_pcore_name, new_pcore_ver)


##############################################################################
# Function: update_synthesis_xst
# Purose:   Rename the synthesis_xst contents
##############################################################################
def update_synthesis_xst(old_dir, old_pcore_name, old_pcore_ver, new_dir, new_pcore_name, new_pcore_ver):
    # Create new synthesis_xst dir (if one exists otherwise exit subroutine)
    if (os.path.isdir(old_dir + "/synthesis_xst")):
        # Temp Variables
        old_syn_dir_mk  = old_dir + "/synthesis_xst/Makefile"
        old_syn_dir_prj = old_dir + "/synthesis_xst/" + old_pcore_name + ".prj"
        old_syn_dir_scr = old_dir + "/synthesis_xst/" + old_pcore_name + ".scr"
        new_syn_dir     = new_dir + "/synthesis_xst/"
        new_syn_dir_mk  = new_dir + "/synthesis_xst/Makefile"
        new_syn_dir_prj = new_dir + "/synthesis_xst/" + new_pcore_name + ".prj"
        new_syn_dir_scr = new_dir + "/synthesis_xst/" + new_pcore_name + ".scr"
        # Remove already existing synthesis_xst directory in new pcore
        os.system("rm -rf " + new_syn_dir)
        # Create Directory
        os.system("mkdir " + new_syn_dir)
        # Copy old files to their new location
        os.system("cp " + old_syn_dir_mk + " "  + new_syn_dir_mk + "_tmp")
        os.system("cp " + old_syn_dir_prj + " "  + new_syn_dir_prj + "_tmp")
        os.system("cp " + old_syn_dir_scr + " "  + new_syn_dir_scr + "_tmp")
        # Update contents to new pcore name
        find_replace(new_syn_dir_mk + "_tmp", new_syn_dir_mk, old_pcore_name, new_pcore_name)
        find_replace(new_syn_dir_prj + "_tmp", new_syn_dir_prj + "_tmp2", old_pcore_name, new_pcore_name)
        find_replace(new_syn_dir_scr + "_tmp", new_syn_dir_scr, old_pcore_name, new_pcore_name)
        # Update PRJ File to use new Pcore Version Number
        find_replace(new_syn_dir_prj + "_tmp2", new_syn_dir_prj, new_pcore_name+old_pcore_ver, new_pcore_name+new_pcore_ver)

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
            print "Usage: rename_pcore.py <old_v1_00_a> <new_v1_00_a>"
            sys.exit(0)
    # process arguments
    if (len(args) == 2):
        rename_pcore(sys.argv[1], sys.argv[2])
    else:
        print "Usage: rename_pcore.py <old_v1_00_a> <new_v1_00_a>"
        sys.exit(0)

###############################################################################
## Main Call
###############################################################################
main()
