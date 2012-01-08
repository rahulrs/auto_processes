library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;
use ieee.std_logic_arith.all;
use ieee.std_logic_unsigned.all;

-- 16 Port Router

package airen_common is
  -- Number of Nodes in 1 Dimension
  constant K_ARY      : integer := $K_ARY;
  constant K_WIDTH    : integer := $K_WIDTH;   -- 2^K_WIDTH = K_ARY
  -- Number of Dimensions
  constant D_CUBE     : integer := $D_CUBE;
  -- Data Width of Router/Switch
  constant D_WIDTH    : natural := $D_WIDTH;

  -- Array of Naturals Type
  type natural_vector is array (natural range <>) of natural;

  -- Offsets for Local Link FIFOs which concatenate DATA, SOF and EOF
  constant SOF_N_OFFSET : integer := D_WIDTH + 0;
  constant EOF_N_OFFSET : integer := D_WIDTH + 1;

  -- Record Type for LocalLink Block Switch Network
  type ll_type is
    record
      src_rdy_n : std_logic;
      dst_rdy_n : std_logic;
      sof_n     : std_logic;
      eof_n     : std_logic;
      data      : std_logic_vector(D_WIDTH-1 downto 0);
    end record;
  -- Array of LocalLink Records for Router (or any component needing multiple ll_types
  type ll_array is array (natural range <>) of ll_type;

  -----------------------------------------------------------------------------
  -- Function Prototypes
  -----------------------------------------------------------------------------
  function set_req_port(direction_array, arrived_array : std_logic_vector; R_WIDTH : natural) return natural;
  function calc_dst_rdy_n (p                           : natural; inuse : std_logic_vector; dst_rdy_array : std_logic_vector; sw_sel : natural_vector; src_rdy_n, eof_n : std_logic) return std_logic;

end airen_common;

-------------------------------------------------------------------------------
-- Package Body
-------------------------------------------------------------------------------
package body airen_common is
  -----------------------------------------------------------------------------
  -- Function: SET_REQ_PORT
  -- PURPOSE:  Based on the Dimension (starting with X, then Y, Z) check
  --           if the data has reached the correct dimension before
  --           routing along the next dimension.
  --           This is for the Routing Module specifically.
  -- RETURN:   The Output Port Number to configure the switch to
  -----------------------------------------------------------------------------
  function set_req_port (direction_array, arrived_array : in std_logic_vector; R_WIDTH : in natural)
    return natural is
    variable sel                                        :    natural := 0;
  begin
    for i in arrived_array'length-1 downto 0 loop
      if (arrived_array(i) = '0') then
        sel                                                          := conv_integer(conv_std_logic_vector(i, R_WIDTH-1) & direction_array(i));
        exit;
      end if;
    end loop;
    return sel;
  end function set_req_port;

  -----------------------------------------------------------------------------
  -- FUNCTION: CALC_DST_RDY_N
  -- PURPOSE:  Output the Destiantion Ready Signal based on the
  --           output port's inuse bit and if the switch_select is
  --           configured to that port.  Only set the dst_ready_n signal
  --           from sof_n to eof_n, after eof_n and src_rdy_n are both 0,
  --           deassert the dst_rdy_n to stop future transfers
  -----------------------------------------------------------------------------
  function calc_dst_rdy_n (p : natural; inuse : std_logic_vector; dst_rdy_array : std_logic_vector; sw_sel : natural_vector; src_rdy_n, eof_n : std_logic)
    return std_logic is
    variable temp            : std_logic := '1';
  begin
    for i in sw_sel'range loop
      if ((src_rdy_n = '0') and (eof_n = '0')) then
        temp                             := '1';
        exit;
      elsif ((sw_sel(i) = p) and (inuse(i) = '1')) then
        temp                             := dst_rdy_array(i);
        exit;
      end if;
    end loop;
    return temp;
  end;

end airen_common;

