library IEEE;
use IEEE.STD_LOGIC_1164.ALL;

entity ro_bank is
    port (
        enable : in  std_logic;
        ro_vec : out std_logic_vector(7 downto 0)
    );
end ro_bank;

architecture RTL of ro_bank is

    attribute dont_touch : string;
    
    component ring_osc
        generic (
            STAGES : positive := 7
        );
        port (
            enable : in  std_logic;
            ro_out : out std_logic
        );
    end component;
    attribute dont_touch of ring_osc : component is "yes";
    attribute dont_touch of RTL      : architecture is "yes";
begin

    ro0 : ring_osc generic map (STAGES => 7)  port map (enable => enable, ro_out => ro_vec(0));
    ro1 : ring_osc generic map (STAGES => 9)  port map (enable => enable, ro_out => ro_vec(1));
    ro2 : ring_osc generic map (STAGES => 11) port map (enable => enable, ro_out => ro_vec(2));
    ro3 : ring_osc generic map (STAGES => 13) port map (enable => enable, ro_out => ro_vec(3));
    ro4 : ring_osc generic map (STAGES => 15) port map (enable => enable, ro_out => ro_vec(4));
    ro5 : ring_osc generic map (STAGES => 17) port map (enable => enable, ro_out => ro_vec(5));
    ro6 : ring_osc generic map (STAGES => 21) port map (enable => enable, ro_out => ro_vec(6));
    ro7 : ring_osc generic map (STAGES => 25) port map (enable => enable, ro_out => ro_vec(7));
    
end RTL;
