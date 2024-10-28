import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, FallingEdge, Timer


# TODO: Write class, needs reset, send data, read data etc

class Spi_Master:
    def __init__(self, dut):
        """Setup SPI master with design under test
        
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
        # Set master data
        self.dut.master_data_in.value = data
        
        # Start transmission
        await RisingEdge(self.dut.clk)
        self.dut.start_tx.value = 1
        await RisingEdge(self.dut.clk)
        self.dut.start_tx.value = 0
        
        # Wait for transmission to complete
        while True:
            await RisingEdge(self.dut.clk)
            if self.dut.master_busy.value == 0:
                break
                
        # Get received data
        received_data = self.dut.master_data_out.value
        
        return received_data