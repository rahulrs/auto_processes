########################################################################
# ADD AURORA CHANNELS TO A SWITCH [INCOMPLETE]                         #                     
# Author : Rahul R Sharma                                              #
#                                                                      #
# DESCRIPTION:                                                         #
#                                                                      #
# This script will ask you how many aurora channels exist in your      #
# system and update the MHS and UCF files accordingly.                 #
#                                                                      #
# LIMITATIONS:                                                         #
# - Not tested for multi-channel aurora                                #
# - Will not support if there is more than one crossbar per chip       #
#                                                                      #
# USAGE:                                                               #
# Create the crossbar core first using the pcore2switch.py script      #
# Copy this file into the system.mhs level of the project              #
# Run: python add_aurora2switch.py <crossbar_pcore> <number_dims>      #     
#                                                                      #
########################################################################

import os, re, sys, commands

if (len(sys.argv)>1):
    crossbar_name = str(sys.argv[1])
    num_dim = int(sys.argv[2])
    print "Crossbar name entered as ", crossbar_name
    print "No. of dimensions entered as ", num_dim
else:
    print "Usage: python add_aurora2switch.py <crossbar_pcore> <number_dims>\n"
    sys.exit(0)
    
### PWD fix
pwd = commands.getoutput("pwd")
print
print "PWD = ", pwd, "\n"


# Backup required files to temp_aurora
backup_status = os.path.isdir(pwd + "/aurora_backup/")
if str(backup_status) == "True":
    print "Backup directory already exists..."
else:
    os.mkdir(pwd + "/aurora_backup/",0755)
backup_dir = pwd + "/aurora_backup/"
print "Backup completed !!\n"
templates_dir = "/home/rsharm14/auto_processes/add_aurora2switch/templates/"


### Backup MHS and UCF files
ucf_file_path = pwd + "/data/system.ucf"
print "UCF = ", ucf_file_path, "\n"
os.system("cp " + ucf_file_path + " " + backup_dir + "/ucf.bak")

mhs_file_path = pwd + "/system.mhs"
print "MHS = ", mhs_file_path, "\n"
os.system("cp " + mhs_file_path + " " + backup_dir + "/mhs.bak")


### Check number of dimensions for sanity
if num_dim < 1 or num_dim > 3:
    print num_dim," dimensions are not possible !!"
    print "Script exiting..."
    sys.exit(0)
else:
    print 2*num_dim, " aurora ports will be connected to the bus !!\n"
num_aurora = 2*num_dim

### Check core name for sanity
if int((open(mhs_file_path).read()).find("BEGIN " + crossbar_name + "\n")) > 0:
    print "Core name found in system.mhs, script will proceed !!\n"
else:
    print "Crossbar not found... script exiting !!\n"

### Copy required cores
os.system("cp -r /home/rsharm14/repository/hw/pcores/verified/gt11clk_buf_v1_00_a/ " + pwd + "/pcores/")
os.system("cp -r /home/rsharm14/repository/hw/pcores/verified/aurora_ll_w_fifo_32b_4Gbps_single_v1_00_a/ " + pwd + "/pcores/")
print "Pcores copied from repository !!\n"


### UCF file modification
# Open UCF file
target_ucf_file = open(backup_dir + "/target_ucf.txt","w")
# gt11_clk_buf additions
temp_string = open(backup_dir + "/ucf.bak").read()
target_ucf_file.write(temp_string)
target_ucf_file.write(open(templates_dir + "/template_gt11_ucf.dat").read())
# Aurora channels additions
target_ucf_file.write("\n## User Clock Constraint\n")
for iter in range(0, num_aurora):
    inst_name = "aurora_link_layer_" + str(iter)
    target_ucf_file.write("NET " + inst_name + "/" + inst_name + "/aurora_clk PERIOD = 10.0 ns;\n")
target_ucf_file.write("\n\n")
ucf_lines = open(templates_dir + "/template_aurora_ucf.dat").readlines()
iter = 0
for line in ucf_lines:
    if iter < 2*num_aurora:
        target_ucf_file.write(str(line))
        iter = iter + 1
print "system UCF file fixed !!\n"


### MHS file modification
# Open MHS file
target_mhs_file = open(backup_dir + "/target_mhs.txt","w")
mhs_lines = open(backup_dir + "/mhs.bak")

begin_flag = 0
crossbar_flag = 0
mgt_flag = 0
clock_flag = 0
# External pin additions
for line in mhs_lines:
    str_line = str(line).strip()
    if int((str(line).strip()).find("BEGIN")) > -1 and begin_flag == 0:
