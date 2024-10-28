import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, FallingEdge, Timer
from testbench_spi import SPI_Testbench


@cocotb.test()
async def spi_test(dut):
    Spi = SPI_Testbench(dut)
    await Spi.reset()


    # Test data
    test_data = 0x5A 

    # Select slave 1 (modify for slave 2)
    dut.cs_n.value = 0
    await RisingEdge(dut.clk)

    # Send data
    dut.mosi.value = test_data
    await RisingEdge(dut.clk)

    # Check received data
    assert dut.miso.value == test_data

    # Deselect slave
    dut.cs_n.value = 1
    await RisingEdge(dut.clk)