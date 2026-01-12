library IEEE;
use IEEE.STD_LOGIC_1164.ALL;
use IEEE.NUMERIC_STD.ALL;

entity shift_reg is
    port (
        clk        : in  std_logic;
        rst_n      : in  std_logic;
        random_bit : in  std_logic;
        tx_ready   : in  std_logic;

        byte_out   : out std_logic_vector(7 downto 0);
        byte_valid : out std_logic
    );
end shift_reg;

architecture RTL of shift_reg is
    signal shift_reg_r  : std_logic_vector(7 downto 0) := (others => '0');
    signal bit_cnt      : unsigned(2 downto 0)         := (others => '0');
    signal byte_valid_r : std_logic                    := '0';
begin

process(clk)
begin
    if rising_edge(clk) then
        -- Sync reset
        if rst_n = '0' then
            shift_reg_r  <= (others => '0');
            bit_cnt      <= (others => '0');
            byte_valid_r <= '0';
        -- Byte waiting for UART
        elsif byte_valid_r = '1' then
            if tx_ready = '1' then
                -- UART accepted byte, restart collection
                byte_valid_r <= '0';
                bit_cnt      <= (others => '0');
                -- NO SHIFT HERE (important)
            end if;
        -- Normal bit collection
        else
            shift_reg_r <= shift_reg_r(6 downto 0) & random_bit;

            if bit_cnt = 7 then
                byte_valid_r <= '1';
            else
                bit_cnt <= bit_cnt + 1;
            end if;
        end if;

    end if;
end process;

byte_out   <= shift_reg_r;
byte_valid <= byte_valid_r;

end RTL;
