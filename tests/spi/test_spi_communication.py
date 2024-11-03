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
    await tb.spi_master.send_data(data)
    received_data = tb.spi_slave.read_data()
    
    # Check results
    assert received_data == data, f"Master received wrong data. Expected 0x{data:02X}, got 0x{int(received_data):02X}"