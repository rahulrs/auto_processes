# To Run the file 
# xmd -tcl <this_file>

# Clean existing locks
# xclean_cablelock

# Program the board with bitstream
fpga -f download.bit

# Connect to processor
connect mb mdm -cable type xilinx_platformusb frequency 12000000

# Stop the processor
stop

# Reset the processor
rst

# Download the ELF
# dow u-boot
dow linux.elf

# Allow free-run
run 

