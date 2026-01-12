library IEEE;
use IEEE.STD_LOGIC_1164.ALL;

entity trng_ro is
    generic ( NUM_RO        : integer := 8;
              RO_STAGES     : integer := 5 );
    port    ( clk           : in std_logic;
              rst_n         : in std_logic;
              random_bit    : out std_logic );                                  -- Final TRNG output bit
end trng_ro;

architecture rtl of trng_ro is
    
    component ring_oscillator is                                                -- Declaration of the ring-oscillator component
        generic ( INVERTERS_NUM : integer := 5 );
        port    ( ro_out        : out std_logic );
    end component;

    signal ro_vector        : std_logic_vector(NUM_RO-1 downto 0);              -- Vector holding outputs of all RO instances
    signal xor_raw          : std_logic;                                        -- XOR-combined value of all oscillators
    signal sync_1           : std_logic;                                        -- First sampling flip-flop
    signal sync_2           : std_logic;                                        -- Second sampling flip-flop
    
    attribute dont_touch              : boolean;                                -- dont_touch is a strict directive telling synthesis to                                             
    attribute dont_touch of ro_vector : signal is true;                         -- preserve the hardware exactly as written.
    
    function xor_reduce(s : std_logic_vector) return std_logic is
        variable r : std_logic := '0';
    begin
        for i in s'range loop                                                   -- Loop over every oscillator output
            r := r xor s(i);
        end loop;
        return r;                                                               -- Final whitened bit
    end function;
    
begin
    gen_ro : for i in 0 to NUM_RO-1 generate                                    -- Instantiate multiple ring oscillators
        ro_inst : ring_oscillator
            generic map ( INVERTERS_NUM => RO_STAGES    )                       -- Set number of inverters for this oscillator
            port map    ( ro_out        => ro_vector(i) );                      -- Connect each RO's output to the vector
    end generate;

    xor_raw <= xor_reduce(ro_vector);                                           -- Whitening: XOR all oscillators together
    
    sample_and_output_random_bit : process(clk, rst_n)                          -- Samples XOR noise and produces a stable TRNG bit
    begin
        if rst_n = '0' then                                                     -- Reset both flip-flops and output
            sync_1      <= '0';
            sync_2      <= '0';
            random_bit  <= '0';
    
        elsif rising_edge(clk) then
            sync_1      <= xor_raw;                                             -- First FF may enter metastability
            sync_2      <= sync_1;                                              -- Second FF stabilizes the sampled value
            random_bit  <= sync_2;                                              -- Output of the TRNG
        end if;
    end process sample_and_output_random_bit;
 
end rtl;
