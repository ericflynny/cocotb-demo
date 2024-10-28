library IEEE;
use IEEE.STD_LOGIC_1164.ALL;

entity spi_top_level is
    generic (
        CLK_DIV : integer := 4;     -- System clock divider
        DATA_WIDTH : integer := 8    -- Data width in bits
    );
    port (
        clk           : in  std_logic;
        rst           : in  std_logic;
        -- Master interface
        start_tx      : in  std_logic;
        master_data_in  : in  std_logic_vector(DATA_WIDTH-1 downto 0);
        master_data_out : out std_logic_vector(DATA_WIDTH-1 downto 0);
        master_busy     : out std_logic;
        -- Slave interface
        slave_data_in   : in  std_logic_vector(DATA_WIDTH-1 downto 0);
        slave_data_out  : out std_logic_vector(DATA_WIDTH-1 downto 0);
        slave_data_valid : out std_logic
    );
end spi_top_level;

architecture Behavioral of spi_top_level is
    -- Internal SPI signals
    signal sclk_int : std_logic;
    signal mosi_int : std_logic;
    signal miso_int : std_logic;
    signal cs_n_int : std_logic;
    
    -- Component declarations
    component spi_master is
        generic (
            CLK_DIV : integer := 4;
            DATA_WIDTH : integer := 8
        );
        port (
            clk          : in  std_logic;
            rst          : in  std_logic;
            start_tx     : in  std_logic;
            busy         : out std_logic;
            data_in      : in  std_logic_vector(DATA_WIDTH-1 downto 0);
            data_out     : out std_logic_vector(DATA_WIDTH-1 downto 0);
            sclk         : out std_logic;
            mosi         : out std_logic;
            miso         : in  std_logic;
            cs_n         : out std_logic
        );
    end component;

    component spi_slave is
        generic (
            DATA_WIDTH : integer := 8
        );
        port (
            clk          : in  std_logic;
            rst          : in  std_logic;
            data_valid   : out std_logic;
            data_in      : in  std_logic_vector(DATA_WIDTH-1 downto 0);
            data_out     : out std_logic_vector(DATA_WIDTH-1 downto 0);
            sclk         : in  std_logic;
            mosi         : in  std_logic;
            miso         : out std_logic;
            cs_n         : in  std_logic
        );
    end component;

begin
    -- Instantiate SPI Master
    master_inst : spi_master
        generic map (
            CLK_DIV => CLK_DIV,
            DATA_WIDTH => DATA_WIDTH
        )
        port map (
            clk => clk,
            rst => rst,
            start_tx => start_tx,
            busy => master_busy,
            data_in => master_data_in,
            data_out => master_data_out,
            sclk => sclk_int,
            mosi => mosi_int,
            miso => miso_int,
            cs_n => cs_n_int
        );

    -- Instantiate SPI Slave
    slave_inst : spi_slave
        generic map (
            DATA_WIDTH => DATA_WIDTH
        )
        port map (
            clk => clk,
            rst => rst,
            data_valid => slave_data_valid,
            data_in => slave_data_in,
            data_out => slave_data_out,
            sclk => sclk_int,
            mosi => mosi_int,
            miso => miso_int,
            cs_n => cs_n_int
        );

end Behavioral;