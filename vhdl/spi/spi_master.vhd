-- spi_master.vhdl
library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;
entity spi_master is
  generic (
    CLK_FREQ    : integer := 50_000_000;  -- System clock frequency in Hz
    SCLK_FREQ   : integer := 1_000_000;   -- SPI clock frequency in Hz
    DATA_WIDTH : integer := 8             -- SPI data width in bits
  );
  port (
    clk     : in  std_logic;
    reset   : in  std_logic;
    start   : in  std_logic;              -- Start SPI transaction
    ss      : out std_logic_vector(1 downto 0); -- Slave select (active low)
    mosi    : out std_logic;              -- Master Out Slave In
    miso    : in  std_logic;              -- Master In Slave Out
    tx_data : in  std_logic_vector(DATA_WIDTH-1 downto 0); -- Data to transmit
    rx_data : out std_logic_vector(DATA_WIDTH-1 downto 0); -- Received data
    done    : out std_logic;              -- Transaction complete
    sclk    : out std_logic               -- SPI clock output <--- Add this line
  );
end entity spi_master;

architecture behavioral of spi_master is

  type state_type is (IDLE, START_TRANSFER, SHIFT_DATA, STOP_TRANSFER);
  signal current_state : state_type := IDLE;

  signal sclk_counter : integer range 0 to CLK_FREQ/SCLK_FREQ/2-1 := 0;
  signal sclk_internal : std_logic := '0';
  signal bit_counter : integer range 0 to DATA_WIDTH-1 := 0;
  signal tx_reg : std_logic_vector(DATA_WIDTH-1 downto 0) := (others => '0');
  signal rx_reg : std_logic_vector(DATA_WIDTH-1 downto 0) := (others => '0');

begin

  -- Generate SPI clock
  process(clk)
  begin
    if rising_edge(clk) then
      if sclk_counter = CLK_FREQ/SCLK_FREQ/2-1 then
        sclk_counter <= 0;
        sclk_internal <= not sclk_internal;
      else
        sclk_counter <= sclk_counter + 1;
      end if;
    end if;
  end process;

  -- SPI state machine
  process(clk)
  begin
    if rising_edge(clk) then
      if reset = '1' then
        current_state <= IDLE;
        bit_counter <= 0;
        ss <= (others => '1');  -- Deselect all slaves
        done <= '0';
      else
        case current_state is
          when IDLE =>
            if start = '1' then
              current_state <= START_TRANSFER;
              tx_reg <= tx_data;
              bit_counter <= 0;
              done <= '0';
            end if;

          when START_TRANSFER =>
            ss <= "01";  -- Select slave 1 (modify for different slave)
            current_state <= SHIFT_DATA;

          when SHIFT_DATA =>
            if sclk_internal = '1' then  -- Capture data on rising edge
              rx_reg(bit_counter) <= miso;
            end if;
            if sclk_internal = '0' then  -- Shift data on falling edge
              mosi <= tx_reg(DATA_WIDTH-1 - bit_counter); 
              if bit_counter = DATA_WIDTH-1 then
                current_state <= STOP_TRANSFER;
              else
                bit_counter <= bit_counter + 1;
              end if;
            end if;

          when STOP_TRANSFER =>
            ss <= (others => '1');  -- Deselect slaves
            rx_data <= rx_reg;
            done <= '1';
            current_state <= IDLE;

        end case;
      end if;
    end if;
  end process;

  -- Output SPI clock
  sclk <= sclk_internal;

end architecture behavioral;