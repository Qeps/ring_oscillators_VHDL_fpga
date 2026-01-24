library IEEE;
use IEEE.STD_LOGIC_1164.ALL;

entity top_level_entity is
    port (
        clk    : in  std_logic;
        rst_n  : in  std_logic;
        tx_out : out std_logic
    );
end top_level_entity;

architecture rtl of top_level_entity is

signal random_bit_s : std_logic;

component trng_ro
    generic (
        NUM_RO     : integer := 8,
        SAMPLE_DIV : integer := 32
    );
    port (
        clk        : in  std_logic;
        rst_n      : in  std_logic;
        random_bit : out std_logic
    );
end component;

component uart
    port (
        clk        : in  std_logic;
        rst_n      : in  std_logic;
        random_bit : in  std_logic;
        tx_out     : out std_logic
    );
end component;

begin

U_TRNG : trng_ro
    generic map (
        NUM_RO     => 8,
        SAMPLE_DIV => 32
    )
    port map (
        clk        => clk,
        rst_n      => rst_n,
        random_bit => random_bit_s
    );

U_UART : uart
    port map (
        clk        => clk,
        rst_n      => rst_n,
        random_bit => random_bit_s,
        tx_out     => tx_out
    );

end rtl;
