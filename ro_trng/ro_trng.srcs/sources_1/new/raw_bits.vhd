library IEEE;
use IEEE.STD_LOGIC_1164.ALL;
use IEEE.NUMERIC_STD.ALL;

entity raw_bits is
    port (
        clk        : in  std_logic;
        rst_l      : in  std_logic;
        ro_sync    : in  std_logic_vector(7 downto 0);

        tx_ready   : in  std_logic;
        data_in    : out std_logic_vector(7 downto 0);
        data_valid : out std_logic
    );
end raw_bits;

architecture RTL of raw_bits is
    signal data_in_s    : std_logic_vector(7 downto 0) := (others => '0');
    signal data_valid_s : std_logic := '0';
    signal last_sent_s  : std_logic_vector(7 downto 0) := (others => '0');
begin

    process(clk)
    begin
        if rising_edge(clk) then
            if rst_l = '0' then
                data_in_s    <= (others => '0');
                data_valid_s <= '0';
                last_sent_s  <= (others => '0');
            else
                data_valid_s <= '0';

                if (tx_ready = '1') and (ro_sync /= last_sent_s) then
                    data_in_s    <= ro_sync;
                    data_valid_s <= '1';
                    last_sent_s  <= ro_sync;
                end if;
            end if;
        end if;
    end process;

    data_in    <= data_in_s;
    data_valid <= data_valid_s;

end RTL;