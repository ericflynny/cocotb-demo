-- spi_slave.vhdl
library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;

entity spi_slave is
  generic (
    DATA_WIDTH : integer := 8  -- SPI data width in bits
  );
  port (
    sclk : in  std_logic;
    ss   : in  std_logic;
    mosi : in  std_logic;
    miso : out std_logic;
    data_out : out std_logic_vector(DATA_WIDTH-1 downto 0) -- Data to output
  );
end entity spi_slave;

architecture behavioral of spi_slave is

  signal shift_reg : std_logic_vector(DATA_WIDTH-1 downto 0) := (others => '0');
  signal bit_counter : integer range 0 to DATA_WIDTH-1 := 0;

begin

  process(sclk, ss)
  begin
    if falling_edge(ss) then  -- Reset on slave select assert
      bit_counter <= 0;
      shift_reg <= (others => '0');
    elsif rising_edge(sclk) then
      if ss = '0' then  -- Only shift when slave is selected
        shift_reg <= shift_reg(DATA_WIDTH-2 downto 0) & mosi; 
        if bit_counter = DATA_WIDTH-1 then
          data_out <= shift_reg;
          bit_counter <= 0;
        else
          bit_counter <= bit_counter + 1;
        end if;
      end if;
    end if;
  end process;

  -- Output data on MISO (with a small delay for timing)
  process(sclk)
  begin
    if falling_edge(sclk) then
      if ss = '0' then
        miso <= shift_reg(DATA_WIDTH-1);
      else
        miso <= 'Z'; -- High impedance when not selected
      end if;
    end if;
  end process;

end architecture behavioral;