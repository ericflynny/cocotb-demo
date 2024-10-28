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
    master_data = 0xA5
    slave_data = 0x5A  # Data slave will send back
    
    # Prepare slave data
    await tb.spi_slave.send_data(slave_data)
    
    # Send data from master and get received data
    received_data = await tb.spi_master.send_data(master_data)
    
    # # Wait for slave to receive data
    # while True:
    #     if dut.slave_data_valid.value == 1:
    #         break
    #     await RisingEdge(dut.clk)
    
    # Check results
    # assert dut.slave_data_out.value == master_data, f"Slave received wrong data. Expected 0x{master_data:02X}, got 0x{int(dut.slave_data_out.value):02X}"
    assert received_data == slave_data, f"Master received wrong data. Expected 0x{slave_data:02X}, got 0x{int(received_data):02X}"