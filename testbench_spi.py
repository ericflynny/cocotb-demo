import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, FallingEdge, Timer
from spi.spi_slave import Spi_Slave
from spi.spi_master import Spi_Master


class SPI_Testbench:
    def __init__(self, dut):
        """Initialize the SPI testbench with a 10 ns clock.
        
        Args:
            dut (cocotb.module.Module): The DUT module.

        Raises:
            None
        
        Returns:
            None
        """
        self.dut = dut
        self.clock = Clock(dut.clk, 10, units="ns")
        cocotb.start_soon(self.clock.start())
        self.spi_slave = Spi_Slave(dut)
        self.spi_master = Spi_Master(dut)


    async def init(self):
        """Reset to begin normal operation.
        
        Args:
            None

        Raises:
            None
        
        Returns:
            None
        """
        self.reset()


    async def reset(self):
        """Reset the DUT.
        
        Args:
            None

        Raises:
            None
        
        Returns:
            None
        """
        self.dut.rst.value = 0
        self.dut.start_tx.value = 0
        self.dut.master_data_in.value = 0
        self.dut.slave_data_in.value = 0
        
        # Hold reset for 2 clock cycles
        for _ in range(2):
            await RisingEdge(self.dut.clk)
        self.dut.rst.value = 1
        for _ in range(2):
            await RisingEdge(self.dut.clk)
        self.dut.rst.value = 0
        for _ in range(2):
            await RisingEdge(self.dut.clk)