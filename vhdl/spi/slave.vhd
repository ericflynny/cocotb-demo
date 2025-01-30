library IEEE;
use IEEE.STD_LOGIC_1164.ALL;
use IEEE.NUMERIC_STD.ALL;

entity spi_slave is
    generic (
        DATA_WIDTH : integer := 8  -- Data width in bits
    );
    port (
        -- Control signals
        clk         : in  std_logic;
        rst         : in  std_logic;
        cpol        : in  std_logic;  -- Clock polarity
        cpha        : in  std_logic;  -- Clock phase
        
        -- Data signals
        data_in     : in  std_logic_vector(DATA_WIDTH-1 downto 0);
        data_out    : out std_logic_vector(DATA_WIDTH-1 downto 0);
        data_valid  : out std_logic;
        
        -- SPI interface
        sclk        : in  std_logic;
        mosi        : in  std_logic;
        miso        : out std_logic;
        ss_n        : in  std_logic
    );
end entity spi_slave;

architecture rtl of spi_slave is
    type state_type is (IDLE, TRANSFER);
    signal state : state_type;
    
    signal bit_counter : integer range 0 to DATA_WIDTH-1;
    signal shift_reg : std_logic_vector(DATA_WIDTH-1 downto 0);
    signal sclk_prev : std_logic;
    signal ss_n_prev : std_logic;
    signal transfer_active : std_logic;
    
begin
    process(clk, rst)
    begin
        if rst = '1' then
            state <= IDLE;
            bit_counter <= DATA_WIDTH-1;
            shift_reg <= (others => '0');
            sclk_prev <= cpol;
            ss_n_prev <= '1';
            transfer_active <= '0';
            data_valid <= '0';
            miso <= '0';
            
        elsif rising_edge(clk) then
            -- Edge detection
            sclk_prev <= sclk;
            ss_n_prev <= ss_n;
            
            case state is
                when IDLE =>
                    data_valid <= '0';
                    
                    -- Start transfer on falling edge of SS_N
                    if ss_n_prev = '1' and ss_n = '0' then
                        state <= TRANSFER;
                        shift_reg <= data_in;
                        bit_counter <= DATA_WIDTH-1;
                        transfer_active <= '1';
                        miso <= data_in(DATA_WIDTH-1);
                    end if;
                    
                when TRANSFER =>
                    -- Handle CPOL/CPHA combinations
                    if ((cpha = '0' and sclk_prev /= sclk and sclk = '1') or
                        (cpha = '1' and sclk_prev /= sclk and sclk = '0')) then
                        -- Sample MOSI
                        shift_reg <= shift_reg(DATA_WIDTH-2 downto 0) & mosi;
                        
                        if bit_counter = 0 then
                            data_valid <= '1';
                            data_out <= shift_reg(DATA_WIDTH-2 downto 0) & mosi;
                            if ss_n = '1' then
                                state <= IDLE;
                                transfer_active <= '0';
                            else
                                bit_counter <= DATA_WIDTH-1;
                                shift_reg <= data_in;
                            end if;
                        else
                            bit_counter <= bit_counter - 1;
                        end if;
                        
                    elsif ((cpha = '0' and sclk_prev /= sclk and sclk = '0') or
                           (cpha = '1' and sclk_prev /= sclk and sclk = '1')) then
                        -- Set up next MISO bit
                        miso <= shift_reg(DATA_WIDTH-1);
                    end if;
                    
                    -- Handle SS_N deassert
                    if ss_n = '1' then
                        state <= IDLE;
                        transfer_active <= '0';
                    end if;
            end case;
        end if;
    end process;
    
end architecture rtl;