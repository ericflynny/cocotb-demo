import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, FallingEdge, Timer


# TODO: Write class, needs reset, send data, read data etc

class Spi_Slave:
    def __init__(self, dut: cocotb.module.Module):
        """Initialize the SPI slave with a 10 ns clock.
        
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
        self.dut.rst.value = 1
        await RisingEdge(self.dut.clk)
        self.dut.rst.value = 0
        await RisingEdge(self.dut.clk)

    async def send_data(self, data: int):
        """Send data over SPI.
        
        Args:
            data (int): The data to SPI slave from SPI master.

        Raises:
            None
        
        Returns:
            None
        """
        self.dut.mosi.value = data
        await RisingEdge(self.dut.clk)

    async def receive_data(self):
        """Receive data to SPI master from SPI slave.
        
        Args:
            None

        Raises:
            None
        
        Returns:
            None
        """
        await RisingEdge(self.dut.clk)
        return self.dut.miso.value