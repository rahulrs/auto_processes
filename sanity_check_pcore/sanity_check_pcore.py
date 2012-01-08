###########################################################################################
# PCORE SANITY CHECK [WIP]                                                                #
# Author : Rahul                                                                          #
###########################################################################################
# Description:                                                                            #
# Checks/completes PAO MPD fixes for Custom IP                                            #
###########################################################################################
# Usage:                                                                                  #
# Sym-link or copy to instde a pcore where you would find the hdl, devl, data directories #
# Run as python sanity_check_pcore.py                                                     #
###########################################################################################

import os, re, sys, commands

print "Performing pcore sanity check..."

# Get a PWD fix
pwd = commands.getoutput('pwd')
print "PWD = ",pwd


# Find a PAO file at relative location or crash here
pao_path = commands.getoutput('find . -name *.pao')
if pao_path == "":
    print "PAO file not found !"
    sys.exit(0)
else:
    print "PAO file found @",pao_path


# Find an MPD file at relative location or crash here
mpd_path = commands.getoutput('find . -name *.mpd')
if pao_path == "":
    print "MPD file not found !"
    sys.exit(0)
else:
    print "MPD file found @",mpd_path


# Backup existing MPD and PAO files
os.system("cp " + mpd_path + " " + mpd_path + ".bak")
os.system("cp " + pao_path + " " + pao_path + ".bak")

# Check for existance of 'netlist' folder
netlist_folder = os.path.isdir("./netlist")
if str(netlist_folder) == "True":
    print "Netlist folder has been found, BBD file will be overwritten !"
    ngc_list = commands.getoutput('ls ./netlist')
    bbd_path = mpd_path.replace("mpd","bbd")
    print "BBD file = ",bbd_path
    ngc_list = ngc_list.replace("\n",", ")
    bbd_path_handle = open(bbd_path, "w")
    bbd_path_handle.write("FILES\n")
    bbd_path_handle.write(ngc_list)
else:
    print "Netlist folder does not exist, no BBD file will be generated/checked !"

# Guess core name
mpd_string = commands.getoutput("grep BEGIN " + mpd_path)
core_name = mpd_string.replace("BEGIN","").strip()
print "Core name =", core_name

# Gues core name w/ver
list2 = []
for token2 in pwd.split("/"):
    list2.append(token2)
full_name = list2[len(list2)-1]
print "Full core name =",full_name

disable_mpd = 0
# Fixing the MPD file
mpd_string = open(mpd_path,"r").readlines()
mpd_file_handle = open(mpd_path,"w")
option_count = 0
for mpd_line in mpd_string:
    if str(mpd_line).startswith("OPTION") == True:
        mpd_file_handle.write(mpd_line)
        option_count = option_count + 1
        if str(mpd_line) == "OPTION STYLE = MIX\n":
            disable_mpd = 1        
    elif option_count > 0 and str(mpd_line) == "\n" and disable_mpd == 0:        
        mpd_file_handle.write("OPTION STYLE = MIX\n\n")
        option_count = 0
    else:
        mpd_file_handle.write(mpd_line)

###################################################
# Check for vhdl files in hdl/vhdl/ or crash here
###################################################
os.system("cd ./hdl/vhdl/; ls *.vhd > ../../temp.dat")
vhdl_list_string = open("temp.dat","r").readlines()
vhdl_list_string.remove("user_logic.vhd\n")
vhdl_list_string.remove(core_name + ".vhd\n")
pao_string = open(pao_path,"r").readlines()

pao_file_handle = open(pao_path,"w")

disable_pao_edits = 0
for pao_line in pao_string:    
    if str(pao_line).find(full_name) > 1 and disable_pao_edits == 0 and str(pao_line).startswith("#") == False:
        for vhdl_line in vhdl_list_string:
            vhdl_module_name = str(vhdl_line).replace(".vhd\n","")
            pao_file_handle.write("lib " + full_name + " " + vhdl_module_name + " vhdl\n")
        disable_pao_edits = 1
        pao_file_handle.write(pao_line)        
    else:
        pao_file_handle.write(pao_line)
       

# Cleanup
os.system("rm temp.dat")

# Instructions
print
print "Check the PAO file for compile order as this is not checked by the script !"
print "If verilog files exist in the project, they have not been checked !"
print "Job done !"
print
