library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;
use ieee.std_logic_arith.all;
use ieee.std_logic_unsigned.all;

package airen_common is

  constant DATA_WIDTH   : integer := 32;

  -- network topology
  constant K_ARY        : integer := $K_ARY ;  -- 4 (nodes in a direction)
  constant K_WIDTH      : integer := $K_WIDTH ;  -- 2 (bits/direction)
  constant D_CUBE       : integer := $D_CUBE ;  -- 2 (no. of dimensions)

  -- router
  constant RADIX        : natural := $RADIX ;  -- 16 (port width)
  constant SW_SEL_WIDTH : integer := $SW_SEL_WIDTH  ;  -- 4 (bits/switch)
  constant CT_WIDTH     : integer := 4  ;

  constant DST_WIDTH    : integer := SW_SEL_WIDTH+K_WIDTH*D_CUBE;

  -- Offsets for Local Link FIFOs which concatenate DATA, SOF and EOF
  constant SOF_N_OFFSET : integer := DATA_WIDTH + 0;
  constant EOF_N_OFFSET : integer := DATA_WIDTH + 1;
  
  -----------------------------------------------------------------------------
  -- Local Link Port Record Type Declaration
  -----------------------------------------------------------------------------
  type ll_port_type is
  record
    data      : std_logic_vector(DATA_WIDTH-1 downto 0);
    sof_n     : std_logic;
    eof_n     : std_logic;
    dst_rdy_n : std_logic;
    src_rdy_n : std_logic;
  end record; 
  
  -----------------------------------------------------------------------------
  -- Array Type for Router which is an array of LL Port Types
  -----------------------------------------------------------------------------
  type ll_router_ports_type is array (RADIX-1 downto 0) of ll_port_type;

  -----------------------------------------------------------------------------
  -- Array Type for Local Link Data to be used with the LL_Switch Component
  -----------------------------------------------------------------------------
  type ll_data_array is array (RADIX-1 downto 0) of std_logic_vector(DATA_WIDTH-1 downto 0);
  
  -----------------------------------------------------------------------------
  -- Switch Select Array (From each Routing Module to Switch Controller)
  -----------------------------------------------------------------------------
  type sw_sel_array_type is array (RADIX-1 downto 0) of std_logic_vector(SW_SEL_WIDTH-1 downto 0);
  
  -----------------------------------------------------------------------------
  -- Function Prototypes
  -----------------------------------------------------------------------------
  function set_rm_sw_sel(direction_array,arrived_array : std_logic_vector) return std_logic_vector;
  function set_sw_sel(channel : integer; inuse : std_logic_vector;  sw_sel_array : sw_sel_array_type) return std_logic_vector;
  function set_inuse(inuse : std_logic_vector) return std_logic_vector;
  function check_request_done ( request, inuse : in std_logic_vector ) return std_logic_vector;
  function check_for_request ( request : in std_logic_vector ) return std_logic_vector;
  
end airen_common;

-------------------------------------------------------------------------------
-- Package Body
-------------------------------------------------------------------------------
package body airen_common is
  -----------------------------------------------------------------------------
  -- Function: SET_RM_SW_SEL
  -- PURPOSE:  Based on the Dimension (starting with X, then Y, Z) check
  --           if the data has reached the correct dimension before
  --           routing along the next dimension.
  --           This is for the Routing Module specifically.
  -- RETURN:   The Switch Controller Bits to route to the output port
  -----------------------------------------------------------------------------
  function set_rm_sw_sel ( direction_array,arrived_array : in std_logic_vector ) return std_logic_vector is
    variable sel : std_logic_vector(SW_SEL_WIDTH-1 downto 0) := (others => '0');
  begin
    for i in D_CUBE-1 downto 0 loop      
      if (arrived_array(i) = '0') then
        sel := conv_std_logic_vector(i,SW_SEL_WIDTH-1) & direction_array(i);
        exit;
      end if;
    end loop;
    return sel;
  end function set_rm_sw_sel;

  -----------------------------------------------------------------------------
  -- Function: SET_SW_SEL
  -- PURPOSE:  Set Switch Controller's sw_sel bits based on inuse and rm arrays
  -- RETURN:   Control Bits (000 = Port 0, 001 = Port 1 etc...)
  -----------------------------------------------------------------------------
  function set_sw_sel ( channel : in integer; inuse : in std_logic_vector;  sw_sel_array : in sw_sel_array_type ) return std_logic_vector is
    variable sw_sel : std_logic_vector(SW_SEL_WIDTH-1 downto 0) := (others => '0');
  begin
    for i in RADIX-1 downto 0 loop
      if ( (sw_sel_array(i) = channel) and
           (inuse((RADIX*channel) + i) = '1') ) then
        sw_sel := conv_std_logic_vector(i,SW_SEL_WIDTH);      
        exit;
      end if;
    end loop;
    return sw_sel;
  end function set_sw_sel;

  -----------------------------------------------------------------------------
  -- Function: SET_INUSE
  -- PURPOSE:  The inuse input is a RADIX*RADIX downto 0 bit vector which
  --           stores which Input Port is connected to which each Output Port
  --           However, for the switch_nxn component I want to have a single
  --           bit for each output port to use as an enable signal to connect
  --           the input port to the output port
  -----------------------------------------------------------------------------
  function set_inuse(inuse : std_logic_vector) return std_logic_vector is
    variable port_inuse : std_logic := '0';
    variable tmp        : std_logic_vector(RADIX-1 downto 0) := (others => '0');
  begin 
    for i in RADIX-1 downto 0 loop
      port_inuse := '0';
      for j in RADIX-1 downto 0 loop
        if inuse(i*RADIX+j) = '1' then
          port_inuse := '1';
          exit;
        end if;
      end loop;
      tmp(i) := port_inuse;
    end loop;
    return tmp;
  end function set_inuse;

  -----------------------------------------------------------------------------
  -- FUNCTION: CHECK_FOR_REQUEST
  -- PURPOSE:  Check for a Request based on request array and set the
  --           inuse bit (this assumes none of the inuse bits are set)
  -----------------------------------------------------------------------------
  function check_for_request ( request : in std_logic_vector )
    return std_logic_vector is
    variable inuse_new : std_logic_vector(RADIX-1 downto 0) := (others => '0');
  begin
    for i in RADIX-1 downto 0 loop    
      if (request(i) = '1') then
        -- Mark only 1 inuse bit and exit for loop
        inuse_new(i) := '1';
        exit;
      else
        inuse_new(i) := '0';
      end if;
    end loop;
    return inuse_new;
  end function;

  -----------------------------------------------------------------------------
  -- FUNCTION: CHECK_REQUEST_DONE
  -- PURPOSE:  Check Request Has Finished based on request array and inuse
  --           This assumes at least one inuse bit is set
  -----------------------------------------------------------------------------
  function check_request_done ( request, inuse : in std_logic_vector )
    return std_logic_vector is
    variable inuse_new : std_logic_vector(RADIX-1 downto 0) := (others => '0');
  begin
    for i in RADIX-1 downto 0 loop
      if (inuse(i) = '1') and (request(i) = '0') then
        -- Request has finished, unset inuse
        inuse_new(i) := '0';
      elsif (inuse(i) = '1') then
        -- Request is still active
        inuse_new(i) := '1';
      else
        inuse_new(i) := '0';
      end if;
    end loop;    
    return inuse_new;
  end function;  
  
end airen_common;

