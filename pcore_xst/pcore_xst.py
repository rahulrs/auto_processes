##################################################################################
# Author: Rahul                                                                  #
# Synthesis estimate generator [STATE: BETA]                                     #
#                                                                                #
# DATE : 29th June 2010                                                          #
#                                                                                #
# DESCRIPTION:                                                                   #
# Build the pcore and copy this file into the                                    #
# <xps_project>/pcores/<core_name_w_version> level. This script will generate a  #
# synthesis estimate using 'xst'. It creates a directory by the name             #
# of 'synthesis_xst' and generates the reports there.                            #
#                                                                                #
# Documentation can be found here:                                               #
# http://docs.google.com/Doc?docid=0ATlAkbQsZdUoZGR0azdnZ2dfNzhrMnJka3BnZg&hl=en #
#                                                                                #
# Limitation:                                                                    #
# - Does not perform a sanity check                                              #
# - Looks up VHDL files only                                                     #
#                                                                                #
##################################################################################
# Variables:                                                                     #
# present_working_dir : Present working directory is recorded here               #
# core_name           : pcore name (recorded from BEGIN <core_name> in MPD file) #
# core_name_w_ver     : pcore name with version number                           #
#                                                                                #
##################################################################################

import os, re, commands, sys

# Record the argument correctly
if (len(sys.argv)!=2):
    print "Usage: python pcore_xst.py <board_name>"
    sys.exit(0)
else:
    board_name = str(sys.argv[1])
    if board_name == "ml410":
        package_name = "xc4vfx60ff1152-11"
    elif board_name == "ml605":
        package_name = "xc6vlx240t-1ff1156"
    else:
        package_name = "xc4vfx60ff1152-11"
        print "Please check the SCR file for the correct board name as input was not recognized... script will continue assuming ML410 !\r"

# Record the current location
present_working_dir = commands.getoutput('pwd')
print "Present working directory is set as:", present_working_dir

# Check for pcore tree and set directory paths
vhdl_path = present_working_dir + "/hdl/vhdl/"
data_path = present_working_dir + "/data/"
xst_path = present_working_dir + "/synthesis_xst/"

# Check and create 'synthesis_xst' directory
dir_status = os.path.isdir(xst_path)
if str(dir_status) == "False":
    print "'synthesis_xst' will be created"
else:
    print "'synthesis_xst' will be regenerated"
    os.system("/bin/rm -rf synthesis_xst")
os.mkdir(xst_path,0755)    
print

# Record <core_name> from MPD file (check for line starting with BEGIN
core_name_filter_cmd = "cat " + data_path + "/*mpd | grep BEGIN"
core_name_filter_output = commands.getoutput(core_name_filter_cmd)
list1 = []
for token1 in core_name_filter_output.split(" "):
    list1.append(token1)
core_name = list1[1] 
print "Name of core is recorded as:"
print core_name
print

# Record full core name with version number
list2 = []
for token2 in present_working_dir.split("/"):
    list2.append(token2)
core_name_w_ver = list2[len(list2)-1]
print "Full core name (with version number is recorded as:"
print core_name_w_ver
print


# Set PRJ and SCR path names
prj_path = present_working_dir + "/synthesis_xst/" + core_name +  ".prj"
scr_path = present_working_dir + "/synthesis_xst/" + core_name +  ".scr"
make_path = present_working_dir + "/synthesis_xst/" + "Makefile"

# Generate PRJ file
print "Generating the PRJ file @ "
print prj_path
print
os.system("touch " + prj_path)
prj_file_handle = open(prj_path, "w")

print "Checking for VHDL libraries used in the project..."
vhdl_lib_list = []
os.system("cp " + vhdl_path + "/*vhd " + xst_path) 
os.system("cat " + xst_path + "/*.vhd | grep library | grep -v ieee > " + xst_path + "/vhdl_lib_list.dat")
lib_list_handle = open(xst_path + "/vhdl_lib_list.dat")
while 1:
    lib_list_reading = lib_list_handle.readline()
    lib_list_reading = lib_list_reading.replace('\n','')
    lib_list_reading = lib_list_reading.replace(';','')
    lib_list_reading = lib_list_reading.replace('library ','')
    if not lib_list_reading:
        break
    else:
        vhdl_lib_list.append(lib_list_reading)
