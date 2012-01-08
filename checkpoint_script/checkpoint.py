##########################################################################
# Checkpoint script
# Author: Rahul
#
# Purpose: Backup contents of $(HOME) to hard-drive, runs every weekly on
# Sunday, 2 am
#
# Method:
# - Record checkpoint name as datestamp
# - Create a directory in HDD by datestamp and copy the entire
# - Log the series of events
# - Email log to UNCC mail
#
# HDD encrypted ??
# To be run on 'ray'
#
##########################################################################

import os, re, sys, commands, smtplib

LOG_FILE = "homer_checkpoint.log"

# Open a log file
log_handle = open(LOG_FILE,"w")

# Generate datestamp for backup directory name
datestamp = commands.getoutput("date")
date_op = datestamp
log_handle.write("Datestamp       : " + date_op + "\n")
datestamp = datestamp.replace(":","_")
datestamp = datestamp.replace(" ","_")

# Backup info
backup_src = "/home/rsharm14/ "

# Location of backup HDD
hdd_loc = "/media/usb_checkpoint_hdd/"

# Location of checkpoint inside backup HDD
backup_dst = hdd_loc + datestamp

# Create a backup location on disc (IMP)
#os.system("mkdir " + backup_dst) 
log_handle.write("Backup location : " + backup_dst + "\n")

# Run the backup command & write to log file
start_time = commands.getoutput("date")
log_handle.write("Backup started at " + start_time + "\n")

# Copy command (IMP)
#os.system("cp -r " + backup_src + backup_dst)

# Signal end of backup & write to log file
end_time = commands.getoutput("date")
log_handle.write("Backup Ended at " + end_time + "\n")

# Close the log file
log_handle.close()

# Email log file to User
SERVER = "localhost"

FROM = "rsharm14@uncc.edu"
TO = ["rsharm14@uncc.edu"] # must be a list

SUBJECT = "Weekly RCS account checkpoint completed"

TEXT = commands.getoutput("cat " + LOG_FILE)

# Prepare actual message
message = """\
From: %s
To: %s
Subject: %s

%s
""" % (FROM, ", ".join(TO), SUBJECT, TEXT)

# Send the mail
server = smtplib.SMTP(SERVER)
server.sendmail(FROM, TO, message)
server.quit()

# Delete the checkpoint log
os.system("rm " + LOG_FILE)
                              
