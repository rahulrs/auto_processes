#!/usr/bin/python
import os,getopt,sys,re

#****************************************************************************
#* File:    update_project.py
#* Author:  Andy Schmidt
#* Date:    03/09/2009
#* Purpose: Update a Xilinx Project from 256 MB system to 512 MB
#*          Each ML-410 Node in the cluster has a 512 MB DIMM instead
#*          Of the original 256 MB DIMM.  Running this script will update
#*          the MHS and UCF files accordingly.
#*          
#* Usage:   update_project.py <XILINX_PROJECT>.xmp
#*          
#* Info:    Must run from within the Project Directory (at same level as XMP)
#*          Script will Generate a backup directory called: PROJ_BKUP
#*          If you need to revert back, check this directory
#*****************************************************************************

##############################################################################
# Function: get_mhs_ucf_files
# Purose:   Parse the XMP File for the MHS and UCF File Names
##############################################################################
def get_mhs_ucf_files(xmp_filename):
    # Strings to Match for MHS and UCF Filanem
    mhs_str = "MHS File:"
    ucf_str = "UcfFile:"
    files = []
    # Open XMP File in Read Only Mode
    xmp_fd = open_file(xmp_filename, 'r')
    for line in xmp_fd:
        if (mhs_str.upper() in line.upper()):
            # Append the name of the MHS File to the files array
            files.append(line.split(": ")[1].split("\n")[0])
        elif (ucf_str.upper() in line.upper()):
            # Append the name of the UCF File to the files array
            files.append(line.split(": ")[1].split("\n")[0].split("data/")[1])

    # Close XMP File
    xmp_fd.close
    return files

##############################################################################
# Function: modify_mhs_file
# Purose:   Backup the MHS and UCF File into a directory called; PROJ_BKUP
##############################################################################
def backup_files(mhs_filename, ucf_filename):
    print "Backing Update MHS and UCF File to \"PROJ_BKUP\" Directory"
    os.system("mkdir PROJ_BKUP")
    os.system("cp " + mhs_filename + " PROJ_BKUP/" + mhs_filename + "_ORIGINAL")
    os.system("cp " + "data/" + ucf_filename + " PROJ_BKUP/" + ucf_filename + "_ORIGINAL")

##############################################################################
# Function: modify_mhs_file
# Purose:   Parse MHS File and Update project from 256 MB to 512 if possible
##############################################################################
def modify_mhs_file(mhs_filename):
    # Delete Total External Memory Comment (I don't care to check for it)
    old_tot_mem_size_str = "# Total Off Chip Memory : "   
    # Change Comment Header from 256 MB DDR2 to 512 MB
    old_mem_size_str = "DDR2_SDRAM = 256 MB"
    new_mem_size_str = "#   - DDR2_SDRAM = 512 MB\n"
    # Change from fpga_0_ddr2_SDRAM_DDR2_Addr, DIR = O, VEC = [12:0] to [13:0]
    old_port_size_str = "PORT fpga_0_DDR2_SDRAM_DDR2_Addr_pin"
    new_port_size_str = " PORT fpga_0_DDR2_SDRAM_DDR2_Addr_pin = fpga_0_DDR2_SDRAM_DDR2_Addr, DIR = O, VEC = [13:0]\n"
    # Change from PARAMETER C_MEM_PARTNO = W1D32M72R8A-5A to HYB18T512800BF-5
    old_part_no_str = "PARAMETER C_MEM_PARTNO = W1D32M72R8A-5A"
    new_part_no_str = " PARAMETER C_MEM_PARTNO = HYB18T512800BF-5\n"
    # DDR2 Address Width Number of Bits (Not already set, it is 13 by default)
    new_mem_width_str = " PARAMETER C_MEM_ADDR_WIDTH = 14\n"
    # Memory High Address String (By Default is 0x0fffffff) Now is 0x1fffffff
    old_high_addr_str = "PARAMETER C_MPMC_HIGHADDR = 0x0fffffff\n"
    new_high_addr_str = " PARAMETER C_MPMC_HIGHADDR = 0x1fffffff\n"  
    # Create Temp copy of MHS File (system.mhs_TMP)
    tmp_filename = mhs_filename + "_TMP"
    # Open MHS and TMP MHS Files
    mhs_fd = open_file(mhs_filename, 'r')
    tmp_fd = open_file(tmp_filename, 'w+')

    ## Read Until Memory Size String Found
    find_and_replace(mhs_fd, tmp_fd, old_mem_size_str, new_mem_size_str)
    ## Read Until Port Size String Found
    find_and_replace(mhs_fd, tmp_fd, old_port_size_str, new_port_size_str)
    ## Read Until Memory Part Number String is Found
    eof = find_and_replace(mhs_fd, tmp_fd, old_part_no_str, new_part_no_str)
    if (eof == 1):
        print "System does not have DDR2"
        os.system("rm " + tmp_filename)
        ## Close All CDC and VHD Files
        mhs_fd.close
        tmp_fd.close
        sys.exit(0)
    else:
        ## Write "Memory Width String"    
        tmp_fd.write(new_mem_width_str)
        ## Read Until C_MPMC_HIGH_ADDR
        find_and_replace(mhs_fd, tmp_fd, old_high_addr_str, new_high_addr_str)
        ## Write Rest of MHS File
        for line in mhs_fd:
            tmp_fd.write(line)            

        ## Rename MHS TMP File to MHS File
        os.system("rm " + mhs_filename)
        os.system("mv " + tmp_filename + " " + mhs_filename) 
    
        ## Close All CDC and VHD Files
        mhs_fd.close
        tmp_fd.close

