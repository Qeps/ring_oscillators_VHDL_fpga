library IEEE;
use IEEE.STD_LOGIC_1164.ALL;

entity trng_ro is
    generic (
        NUM_RO : integer := 8;
        SAMPLE_DIV : integer := 32
    );
    port (
        clk        : in  std_logic;
        rst_n      : in  std_logic;
        random_bit : out std_logic
    );
end trng_ro;

architecture rtl of trng_ro is

    component ring_oscillator is
        generic ( INVERTERS_NUM : integer := 5 );
        port    ( ro_out        : out std_logic );
    end component;

    signal ro_vector                  : std_logic_vector(NUM_RO-1 downto 0);
    signal s1                         : std_logic_vector(NUM_RO-1 downto 0); -- 2FF sampling per RO
    signal s2                         : std_logic_vector(NUM_RO-1 downto 0);
    attribute dont_touch              : string;
    attribute dont_touch of ro_vector : signal is "true";
    attribute dont_touch of s1        : signal is "true";
    attribute dont_touch of s2        : signal is "true";

    function xor_reduce(s : std_logic_vector) return std_logic is
        variable r : std_logic := '0';
    begin
        for i in s'range loop
            r := r xor s(i);
        end loop;
        return r;
    end function;

    -- Map index -> odd stages in [3..15]
    function ro_stages(i : integer) return integer is
        variable v : integer;
    begin
        v := 3 + 2*(i mod 7); -- For NUM_RO > 7 it wraps: 3,5,7,9,11,13,15,3,5,...
        return v;
    end function;

begin

    gen_ro : for i in 0 to NUM_RO-1 generate
        ro_inst : ring_oscillator
            generic map (
                INVERTERS_NUM => ro_stages(i)
            )
            port map (
                ro_out => ro_vector(i)
            );
    end generate;

    process(clk)
    begin
        if rising_edge(clk) then
            if rst_n = '0' then
                s1         <= (others => '0');
                s2         <= (others => '0');
                sample_cnt <= (others => '0');
                random_bit <= '0';
            else
                s1 <= ro_vector;
                s2 <= s1;
                if sample_cnt = SAMPLE_DIV-1 then -- prescaler
                    sample_cnt <= (others => '0');
                    random_bit <= xor_reduce(s2);
                else
                    sample_cnt <= sample_cnt + 1;
                end if;
            end if;
        end if;
    end process;

end rtl;
