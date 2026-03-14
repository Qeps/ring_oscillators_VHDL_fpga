library IEEE;
use IEEE.STD_LOGIC_1164.ALL;

entity entropy_mixer is
    port (
        clk          : in std_logic;
        rst_l        : in std_logic;
        ro_sync      : in std_logic_vector(7 downto 0);
        uart_ready   : in std_logic;
        random_byte  : out std_logic_vector(7 downto 0);
        random_valid : out std_logic
    );
end;

architecture RTL of entropy_mixer is
    signal prev_vec      : std_logic_vector(7 downto 0) := (others => '0');
    signal have_first    : std_logic := '0';
    signal bit_fifo      : std_logic_vector(15 downto 0) := (others => '0');
    signal fifo_count    : integer range 0 to 16 := 0;
    signal random_byte_r : std_logic_vector(7 downto 0) := (others => '0');
    signal valid_r       : std_logic := '0';
begin

    process(clk)
        variable fifo_v : std_logic_vector(15 downto 0);
        variable cnt_v  : integer range 0 to 16;
    begin
        if rising_edge(clk) then
            if rst_l = '0' then
                prev_vec      <= (others => '0');
                have_first    <= '0';
                bit_fifo      <= (others => '0');
                fifo_count    <= 0;
                random_byte_r <= (others => '0');
                valid_r       <= '0';
    
            else
                valid_r <= '0';
    
                if have_first = '0' then
                    prev_vec   <= ro_sync;
                    have_first <= '1';
                else
                    fifo_v := bit_fifo;
                    cnt_v  := fifo_count;
    
                    for i in 0 to 7 loop
                        if prev_vec(i) = '0' and ro_sync(i) = '1' then
                            if cnt_v < 16 then
                                fifo_v(cnt_v) := '0';
                                cnt_v := cnt_v + 1;
                            end if;
                        elsif prev_vec(i) = '1' and ro_sync(i) = '0' then
                            if cnt_v < 16 then
                                fifo_v(cnt_v) := '1';
                                cnt_v := cnt_v + 1;
                            end if;
                        end if;
                    end loop;
    
                    if cnt_v >= 8 and uart_ready = '1' then
                        random_byte_r <= fifo_v(7 downto 0);
                        valid_r       <= '1';
    
                        for j in 0 to 7 loop
                            fifo_v(j) := fifo_v(j + 8);
                        end loop;
    
                        for j in 8 to 15 loop
                            fifo_v(j) := '0';
                        end loop;
    
                        cnt_v := cnt_v - 8;
                    end if;
    
                    bit_fifo   <= fifo_v;
                    fifo_count <= cnt_v;
                    have_first <= '0';
                end if;
            end if;
        end if;
    end process;
    
    random_byte  <= random_byte_r;
    random_valid <= valid_r;

end RTL;
