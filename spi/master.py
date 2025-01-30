from cocotb.triggers import RisingEdge


class SpiMaster:
    def __init__(self, dut):
        """Setup SPI master with design under test

        Args:
            dut (cocotb.module.Module): The DUT module.
            
        The DUT should have the following signals:
        - clk: System clock
        - rst: Reset signal
        - start_transfer: Signal to start SPI transfer
        - master_data_in: Input data to master
        - master_data_out: Output data from master
        - master_busy: Busy signal from master
        - master_valid: Data valid signal from master
        """
        self.dut = dut
        self.data_width = len(self.dut.master_data_in)
        
        # Initialize default values
        self.dut.start_transfer.value = 0
        self.dut.master_data_in.value = 0
        self.dut.cpol.value = 0
        self.dut.cpha.value = 0

    async def reset(self):
        """Reset the SPI master"""
        self.dut.rst.value = 1
        await RisingEdge(self.dut.clk)
        await RisingEdge(self.dut.clk)
        self.dut.rst.value = 0
        await RisingEdge(self.dut.clk)

    async def configure_mode(self, cpol: int = 0, cpha: int = 0):
        """Configure SPI mode using CPOL and CPHA

        Args:
            cpol: Clock polarity (0 or 1)
            cpha: Clock phase (0 or 1)
        """
        self.dut.cpol.value = cpol
        self.dut.cpha.value = cpha
        await RisingEdge(self.dut.clk)

    async def send_data(self, data: int, timeout: int = 1000) -> int:
        """Send data from master and return received data.

        Args:
            data: The data to send (integer value)
            timeout: Maximum number of clock cycles to wait for transfer

        Returns:
            Integer value of received data

        Raises:
            TimeoutError: If transfer doesn't complete within timeout
            ValueError: If data exceeds data width
        """
        # Validate data width
        if data.bit_length() > self.data_width:
            raise ValueError(f"Data {data} exceeds data width of {self.data_width} bits")

        # Set up data to send
        self.dut.master_data_in.value = data
        await RisingEdge(self.dut.clk)

        # Start transfer
        self.dut.start_transfer.value = 1
        await RisingEdge(self.dut.clk)
        self.dut.start_transfer.value = 0

        # Wait for busy to go high (transfer started)
        count = 0
        while count < timeout:
            await RisingEdge(self.dut.clk)
            if self.dut.master_busy.value == 1:
                break
            count += 1
        else:
            raise TimeoutError("Timeout waiting for master_busy to assert")

        # Wait for busy to go low (transfer complete)
        count = 0
        while count < timeout:
            await RisingEdge(self.dut.clk)
            if self.dut.master_busy.value == 0:
                break
            count += 1
        else:
            raise TimeoutError("Timeout waiting for transfer to complete")

        # Wait one more clock cycle for data to stabilize
        await RisingEdge(self.dut.clk)

        # Verify data valid flag
        if not self.dut.master_valid.value:
            raise ValueError("Transfer completed but master_valid not asserted")

        return int(self.dut.master_data_out.value)

    async def send_bytes(self, data_bytes: bytes, timeout: int = 1000) -> list:
        """Send multiple bytes and return received data.

        Args:
            data_bytes: Bytes object containing data to send
            timeout: Maximum number of clock cycles to wait per transfer

        Returns:
            List of received data bytes

        Raises:
            TimeoutError: If any transfer doesn't complete within timeout
        """
        received_data = []
        for byte in data_bytes:
            rx_data = await self.send_data(byte, timeout)
            received_data.append(rx_data)
        return received_data
