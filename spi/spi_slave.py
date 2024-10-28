import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, FallingEdge, Timer


# TODO: Write class, needs reset, send data, read data etc

class Spi_Slave:
    def __init__(self, dut):
        """Setup SPI slave with design under test
        
        Args:
            dut (cocotb.module.Module): The DUT module.

        Raises:
            None
        
        Returns:
            None
        """
        self.dut = dut

    async def send_data(self, data: int):
        """Prepare slave to send data back to master
        
        Args:
            data (int): The data to SPI slave from SPI master.

        Raises:
            None
        
        Returns:
            None
        """
        self.dut.slave_data_in.value = data
        await RisingEdge(self.dut.clk)