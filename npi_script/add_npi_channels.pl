#!/usr/bin/perl
##################################################################################
## Author: Siddharth Taduri
## 06.10.2009
## add_npi_channels.pl
##################################################################################
## This script adds NPI bus interfaces, signals, port maps required by your core
## to use the CORE-DDR2-Native Port Interface
## 1. Modify the MPD file, i.e, add the NPI bus interface and ports to it.
## 2. Modify the PAO file, i.e, add the npi vhdl module.
## 3. Modify the core's top level entity, i.e, add the NPI ports to its entity, 
##    add any required signals, port map the user_logic and npi.vhd components
## 4. Modify the user_logic by adding the Read/Write FSM's, the registered signal 
##    process, editing the entity port declaration, and define any signals that 
##    are needed. I haven't included the FIFO's in this as their design may change
##    according to the application. Also, the slv_reg-npi interface is not included.
## 5. Lastly, copy the NPI.VHD file to the hdl/vhdl/ directory.
##################################################################################
##################################################################################



use File::Copy;
## Reading Command line arguments
$numArgs = $#ARGV + 1;
print "The core you wish to modify is $ARGV[0]\n";
chdir($ARGV[0]) || die"Could not navigate to the directory, make sure you are in the pcores directory within your XPS project\n";
$CORE_LIB = $ARGV[0];
system"pwd";

##Opening all the files that will be modified

## 1. Opening the MPD file
chdir("data/") || die"Could not navigate to the data folder\n";
system "pwd";
$MPD_NAME=<*.mpd>;     #Name of the MPD file
copy("$MPD_NAME", "$MPD_NAME.bak") || die"Could'nt make a backup of $MPD_NAME\n";
open(MPD,"<$MPD_NAME") || die"Could not open MPD file\n";
@mpd = <MPD>;
close(MPD);
#print @mpd;
$mpd = join("", @mpd);

## 2. Opening the PAO file
$PAO_NAME=<*.pao>;     #Name of the pao file
copy("$PAO_NAME", "$PAO_NAME.bak") || die"Could'nt make a backup of $PAO_NAME\n";
open(PAO,"<$PAO_NAME") || die"Could not open PAO file\n";
@pao = <PAO>;
close(PAO);
$pao = join("", @pao);
chdir("../");

## 3. Opening the Top level VHDL file
chdir("hdl/vhdl") || die"Could'nt navigate to the HDL directory\n";
system"pwd";
@CORE = split("_v", $CORE_LIB);
$CORE = @CORE[0];     ##Getting the name of the Top level entity
copy("$CORE.vhd", "$CORE.vhd.bak") || die"Could'nt make a backup of $CORE.vhd\n";
open(TOP,"<$CORE.vhd");
@top = <TOP>;
close(TOP);
$top = join("",@top);

## 4. Opening the User Logic file
copy("user_logic.vhd", "user_logic.vhd.bak") || die"Could'nt make a backup of user_logic.vhd\n";
open(ULOGIC, "<user_logic.vhd");
@ulogic = <ULOGIC>;
close(ULOGIC);
$ulogic = join("", @ulogic);
chdir("../../");


###################################################################################
## Constant Strings that will be inserted into the above files
###################################################################################
$Ch = 0; ## For now, this will change later depending upon the number of channels.
$OPTION="OPTION STYLE = MIX\n";
$BUS_INTERFACE="BUS_INTERFACE BUS = XIL_NPI_$Ch,   BUS_STD = XIL_NPI,     BUS_TYPE = INITIATOR\n";
$MPD_PORTS="
\#\# 200 MHz MPMC Clk
PORT MPMC_Clk                = \"\",                DIR = I\n

