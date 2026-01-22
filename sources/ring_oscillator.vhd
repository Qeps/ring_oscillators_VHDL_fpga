library IEEE;
use IEEE.STD_LOGIC_1164.ALL;

-- "dont_touch" tells the synthesis tool not to optimize, modify, merge, or remove this signal, even if it looks
-- redundant or forms a combinational loop.
-- KEEP tells synthesis prefer not to modify this signal but later optimization stages may still restructure the surrounding logic.
-- dont_touch is stronger:
-- it instructs the tool to preserve the marked hardware exactly, preventing removal, merging,
-- or transformation across all synthesis and implementation steps.
-- This increases the chance that the tool will preserve the physical ring structure needed for oscillation. However, it is
-- not an absolute guarantee: some tools or optimization passes may still restructure logic, especially if device routing
-- constraints or timing analysis force changes.

entity ring_oscillator is
    generic ( INVERTERS_NUM : integer := 5 );                                     -- Parameter: number of inverters in the ring (must be odd)
    port    ( ro_out : out std_logic       );                                     -- Output of the oscillator - last stage
end ring_oscillator;

architecture rtl of ring_oscillator is
    signal    chain                 : std_logic_vector(INVERTERS_NUM-1 downto 0); -- Vector of signals, each element represents one inverter stage
    attribute dont_touch            : string;                                     -- Attribute declaration for synthesis tools
    attribute dont_touch of chain   : signal is "true";                           -- Feedback loop should not be optimized or removed
begin
    chain(0) <= not chain(INVERTERS_NUM-1);                                       -- First inverter takes the inverted value of the last stage
    gen_chain : for i in 1 to INVERTERS_NUM-1 generate 
        chain(i) <= not chain(i-1);                                               -- Each following stage inverts the previous one
    end generate;
    
    ro_out <= chain(INVERTERS_NUM-1);                                             -- The output of the oscillator is the last stage in the ring
end rtl;
