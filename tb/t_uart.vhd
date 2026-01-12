library IEEE;
use IEEE.STD_LOGIC_1164.ALL;

entity tb_uart is
end tb_uart;

architecture sim of tb_uart is

    signal clk        : std_logic := '0';
    signal rst_n      : std_logic := '0';
    signal random_bit : std_logic := '0';
    signal tx_out     : std_logic;

    constant CLK_PERIOD : time := 10 ns;

begin

    clk <= not clk after CLK_PERIOD/2;

    dut : entity work.uart
        port map (
            clk        => clk,
            rst_n      => rst_n,
            random_bit => random_bit,
            tx_out     => tx_out
        );

    stim_proc : process
    begin
        -- synchronous reset
        rst_n <= '0';
        random_bit <= '0';
        wait until rising_edge(clk);
        wait until rising_edge(clk);
        rst_n <= '1';

        -- deterministic bit stream, synchronous to clk
        random_bit <= '1'; wait until rising_edge(clk);
        random_bit <= '0'; wait until rising_edge(clk);
        random_bit <= '1'; wait until rising_edge(clk);
        random_bit <= '1'; wait until rising_edge(clk);
        random_bit <= '0'; wait until rising_edge(clk);
        random_bit <= '0'; wait until rising_edge(clk);
        random_bit <= '1'; wait until rising_edge(clk);
        random_bit <= '0'; wait until rising_edge(clk);

        -- continue with free-running bits
        loop
            random_bit <= not random_bit;
            wait until rising_edge(clk);
        end loop;
    end process;

end sim;
