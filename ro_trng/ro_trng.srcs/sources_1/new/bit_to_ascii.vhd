library IEEE;
use IEEE.STD_LOGIC_1164.ALL;
use IEEE.NUMERIC_STD.ALL;

entity bit_to_ascii is
    generic (
        SEND_PERIOD : integer := 100_000      -- 1 ms 100 MHz
    );
    port (
        clk        : in  std_logic;
        rst_l      : in  std_logic;
        bit_in     : in  std_logic;
        tx_ready   : in  std_logic;

        data_out   : out std_logic_vector(7 downto 0);
        data_valid : out std_logic
    );
end bit_to_ascii;

architecture RTL of bit_to_ascii is

    signal cnt    : unsigned(31 downto 0) := (others => '0');
    signal dv_r   : std_logic := '0';
    signal data_r : std_logic_vector(7 downto 0) := (others => '0');

begin

process(clk)
begin
    if rising_edge(clk) then

        dv_r <= '0';

        if rst_l = '0' then
            cnt    <= (others => '0');
            data_r <= (others => '0');

        else
            if cnt = SEND_PERIOD-1 then

                if tx_ready = '1' then
                    cnt <= (others => '0');

                    if bit_in = '1' then
                        data_r <= x"31";  -- '1'
                    else
                        data_r <= x"30";  -- '0'
                    end if;

                    dv_r <= '1';
                end if;

            else
                cnt <= cnt + 1;
            end if;
        end if;

    end if;
end process;

data_out   <= data_r;
data_valid <= dv_r;

end RTL;
