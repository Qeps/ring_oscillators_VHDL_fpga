library IEEE;
use IEEE.STD_LOGIC_1164.ALL;
use IEEE.NUMERIC_STD.ALL;

-- clks_per_bit = CLK_FREQ / BAUD_RATE
-- 100 MHz:
--   9600 baud   -> 10417
--   19200 baud  -> 5208
--   38400 baud  -> 2604
--   57600 baud  -> 1736
--   115200 baud -> 868
--
-- 50 MHz:
--   9600 baud   -> 5208
--   19200 baud  -> 2604
--   38400 baud  -> 1302
--   57600 baud  -> 868
--   115200 baud -> 434
--
-- 25 MHz:
--   9600 baud   -> 2604
--   19200 baud  -> 1302
--   38400 baud  -> 651
--   57600 baud  -> 434
--   115200 baud -> 217

entity uart_tx is
    generic (
        clks_per_bit : integer := 10417
    );
    port (
        clk        : in  std_logic;
        rst_n      : in  std_logic;
        data_in    : in  std_logic_vector(7 downto 0);
        data_valid : in  std_logic;
        tx_ready   : out std_logic;
        tx_out     : out std_logic
    );
end uart_tx;

architecture BEHAV of uart_tx is
    signal cnt     : integer range 0 to clks_per_bit-1 := 0;
    signal busy    : std_logic := '0';
    signal bit_cnt : unsigned(3 downto 0) := (others => '0');
    signal tx_buf  : std_logic_vector(7 downto 0) := (others => '0');
begin

process(clk)
begin
    if rising_edge(clk) then
        if rst_n = '0' then
            tx_out   <= '1';
            busy     <= '0';
            tx_ready <= '1';
            cnt      <= 0;
            bit_cnt  <= (others => '0');

        elsif busy = '0' then
            tx_out   <= '1';
            tx_ready <= '1';
            if data_valid = '1' then
                tx_buf   <= data_in;
                busy     <= '1';
                tx_ready <= '0';
                bit_cnt  <= (others => '0');
                cnt      <= clks_per_bit-1;
            end if;

        else
            if cnt = 0 then
                if bit_cnt = 0 then
                    tx_out  <= '0';
                    bit_cnt <= bit_cnt + 1;
                elsif bit_cnt = 9 then
                    tx_out <= '1';
                    busy   <= '0';
                else
                    tx_out  <= tx_buf(to_integer(bit_cnt) - 1);
                    bit_cnt <= bit_cnt + 1;
                end if;
                cnt <= clks_per_bit-1;
            else
                cnt <= cnt - 1;
            end if;
        end if;
    end if;
end process;

end BEHAV;