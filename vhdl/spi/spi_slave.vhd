library IEEE;
use IEEE.STD_LOGIC_1164.ALL;
use IEEE.NUMERIC_STD.ALL;

entity spi_slave is
    generic (
        DATA_WIDTH : integer := 8  -- Data width in bits
    );
    port (
        clk          : in  std_logic;
        rst          : in  std_logic;
        -- Control signals
        data_valid   : out std_logic;
        -- Data signals
        data_in      : in  std_logic_vector(DATA_WIDTH-1 downto 0);
        data_out     : out std_logic_vector(DATA_WIDTH-1 downto 0);
        -- SPI signals
        sclk         : in  std_logic;
        mosi         : in  std_logic;
        miso         : out std_logic;
        cs_n         : in  std_logic
    );
end spi_slave;

architecture Behavioral of spi_slave is
    signal shift_reg : std_logic_vector(DATA_WIDTH-1 downto 0);
    signal bit_counter : integer range 0 to DATA_WIDTH-1;
    signal data_valid_int : std_logic;
begin
    process(clk, rst)
    begin
        if rst = '1' then
            shift_reg <= (others => '0');
            bit_counter <= DATA_WIDTH-1;
            data_valid_int <= '0';
            
        elsif rising_edge(clk) then
            data_valid_int <= '0';
            
            if cs_n = '0' then  -- Chip select active
                if rising_edge(sclk) then  -- Sample MOSI
                    shift_reg <= shift_reg(DATA_WIDTH-2 downto 0) & mosi;
                    
                    if bit_counter = 0 then
                        bit_counter <= DATA_WIDTH-1;
                        data_out <= shift_reg;
                        data_valid_int <= '1';
                    else
                        bit_counter <= bit_counter - 1;
                    end if;
                end if;
            else
                bit_counter <= DATA_WIDTH-1;
                shift_reg <= data_in;  -- Load new data to send
            end if;
        end if;
    end process;

    miso <= shift_reg(DATA_WIDTH-1) when cs_n = '0' else 'Z';
    data_valid <= data_valid_int;
end Behavioral;