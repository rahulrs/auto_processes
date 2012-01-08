import re
import os

os.system("pwd")
os.system("rm -rf ace")
os.system("mkdir ace")
os.system("make init_bram")
os.system("cp implementation/download.bit ./ace")
os.system("cp app/executable.elf ./ace")
os.system("cd ace")
os.system("xmd -tcl $XILINX_EDK/data/xmd/genace.tcl -jprog -hw download.bit -ace sw_hw_ace.ace -board ml410")
os.system("chmod 777 *.ace")
os.system("md5sum *.ace")
os.system("cd ..")
print "***** Done !! *****"
