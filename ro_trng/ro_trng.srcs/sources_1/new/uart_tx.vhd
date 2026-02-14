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
        rst_l      : in  std_logic;
        data_in    : in  std_logic_vector(7 downto 0);
        data_valid : in  std_logic;
        tx_ready   : out std_logic;
        tx_out     : out std_logic
    );
end uart_tx;

architecture RTL of uart_tx is
    type t_state is (
        IDLE,
        START_BIT,
        DATA_BITS,
        STOP_BIT
    );
    signal state        : t_state := IDLE;
    signal clk_cnt      : integer range 0 to clks_per_bit-1 := 0;
    signal bit_idx      : integer range 0 to 7 := 0;
    signal tx_buf       : std_logic_vector(7 downto 0) := (others => '0');
begin

    process(clk)
    begin
        if rising_edge(clk) then
            if rst_l = '0' then
                state    <= IDLE;
                tx_out   <= '1';
                tx_ready <= '1';
                clk_cnt  <= 0;
                bit_idx  <= 0;
    
            else
                case state is
                    when IDLE =>
                        tx_out   <= '1';
                        tx_ready <= '1';
                        clk_cnt  <= 0;
                        bit_idx  <= 0;
    
                        if data_valid = '1' then
                            tx_buf  <= data_in;
                            tx_ready <= '0';
                            state   <= START_BIT;
                        end if;
                    when START_BIT =>
                        tx_out <= '0';
    
                        if clk_cnt < clks_per_bit-1 then
                            clk_cnt <= clk_cnt + 1;
                        else
                            clk_cnt <= 0;
                            state   <= DATA_BITS;
                        end if;
                    when DATA_BITS =>
                        tx_out <= tx_buf(bit_idx);
                        if clk_cnt < clks_per_bit-1 then
                            clk_cnt <= clk_cnt + 1;
                        else
                            clk_cnt <= 0;
    
                            if bit_idx < 7 then
                                bit_idx <= bit_idx + 1;
                            else
                                bit_idx <= 0;
                                state   <= STOP_BIT;
                            end if;
                        end if;
                    when STOP_BIT =>
                        tx_out <= '1';
                        if clk_cnt < clks_per_bit-1 then
                            clk_cnt <= clk_cnt + 1;
                        else
                            clk_cnt <= 0;
                            state   <= IDLE;
                        end if;
                end case;
            end if;
        end if;
    end process;

end RTL;