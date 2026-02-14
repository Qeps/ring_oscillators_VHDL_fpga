library IEEE;
use IEEE.STD_LOGIC_1164.ALL;

entity entropy_mixer is
    port (
        clk      : in  std_logic;
        rst_l    : in  std_logic;
        ro_sync  : in  std_logic_vector(7 downto 0);
        raw_bit  : out std_logic
    );
end entropy_mixer;

architecture RTL of entropy_mixer is
    signal xor_reg : std_logic;
begin

    process(clk, rst_l)
        variable tmp : std_logic;
    begin
        if rst_l = '0' then
            xor_reg <= '0';
        elsif rising_edge(clk) then
            tmp := ro_sync(0) xor ro_sync(1) xor ro_sync(2) xor ro_sync(3) xor ro_sync(4) xor ro_sync(5) xor ro_sync(6) xor ro_sync(7);
            xor_reg <= tmp;
        end if;
    end process;

    raw_bit <= xor_reg;

end RTL;