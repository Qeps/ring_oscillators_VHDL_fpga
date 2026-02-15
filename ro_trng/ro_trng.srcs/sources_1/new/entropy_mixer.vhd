library IEEE;
use IEEE.STD_LOGIC_1164.ALL;

entity entropy_mixer is
    port (
        clk       : in  std_logic;
        rst_l     : in  std_logic;
        ro_sync   : in  std_logic_vector(7 downto 0);
        bit_out   : out std_logic
    );
end;

architecture RTL of entropy_mixer is
    signal raw_bit    : std_logic;
    signal prev_bit   : std_logic;
begin

    raw_bit <= ro_sync(0) xor ro_sync(1) xor ro_sync(2) xor ro_sync(3)
            xor ro_sync(4) xor ro_sync(5) xor ro_sync(6) xor ro_sync(7);

    process(clk)
    begin
        if rising_edge(clk) then
            if rst_l = '0' then
                prev_bit <= '0';
            else
                prev_bit <= raw_bit;
            end if;
        end if;
    end process;

    bit_out <= raw_bit xor prev_bit;

end RTL;
