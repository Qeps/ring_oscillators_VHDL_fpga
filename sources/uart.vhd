library IEEE;
use IEEE.STD_LOGIC_1164.ALL;

entity uart is
    port (
        clk        : in  std_logic;
        rst_n      : in  std_logic;
        random_bit : in  std_logic;
        tx_out     : out std_logic
    );
end uart;

architecture BEHAV of uart is

component shift_reg
    port (
        clk        : in  std_logic;
        rst_n      : in  std_logic;
        random_bit : in  std_logic;
        tx_ready   : in  std_logic;
        byte_out   : out std_logic_vector(7 downto 0);
        byte_valid : out std_logic
    );
end component;

component uart_tx
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
end component;

signal byte_out   : std_logic_vector(7 downto 0);
signal byte_valid : std_logic;
signal tx_ready_i : std_logic;

begin

U1: shift_reg
    port map (
        clk        => clk,
        rst_n      => rst_n,
        random_bit => random_bit,
        tx_ready   => tx_ready_i,
        byte_out   => byte_out,
        byte_valid => byte_valid
    );

U2: uart_tx
    generic map (
        clks_per_bit => 868
    )
    port map (
        clk        => clk,
        rst_n      => rst_n,
        data_in    => byte_out,
        data_valid => byte_valid,
        tx_ready   => tx_ready_i,
        tx_out     => tx_out
    );

end BEHAV;
