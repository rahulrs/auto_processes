library ieee;
use ieee.std_logic_1164.all;
use ieee.std_logic_arith.all;
use ieee.std_logic_unsigned.all;

use work.airen_common.all;
-------------------------------------------------------------------------------
-- ENTITY: USER_LOGIC
-- AUTHOR: Andy Schmidt
-- DATE: 10/14/2008
-- PURPOSE: Connect all of the components that make up the Router:
-- ll_switch - Local Link Switch
-- switch_ctlr - Switch Controller
-- routing_module - Routing Modules (one per port)
-- Each Port is a Local Link Input or Output and the signals
-- are registered once in the switch and once in this component
-- to provide a higher theoretical operating frequency
-- PORTS:
-- router_clk - Clock Input for the Router (all comps use same clock)
-- router_rst - Reset Output (set from software to reset system)
-- ll_rx_port - Local Link Receive Port (input array of LL ports)
-- ll_tx_port - Local Link Transmit Port (output array of LL ports)
-- Bus2IP_* - Input Signals from the Bus (via IPIC Signals)
-- IP2BUS_* - Output Signals from IP Core to Bus (via IPIC Signals)
-------------------------------------------------------------------------------
entity user_logic is
  generic (
    -- PLB IPIC Generics
    C_SLV_DWIDTH :       integer := 32;
    C_NUM_REG    :       integer := 1
    );
  port (
    -- Router Clk
    router_clk   : in    std_logic;
    -- Reset Output
    router_rst   : out   std_logic;
    -- Local Link Type (Rx - Input)
    ll_rx_port   : inout ll_array;
    -- Local Link Type (Tx - Output)
    ll_tx_port   : inout ll_array;
    -- PLB IPIF Ports
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
    );
end entity user_logic;

------------------------------------------------------------------------------
-- ARCHITECTURE
------------------------------------------------------------------------------
architecture IMP of user_logic is
  constant DST_WIDTH : integer := SW_SEL_WIDTH+K_WIDTH*D_CUBE;

  -- Slave Register(s) and IPIF Signals
  signal location_reg  : std_logic_vector(0 to C_SLV_DWIDTH-1);
  signal slv_read_ack  : std_logic;
  signal slv_write_ack : std_logic;

  -- Internal Signals
  signal loc           : std_logic_vector(K_WIDTH*D_CUBE-1 downto 0);
  signal sw_reset      : std_logic;
  -- Switch Select Control Bits
  signal sw_sel        : sw_sel_array_type;
  -- Routing Module Switch Select Bits
  signal rm_sw_sel     : sw_sel_array_type;
  -- Routing Module sw_sel Ready to signal Sw Ctlr to configure output port
  signal rm_sw_sel_rdy : std_logic_vector(RADIX-1 downto 0);
  -- Switch Controller In Use Bits
  signal inuse         : std_logic_vector(RADIX-1 downto 0);

-------------------------------------------------------------------------------
-- BEGIN
-------------------------------------------------------------------------------
begin
  -----------------------------------------------------------------------------
  -- Internal Software Addressible Information
  -----------------------------------------------------------------------------
  slv_write_ack <= Bus2IP_WrCE(0);
  slv_read_ack  <= Bus2IP_RdCE(0);

  -----------------------------------------------------------------------------
  -- Internal Signal Renaming / Reordering to Simplify Reading
  -----------------------------------------------------------------------------
  loc      <= location_reg(32-K_WIDTH*D_CUBE to 31);
  sw_reset <= location_reg(0) or Bus2IP_Reset;

  -----------------------------------------------------------------------------
  -- Core to Bus Output Signals
  -----------------------------------------------------------------------------
  IP2Bus_Data  <= location_reg when (slv_read_ack = '1') else (others => '0');
  IP2Bus_WrAck <= slv_write_ack;
  IP2Bus_RdAck <= slv_read_ack;
  IP2Bus_Error <= '0';

  -----------------------------------------------------------------------------
  -- Router Output Reset Signal
  -----------------------------------------------------------------------------
  router_rst <= sw_reset;

  -----------------------------------------------------------------------------
  -- PROCESS: SLAVE_REG_WRITE_PROC
  -- PURPOSE: Give PowerPC Write Access to select Registers
  -----------------------------------------------------------------------------
  SLAVE_REG_WRITE_PROC : process( Bus2IP_Clk ) is
  begin
    if ((Bus2IP_Clk'event) and (Bus2IP_Clk = '1')) then
      if Bus2IP_Reset = '1' then
        location_reg <= (others => '0');
      elsif (Bus2IP_WrCE(0) = '1') then
        location_reg <= Bus2IP_Data;
      end if;
    end if;
  end process SLAVE_REG_WRITE_PROC;

  -----------------------------------------------------------------------------
  -- Switch Instantiation
  -----------------------------------------------------------------------------
  ll_switch_i : entity work.ll_switch
    port map (
      clk    => router_clk,
      rst    => sw_reset,
      sw_sel => sw_sel,
      inuse  => inuse,
      input  => ll_rx_port,
      output => ll_tx_port
      );

  -----------------------------------------------------------------------------
  -- Switch Controller Instantiation
  -----------------------------------------------------------------------------
  switch_ctlr_i : entity work.switch_ctlr
    port map(
      clk           => router_clk,
      rst           => sw_reset,
      rm_sw_sel     => rm_sw_sel,
      rm_sw_sel_rdy => rm_sw_sel_rdy,
      sw_sel        => sw_sel,
      inuse         => inuse
      );

  -----------------------------------------------------------------------------
  -- Routing Module Instance
  -----------------------------------------------------------------------------
  rm_generate : for i in RADIX-1 downto 0 generate
  begin
    rm_i      : entity work.routing_module
      port map(
        clk           => router_clk,
        rst           => sw_reset,
        loc           => loc,
        sof_n         => ll_rx_port(i).sof_n,
        eof_n         => ll_rx_port(i).eof_n,
        src_rdy_n     => ll_rx_port(i).src_rdy_n,
        dst           => ll_rx_port(i).data(DST_WIDTH-1 downto 0),
        rm_sw_sel_rdy => rm_sw_sel_rdy(i),
        rm_sw_sel     => rm_sw_sel(i)
        );
  end generate rm_generate;

end IMP;
