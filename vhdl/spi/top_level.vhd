library IEEE;
use IEEE.STD_LOGIC_1164.ALL;
use IEEE.NUMERIC_STD.ALL;

entity spi_top is
    generic (
        CLK_DIV : integer := 4;     -- System clock divider
        DATA_WIDTH : integer := 8    -- Data width in bits
    );
    port (
        -- System signals
        clk         : in  std_logic;
        rst         : in  std_logic;

        -- Control signals
        start_transfer : in  std_logic;
        cpol          : in  std_logic;
        cpha          : in  std_logic;

        -- Master data
        master_data_in  : in  std_logic_vector(DATA_WIDTH-1 downto 0);
        master_data_out : out std_logic_vector(DATA_WIDTH-1 downto 0);
        master_busy     : out std_logic;
        master_valid    : out std_logic;

        -- Slave data
        slave_data_in   : in  std_logic_vector(DATA_WIDTH-1 downto 0);
        slave_data_out  : out std_logic_vector(DATA_WIDTH-1 downto 0);
        slave_valid     : out std_logic
    );
end entity spi_top;

architecture rtl of spi_top is
    -- Internal SPI signals
    signal sclk_int : std_logic;
    signal mosi_int : std_logic;
    signal miso_int : std_logic;
    signal ss_n_int : std_logic;

begin
    -- Instantiate SPI Master
    master_inst : entity work.spi_master
        generic map (
            CLK_DIV => CLK_DIV,
            DATA_WIDTH => DATA_WIDTH
        )
        port map (
            clk => clk,
            rst => rst,
            enable => start_transfer,
            cpol => cpol,
            cpha => cpha,
            data_in => master_data_in,
            data_out => master_data_out,
            data_valid => master_valid,
            busy => master_busy,
            sclk => sclk_int,
            mosi => mosi_int,
            miso => miso_int,
            ss_n => ss_n_int
        );

    -- Instantiate SPI Slave
    slave_inst : entity work.spi_slave
        generic map (
            DATA_WIDTH => DATA_WIDTH
        )
        port map (
            clk => clk,
            rst => rst,
            cpol => cpol,
            cpha => cpha,
            data_in => slave_data_in,
            data_out => slave_data_out,
            data_valid => slave_valid,
            sclk => sclk_int,
            mosi => mosi_int,
            miso => miso_int,
            ss_n => ss_n_int
        );

end architecture rtl;