import cocotb
from cocotb.handle import SimHandle
from cocotb.clock import Clock
from cocotb.triggers import Timer, RisingEdge
from spi.master import SpiMaster
from spi.slave import SpiSlave


class SpiTestbench:
    def __init__(self, dut: SimHandle):
        """Setup SPI transactor with design under test

        Args:
            dut (cocotb.module.Module): The DUT module.
        """
        # Design under test
        self.dut = dut

        # Clock generation (10ns period clock on port clk)
        self.clock = Clock(dut.clk, 10, units="ns")
        cocotb.start_soon(self.clock.start())  # Start the clock (Non blocking)

        # Master and slave devices
        self.master = SpiMaster(dut)
        self.slave = SpiSlave(dut)

    async def init(self):
        await self.reset()

    async def reset(self):
        """Resets the DUT."""
        self.dut.start_tx.value = 0
        self.dut.master_data_in.value = 0
        self.dut.slave_data_in.value = 0

        self.dut.rst.value = 1  # Assert reset
        await Timer(100, units="ns")  # Hold reset for a short period
        self.dut.rst.value = 0  # De-assert reset
        await RisingEdge(self.dut.clk)  # let signals propagate
