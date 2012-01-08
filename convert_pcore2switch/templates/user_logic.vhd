library ieee;
use ieee.std_logic_1164.all;
use ieee.std_logic_arith.all;
use ieee.std_logic_unsigned.all;

library proc_common_v3_00_a;
use proc_common_v3_00_a.proc_common_pkg.all;

use work.airen_common.all;

entity user_logic is
  generic
    (
      C_SLV_DWIDTH :       integer := 32;
      C_NUM_REG    :       integer := 1
      );
  port
    (
      rx_port      : inout ll_array(11 downto 0);
      tx_port      : inout ll_array(11 downto 0);
      -- Bus protocol ports, do not add to or delete
      Bus2IP_Clk   : in    std_logic;
      Bus2IP_Reset : in    std_logic;
      Bus2IP_Data  : in    std_logic_vector(0 to C_SLV_DWIDTH-1);
      Bus2IP_BE    : in    std_logic_vector(0 to C_SLV_DWIDTH/8-1);
      Bus2IP_RdCE  : in    std_logic_vector(0 to C_NUM_REG-1);
      Bus2IP_WrCE  : in    std_logic_vector(0 to C_NUM_REG-1);
      IP2Bus_Data  : out   std_logic_vector(0 to C_SLV_DWIDTH-1);
      IP2Bus_RdAck : out   std_logic;
      IP2Bus_WrAck : out   std_logic;
      IP2Bus_Error : out   std_logic
      -- DO NOT EDIT ABOVE THIS LINE    ---------------------
      );

  attribute SIGIS                 : string;
  attribute SIGIS of Bus2IP_Clk   : signal   is "CLK";
  attribute SIGIS of Bus2IP_Reset : signal is "RST";

end entity user_logic;

------------------------------------------------------------------------------
-- Architecture section
------------------------------------------------------------------------------

architecture IMP of user_logic is

  --USER signal declarations added here, as needed for user logic

  ------------------------------------------
  -- Signals for user logic slave model s/w accessible register example
  ------------------------------------------
  signal location_reg      : std_logic_vector(0 to C_SLV_DWIDTH-1);
  signal slv_reg_write_sel : std_logic_vector(0 to 0);
  signal slv_reg_read_sel  : std_logic_vector(0 to 0);
  signal slv_ip2bus_data   : std_logic_vector(0 to C_SLV_DWIDTH-1);
  signal slv_read_ack      : std_logic;
  signal slv_write_ack     : std_logic;

  component airen_router
    generic (
      RADIX       :       natural := 12;
      R_WIDTH     :       natural := 4  -- 2^R_WIDTH = RADIX
      );
    port (
      clk         : in    std_logic;
      rst         : in    std_logic;
      location    : in    std_logic_vector(D_WIDTH-1 downto 0);
      ll_rx_ports : inout ll_array(RADIX-1 downto 0);
      ll_tx_ports : inout ll_array(RADIX-1 downto 0)
      );
  end component;

begin

  --USER logic implementation added here

  ------------------------------------------
  -- Example code to read/write user logic slave model s/w accessible registers
  -- 
  -- Note:
  -- The example code presented here is to show you one way of reading/writing
  -- software accessible registers implemented in the user logic slave model.
  -- Each bit of the Bus2IP_WrCE/Bus2IP_RdCE signals is configured to correspond
  -- to one software accessible register by the top level template. For example,
  -- if you have four 32 bit software accessible registers in the user logic,
  -- you are basically operating on the following memory mapped registers:
  -- 
  --    Bus2IP_WrCE/Bus2IP_RdCE   Memory Mapped Register
  --                     "1000"   C_BASEADDR + 0x0
  --                     "0100"   C_BASEADDR + 0x4
  --                     "0010"   C_BASEADDR + 0x8
  --                     "0001"   C_BASEADDR + 0xC
  -- 
  ------------------------------------------
  slv_reg_write_sel <= Bus2IP_WrCE(0 to 0);
  slv_reg_read_sel  <= Bus2IP_RdCE(0 to 0);
  slv_write_ack     <= Bus2IP_WrCE(0);
  slv_read_ack      <= Bus2IP_RdCE(0);

  -- implement slave model software accessible register(s)
  SLAVE_REG_WRITE_PROC : process( Bus2IP_Clk ) is
  begin

    if Bus2IP_Clk'event and Bus2IP_Clk = '1' then
      if Bus2IP_Reset = '1' then
        location_reg                                         <= (others => '0');
      else
        case slv_reg_write_sel is
          when "1"                                                      =>
            for byte_index in 0 to (C_SLV_DWIDTH/8)-1 loop
              if ( Bus2IP_BE(byte_index) = '1' ) then
                location_reg(byte_index*8 to byte_index*8+7) <= Bus2IP_Data(byte_index*8 to byte_index*8+7);
              end if;
            end loop;
          when others                                                   => null;
        end case;
      end if;
    end if;

  end process SLAVE_REG_WRITE_PROC;

  -- implement slave model software accessible register(s) read mux
  SLAVE_REG_READ_PROC : process( slv_reg_read_sel, location_reg ) is
  begin

    case slv_reg_read_sel is
      when "1"    => slv_ip2bus_data <= location_reg;
      when others => slv_ip2bus_data <= (others => '0');
    end case;

  end process SLAVE_REG_READ_PROC;

  ------------------------------------------
  -- Example code to drive IP to Bus signals
  ------------------------------------------
  IP2Bus_Data <= slv_ip2bus_data when slv_read_ack = '1' else
                 (others => '0');

  IP2Bus_WrAck <= slv_write_ack;
  IP2Bus_RdAck <= slv_read_ack;
  IP2Bus_Error <= '0';

  -----------------------------------------------------------------------------
  -- Router instance
  -----------------------------------------------------------------------------
  router_inst : airen_router
    port map (
      clk         => Bus2IP_Clk,
      rst         => Bus2IP_Reset,
      location    => location_reg,
      ll_rx_ports => rx_port,
      ll_tx_ports => tx_port
      );

end IMP;
