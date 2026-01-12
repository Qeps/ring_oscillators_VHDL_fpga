library IEEE;
use IEEE.STD_LOGIC_1164.ALL;
use IEEE.NUMERIC_STD.ALL;

entity tb_shift_reg is
end tb_shift_reg;

architecture sim of tb_shift_reg is

    signal clk        : std_logic := '0';
    signal rst_n      : std_logic := '0';
    signal random_bit : std_logic := '0';
    signal tx_ready   : std_logic := '0';

    signal byte_out   : std_logic_vector(7 downto 0);
    signal byte_valid : std_logic;

    constant CLK_PERIOD : time := 10 ns;

    constant BYTE1 : std_logic_vector(7 downto 0) := "11011111";
    constant BYTE2 : std_logic_vector(7 downto 0) := "10100011";

    procedure send_bit(
        signal bit_sig : out std_logic;
        constant b     : in  std_logic
    ) is
    begin
        bit_sig <= b;
        wait until rising_edge(clk);
    end procedure;

begin

    clk <= not clk after CLK_PERIOD/2;

    dut : entity work.shift_reg
        port map (
            clk        => clk,
            rst_n      => rst_n,
            random_bit => random_bit,
            tx_ready   => tx_ready,
            byte_out   => byte_out,
            byte_valid => byte_valid
        );

    stim_proc : process
    begin
        rst_n <= '0';
        tx_ready <= '0';
        random_bit <= '0';
        wait for 30 ns;
        rst_n <= '1';

        for i in 7 downto 0 loop
            send_bit(random_bit, BYTE1(i));
        end loop;

        wait until byte_valid = '1';

        send_bit(random_bit, '0');

        tx_ready <= '1';
        wait until rising_edge(clk);
        tx_ready <= '0';

        wait until byte_valid = '0';

        send_bit(random_bit, '1');

        for i in 7 downto 0 loop
            send_bit(random_bit, BYTE2(i));
        end loop;

        wait until byte_valid = '1';

        tx_ready <= '1';
        wait until rising_edge(clk);
        tx_ready <= '0';

        wait until byte_valid = '0';

    end process;

end sim;
