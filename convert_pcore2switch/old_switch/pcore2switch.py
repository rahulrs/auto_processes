########################################################################
# CONVERT AN EMPTY PCORE TO A SWITCH [BETA]                            #                   
# Author : Rahul R Sharma                                              #
#                                                                      #
# DESCRIPTION:                                                         # 
# Convert an empty pcore to a switch: Use 'createip' to create a pcore #
# with just one register and run this core to build an n-port switch   #
# out of it. Then run this script at the level where you find the      #
# 'devl', 'data', 'hdl' etc. This will fill in all the required code   #
# in the correct places.                                               #
#                                                                      #
# LIMITATIONS:                                                         #
#                                                                      #
# USAGE: python pcore2switch.py                                        #
#                                                                      #
########################################################################

import os, re, sys, commands

# PWD fix
pwd = commands.getoutput("pwd")
print
print "PWD = ", pwd
print


# Backup existing pcore to a 'backup' directory
backup_status = os.path.isdir(pwd + "/../backup/")
if str(backup_status) == "True":
    print "Backup directory already exists..."
else:
    os.mkdir(pwd + "/../backup/",0755)
os.system("cp -r " + pwd + " ../backup/")
print "Backup completed !!"
print


# Record <core_name> from MPD file (check for line starting with BEGIN
core_name_filter_cmd = "cat " + pwd + "/data/*mpd | grep BEGIN"
core_name_filter_output = commands.getoutput(core_name_filter_cmd)
list1 = []
for token1 in core_name_filter_output.split(" "):
    list1.append(token1)
core_name = list1[1]
print "Core name is recorded as: ", core_name
print

# Record full core name with version number
list2 = []
for token2 in pwd.split("/"):
    list2.append(token2)
core_name_w_ver = list2[len(list2)-1]
print "Full core name (with version number is recorded as:", core_name_w_ver
print
        

# Check for existing files and place file handles on them (IPIC, UL, MPD)
mpd_file_path = commands.getoutput("find " + pwd + " -name *.mpd")
ul_file_path = pwd + "/hdl/vhdl/user_logic.vhd"
ipic_file_path = pwd + "/hdl/vhdl/" + core_name + ".vhd"
pao_file_path = commands.getoutput("find " + pwd + " -name *.pao")

print "MPD      = ",mpd_file_path,"\n"
print "PAO      = ",pao_file_path,"\n"
print "IPIC-VHD = ",ipic_file_path,"\n"

# Load the Templates path
templates_path = "/home/rsharm14/auto_processes/convert_pcore2switch/templates/"
airen_common_path = pwd + "/../airen_common.vhd"

### Configure airen_common.vhd and copy to "<PWD>/../"
print "##########################################################"
print
K_ARY        = input("Enter no. of nodes in a direction [K_ARY] : ")
K_WIDTH      = input("Enter no. of bits per direction [K_WIDTH] : ")
D_CUBE       = input("Enter no. of dimensions [D_CUBE]          : ")
RADIX        = input("Enter no. of ports in crossbar [RADIX]    : ")
SW_SEL_WIDTH = input("Enter no. of bits/crossbar [SW_SEL_WIDTH] : ")

temp_string = open("/home/rsharm14/auto_processes/convert_pcore2switch/templates/airen_common.vhd").read()
temp_string = temp_string.replace("$K_ARY",str(K_ARY))
temp_string = temp_string.replace("$K_WIDTH",str(K_WIDTH))
temp_string = temp_string.replace("$D_CUBE",str(D_CUBE))
temp_string = temp_string.replace("$RADIX",str(RADIX))
temp_string = temp_string.replace("$R_WIDTH",str(SW_SEL_WIDTH))
airen_common_handle = open(airen_common_path,"w")
airen_common_handle.write(temp_string)
print "airen_common.vhd configured...\n"
print "##########################################################\n"

# Copy airen_common.vhd and symbolic link the other blocks
os.system("cp /home/rsharm14/repository/hw/router/old/direction.vhd " + pwd + "/hdl/vhdl/direction.vhd")
os.system("cp /home/rsharm14/repository/hw/router/old/ll_switch.vhd " + pwd + "/hdl/vhdl/ll_switch.vhd")
os.system("cp /home/rsharm14/repository/hw/router/old/output_port_ctlr.vhd " + pwd + "/hdl/vhdl/output_port_ctlr.vhd")
os.system("cp /home/rsharm14/repository/hw/router/old/routing_module.vhd " + pwd + "/hdl/vhdl/routing_module.vhd")
os.system("cp /home/rsharm14/repository/hw/router/old/switch_ctlr.vhd " + pwd + "/hdl/vhdl/switch_ctlr.vhd")
os.system("ln -s " + pwd + "/../airen_common.vhd " + pwd + "/hdl/vhdl/airen_common.vhd")

# USER LOGIC fix
print "Replacing user_logic.vhd..."
os.system("cp " + templates_path + "/user_logic.vhd " + ul_file_path)
print

os.mkdir(pwd + "/temp/",0755)

### Generate IPIC-VHD code
# IPIC entity port generator
ipic_entity_port_handle = open(pwd + "/temp/ipic_entity_port.gen", "w")
ipic_entity_port_handle.write("-- Router signals\n")
ipic_entity_port_handle.write("router_clk :  in  std_logic;\n")
ipic_entity_port_handle.write("router_rst : out std_logic;\n")
temp_string = open(templates_path + "/template_ipic_entity.dat","r").read()
for iter in range(0, RADIX):
    ipic_entity_port_handle.write(temp_string.replace("$NUM", str(iter)))