#        target_mhs_file.write("## Clock and Reset")                                                           
#        target_mhs_file.write("\n PORT sys_clk_pin = dcm_clk_s, DIR = I, SIGIS = CLK, CLK_FREQ = 100000000") 
#        target_mhs_file.write("\n PORT sys_rst_pin = sys_rst_s, DIR = I, RST_POLARITY = 0, SIGIS = RST")     
        target_mhs_file.write("\n## AURORA Pins")                                                           
        target_mhs_file.write("\n PORT ref_clk_right_p_pin = ref_clk_right_p, DIR = I, SIGIS = CLK")         
        target_mhs_file.write("\n PORT ref_clk_right_n_pin = ref_clk_right_n, DIR = I, SIGIS = CLK")
        target_mhs_file.write("\n\n")
        # Aurora additions
        temp_string = open(templates_dir + "/template_aurora_mhs_pins.dat").read()    
        for iter in range(0, num_aurora):
            target_mhs_file.write(temp_string.replace("$NUM",str(iter)))
        target_mhs_file.write("\n" + str(line))
        begin_flag = 1
    elif str_line == "BEGIN " + crossbar_name:
        target_mhs_file.write(str(line))
        crossbar_flag = 1        
    elif crossbar_flag == 1 and str_line == "END":
#        target_mhs_file.write(" PORT router_clk = clk_100_0000MHzDCM0\n")
#        target_mhs_file.write(" PORT router_rst = router_rst\n")
        temp_string = open(templates_dir + "/template_aurora_mhs_ports.dat").read()
        for iter in range(0, num_aurora):
            target_mhs_file.write(temp_string.replace("$NUM",str(iter)))
        crossbar_flag = 0
        target_mhs_file.write(str(line))
    elif str_line == "BEGIN mgt_protector":
        target_mhs_file.write(str(line))
        mgt_flag = 1
    elif mgt_flag == 1 and num_dim == 2 and ((int(str_line.find("C_USE_5")) > -1 or int(str_line.find("C_USE_7")) > -1)):
        target_mhs_file.write(str(line).replace("1", "0"))        # Warning - dangerous
    elif mgt_flag == 1 and num_dim == 2 and ((int(str_line.find("C_LOC_5_AB")) > -1 or int(str_line.find("C_LOC_7_AB")) > -1)):
        target_mhs_file.write("#")
        target_mhs_file.write(str(line))
    elif mgt_flag==1 and num_dim==3 and ( int(str_line.find("C_USE_5"))>-1 or int(str_line.find("C_USE_7"))>-1 or int(str_line.find("C_USE_6"))>-1 ):
        target_mhs_file.write(str(line).replace("1", "0"))        # Warning - dangerous
    elif mgt_flag==1 and num_dim==3 and ((int(str_line.find("C_LOC_5_AB"))>-1 or int(str_line.find("C_LOC_7_AB"))>-1 or int(str_line.find("C_LOC_6_AB"))>-1)):
        target_mhs_file.write("#")
        target_mhs_file.write(str(line))
    elif mgt_flag == 1 and str_line == "END":
        mgt_flag = 0
        target_mhs_file.write(str(line))
    elif str_line == "BEGIN clock_generator":
        clock_flag = 1
        target_mhs_file.write(str(line))
    elif clock_flag == 1 and str_line == "END":
        clock_flag = 0
        target_mhs_file.write(" PARAMETER C_CLKOUT7_FREQ = 100000000 \n")
        target_mhs_file.write(" PARAMETER C_CLKOUT7_PHASE = 0        \n")
        target_mhs_file.write(" PARAMETER C_CLKOUT7_GROUP = DCM0     \n")
        target_mhs_file.write(" PARAMETER C_CLKOUT7_BUF = TRUE       \n")
        target_mhs_file.write(" PORT CLKOUT7 = init_clk\n")
        target_mhs_file.write(str(line))
    else:
        target_mhs_file.write(str(line))

# Aurora Channel additions
temp_string = open(templates_dir + "/template_aurora_mhs_instance.dat").read()
for iter in range(0, num_aurora):
    print "aurora_link_layer connected"
    target_mhs_file.write(temp_string.replace("$NUM",str(iter)))

# gt11_blk_buf addition
target_mhs_file.write(open(templates_dir + "/template_gt11_mhs.dat").read())
print "gt11_clk_buf added to project !!"

# Close opened files
target_ucf_file.close()
target_mhs_file.close()

os.system("cp " + backup_dir + "/target_mhs.txt " + mhs_file_path)
os.system("cp " + backup_dir + "/target_ucf.txt " + ucf_file_path)

### Job done
print "Fin !!\n"
