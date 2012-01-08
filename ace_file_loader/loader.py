import re, os, sys, commands, time

# Check machine if FSC will work
if commands.getoutput('uname -n') != "marge":
    print "FSC cannot be run here !!\n"
    sys.exit(0)

# Get user name
username = commands.getoutput('echo $USER')

# Get timestamp
timestamp = commands.getoutput('date')

# Get the correct options
if (len(sys.argv)>2):
    node_name = str(sys.argv[1])
    slot_num = str(sys.argv[2])
    ace_file_path = str(sys.argv[3])
    print "Node name = ",node_name
    print "Slot no.  = ",slot_num
    print "ACE path  = ",ace_file_path
else:
    print "Usage: python loader.py <node name> <slot number> <ace file path>\n"
    sys.exit(0)

# See if board belongs to $USER
if int(commands.getoutput('fsc list|grep ' + node_name).find(username)) > 1:
    print "All is well, script will continue !!\n"
else:
    print node_name, "has not been requested by", username, "...exiting !!\n"
    sys.exit(0)

# md5sum
print commands.getoutput('md5sum ' + ace_file_path)

# Restart board
print "Restarting..."
command_op = commands.getoutput('fsc down ' + node_name)
time.sleep(5)
command_op = commands.getoutput('fsc up ' + node_name)
time.sleep(55)

# Upload file
print "Uploading..."
command_op = commands.getoutput('fsc upload ' + node_name + ' ' + slot_num + ' ' + ace_file_path + ' "' + timestamp + '"')
time.sleep(5)

# Select Slot
print "Selecting..."
command_op = commands.getoutput('fsc select ' + node_name + ' ' + slot_num)

# Boot from slot
print "Rebooting", node_name, "..."
command_op = commands.getoutput('fsc boot ' + node_name)

print "Job done !!\n"
