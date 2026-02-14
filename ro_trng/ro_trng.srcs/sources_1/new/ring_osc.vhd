library IEEE;
use IEEE.STD_LOGIC_1164.ALL;

entity ring_osc is
    generic (
        STAGES : positive := 7
    );
    port (
        enable : in  std_logic;
        ro_out : out std_logic
    );
    attribute dont_touch : string;
    attribute dont_touch of ring_osc : entity is "yes";
end ring_osc;

architecture RTL of ring_osc is

    signal w : std_logic_vector(STAGES-1 downto 0);

    attribute keep              : string;
    attribute dont_touch of w   : signal is "yes";
    attribute keep       of w   : signal is "true";
    attribute dont_touch of RTL : architecture is "yes";
begin

    w(0) <= not w(STAGES-1);

    gen_inv : for i in 1 to STAGES-1 generate
        w(i) <= not w(i-1);
    end generate;

    ro_out <= w(STAGES-1) when enable = '1' else '0';

end RTL;
