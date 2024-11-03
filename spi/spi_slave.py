import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, FallingEdge, Timer, ClockCycles

class SpiSlave:
  def __init__(self, dut):
      """Setup SPI slave with design under test
      
      Args:
          dut (cocotb.module.Module): The DUT module.
      """
      self.dut = dut
      self.data_width = 8  # 8-bit data width
      
  async def reset(self):
      """Reset the SPI slave
      """
      self.dut.rst.value = 1
      await ClockCycles(self.dut.clk, 2)
      self.dut.rst.value = 0
      await RisingEdge(self.dut.clk)
      self.dut.cs_n.value = 1
      self.dut.sclk.value = 0
      self.dut.mosi.value = 0
      
  async def write_data(self, data: int):
      """Write data to the SPI slave
      
      Args:
          data (int): 8-bit data to write to the slave
      """
      # Set up initial conditions
      self.dut.cs_n.value = 1
      self.dut.sclk.value = 0
      await RisingEdge(self.dut.clk)
      
      # Load data to transmit
      self.dut.data_in.value = data
      
      # Start transaction
      self.dut.cs_n.value = 0
      await RisingEdge(self.dut.clk)
      
      # Transmit 8 bits
      for i in range(self.data_width):
          bit = (data >> (self.data_width - 1 - i)) & 0x1
          
          # Setup bit on MOSI
          self.dut.mosi.value = bit
          await RisingEdge(self.dut.clk)
          
          # Rising edge of SCLK
          self.dut.sclk.value = 1
          await RisingEdge(self.dut.clk)
          
          # Falling edge of SCLK
          self.dut.sclk.value = 0
          await RisingEdge(self.dut.clk)
          
      # End transaction
      await RisingEdge(self.dut.clk)
      self.dut.cs_n.value = 1
      
  async def read_data(self) -> int:
      """Read data from the SPI slave
      
      Returns:
          int: Received 8-bit data
      """
      # Wait for data_valid
      while self.dut.data_valid.value == 0:
          await RisingEdge(self.dut.clk)
          
      # Read the received data
      data = int(self.dut.data_out.value)
      return data
  
  async def transfer(self, write_data: int) -> int:
      """Perform a full SPI transfer (write and read)
      
      Args:
          write_data (int): Data to write to slave
          
      Returns:
          int: Data read from slave
      """
      await self.write_data(write_data)
      return await self.read_data()
  
  async def wait_for_idle(self):
      """Wait for the SPI slave to return to idle state
      """
      while True:
          if self.dut.cs_n.value == 1:
              break
          await RisingEdge(self.dut.clk)

# Example test function
@cocotb.test()
async def test_spi_slave(dut):
  """Test SPI slave functionality"""
  
  # Create clock
  clock = Clock(dut.clk, 10, units="ns")
  cocotb.start_soon(clock.start())
  
  # Create SPI slave object
  spi = SpiSlave(dut)
  
  # Reset
  await spi.reset()
  
  # Test transfers
  test_data = 0x5A
  received_data = await spi.transfer(test_data)
  
  # Verify received data
  assert received_data == test_data, f"Expected {test_data:02X}, got {received_data:02X}"