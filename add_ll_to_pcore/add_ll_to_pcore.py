######################################################################
# Script to add locallink RX and TX ports to a pcore
# Author : Rahul
######################################################################
# Process followed
# - Add ll_type RX/TX ports to user_logic.vhd and accessible
# constituent signals
# - Create std_logic and 32 bit std_logic_vector ports into the IPIF
# - Edit MPD file suitably
######################################################################
# Usage: python add_ll_to_pcore.py <pcore_name_w_ver>
######################################################################

import os, re, sys, commands

# Check for correct input
if (len(sys.argv)!=2):
    print "Usage: python add_ll_to_pcore.py <pcore_name_w_ver>"
    sys.exit(0)
else:
    pcore_name_w_ver = str(sys.argv[1])
    pcore_name_w_ver = pcore_name_w_ver.replace("/","")
    pwd = commands.getoutput("pwd")
    print "PWD        = ",pwd
    print "Pcore name = ", pcore_name_w_ver

# Record MPD path name
mpd_path = commands.getoutput("find " + pcore_name_w_ver + " -name *.mpd")
mpd_temp_path = pwd + "/" + pcore_name_w_ver + "/mpd.txt"
print "MPD        = ", mpd_path
mpd_read_handle = open(mpd_path, "r")
mpd_write_handle = open(mpd_temp_path,"w")
mpd_addenda_str = open("/home/rsharm14/auto_processes/add_ll_to_pcore/templates/template_mpd.dat").read()

# Edit MPD
mpd_lines_read = mpd_read_handle.readlines()
for mpd_line in mpd_lines_read:
    if (int(str(mpd_line).find("BEGIN")) > -1):
        top_level_vhd = mpd_line.replace("\n","").replace("BEGIN","").strip()
        mpd_write_handle.write(mpd_line)
    elif (int(str(mpd_line).find("END")) > -1):
        mpd_write_handle.write(mpd_addenda_str)
        mpd_write_handle.write(mpd_line)
    else:
        mpd_write_handle.write(mpd_line)
print "MPD file edited !"

# IPIF-VHD path names
ipif_path = commands.getoutput("find " + pcore_name_w_ver + " -name " + top_level_vhd + ".vhd")
ipif_read_handle = open(ipif_path,"r")
ipif_temp_path = pwd + "/" + pcore_name_w_ver + "/ipif.txt"
ipif_write_handle = open(ipif_temp_path,"w")

# Edit IPIF-VHD
ipif_lines_read = ipif_read_handle.readlines()
for ipif_line in ipif_lines_read:
    ipif_line_str = str(ipif_line)
    if int(ipif_line.find("ADD USER PORTS BELOW THIS LINE")) > 0:
        temp1_string = open("/home/rsharm14/auto_processes/add_ll_to_pcore/templates/template_ipic_entity.dat").read()
        ipif_write_handle.write(temp1_string)
    elif ipif_line_str.strip() == "begin":
        temp2_string = open("/home/rsharm14/auto_processes/add_ll_to_pcore/templates/template_ipic_arch_decl.dat").read()
        ipif_write_handle.write(temp2_string)
        ipif_write_handle.write(ipif_line_str)
    elif ipif_line_str.strip() == "end IMP;":
        temp3_string = open("/home/rsharm14/auto_processes/add_ll_to_pcore/templates/template_ipic_arch.dat").read()
        ipif_write_handle.write(temp3_string)
        ipif_write_handle.write(ipif_line_str)
    elif ipif_line_str.strip() == "--USER ports mapped here":
        temp4_string = open("/home/rsharm14/auto_processes/add_ll_to_pcore/templates/template_ipic_arch_portmap.dat").read()
        ipif_write_handle.write(temp4_string)
        ipif_write_handle.write(ipif_line_str)
    elif ipif_line_str.strip() == "use " + pcore_name_w_ver + ".user_logic;":
        ipif_write_handle.write("use " + pcore_name_w_ver + ".airen_common.all;\n")
        ipif_write_handle.write(ipif_line_str)
    else:
        ipif_write_handle.write(ipif_line_str)
print "IPIF VHD file edited !"

# UL VHD paths
ul_path = commands.getoutput("find " + pcore_name_w_ver + " -name user_logic.vhd")
ul_read_handle = open(ul_path,"r")
ul_temp_path = pwd + "/" + pcore_name_w_ver + "/ul.txt"
ul_write_handle = open(ul_temp_path,"w")

# UL fix 
ul_lines_read = ul_read_handle.readlines()
for ul_line in ul_lines_read:
    ul_line_str = str(ul_line)
    if ul_line_str.startswith("entity") == True:
        ul_write_handle.write("use work.airen_common.all;\n")
        ul_write_handle.write(ul_line)
    elif int(ul_line_str.find("ADD USER PORTS BELOW THIS LINE")) > 0:
        ul_temp_string = open("/home/rsharm14/auto_processes/add_ll_to_pcore/templates/template_ul_entity.dat").read()
        ul_write_handle.write(ul_temp_string)
        ul_write_handle.write(ul_line)
    else:
        ul_write_handle.write(ul_line)
print "User Logic edited !"

# Move generated files to respective locations
os.system("mv " + mpd_temp_path + " " + mpd_path)
os.system("mv " + ipif_temp_path + " " + ipif_path)
os.system("mv " + ul_temp_path + " " + ul_path)

# Closure
print "Copy the airen_common.vhd into the ./hdl/vhdl/ directory if not done so yet !"
print "Done !"
