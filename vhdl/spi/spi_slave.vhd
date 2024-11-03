library IEEE;
use IEEE.STD_LOGIC_1164.ALL;
use IEEE.NUMERIC_STD.ALL;

entity spi_slave is
    generic (
        DATA_WIDTH : integer := 8
    );
    port (
        clk : in std_logic;
        rst : in std_logic;
        data_valid : out std_logic;
        data_in : in std_logic_vector(DATA_WIDTH-1 downto 0);
        data_out : out std_logic_vector(DATA_WIDTH-1 downto 0);
        sclk : in std_logic;
        mosi : in std_logic;
        miso : out std_logic;
        cs_n : in std_logic
    );
end spi_slave;

architecture Behavioral of spi_slave is
    type state_type is (IDLE, TRANSFER);
    signal state : state_type;
    signal shift_reg_rx : std_logic_vector(DATA_WIDTH-1 downto 0);
    signal shift_reg_tx : std_logic_vector(DATA_WIDTH-1 downto 0);
    signal bit_counter : integer range 0 to DATA_WIDTH-1;
    signal data_valid_int : std_logic;
    signal sclk_prev : std_logic;
    signal cs_n_prev : std_logic;
    signal transfer_active : std_logic;
begin
    process(clk, rst)
    begin
        if rst = '1' then
            shift_reg_rx <= (others => '0');
            shift_reg_tx <= (others => '0');
            bit_counter <= DATA_WIDTH-1;
            data_valid_int <= '0';
            sclk_prev <= '0';
            cs_n_prev <= '1';
            data_out <= (others => '0');
            state <= IDLE;
            transfer_active <= '0';
            
        elsif rising_edge(clk) then
            -- Edge detection
            sclk_prev <= sclk;
            cs_n_prev <= cs_n;
            
            -- Default assignments
            data_valid_int <= '0';
            
            -- Detect CS_N falling edge to start transfer
            if cs_n_prev = '1' and cs_n = '0' then
                transfer_active <= '1';
                shift_reg_tx <= data_in;
                bit_counter <= DATA_WIDTH-1;
                state <= TRANSFER;
            end if;
            
            -- Detect CS_N rising edge to end transfer
            if cs_n_prev = '0' and cs_n = '1' then
                transfer_active <= '0';
                state <= IDLE;
            end if;
            
            if transfer_active = '1' then
                -- Sample MOSI on rising edge of SCLK
                if sclk_prev = '0' and sclk = '1' then
                    shift_reg_rx <= shift_reg_rx(DATA_WIDTH-2 downto 0) & mosi;
                    
                    if bit_counter = 0 then
                        data_valid_int <= '1';
                        data_out <= shift_reg_rx(DATA_WIDTH-2 downto 0) & mosi;
                        bit_counter <= DATA_WIDTH-1;
                    else
                        bit_counter <= bit_counter - 1;
                    end if;
                
                -- Update MISO on falling edge of SCLK
                elsif sclk_prev = '1' and sclk = '0' then
                    if bit_counter = DATA_WIDTH-1 then
                        shift_reg_tx <= data_in;
                    else
                        shift_reg_tx <= shift_reg_tx(DATA_WIDTH-2 downto 0) & '0';
                    end if;
                end if;
            end if;
        end if;
    end process;

    -- Drive MISO output
    miso <= shift_reg_tx(DATA_WIDTH-1) when cs_n = '0' else 'Z';
    data_valid <= data_valid_int;
    
end Behavioral;