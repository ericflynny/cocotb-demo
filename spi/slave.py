from cocotb.triggers import RisingEdge


class SpiSlave:
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
        """Prepare slave to send data back to master.

        Args:
            data (int): The data for the slave to send.
        """
        self.dut.slave_data_in.value = data
        await RisingEdge(self.dut.clk)

    async def get_received_data(self, timeout=1000):
        """Retrieve the data received by the slave.

        Args:
            timeout: The maximum number of clock cycles to wait for valid data.

        Returns:
            The received data.

        Raises:
            TimeoutError: If no valid data is received within the timeout period.
        """
        count = 0
        while True:
            count += 1
            if count < timeout:
                await RisingEdge(self.dut.clk)
                if self.dut.slave_data_valid.value == 1:
                    return self.dut.slave_data_out.value
            else:
                raise TimeoutError("Slave timed out waiting for valid data")
