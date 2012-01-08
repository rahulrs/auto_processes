all: clean comp run

comp:
	export VCS_ARCH_OVERRIDE="linux"
	mkdir -p work
	vhdlan -nc -full64 reg_file_pkg.vhd
	vhdlan -nc -full64 reg_file.vhd
	vhdlan -nc -full64 reg_file_wrapper.vhd
	vlogan -nc -full64 -sverilog +librescan -work work tb.sv
	vcs -nc -full64 +vhdllib+work tb

run:


clean:
	rm -rf work *~
	rm -rf simv* csrc/ DVEfiles/
