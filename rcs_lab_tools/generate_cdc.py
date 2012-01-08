#!/usr/bin/python
import os,getopt,sys,re

#****************************************************************************
#* File:    generate_cdc.py
#* Author:  Andy Schmidt
#* Date:    12/26/2008
#* Purpose: To generate the CDC file for ChipScope from a template cdc file
#*          provided by CoreGen and the VHD file where the component is
#*          instantiated.  Aftewards the new CDC file can be used via
#*          ChipScope by importing the CDC file to save time.
#*
#* Usage:   ./generate_cdc.py <ILA>.cdc <VHDL>.vhd <ILA Instance Name in vhdl>
#*          
#* Info:    The ILA Instance Name in VHD allows multiple instances of the ILA
#*          to be generated based on the Name.  
#*          The file generated is the Capitalized Component Instance Name
#*****************************************************************************
##############################################################################
# Function: find_replace
# Purose:   Find and Replace all Strings and File Names
##############################################################################
def generate_cdc(ila_filename, vhd_filename, ila_inst_name):
    ## Get ILA Component Name from file_name
    ila_component = ila_filename.split(".cdc")[0]

    ## Create a temporary CDC File to write to
    tmp_filename = ila_inst_name.upper() + ".cdc"

    ##------------------------------------------------------------------------ 
    ## Open Files
    ##------------------------------------------------------------------------
    cdc_fd = open_file(ila_filename, 'r')
    vhd_fd = open_file(vhd_filename, 'r')
    tmp_fd = open_file(tmp_filename, 'w+')    

    ##------------------------------------------------------------------------
    ## Initialize Arrays and Indicators
    ##------------------------------------------------------------------------
    triggers = []
    cdc_replace = []
    found_component = 0
    found_instance = 0

    ##------------------------------------------------------------------------
    ## Search VHDL File for ILA Component Declaration and Check if ILA Found
    ##------------------------------------------------------------------------
    for line in vhd_fd:
        if (("COMPONENT " + ila_component.upper()) in line.upper()): 
            found_component = 1
            break

    # Check if ILA Component Declaration was Found
    if (found_component == 0):
        print "\tError: Unable to find ILA Component: " + ila_component
        cdc_fd.close()
        vhd_fd.close()
        tmp_fd.close()
        os.system("rm " + tmp_filename)
        sys.exit(0)

    ##------------------------------------------------------------------------
    ## Create a list of the triggers in the ILA for use later
    ##------------------------------------------------------------------------
    trig_num = 0
    for line in vhd_fd:
        if ("TRIG" + str(trig_num) in line.upper()):
            # Get Vector Size and Insert into triggers list
            vector_size = line.split("(")[1].split()[0]
            triggers.append(vector_size)
            trig_num = trig_num + 1            
        elif ("END COMPONENT" in line.upper()):
            # Check to see if reached the end of the component and stop
            break

    ##------------------------------------------------------------------------
    ## Search for ILA Component Instantiation and check if ILA Inst was Found
    ##------------------------------------------------------------------------
    for line in vhd_fd:
        # I assume there is a space between the ILA Instance Name and the :
        if ((ila_inst_name.upper() + " : " + ila_component.upper()) in line.upper()):
            found_instance = 1
            break

    # Check if ILA Component Instance was Found
    if (found_instance == 0):
        print "\tError: Unable to find ILA Instance: " + ila_inst_name
        cdc_fd.close()
        vhd_fd.close()
        tmp_fd.close()
        os.system("rm " + tmp_filename)
        sys.exit(0)

    ##------------------------------------------------------------------------
    ## Search for ILA's 1st Trigger (TRIG0)
    ##------------------------------------------------------------------------
    for line in vhd_fd:
        if ("TRIG0" in line.upper()):
            break

    ##------------------------------------------------------------------------
    ## For Each Trigger in the ILA Instance Store name into cdc_replace list
    ##------------------------------------------------------------------------ 
    for trig_num in range(len(triggers)):
        # If the Trigger is Indexed (IE trig3(18) =>) then get all bit signals
        if (("TRIG" + str(trig_num) + "(") in line.upper()):
            sub_array = []
            # For each indexed bit signal in Trigger
            for i in range(int(triggers[trig_num])+1):
                if (("TRIG" + str(trig_num) + "(") in line.upper()):
                    # Store each subsignal in sub_array
                    trig_array = line.split()
                    sub_array.append(trig_array[2].split(',')[0])
                    line = vhd_fd.next()
                else:
                    # Current line is the next trigger
                    break
            # Insert into list as a tuple where 1 represents it is a bit vector
            # and the sub_array are all of the bit signals. To be used later
            cdc_replace.append((1,sub_array))

        # Check if Trigger is not a bit vector Indexed
        if (("TRIG" + str(trig_num)) in line.upper()):
            trig_str = line.split()[2].split(',')[0].split("(")[0]
            if (trig_str == ""):
                # Signal was an (others => or something else, ignore it
                cdc_replace.append((0,"TRIG" + str(trig_num)))
            else:
                # Tuple 0 represents a non bit vector index trigger
                cdc_replace.append((0,trig_str))
            trig_num = trig_num + 1
            line = vhd_fd.next()

    ##------------------------------------------------------------------------
    ## Begin Writing to new cdc File
    ##------------------------------------------------------------------------
    trig_num = 0 
    old_string = ("TRIG" + str(trig_num))
    for line in cdc_fd:
        # Check if cdc_replace is a Bit Vector (don't rename if it is not)
        # only replace individual bit signals below
        if (old_string in line.upper()):
            if (cdc_replace[trig_num][0] == 0):
                line = line.replace(old_string, cdc_replace[trig_num][1].upper())
            # Write Line to File and Increment to next Trigger
            tmp_fd.write(line)
            trig_num = trig_num + 1
            old_string = ("TRIG" + str(trig_num))
        elif ("RADIX=BIN" in line.upper()):
            # Check if Line Contain RADIX (change to Hex for easier use)
            line = line.replace("radix=Bin", "radix=Hex")
            tmp_fd.write(line)
        else:
            tmp_fd.write(line)

        # Stop when written valid number of triggers
        if (trig_num == len(triggers)):
            break
        
    ##------------------------------------------------------------------------
    ## Search for TRIG0 Bit Index
    ##------------------------------------------------------------------------
    for line in cdc_fd:
        if ("TRIG0" in line.upper()):
            # If found CDC Files next TRIG0 Instance
            break        
        elif ("RADIX=BIN" in line.upper()):
            # Check if Line has RADIX (change to Hex for easier readability)
            line = line.replace("radix=Bin", "radix=Hex")
            tmp_fd.write(line)
        else:
            # Write line as is to tmp CDC File
            tmp_fd.write(line)        

    ##------------------------------------------------------------------------
    ## Replace Sub Arrays
    ##------------------------------------------------------------------------
    trig_num = 0 
    old_string = ("TRIG" + str(trig_num))
    for trigger_size in triggers:
        # For each bit replace each TRIGx[y]
        for i in range(int(trigger_size)+1):
            if (cdc_replace[trig_num][0] == 0):
                # Replace the Trigger from the ILA with the Actual Signal
                new_line = line.replace(old_string, cdc_replace[trig_num][1].upper())
                tmp_fd.write(new_line)
            elif (cdc_replace[trig_num][1][i] == "'0'"):
                # Ignore if any of the sub-arrays have '0'
                tmp_fd.write(line)
            else:
                # Get rid of the [y] as well
                new_line = line.replace(old_string+"["+str(i)+"]", cdc_replace[trig_num][1][i].upper())
                tmp_fd.write(new_line)
            # Read the Next Line
            line = cdc_fd.next()
        # Increment to the next Trigger
        trig_num = trig_num + 1
        old_string = ("TRIG" + str(trig_num))

    ##------------------------------------------------------------------------
    ## Replace Trigger Port Single Names (like 1st Replace above)
    ##------------------------------------------------------------------------ 
    for trig_num in range(len(triggers)):
        old_string = ("TRIG" + str(trig_num))
        if (cdc_replace[trig_num][0] == 0):
            new_line = line.replace(old_string, cdc_replace[trig_num][1].upper())
            tmp_fd.write(new_line)
        else:
            tmp_fd.write(line)
        # Read the Next Line
        line = cdc_fd.next()

    ##------------------------------------------------------------------------
    ## Check to make sure Current Line has same number of ILA Triggers
    ##------------------------------------------------------------------------ 
    if ("SIGNALEXPORT.TRIGGERPORTCOUNT=" in line.upper()):
        tmp_fd.write(line)

    ##------------------------------------------------------------------------
    ## Write REst of file
    ##------------------------------------------------------------------------
    for line in cdc_fd:
        tmp_fd.write(line)        

    ##------------------------------------------------------------------------
    ## Close All CDC and VHD Files
    ##------------------------------------------------------------------------
    cdc_fd.close
    vhd_fd.close
    tmp_fd.close

    ##------------------------------------------------------------------------
    ## Print Success Message
    ##------------------------------------------------------------------------
    print "Successfully Generated: " + tmp_filename


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
            print "Usage: generate_cdc.py <ILA>.cdc <HW_CORE>.vhd <ILA Instance>"
            sys.exit(0)
    # process arguments
    if (len(args) == 3):
        generate_cdc(sys.argv[1], sys.argv[2], sys.argv[3])
    else:
        print "Usage: generate_cdc.py <ILA>.cdc <HW_CORE>.vhd <ILA Instance>"
        sys.exit(0)

###############################################################################
## Main Call
###############################################################################
main()
