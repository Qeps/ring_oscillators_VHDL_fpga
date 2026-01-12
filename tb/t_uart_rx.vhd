library IEEE;
use IEEE.STD_LOGIC_1164.ALL;

entity tb_uart_tx is
end tb_uart_tx;

architecture sim of tb_uart_tx is
    signal clk        : std_logic := '0';
    signal rst_n      : std_logic := '0';
    signal data_in    : std_logic_vector(7 downto 0) := (others => '0');
    signal data_valid : std_logic := '0';
    signal tx_ready   : std_logic;
    signal tx_out     : std_logic;

    constant CLK_PERIOD : time := 10 ns; -- 100 MHz
begin

    clk <= not clk after CLK_PERIOD/2;

    dut : entity work.uart_tx
        port map (
            clk        => clk,
            rst_n      => rst_n,
            data_in    => data_in,
            data_valid => data_valid,
            tx_ready   => tx_ready,
            tx_out     => tx_out
        );

    stim_proc : process
    begin
        rst_n <= '0';
        wait for 20*CLK_PERIOD;
        rst_n <= '1';

        -- 0xA5 = 10100101
        wait until rising_edge(clk);
        data_in    <= x"A5";
        data_valid <= '1';

        wait until rising_edge(clk);
        data_valid <= '0';

        wait until tx_ready = '0';
        wait until tx_ready = '1';

        -- 0x3C = 00111100
        wait until rising_edge(clk);
        data_in    <= x"3C";
        data_valid <= '1';

        wait until rising_edge(clk);
        data_valid <= '0';

        wait for 3 ms;
        assert false report "END OF SIM" severity failure;
    end process;


end sim;
