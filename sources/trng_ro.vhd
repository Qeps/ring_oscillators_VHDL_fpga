library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;

entity trng_ro is
    generic (
        NUM_RO     : integer := 8
    );
    port (
        clk        : in  std_logic;
        rst_n      : in  std_logic;
        random_bit : out std_logic
    );
end entity;

architecture rtl of trng_ro is

    component ring_oscillator is
        port (
            enable : in  std_logic;
            ro_out : out std_logic
        );
    end component;

    signal ro_vector  : std_logic_vector(NUM_RO-1 downto 0);
    signal s1, s2     : std_logic_vector(NUM_RO-1 downto 0);
    attribute dont_touch : string;
    attribute dont_touch of ro_vector : signal is "yes";
    attribute dont_touch of s1        : signal is "yes";
    attribute dont_touch of s2        : signal is "yes";

    function xor_reduce(s : std_logic_vector) return std_logic is
        variable r : std_logic := '0';
    begin
        for i in s'range loop
            r := r xor s(i);
        end loop;
        return r;
    end function;

begin

    gen_ro : for i in 0 to NUM_RO-1 generate
        ro_inst : ring_oscillator
            port map (
                enable => '1',          -- free-running
                ro_out => ro_vector(i)
            );
    end generate;

    process(clk)
    begin
        if rising_edge(clk) then
            if rst_n = '0' then
                s1         <= (others => '0');
                s2         <= (others => '0');
                random_bit <= '0';
            else
                s1 <= ro_vector;
                s2 <= s1;
                random_bit <= xor_reduce(s2);
            end if;
        end if;
    end process;
    
end architecture;