\#\# Native Port Interface PORTs
\# Port $Ch
PORT NPI_Addr_$Ch            = \"Addr\",              DIR = O, BUS = XIL_NPI_$Ch, VEC = [31:0], ENDIAN = LITTLE
PORT NPI_AddrReq_$Ch           = \"AddrReq\",           DIR = O, BUS = XIL_NPI_$Ch
PORT NPI_AddrAck_$Ch           = \"AddrAck\",           DIR = I, BUS = XIL_NPI_$Ch
PORT NPI_RNW_$Num_$Ch               = \"RNW\",               DIR = O, BUS = XIL_NPI_$Ch
PORT NPI_Size_$Ch              = \"Size\",              DIR = O, BUS = XIL_NPI_$Ch, VEC = [3:0],  ENDIAN = LITTLE
PORT NPI_WrFIFO_Data_$Ch       = \"WrFIFO_Data\",       DIR = O, BUS = XIL_NPI_$Ch, VEC = [63:0], ENDIAN = LITTLE
PORT NPI_WrFIFO_BE_$Ch         = \"WrFIFO_BE\",         DIR = O, BUS = XIL_NPI_$Ch, VEC = [7:0],  ENDIAN = LITTLE
PORT NPI_WrFIFO_Push_$Ch       = \"WrFIFO_Push\",       DIR = O, BUS = XIL_NPI_$Ch
PORT NPI_RdFIFO_Data_$Ch       = \"RdFIFO_Data\",       DIR = I, BUS = XIL_NPI_$Ch, VEC = [63:0], ENDIAN = LITTLE
PORT NPI_RdFIFO_Pop_$Ch        = \"RdFIFO_Pop\",        DIR = O, BUS = XIL_NPI_$Ch
PORT NPI_RdFIFO_RdWdAddr_$Ch   = \"RdFIFO_RdWdAddr\",   DIR = I, BUS = XIL_NPI_$Ch, VEC = [3:0],  ENDIAN = LITTLE
PORT NPI_WrFIFO_AlmostFull_$Ch = \"WrFIFO_AlmostFull\", DIR = I, BUS = XIL_NPI_$Ch
PORT NPI_WrFIFO_Flush_$Ch      = \"WrFIFO_Flush\",      DIR = O, BUS = XIL_NPI_$Ch
PORT NPI_WrFIFO_Empty_$Ch      = \"WrFIFO_Empty\",      DIR = I, BUS = XIL_NPI_$Ch
PORT NPI_RdFIFO_Empty_$Ch      = \"RdFIFO_Empty\",      DIR = I, BUS = XIL_NPI_$Ch
PORT NPI_RdFIFO_Flush_$Ch      = \"RdFIFO_Flush\",      DIR = O, BUS = XIL_NPI_$Ch
PORT NPI_RdModWr_$Ch           = \"RdModWr\",           DIR = O, BUS = XIL_NPI_$Ch
PORT NPI_InitDone_$Ch          = \"InitDone\",          DIR = I, BUS = XIL_NPI_$Ch
PORT NPI_RdFIFO_Latency_$Ch    = \"RdFIFO_Latency\",    DIR = I, BUS = XIL_NPI_$Ch, VEC = [1:0], ENDIAN = LITTLE

";

$TOP_LEVEL_PORTS = "
    --------------------------------------
    -- NPI_Ports
    --------------------------------------
    MPMC_Clk                : in std_logic;
    -- NPI Signals
    NPI_AddrAck_$Ch             : in  std_logic;
    NPI_WrFIFO_AlmostFull_$Ch   : in  std_logic;
    NPI_RdFIFO_Empty_$Ch        : in  std_logic;
    NPI_InitDone_$Ch            : in  std_logic;
    NPI_WrFIFO_Empty_$Ch        : in  std_logic;
    NPI_RdFIFO_Latency_$Ch      : in  std_logic_vector(1 downto 0);
    NPI_RdFIFO_RdWdAddr_$Ch     : in  std_logic_vector(3 downto 0);    
    NPI_RdFIFO_Data_$Ch         : in  std_logic_vector(63 downto 0);
    NPI_AddrReq_$Ch             : out std_logic;
    NPI_RNW_$Ch                 : out std_logic;
    NPI_WrFIFO_Push_$Ch         : out std_logic;
    NPI_RdFIFO_Pop_$Ch          : out std_logic;
    NPI_RdModWr_$Ch             : out std_logic; 
    NPI_WrFIFO_Flush_$Ch        : out std_logic;    
    NPI_RdFIFO_Flush_$Ch        : out std_logic;
    NPI_Size_$Ch                : out std_logic_vector(3 downto 0);
    NPI_WrFIFO_BE_$Ch           : out std_logic_vector(7 downto 0);    
    NPI_Addr_$Ch                : out std_logic_vector(31 downto 0);
    NPI_WrFIFO_Data_$Ch         : out std_logic_vector(63 downto 0);
