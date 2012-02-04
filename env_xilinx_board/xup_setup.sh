#export LD_PRELOAD=/usr/local/lib/libftdi.so:/install_tmp/usbjtag/libusb-driver.so
export LD_PRELOAD=/install_temp/usbjtag/libusb-driver.so
#export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/user/local/lib
export XILINX_USB_DEV=$1
echo "Using JTAG on $1"