ipic_entity_port_handle.close()

# IPIC Architecture signals map
ipic_arch_handle = open(pwd + "/temp/ipic_arch.gen","w")
temp_string = open(templates_path + "template_ipic_arch.dat","r").read()
for iter in range(0, RADIX):
    ipic_arch_handle.write(temp_string.replace("$NUM", str(iter)))
ipic_arch_handle.close()
print "IPIC inserts have been generated...\n"

### IPIC fix - BAD-ASS ALPHA CODE - might break
os.system("cp " + ipic_file_path + " " + pwd + "/temp/ipic.txt")
ipic_temp_handle = open(pwd + "/temp/ipic.txt","r")
ipic_out_handle = open(ipic_file_path,"w")
ipic_temp_lines = ipic_temp_handle.readlines()
for ipic_line in ipic_temp_lines:
    ipic_string = str(ipic_line).strip()
    if int(ipic_string.find("ADD USER PORTS BELOW THIS LINE")) > 0:
        temp_string = open(pwd + "/temp/ipic_entity_port.gen").read()
        ipic_out_handle.write(temp_string)
    elif ipic_string == "begin":
        temp_string = open(templates_path + "template_ipic_arch_decl.dat").read()
        ipic_out_handle.write(temp_string)
        ipic_out_handle.write("\nbegin\n")
    elif ipic_string == "end IMP;":
        temp_string = open(templates_path + "template_ipic_arch.dat").read()
        for iter in range(0, RADIX):            
            ipic_out_handle.write(temp_string.replace("$NUM", str(iter)))
        ipic_out_handle.write("\nend IMP;\n")
    elif ipic_string == "--USER ports mapped here":
        temp_string = open(templates_path + "template_ipic_arch_portmap.dat").read()
        ipic_out_handle.write(temp_string)
        ipic_out_handle.write("\n")
    elif ipic_string == "use " + core_name_w_ver + ".user_logic;":
        print "line found"
        ipic_out_handle.write(str(ipic_line))
        ipic_out_handle.write("\nuse " + core_name_w_ver + ".airen_common.all;\n")
    else:
        ipic_out_handle.write(str(ipic_line))
print "IPIC-VHD has been fixed...\n"

### MPD code generate
mpd_gen_handle = open(pwd + "/temp/mpd_code.gen","w")
mpd_gen_handle.write("\n## Router Signals")
mpd_gen_handle.write("\nPORT router_clk       = "", DIR = I")
mpd_gen_handle.write("\nPORT router_rst       = "", DIR = O\n")
temp_string = open(templates_path + "/template_mpd.dat","r").read()
for iter in range(0,RADIX):
    mpd_gen_handle.write(temp_string.replace("$NUM", str(iter)))
mpd_gen_handle.close()
print "MPD code generated ...\n"


### MPD fix
os.system("cp " + mpd_file_path + " " + pwd + "/temp/mpd.txt")
temp_mpd_file_handle = open(pwd + "/temp/mpd.txt","r")
temp_mpd_lines = temp_mpd_file_handle.readlines()
mpd_file_handle = open(mpd_file_path,"w")
mpd_addenda = open(pwd + "/temp/mpd_code.gen").read()

for mpd_line in temp_mpd_lines:
    if str(mpd_line).strip() == "END":
        mpd_file_handle.write(mpd_addenda)
        break
    else:
        mpd_file_handle.write(mpd_line)
mpd_file_handle.write("END\n")
print "MPD file fixed ...\n"


### PAO fix
os.system("cp " + pao_file_path + " " + pwd + "/temp/pao.txt")
temp_pao_file_handle = open(pwd + "/temp/pao.txt","r")
temp_pao_lines = temp_pao_file_handle.readlines()
pao_file_handle = open(pao_file_path,"w")

for pao_line in temp_pao_lines:
    if (int(str(pao_line).find(core_name_w_ver)) > 0):
        continue
    else:
        pao_file_handle.write(pao_line)

os.system("ls " + pwd + "/hdl/vhdl/ > " + pwd + "/temp/vhdl.temp")
vhdl_temp_handle = open(pwd + "/temp/vhdl.temp")
for line in vhdl_temp_handle.readlines():
    vhdl_module_name = str(line).replace(".vhd","")
    vhdl_module_name = vhdl_module_name.replace("\n","")
    if (vhdl_module_name == core_name) or (vhdl_module_name == "user_logic"):
        continue
    else:
        pao_file_handle.write("lib " + core_name_w_ver + " " + vhdl_module_name + " vhdl\n")
pao_file_handle.write("lib " + core_name_w_ver + " user_logic vhdl\n")
pao_file_handle.write("lib " + core_name_w_ver + " " + core_name + " vhdl\n")
print "PAO file fixed ...\n"


# Instructions to user & cleanup
#os.system("/bin/rm -rf " + pwd + "/temp/")
print "Please check airen_common.vhd for correctness."
print "Check for parenthesis in the VHDL files."
print "Check IPIC, UL, PAO and MPD files for problems..."
print "Auto-align the VHDL code using Ctrl-C, Ctrl-B in EMACS."
print "Fin !!"