";
$USER_LOGIC_PORTS = "
    MPMC_Clk            : in  std_logic;
    NPI_Reset_$Ch           : out std_logic;    
    -- NPI Signals
    data_to_mem_$Ch         : out std_logic_vector(0 to 63);
    data_to_mem_we_$Ch      : out std_logic;
    data_to_mem_re_$Ch      : in  std_logic;
    data_to_core_$Ch        : in  std_logic_vector(0 to 63);
    data_to_core_we_$Ch     : in  std_logic;    
    num_rd_bytes_$Ch        : out std_logic_vector(0 to 31);
    num_wr_bytes_$Ch        : out std_logic_vector(0 to 31);    
    init_rd_addr_$Ch        : out std_logic_vector(0 to 31);
    init_wr_addr_$Ch        : out std_logic_vector(0 to 31);    
    rd_req_start_$Ch        : out std_logic;
    wr_req_start_$Ch        : out std_logic;    
    rd_req_done_$Ch         : in  std_logic;
    wr_req_done_$Ch         : in  std_logic;
";
$USER_LOGIC_SIGNALS = "
  -----------------------------------------------------------------------------
  -- User Logic / NPI Interconnect Signals
  -----------------------------------------------------------------------------
  signal NPI_Reset_$Ch           : std_logic;
  signal data_to_mem_$Ch         : std_logic_vector(0 to 63);
  signal data_to_mem_we_$Ch      : std_logic;
  signal data_to_mem_re_$Ch      : std_logic;       
  signal data_to_core_$Ch        : std_logic_vector(0 to 63);        
  signal data_to_core_we_$Ch     : std_logic;    
  signal num_rd_bytes_$Ch        : std_logic_vector(0 to 31);
  signal num_wr_bytes_$Ch        : std_logic_vector(0 to 31);  
  signal init_rd_addr_$Ch        : std_logic_vector(0 to 31);
  signal init_wr_addr_$Ch        : std_logic_vector(0 to 31);  
  signal rd_req_start_$Ch        : std_logic;
  signal wr_req_start_$Ch        : std_logic;  
  signal rd_req_done_$Ch         : std_logic;
  signal wr_req_done_$Ch         : std_logic;
";

$USER_LOGIC_PORT_MAP = "
      MPMC_Clk            => mpmc_clk,
      NPI_Reset_$Ch           => NPI_Reset_$Ch,      
      data_to_mem_$Ch         => data_to_mem_$Ch,     
      data_to_mem_we_$Ch      => data_to_mem_we_$Ch,  
      data_to_mem_re_$Ch      => data_to_mem_re_$Ch,  
      data_to_core_$Ch        => data_to_core_$Ch,    
      data_to_core_we_$Ch     => data_to_core_we_$Ch, 
      num_rd_bytes_$Ch        => num_rd_bytes_$Ch,
      num_wr_bytes_$Ch        => num_wr_bytes_$Ch,             
      init_rd_addr_$Ch        => init_rd_addr_$Ch,
      init_wr_addr_$Ch        => init_wr_addr_$Ch,             
      rd_req_start_$Ch        => rd_req_start_$Ch,
      wr_req_start_$Ch        => wr_req_start_$Ch,             
      rd_req_done_$Ch         => rd_req_done_$Ch,
      wr_req_done_$Ch         => wr_req_done_$Ch,
