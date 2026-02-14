library IEEE;
use IEEE.STD_LOGIC_1164.ALL;

entity von_neumann is
    port (
        clk        : in  std_logic;
        rst_l      : in  std_logic;
        raw_bit    : in  std_logic;
        rnd_bit    : out std_logic;
        rnd_valid  : out std_logic
    );
end von_neumann;

architecture RTL of von_neumann is
    signal bit_prev   : std_logic;
    signal have_first : std_logic;
    signal rnd_bit_r  : std_logic;
    signal valid_r    : std_logic;
begin

    process(clk, rst_l)
    begin
        if rst_l = '0' then
            bit_prev   <= '0';
            have_first <= '0';
            rnd_bit_r  <= '0';
            valid_r    <= '0';

        elsif rising_edge(clk) then
            valid_r <= '0';

            if have_first = '0' then
                bit_prev   <= raw_bit;
                have_first <= '1';
            else
            
                if bit_prev = '0' and raw_bit = '1' then
                    rnd_bit_r <= '0';
                    valid_r   <= '1';
                elsif bit_prev = '1' and raw_bit = '0' then
                    rnd_bit_r <= '1';
                    valid_r   <= '1';
                end if;

                have_first <= '0';
            end if;
        end if;
    end process;

    rnd_bit   <= rnd_bit_r;
    rnd_valid <= valid_r;

end RTL;
