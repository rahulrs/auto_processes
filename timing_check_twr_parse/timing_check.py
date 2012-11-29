#####################################################################
# Author: Rahul
# Timing check output parser
# Conduct timing check
# 
# RUN this file in the 'implementation' folder
# 
# Operation
# - Sanity check
# - Run "trce -v -o timing.twr system.ncd system.pcf"
# - Parse the output file 'TWR' and find "timing errors"
# --- Dump output to parse
# --- Rename as 'twr.parsed'
# - Return to MHS level
#
#####################################################################

import os, re, commands, sys

# Check if MHS file exists
if (os.path.exists("system.ncd") and os.path.exists("system.pcf")):
    print "Sanity check complete... script will continue..."
else:
    print "Either NCD or PCF file was not found !"
    sys.exit(0)

# Run timing check file
os.system("trce -v -o timing.twr system.ncd system.pcf -tsi timing.tsi")

# Read the TWR file
twr_file_handle = open("timing.twr", "r")

# Create a parsed TWR file handle
parsed_twr_file_handle = open("parsed_timing.twr","w")

# Start parsing
# Store paragraph from line0 to first "====="
# Print to parsed file
# Find next "==============" and store to paragraph
# IF <non zero> "timing errors" is found, dump paragraph to output
# Run last two commands to end
first_instance = 0
paragraph = ""

# Print the entire first warnings block
for line in twr_file_handle:
    if(first_instance == 0):
        paragraph = paragraph + line
    if line.startswith("====================="):
        # Parse the paragraph block
        first_instance = 1
        parsed_twr_file_handle.write(paragraph)
        break

paragraph = ""
# Get paragraph by paragraph to target string
for line in twr_file_handle:
    paragraph = paragraph + line
    if line.startswith("====================="):
        # Start parsing paragraph, if "0 timing error" is found, drop paragraph
        if(paragraph.find("0 timing error") != -1):
            paragraph = ""
        else:
            parsed_twr_file_handle.write(paragraph)
            paragraph = ""                

# Job done
print "Done... see parsed_timing.twr"

       