";
$NPI_PORT_MAP = " 
  -----------------------------------------------------------------------------
  -- Instantiate Native Port Interface
  -----------------------------------------------------------------------------
  NPI_$Ch : entity $CORE_LIB.npi
    port map
    (
      -- MPMC 200 MHz Clock
      MPMC_Clk              => MPMC_Clk,
      NPI_Reset             => NPI_Reset_$Ch,
      -- Signals to/from User Logic
      data_to_mem           => data_to_mem_$Ch,     
      data_to_mem_we        => data_to_mem_we_$Ch,  
      data_to_mem_re        => data_to_mem_re_$Ch,  
      data_to_core          => data_to_core_$Ch,    
      data_to_core_we       => data_to_core_we_$Ch, 
      num_rd_bytes          => num_rd_bytes_$Ch,
      num_wr_bytes          => num_wr_bytes_$Ch,             
      init_rd_addr          => init_rd_addr_$Ch,
      init_wr_addr          => init_wr_addr_$Ch,             
      rd_req_start          => rd_req_start_$Ch,
      wr_req_start          => wr_req_start_$Ch,             
      rd_req_done           => rd_req_done_$Ch,
      wr_req_done           => wr_req_done_$Ch,
      -- NPI Signals to/from MPMC
      NPI_Addr              => NPI_Addr_$Ch,
      NPI_AddrReq           => NPI_AddrReq_$Ch,
      NPI_AddrAck           => NPI_AddrAck_$Ch,
      NPI_RNW               => NPI_RNW_$Ch,
      NPI_Size              => NPI_Size_$Ch,
      NPI_WrFIFO_Data       => NPI_WrFIFO_Data_$Ch,
      NPI_WrFIFO_BE         => NPI_WrFIFO_BE_$Ch,
      NPI_WrFIFO_Push       => NPI_WrFIFO_Push_$Ch,
      NPI_RdFIFO_Data       => NPI_RdFIFO_Data_$Ch,
      NPI_RdFIFO_Pop        => NPI_RdFIFO_Pop_$Ch,
      NPI_RdFIFO_RdWdAddr   => NPI_RdFIFO_RdWdAddr_$Ch,
      NPI_RdModWr           => NPI_RdModWr_$Ch,
      NPI_WrFIFO_AlmostFull => NPI_WrFIFO_AlmostFull_$Ch,
      NPI_WrFIFO_Flush      => NPI_WrFIFO_Flush_$Ch,
      NPI_WrFIFO_Empty      => NPI_WrFIFO_Empty_$Ch,
      NPI_RdFIFO_Empty      => NPI_RdFIFO_Empty_$Ch,
      NPI_RdFIFO_Flush      => NPI_RdFIFO_Flush_$Ch,
      NPI_InitDone          => NPI_InitDone_$Ch,
      NPI_RdFIFO_Latency    => NPI_RdFIFO_Latency_$Ch
    );
  
";
$READ_WRITE_FSM_SIGNALS = "
-----------------------------------------------------------------------------
-- request fsm
-----------------------------------------------------------------------------
  type FSM_TYPE is (idle, wait_for_done, done);
  signal rd_fsm_cs_$Ch, rd_fsm_ns_$Ch : FSM_TYPE := idle;
  signal rd_fsm_value_$Ch         : std_logic_vector(0 to 3);

  signal wr_fsm_cs_$Ch, wr_fsm_ns_$Ch : FSM_TYPE := idle;
  signal wr_fsm_value_$Ch         : std_logic_vector(0 to 3);  
  signal sw_reset                 : std_logic:= '0';

