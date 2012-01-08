all: clean comp run

comp:
	vlib work
	vcom memory.vhd
	vlog tb.sv

run:
	vsim work.tb -do wave.do

clean:
	rm -rf work/