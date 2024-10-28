import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, FallingEdge, Timer
from testbench_spi import SPI_Testbench


@cocotb.test()
async def spi_test(dut):
    tb = SPI_Testbench(dut)
    await tb.init(dut)