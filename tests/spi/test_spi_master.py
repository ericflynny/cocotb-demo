import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, FallingEdge, Timer

@cocotb.test()
async def spi_test(dut):
    clock = Clock(dut.clk, 10, units="ns")  # Create a 10ns clock
    cocotb.start_soon(clock.start())

    