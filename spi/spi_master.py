import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, FallingEdge, Timer, ClockCycles

class Spi_Master:
  def __init__(self, dut):
      """Setup SPI master with design under test
      
      Args:
          dut (cocotb.module.Module): The DUT module.
      """
      self.dut = dut
      self.data_width = 8  # 8-bit data width
      self.clock_period = 10  # ns
      
  async def reset(self):
      """Reset the SPI master
      """
      self.dut.master_inst.rst.value = 1
      self.dut.master_inst.cs_n.value = 1
      self.dut.master_inst.sclk.value = 0
      self.dut.master_inst.mosi.value = 0
      await ClockCycles(self.dut.clk, 2)
      self.dut.master_inst.rst.value = 0
      await RisingEdge(self.dut.clk)
      
  async def write_data(self, data: int, timeout: int = 100):
      """Send data to SPI slave
      
      Args:
          data (int): 8-bit data to send
          timeout (int): Maximum clock cycles to wait for completion
          
      Returns:
          int: Received data from slave
          
      Raises:
          TimeoutError: If transmission takes longer than timeout
      """
      # Set initial state
      self.dut.master_inst.cs_n.value = 1
      self.dut.master_inst.sclk.value = 0
      await RisingEdge(self.dut.clk)
      
      # Load transmit data
      self.dut.master_inst.data_in.value = data
      await RisingEdge(self.dut.clk)
      
      # Start transmission
      self.dut.master_inst.cs_n.value = 0
      await RisingEdge(self.dut.clk)
      
      # Transmit 8 bits
      for i in range(self.data_width):
          bit = (data >> (self.data_width - 1 - i)) & 0x1
          
          # Setup MOSI
          self.dut.master_inst.mosi.value = bit
          await RisingEdge(self.dut.master_inst.clk)
          
          # SCLK rising edge
          self.dut.master_inst.sclk.value = 1
          await RisingEdge(self.dut.master_inst.clk)
          
          # Sample MISO on SCLK rising edge
          miso_bit = int(self.dut.master_inst.miso.value)
          
          # SCLK falling edge
          self.dut.master_inst.sclk.value = 0
          await RisingEdge(self.dut.master_inst.clk)
      
      # End transmission
      await RisingEdge(self.dut.master_inst.clk)
      self.dut.master_inst.cs_n.value = 1
      
      # Wait for busy to clear
      for _ in range(timeout):
          if not self.dut.master_inst.busy.value:
              return self.dut.master_inst.data_out.value
          await RisingEdge(self.dut.master_inst.clk)
          
      raise TimeoutError("SPI Master Timeout: Transfer did not complete")

  async def read_data(self) -> int:
      """Read last received data
      
      Returns:
          int: Last received 8-bit data
      """
      return self.dut.master_inst.data_out.value
  
  async def transfer(self, write_data: int) -> int:
      """Perform full-duplex SPI transfer
      
      Args:
          write_data (int): Data to write to slave
          
      Returns:
          int: Data read from slave
      """
      return await self.write_data(write_data)
  
  async def wait_for_idle(self):
      """Wait for master to return to idle state
      """
      while True:
          if not self.dut.master_inst.busy.value and self.dut.master_inst.cs_n.value == 1:
              break
          await RisingEdge(self.dut.clk)

