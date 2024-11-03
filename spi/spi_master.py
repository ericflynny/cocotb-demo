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
        """Send data one byte at a time with timeout
        
        Args:
            data (int): The data to send to SPI slave.
            timeout (int, optional): Timeout in clock cycles. Defaults to 10.

        Raises:
            TimeoutError: If transmission takes longer than timeout.
        
        Returns:
            int: The data received from the slave.
        """

        # First set the data
        self.dut.master_inst.data_in.value = data
        await RisingEdge(self.dut.clk)

        # Then start transmission
        self.dut.master_inst.start_tx.value = 1
        await RisingEdge(self.dut.clk)
        self.dut.master_inst.start_tx.value = 0

        # Wait for transmission to complete (with timeout)
        timeout = 100 # 60 clock cycles to complete transmission
        for _ in range(timeout):
            await RisingEdge(self.dut.clk)
            if self.dut.master_inst.busy.value == 0:
                for _ in range(timeout):
                    await RisingEdge(self.dut.clk)
                return self.dut.master_inst.data_out.value  # Transmission successful

        raise TimeoutError("SPI Master Timeout: Data transmission took too long.")

    async def read_data(self) -> int:
        """ Read data

        Args:
            None

        Raises:
            None
        
        Returns:
            None
        """
        return self.dut.master_inst.data_in.value