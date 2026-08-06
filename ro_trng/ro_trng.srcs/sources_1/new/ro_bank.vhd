library ieee;
use ieee.std_logic_1164.all;

entity ro_bank is
    generic (
        OUT_WIDTH : positive := 8
    );
    port (
        enable        : in  std_logic;
        ro_xor_vector : out std_logic_vector(OUT_WIDTH - 1 downto 0)
    );
end entity ro_bank;

architecture rtl of ro_bank is

    constant RO_COUNT : positive := 2 * OUT_WIDTH;

    type stage_count_array is array (natural range <>) of positive;

    constant STAGE_TABLE : stage_count_array(0 to 15) := (
         7,  9, 11, 13, 15, 17, 19, 21,
        23, 25, 27, 29, 31, 33, 35, 37
    );

    signal ro_vec : std_logic_vector(RO_COUNT - 1 downto 0);

    attribute dont_touch : string;
    attribute keep       : string;

    component ring_osc is
        generic (
            STAGES : positive := 7
        );
        port (
            enable : in  std_logic;
            ro_out : out std_logic
        );
    end component ring_osc;

    attribute dont_touch of ring_osc      : component    is "yes";
    attribute dont_touch of ro_vec        : signal       is "yes";
    attribute keep       of ro_vec        : signal       is "true";
    attribute dont_touch of ro_xor_vector : signal       is "yes";
    attribute keep       of ro_xor_vector : signal       is "true";
    attribute dont_touch of rtl           : architecture is "yes";

begin


    gen_ro : for i in 0 to RO_COUNT - 1 generate
        u_ro : ring_osc
            generic map (
                STAGES => STAGE_TABLE(i)
            )
            port map (
                enable => enable,
                ro_out => ro_vec(i)
            );
    end generate gen_ro;

    gen_xor : for i in 0 to OUT_WIDTH - 1 generate
        ro_xor_vector(i) <= ro_vec(2 * i) xor ro_vec(2 * i + 1);
    end generate gen_xor;

end architecture rtl;