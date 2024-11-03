import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, FallingEdge, Timer
from testbench_spi import SPI_Testbench


@cocotb.test()
async def spi_test(dut):
    """Test data transfer from master to slave"""
    tb = SPI_Testbench(dut)
    await tb.init()
    await tb.reset()
    
    # Test data
    data = 0x0F
    
    # Send data from master and get received data
    await tb.spi_master.write_data(data)
    received_data = await tb.spi_slave.read_data()
    
    # Check results
    assert received_data == data, f"Master received wrong data. Expected {data}, got {received_data}"


@cocotb.test()
async def test_spi_master(dut):
  """Test SPI master functionality"""
  tb = SPI_Testbench(dut)
  await tb.init()
  
  # Create clock
  clock = Clock(dut.clk, 10, units="ns")
  cocotb.start_soon(clock.start())
  
  # Reset
  await tb.spi_slave.reset()
  
  # Test transfers
  test_data = [0x5A, 0xA5, 0xFF, 0x00]
  for data in test_data:
      received = await tb.spi_slave.transfer(data)
      await tb.spi_slave.wait_for_idle()
      
      # Verify received data
      assert received == data, f"Expected {data:02X}, got {received:02X}"