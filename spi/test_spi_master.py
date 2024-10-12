import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, FallingEdge, Timer

@cocotb.test()
async def spi_test(dut):
    clock = Clock(dut.clk, 10, units="ns")  # Create a 10ns clock
    cocotb.start_soon(clock.start())

    dut.reset.value = 1
    await RisingEdge(dut.clk)
    dut.reset.value = 0

    # Test data
    test_data = 0x5A 

    # Select slave 1 (modify for slave 2)
    dut.