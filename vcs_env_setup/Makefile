# VCS Run template

# VCD file name
WAVE_VCD=wave.vcd

# Top level module
TOP_MODULE=tb

# VHDL options
VHD_OPT = -nc -full64
VHD_OPT+= -work work
VHD_OPT+= -verbose

# [System]Verilog options
VLOG_OPT = -nc -full64
VLOG_OPT+= +librescan -work work

# VCS options
VCS_OPT = -nc -full64
VCS_OPT+= +vhdllib+work  
VCS_OPT+= -marchive 100 -l comp.log
VCS_OPT+= +vcs+dumpvars+$(WAVE_VCD)
#VCS_OPT+= -LDFLAGS="-m64"
#VCS_OPT+= -P $(VCS_HOME)/include/hdl_xmr.tab -debug_pp


all: clean comp run wave

clean:
	rm -rf *.vcd *.vpd
	rm -rf work *~

run:
	./simv -l run.log

wave:
	dve -vpd wave.vpd

comp:
	vhdlan $(VHD_OPT) # VHDL files here
	vlogan $(VLOG_OPT) # Vlog files here
	vcs $(VCS_OPT) $(TOP_MODULE)

