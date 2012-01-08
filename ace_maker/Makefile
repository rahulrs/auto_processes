ACE=system.ace
BIT=../implementation/download.bit
ELF0=../app0/executable.elf
#ELF1=../app1/executable.elf

$(ACE): $(BIT) $(ELF0) # List other ELFs here (multi-processor systems)
	xmd -tcl $(XILINX_EDK)/data/xmd/genace.tcl -opt opt_file.opt

clean:
	rm -rf *.ace *.scr *.svg *.svf *.log *~
