library IEEE;
use IEEE.STD_LOGIC_1164.ALL;

entity ro_sampler is
    port (
        clk     : in  std_logic;
        rst_l   : in  std_logic;
        ro_vec  : in  std_logic_vector(7 downto 0);
        ro_sync : out std_logic_vector(7 downto 0)
    );
end ro_sampler;

architecture RTL of ro_sampler is
    signal ff1, ff2 : std_logic_vector(7 downto 0);

    attribute ASYNC_REG  : string;
    attribute dont_touch : string;
    attribute KEEP       : string;

    attribute ASYNC_REG  of ff1 : signal is "TRUE";
    attribute ASYNC_REG  of ff2 : signal is "TRUE";
    attribute dont_touch of ff1 : signal is "yes";
    attribute dont_touch of ff2 : signal is "yes";
    attribute keep       of ff1 : signal is "true";
    attribute keep       of ff2 : signal is "true";
begin

    process(clk, rst_l)
    begin
        if rst_l = '0' then
            ff1 <= (others => '0');
            ff2 <= (others => '0');
        elsif rising_edge(clk) then
            ff1 <= ro_vec;
            ff2 <= ff1;
        end if;
    end process;

    ro_sync <= ff2;

end RTL;
