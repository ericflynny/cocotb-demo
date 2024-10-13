-- spi_top.vhd
library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;

entity spi_top_level is
  generic (
    CLK_FREQ    : integer := 50_000_000;  -- System clock frequency in Hz
    SCLK_FREQ   : integer := 1_000_000;   -- SPI clock frequency in Hz
    DATA_WIDTH : integer := 8             -- SPI data width in bits
  );
  port (
    clk     : in  std_logic;
    reset   : in  std_logic;
    start   : in  std_logic;              -- Start SPI transaction
    tx_data : in  std_logic_vector(DATA_WIDTH-1 downto 0); -- Data to transmit
    rx_data_slave1 : out std_logic_vector(DATA_WIDTH-1 downto 0); -- Received data from slave 1
    rx_data_slave2 : out std_logic_vector(DATA_WIDTH-1 downto 0); -- Received data from slave 2
    done    : out std_logic               -- Transaction complete
  );
end entity spi_top_level;

architecture structural of spi_top_level is

  -- Component declarations for master and slaves
  component spi_master is
    generic (
      CLK_FREQ    : integer := 50_000_000;
      SCLK_FREQ   : integer := 1_000_000;
      DATA_WIDTH : integer := 8
    );
    port (
      clk     : in  std_logic;
      reset   : in  std_logic;
      start   : in  std_logic;
      ss      : out std_logic_vector(1 downto 0);
      mosi    : out std_logic;
      miso    : in  std_logic;
      tx_data : in  std_logic_vector(DATA_WIDTH-1 downto 0);
      rx_data : out std_logic_vector(DATA_WIDTH-1 downto 0);
      done    : out std_logic;
      sclk    : out std_logic
    );
  end component;

  component spi_slave is
    generic (
      DATA_WIDTH : integer := 8
    );
    port (
      sclk : in  std_logic;
      ss   : in  std_logic;
      mosi : in  std_logic;
      miso : out std_logic;
      data_out : out std_logic_vector(DATA_WIDTH-1 downto 0)
    );
  end component;

  -- Internal signals
  signal master_ss : std_logic_vector(1 downto 0);
  signal master_mosi : std_logic;
  signal master_miso : std_logic;
  signal master_sclk : std_logic;

begin

  -- Instantiate the SPI master
  spi_master_inst : entity work.spi_master
    generic map (
      CLK_FREQ => CLK_FREQ,
      SCLK_FREQ => SCLK_FREQ,
      DATA_WIDTH => DATA_WIDTH
    )
    port map (
      clk     => clk,
      reset   => reset,
      start   => start,
      ss      => master_ss,
      mosi    => master_mosi,
      miso    => master_miso,
      tx_data => tx_data,
      rx_data => rx_data_slave1, -- Connect to slave 1's output
      done    => done,
      sclk    => master_sclk
    );

  -- Instantiate SPI slave 1
  spi_slave1_inst : entity work.spi_slave
    generic map (
      DATA_WIDTH => DATA_WIDTH
    )
    port map (
      sclk => master_sclk,
      ss   => master_ss(0), -- Connect to master's SS0
      mosi => master_mosi,
      miso => master_miso,
      data_out => rx_data_slave1
    );

  -- Instantiate SPI slave 2
  spi_slave2_inst : entity work.spi_slave
    generic map (
      DATA_WIDTH => DATA_WIDTH
    )
    port map (
      sclk => master_sclk,
      ss   => master_ss(1), -- Connect to master's SS1
      mosi => master_mosi,
      miso => master_miso,
      data_out => rx_data_slave2
    );

end architecture structural;