vhdl_lib_list = list(set(vhdl_lib_list))
#vhdl_lib_list.remove(core_name_w_ver)
#print "Following libraries have been recognized in the VHDL files:"
#print vhdl_lib_list

for lib_name in vhdl_lib_list:
    os.system("find $XILINX_EDK/hw/XilinxProcessorIPLib/pcores/" + lib_name + " -name '*.vhd' > " + xst_path + "/temp.dat")
    temp_file_handle = open(xst_path + "/temp.dat") ## problem area
    while 1:
        temp_string = temp_file_handle.readline()
        if not temp_string:
            break
        else:
            temp_string = temp_string.replace('\n','')
            prj_file_handle.write('vhdl ' + lib_name + ' "' + temp_string + '"\n')
    temp_file_handle.close()
                
os.system("ls " + vhdl_path + "*.vhd > " + xst_path + "/vhdl_temp.dat")
vhdl_file_handle = open(xst_path + "vhdl_temp.dat")
while 1:
    vhdl_string = vhdl_file_handle.readline()
    if not vhdl_string:
        break
    else:
        vhdl_string = vhdl_string.replace('\n','')
        prj_file_handle.write('vhdl ' + core_name_w_ver + ' "' + vhdl_string + '"\n')

        
# Generate SCR file - DONE
print "Generating the SCR file @ "
print scr_path
print
os.system("touch " + scr_path)
scr_string = "run\n-opt_mode speed\n-netlist_hierarchy as_optimized\n-opt_level 1\n-p " + package_name + "\n-top " + core_name + "\n-ifmt MIXED\n-ifn " + core_name + ".prj\n-ofn " + core_name + ".ngc\n-hierarchy_separator /\n-iobuf NO\n-sd {../netlist}\n-work_lib " + core_name_w_ver + "\n"
scr_file_handle = open(scr_path, "w")
scr_file_handle.write(scr_string)


# Generate Makefile - DONE
print "Generating the Makefile @ "
print make_path
print
os.system("touch " + make_path)
make_file_handle = open(make_path, "w")
make_file_handle.write("PROJECT=" + core_name + "\n")
make_file_handle.write("COMPONENT=" + core_name + "\n")
make_file_handle.write("XST_PRJ=$(PROJECT).scr\n")
make_file_handle.write("XST_SRP=$(PROJECT).srp\nSRC=")
os.system("ls " + vhdl_path + "*.vhd > " + xst_path + "vhdl_temp.dat")
vhdl_temp_handle = open(xst_path + "vhdl_temp.dat", "r")
while 1:
    vhdl_temp_line_reading = vhdl_temp_handle.readline()
    if not vhdl_temp_line_reading:
        break
    else:
        vhdl_temp_line_reading =  vhdl_temp_line_reading.replace(present_working_dir,'..')
        vhdl_temp_line_reading =  vhdl_temp_line_reading.replace('\n','')
        make_file_handle.write(vhdl_temp_line_reading + " ")     

make_file_handle.write("\n\n$(COMPONENT).ngc: $(SRC) \n\txst -ifn $(XST_PRJ) -ofn $(XST_SRP)\n\nclean: \n\trm -rf $(COMPONENT).lso $(COMPONENT).ngc $(COMPONENT).ngc_xst.xrpt $(PROJECT).ngr $(XST_SRP) xlnx_auto_0.ise xlnx_auto_0_xdb xst *~")
make_file_handle.close()
os.system("chmod 755 " + xst_path + "Makefile")


# Instructions to user & cleanup
os.system("/bin/rm synthesis_xst/*vhd synthesis_xst/*dat")
print "Job Done !!"
print "Please check the 'synthesis_xst' folder if the files have been generated correctly. Only a rudimentary sanity check has been performed."
print "Specifically look if the device name is as per requirements."
print "Run 'make' to generate the synthesis reports."
print 