";
$READ_WRITE_FSM = "
  -----------------------------------------------------------------------------
  -- process: FSM_STATE_PROC
  -- purpose: Register FSM
  -----------------------------------------------------------------------------
  FSM_STATE_PROC_$Ch : process (Bus2ip_Clk) is
  begin
    if ((Bus2ip_Clk\'event) and (Bus2ip_Clk=\'1\')) then
      if (sw_reset = \'1\') then
        rd_fsm_cs_$Ch      <= idle;
        wr_fsm_cs_$Ch      <= idle;
      else
        rd_fsm_cs_$Ch      <= rd_fsm_ns_$Ch;
        wr_fsm_cs_$Ch      <= wr_fsm_ns_$Ch;
      end if;
    end if;
  end process FSM_STATE_PROC_$Ch;
  
  -----------------------------------------------------------------------------
  -- process: RD_FSM_VALUE_PROC
  -- purpose: state indicator signal for chipscope
  -----------------------------------------------------------------------------
  RD_FSM_VALUE_PROC_$Ch : process (rd_fsm_cs_$Ch) is
  begin
    case (rd_fsm_cs_$Ch) is
      when idle          => rd_fsm_value_$Ch <= x\"0\";
      when wait_for_done => rd_fsm_value_$Ch <= x\"1\";
      when done          => rd_fsm_value_$Ch <= x\"2\";
      when others        => rd_fsm_value_$Ch <= x\"3\";
    end case;
  end process RD_FSM_VALUE_PROC_$Ch;
  
  -----------------------------------------------------------------------------
  -- process: RD_FSM_LOGIC_PROC
  -- purpose: when sw=1 assert until rest finish
  -----------------------------------------------------------------------------
  RD_FSM_LOGIC_PROC_$Ch : process (rd_fsm_cs_$Ch, rd_req_start_out_$Ch, rd_req_done_$Ch) is
  begin
    rd_fsm_ns_$Ch              <= rd_fsm_cs_$Ch;

    case (rd_fsm_cs_$Ch) is
      -------------------------------------------------------------------------
      -- idle state: 0
      -------------------------------------------------------------------------
      when idle =>
        if (rd_req_start_out_$Ch = \'1\') then
          rd_fsm_ns_$Ch         <= wait_for_done;
        end if;

      -------------------------------------------------------------------------
      -- wait for done state: 1
      -------------------------------------------------------------------------
      when wait_for_done =>
        if (rd_req_done_$Ch = \'1\') then
          rd_fsm_ns_$Ch         <= done;
        end if;

      -------------------------------------------------------------------------
      -- done state: 2
      -------------------------------------------------------------------------
      when done =>
        if (rd_req_start_out_$Ch = \'0\') then
          rd_fsm_ns_$Ch          <= idle;
        end if;

      when others =>
        rd_fsm_ns_$Ch          <= idle;
    end case;
  end process RD_FSM_LOGIC_PROC_$Ch;

  -----------------------------------------------------------------------------
  -- process: WR_FSM_VALUE_PROC_$Ch
  -- purpose: state indicator signal for chipscope
  -----------------------------------------------------------------------------
  WR_FSM_VALUE_PROC_$Ch : process (wr_fsm_cs_$Ch) is
  begin
    case (wr_fsm_cs_$Ch) is
      when idle          => wr_fsm_value_$Ch <= x\"0\";
      when wait_for_done => wr_fsm_value_$Ch <= x\"1\";
      when done          => wr_fsm_value_$Ch <= x\"2\";
      when others        => wr_fsm_value_$Ch <= x\"3\";
    end case;
  end process WR_FSM_VALUE_PROC_$Ch;
  
  -----------------------------------------------------------------------------
  -- process: WR_FSM_LOGIC_PROC_$Ch
  -- purpose: when sw=1 assert until rest finish
  -----------------------------------------------------------------------------
  WR_FSM_LOGIC_PROC_$Ch : process (wr_fsm_cs_$Ch, wr_req_start_out_$Ch, wr_req_done_$Ch) is
  begin
    wr_fsm_ns_$Ch              <= wr_fsm_cs_$Ch;

    case (wr_fsm_cs_$Ch) is
      -------------------------------------------------------------------------
      -- idle state: 0
      -------------------------------------------------------------------------
      when idle =>
        if (wr_req_start_out_$Ch = \'1\') then
          wr_fsm_ns_$Ch         <= wait_for_done;
        end if;

      -------------------------------------------------------------------------
      -- wait for done state: 1
      -------------------------------------------------------------------------
      when wait_for_done =>
        if (wr_req_done_$Ch = \'1\') then
          wr_fsm_ns_$Ch         <= done;
        end if;

      -------------------------------------------------------------------------
      -- done state: 2
      -------------------------------------------------------------------------
      when done =>
        if (wr_req_start_out_$Ch = \'0\') then
          wr_fsm_ns_$Ch          <= idle;
        end if;

      when others =>
        wr_fsm_ns_$Ch          <= idle;
    end case;
  end process WR_FSM_LOGIC_PROC_$Ch;
";

$REGISTERED_SIG = "
  -----------------------------------------------------------------------------
  -- NPI Registered Signals CH $Ch
  -----------------------------------------------------------------------------
  signal num_rd_bytes_out_$Ch    : std_logic_vector(0 to 31);
  signal num_rd_bytes_next_$Ch   : std_logic_vector(0 to 31);  
  signal num_wr_bytes_out_$Ch    : std_logic_vector(0 to 31);
  signal num_wr_bytes_next_$Ch   : std_logic_vector(0 to 31);      
  signal init_rd_addr_out_$Ch    : std_logic_vector(0 to 31);
  signal init_rd_addr_next_$Ch   : std_logic_vector(0 to 31);  
  signal init_wr_addr_out_$Ch    : std_logic_vector(0 to 31);
  signal init_wr_addr_next_$Ch   : std_logic_vector(0 to 31);      
  signal rd_req_start_out_$Ch    : std_logic;
  signal rd_req_start_next_$Ch   : std_logic; 
  signal wr_req_start_out_$Ch    : std_logic;
  signal wr_req_start_next_$Ch   : std_logic;  
  
  -----------------------------------------------------------------------------
  -- ILA Signals
  -----------------------------------------------------------------------------
  signal data_to_mem_out_$Ch     : std_logic_vector(0 to 63);  
  signal data_to_mem_we_out_$Ch  : std_logic;
  
";

$REGISTERED_PROCESS = "
  -----------------------------------------------------------------------------
  -- PROCESS: BUS2IP_CLK_REG_PROC_$Ch
  -- PURPOSE: Register Signals on the bus2ip_clk
  -----------------------------------------------------------------------------
  BUS2IP_CLK_REG_PROC_$Ch : process(Bus2ip_Clk)
  begin
    if ((Bus2ip_Clk'event) and (Bus2ip_Clk='1')) then
      if (sw_reset = '1') then
        rd_req_start_out_$Ch  <= '0';
        wr_req_start_out_$Ch  <= '0';
        init_rd_addr_out_$Ch  <= (others => '0');
        init_wr_addr_out_$Ch  <= (others => '0');
        num_rd_bytes_out_$Ch  <= (others => '0');
        num_wr_bytes_out_$Ch  <= (others => '0');
      else
        rd_req_start_out_$Ch  <= rd_req_start_next_$Ch;
        wr_req_start_out_$Ch  <= wr_req_start_next_$Ch;
        init_rd_addr_out_$Ch  <= init_rd_addr_next_$Ch;
        init_wr_addr_out_$Ch  <= init_wr_addr_next_$Ch;
        num_rd_bytes_out_$Ch  <= num_rd_bytes_next_$Ch;
        num_wr_bytes_out_$Ch  <= num_wr_bytes_next_$Ch;
      end if;
    end if;
  end process BUS2IP_CLK_REG_PROC_$Ch;
  
";

####################################################################################
## Copying the NPI.VHD File from Andy's Directory
####################################################################################
copy("/home/staduri/npi_script/npi.vhd", "hdl/vhdl/"); ## This copy of npi.vhd does 
                                                       ## not have the npi_ila

####################################################################################
## Modifying the MPD/PAO file
####################################################################################

## 1. Modifying the MPD file
chdir 'data' || die"No directory by the name data\n";
system"pwd";
open(NEW_MPD, ">$MPD_NAME");

## Adding Option Style = Mix
#$mpd =~ m/(\#\#.*?Peripheral.*?Options)\n/i;
#$temp =  $1;
#$mpd =~ s/\#\#.*?Peripheral.*?Options\n/$temp\n$OPTION/;

## Adding the Bus Interface
$mpd =~ m/(\#\#.*?Bus.*?Interfaces)\n/i;
$temp = $1;
$mpd =~ s/\#\#.*?Bus.*?Interfaces\n/$temp\n$BUS_INTERFACE/i;

## Adding the NPI PORTS
$mpd =~ m/(END)\n/i;
$temp = $1;
$mpd =~ s/END\n/$MPD_PORTS\nEND\n/;

print NEW_MPD $mpd;
close(NEW_MPD);

## 2. Modifying the PAO File
$pao =~ s/lib $CORE_LIB user_logic vhdl\n/lib $CORE_LIB npi vhdl\nlib $CORE_LIB user_logic vhdl\n/;
open(NEW_PAO, ">$PAO_NAME");
print NEW_PAO $pao;
close(NEW_PAO);
chdir("../");
###############################################################################
## Editing the top level HDL file
###############################################################################

## Edit and create the new top-level VHD file
chdir("hdl/vhdl");
open(NEW_TOP, ">$CORE.vhd");

## 1. Add NPI Ports
$top =~ m/(entity $CORE.*?port.*?\Q(\E)/s;
$temp = $1;
$top =~ s/entity $CORE.*?port.*?\Q(\E/$temp$TOP_LEVEL_PORTS/s;

#				   print $top;
## 2. Add NPI_User Logic connect signals Ports

$top =~ m/(begin\n)/;
$temp = $1;
$top =~ s/begin\n/$USER_LOGIC_SIGNALS$temp/;
## 3. Add NPI Instance

$top =~ m/(end IMP)/;
$temp = $1;
#print "${temp}\n";
$top =~ s/end IMP/$NPI_PORT_MAP$temp/;
## 4. Add User Logic Port Map

$top =~ m/(USER_LOGIC_I.*?entity.*?.user_logic.*?port map.*?\Q(\E\n)/s;
$temp = $1;
$top =~ s/USER_LOGIC_I.*?entity.*?.user_logic.*?port map.*?\Q(\E\n/$temp$USER_LOGIC_PORT_MAP/s;
print NEW_TOP $top;
close(NEW_TOP);

###############################################################################
## Editing the user_logic_HDL file)))
###############################################################################
open(NEW_UL, ">user_logic.vhd");

## 1. Adding the User Logic Ports
$ulogic =~ m/(entity user_logic.*?port.*?\Q(\E\n)/s;
#)
$temp = $1;
$ulogic =~ s/entity user_logic.*?port.*?\Q(\E\n/$temp$USER_LOGIC_PORTS/s;

## 2. Add the Read/Write FSM signals))))))
$ulogic =~ m/(begin\n)/;
$temp = $1;
$ulogic =~ s/begin\n/$REGISTERED_SIG\n$READ_WRITE_FSM_SIGNALS\n$temp/;

## 3. Add the Read/Write FSMs
$ulogic =~ m/(begin\n)/;
$temp = $1;
$ulogic =~ s/begin\n/$temp\n sw_reset <= bus2ip_reset;\n$READ_WRITE_FSM$REGISTERED_PROCESS/;
print NEW_UL $ulogic;
close(NEW_UL);

exit();
