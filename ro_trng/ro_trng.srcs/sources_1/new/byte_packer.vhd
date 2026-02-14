library IEEE;
use IEEE.STD_LOGIC_1164.ALL;
use IEEE.NUMERIC_STD.ALL;

entity byte_packer is
    port (
        clk        : in  std_logic;
        rst_l      : in  std_logic;
        rnd_bit    : in  std_logic;
        bit_valid  : in  std_logic;   -- von_neumann
        tx_ready   : in  std_logic;
        byte_out   : out std_logic_vector(7 downto 0);
        byte_valid : out std_logic
    );
end byte_packer;

architecture RTL of byte_packer is
    signal shift_reg_r  : std_logic_vector(7 downto 0) := (others => '0');
    signal bit_cnt      : unsigned(2 downto 0)         := (others => '0');
    signal byte_valid_r : std_logic                    := '0';
begin
    process(clk)
    begin
        if rising_edge(clk) then
    
            if rst_l = '0' then
                shift_reg_r  <= (others => '0');
                bit_cnt      <= (others => '0');
                byte_valid_r <= '0';
    
            elsif byte_valid_r = '1' then
                if tx_ready = '1' then
                    byte_valid_r <= '0';
                    bit_cnt      <= (others => '0');
                end if;
    
            elsif bit_valid = '1' then
                shift_reg_r <= shift_reg_r(6 downto 0) & rnd_bit;
    
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
