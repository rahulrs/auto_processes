###########################################################
# VHDL modules synthesis estimate                         #
# Author : Rahul                                          #
###########################################################
# Sym-link or copy this file to the VHDL files level in   #
# the Modelsim directory                                  #
# Usage: python vhdl_synth_estimate.py <VHDL Top Level>   #
#                                                         #
###########################################################

import re, os, sys, commands

# Input a file containing VHDL modules & top-level VHDL module
if (len(sys.argv)!=2):
    print "Usage: python vhdl_synth_estimate.py <VHDL Top Level>"
    sys.exit(0)
else:
    vhdl_top_level = str(sys.argv[1])
    if vhdl_top_level.find(".vhd")>1:
        vhdl_top_level = vhdl_top_level.replace(".vhd","")
    print "VHDL Top Level = ",vhdl_top_level

# List all VHDL files into PRJ file
present_working_dir = commands.getoutput('pwd')
print "PWD = ", present_working_dir

# Set file paths
xst_path = present_working_dir + "/synthesis_xst/"
scr_path = present_working_dir + "/synthesis_xst/" + vhdl_top_level + ".scr"
prj_path = present_working_dir + "/synthesis_xst/" + vhdl_top_level + ".prj"
make_path = present_working_dir + "/synthesis_xst/Makefile"
temp_vhd_path = present_working_dir + "/synthesis_xst/temp.dat"


# Create a synthesis directory if it does not already exist
dir_status = os.path.isdir(xst_path)
if str(dir_status) == "False":
    print "Synthesis folder will be created"
else:
    print "Synthesis folder will be regenerated"
    os.system("/bin/rm -rf synthesis_xst")
os.mkdir(xst_path,0755)


# Populate VHDL dat file
vhdl_list = commands.getoutput('ls *.vhd > ./synthesis_xst/temp.dat')
vhdl_lines = open(temp_vhd_path)


# Create the PRJ file
prj_file_handle = open(prj_path, "w")
for line in vhdl_lines:
    str_line=str(line).strip()
    # Open each VHDL file and check if wait statements exists, ignore comment lines
    prj_vhdl_string = str(open(str_line).readlines())
    if int(prj_vhdl_string.find("wait for ")) > -1:
        continue
    else:
        prj_file_handle.write('vhdl work "' + present_working_dir + "/" + str_line + '"\n')
print "PRJ file generated..."


# Create the SCR file
scr_file_handle = open(scr_path,"w")
scr_string = "run\n-opt_mode speed\n-netlist_hierarchy as_optimized\n-opt_level 1\n-p xc4vfx60ff1152-11\n-top " + vhdl_top_level + "\n-ifmt MIXED\n-ifn " + vhdl_top_level + ".prj\n-ofn " + vhdl_top_level + ".ngc\n-hierarchy_separator /\n-iobuf NO\n-sd {../netlist}\n-work_lib work\n"
scr_file_handle.write(scr_string)
print "SCR file generated..."


# Create the Makefile
make_file_handle = open(make_path, "w")
make_file_handle.write("PROJECT=" + vhdl_top_level + "\n")
make_file_handle.write("COMPONENT=" + vhdl_top_level + "\n")
make_file_handle.write("XST_PRJ=$(PROJECT).scr\n")
make_file_handle.write("XST_SRP=$(PROJECT).srp\nSRC=")
vhdl_temp_handle = open(xst_path + "temp.dat", "r")
while 1:
    vhdl_temp_line_reading = vhdl_temp_handle.readline()
    if not vhdl_temp_line_reading:
        break
    else:
        vhdl_temp_line_reading =  vhdl_temp_line_reading.replace('\n','')
        make_file_handle.write("../" + vhdl_temp_line_reading + " ")
        
make_file_handle.write("\n\n$(COMPONENT).ngc: $(SRC) \n\txst -ifn $(XST_PRJ) -ofn $(XST_SRP)\n\nclean: \n\trm -rf $(COMPONENT).lso $(COMPONENT).ngc $(COMPONENT).ngc_xst.xrpt $(PROJECT).ngr $(XST_SRP) xlnx_auto_0.ise xlnx_auto_0_xdb $(COMPONENT)_vhdl.prj xst *~")
make_file_handle.close()
os.system("chmod 755 " + xst_path + "Makefile")
print "Makefile generated..."

os.system("/bin/rm -rf ./synthesis_xst/temp.dat")

print "Fin !"
