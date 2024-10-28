library IEEE;
use IEEE.STD_LOGIC_1164.ALL;
use IEEE.NUMERIC_STD.ALL;

entity spi_master is
    generic (
        CLK_DIV : integer := 4;  -- System clock divider to generate SCLK
        DATA_WIDTH : integer := 8 -- Data width in bits
    );
    port (
        clk          : in  std_logic;
        rst          : in  std_logic;
        -- Control signals
        start_tx     : in  std_logic;
        busy         : out std_logic;
        -- Data signals
        data_in      : in  std_logic_vector(DATA_WIDTH-1 downto 0);
        data_out     : out std_logic_vector(DATA_WIDTH-1 downto 0);
        -- SPI signals
        sclk         : out std_logic;
        mosi         : out std_logic;
        miso         : in  std_logic;
        cs_n         : out std_logic
    );
end spi_master;

architecture Behavioral of spi_master is
    type state_type is (IDLE, TRANSFER);
    signal state : state_type;
    
    signal bit_counter : integer range 0 to DATA_WIDTH-1;
    signal clk_counter : integer range 0 to CLK_DIV-1;
    signal shift_reg   : std_logic_vector(DATA_WIDTH-1 downto 0);
    signal sclk_int    : std_logic;
    signal active      : std_logic;
begin
    process(clk, rst)
    begin
        if rst = '1' then
            state <= IDLE;
            bit_counter <= DATA_WIDTH-1;
            clk_counter <= 0;
            shift_reg <= (others => '0');
            sclk_int <= '0';
            active <= '0';
            cs_n <= '1';
            busy <= '0';
            
        elsif rising_edge(clk) then
            case state is
                when IDLE =>
                    if start_tx = '1' then
                        state <= TRANSFER;
                        shift_reg <= data_in;
                        active <= '1';
                        cs_n <= '0';
                        busy <= '1';
                    end if;
                    
                when TRANSFER =>
                    if clk_counter = CLK_DIV-1 then
                        clk_counter <= 0;
                        sclk_int <= not sclk_int;
                        
                        if sclk_int = '1' then  -- Sample MISO on rising edge
                            shift_reg <= shift_reg(DATA_WIDTH-2 downto 0) & miso;
                        end if;
                        
                        if sclk_int = '0' and bit_counter = 0 then  -- End of transfer
                            state <= IDLE;
                            active <= '0';
                            cs_n <= '1';
                            busy <= '0';
                            data_out <= shift_reg;
                            bit_counter <= DATA_WIDTH-1;
                        elsif sclk_int = '0' then
                            bit_counter <= bit_counter - 1;
                        end if;
                    else
                        clk_counter <= clk_counter + 1;
                    end if;
            end case;
        end if;
    end process;

    sclk <= sclk_int when active = '1' else '0';
    mosi <= shift_reg(DATA_WIDTH-1) when active = '1' else '0';
end Behavioral;