##############################################################################
# Function: modify_ucf_file
# Purose:   Parse UCF File and Update project from 256 MB to 512 if possible
##############################################################################
def modify_ucf_file(ucf_filename):
    # String to Find
    old_line_12_str="Net fpga_0_DDR2_SDRAM_DDR2_Addr_pin<12> IOSTANDARD = SSTL18_I;"
    new_line_12_str="Net fpga_0_DDR2_SDRAM_DDR2_Addr_pin<12> IOSTANDARD = SSTL18_I;\n"    
    addr_13_loc_str="Net fpga_0_DDR2_SDRAM_DDR2_Addr_pin<13> LOC=AA28;\n"
    addr_13_ios_str="Net fpga_0_DDR2_SDRAM_DDR2_Addr_pin<13> IOSTANDARD = SSTL18_I;\n"

    ## Create Temp copy of UCF File (system.ucf_TMP)
    tmp_filename = ucf_filename + "_TMP"
    ## Open MHS File
    ucf_fd = open_file("data/" + ucf_filename, 'r')
    ## Create/Open Temp File
    tmp_fd = open_file("data/" + tmp_filename, 'w+')
    
    ## Find Address Pin 12
    eof = find_and_replace(ucf_fd, tmp_fd, old_line_12_str, new_line_12_str)
    if (eof == 1):
        print "System does not have DDR2"        
        os.system("rm data/" + tmp_filename)
        ## Close All CDC and VHD Files
        ucf_fd.close
        tmp_fd.close
        sys.exit(0)        
    else:
        # Write Address Pin 13 Info to UCF
        tmp_fd.write(addr_13_loc_str)
        tmp_fd.write(addr_13_ios_str)            

        ## Write Rest of UCF File
        for line in ucf_fd:
            tmp_fd.write(line)

        ## Rename UCF TMP File to UCF File
        os.system("rm data/" + ucf_filename)
        os.system("mv data/" + tmp_filename + " data/" + ucf_filename) 
    
        ## Close All CDC and VHD Files
        ucf_fd.close
        tmp_fd.close

##############################################################################
# Function: open_file
# Purpose:  Try to open file with file option if not possible error and exit
##############################################################################
def open_file(filename, fileoption):
    try:
        fd = open(filename, fileoption)
    except:
        print "\tFile Open Error: " + filename + " Doesn't Exist!"
        sys.exit(0)        
    return fd

##############################################################################
# Function: find_and_replace
# Purpose:  Find a String in one file and replace it in the other file
##############################################################################
def find_and_replace(old_fd, new_fd, old_str, new_str):
    eof = 1
    for line in old_fd:
        if (old_str.upper() in line.upper()):
            new_fd.write(new_str)
            eof = 0
            break
        else:
            new_fd.write(line)
    return eof

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
            print "Usage: update_project.py <Project File>.xmp"
            sys.exit(0)
    # process arguments
    if (len(args) == 1):
        files = get_mhs_ucf_files(sys.argv[1]);
        mhs_filename = files[0]
        ucf_filename = files[1]
        backup_files(mhs_filename, ucf_filename)
        modify_mhs_file(mhs_filename)
        modify_ucf_file(ucf_filename)
    else:
        print "Usage: update_project.py <Project File>.xmp"
        sys.exit(0)

###############################################################################
## Main Call
###############################################################################
main()

