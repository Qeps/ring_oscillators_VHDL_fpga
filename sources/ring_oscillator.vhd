library ieee;
use ieee.std_logic_1164.all;

entity ring_oscillator is
    port (
        enable : in  std_logic;
        ro_out : out std_logic
    );
end entity;

architecture rtl of ring_oscillator is
    signal w1, w2, w3, w4, w5, w6, w7, w8 : std_logic;
    attribute dont_touch : string;
    attribute dont_touch of w1, w2, w3, w4, w5, w6, w7, w8 : signal is "yes";
begin

    w1 <= w8 when enable = '1' else '0';
    w2 <= not w1;
    w3 <= not w2;
    w4 <= not w3;
    w5 <= not w4;
    w6 <= not w5;
    w7 <= not w6;
    w8 <= not w7;

    ro_out <= w8;

end architecture;
