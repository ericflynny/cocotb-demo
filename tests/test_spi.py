import cocotb
from cocotb.clock import Clock
import random
import pytest
from testbench_spi import SpiTestbench


@cocotb.test()
async def test_basic_transfer(dut):
    """Test basic data transfer between master and slave"""
    # Create clock
    clock = Clock(dut.clk, 10, units="ns")
    cocotb.start_soon(clock.start())

    # Create master and slave instances
    tb = SpiTestbench(dut)

    # Reset devices
    await tb.master.reset()

    # Configure SPI mode 0
    await tb.master.configure_mode(cpol=0, cpha=0)

    # Prepare test data
    tx_data = 0xA5
    rx_data = 0x5A

    # Set up slave response data
    await tb.slave.send_data(rx_data)

    # Send data from master
    received_data = await tb.master.send_data(tx_data)

    # Get data received by slave
    slave_received = await tb.slave.get_received_data()

    # Verify data
    assert received_data == rx_data, f"Master received wrong data: {received_data} != {rx_data}"
    assert slave_received == tx_data, f"Slave received wrong data: {slave_received} != {tx_data}"


# TODO: Failing
@cocotb.test()
async def test_all_spi_modes(dut):
    """Test all four SPI modes (CPOL/CPHA combinations)"""
    clock = Clock(dut.clk, 10, units="ns")
    cocotb.start_soon(clock.start())

    tb = SpiTestbench(dut)

    for cpol in [0, 1]:
        for cpha in [0, 1]:
            await tb.master.reset()
            await tb.master.configure_mode(cpol=cpol, cpha=cpha)

            tx_data = 0x55
            rx_data = 0xAA

            await tb.slave.send_data(rx_data)
            received_data = await tb.master.send_data(tx_data)
            slave_received = await tb.slave.get_received_data()

            assert received_data == rx_data, \
                f"Mode {cpol}{cpha}: Master received wrong data: {received_data} != {rx_data}"
            assert slave_received == tx_data, \
                f"Mode {cpol}{cpha}: Slave received wrong data: {slave_received} != {tx_data}"


@cocotb.test()
async def test_multiple_bytes(dut):
    """Test sending multiple bytes in sequence"""
    clock = Clock(dut.clk, 10, units="ns")
    cocotb.start_soon(clock.start())

    tb = SpiTestbench(dut)

    await tb.master.reset()
    await tb.master.configure_mode(cpol=0, cpha=0)

    # Test data
    tx_bytes = [0x55, 0xAA, 0x33, 0xCC]
    rx_bytes = [0xAA, 0x55, 0xCC, 0x33]

    for tx_byte, rx_byte in zip(tx_bytes, rx_bytes):
        await tb.slave.send_data(rx_byte)
        received_data = await tb.master.send_data(tx_byte)
        slave_received = await tb.slave.get_received_data()

        assert received_data == rx_byte, \
            f"Master received wrong data: {received_data} != {rx_byte}"
        assert slave_received == tx_byte, \
            f"Slave received wrong data: {slave_received} != {tx_byte}"


@cocotb.test()
async def test_random_data(dut):
    """Test with random data values"""
    clock = Clock(dut.clk, 10, units="ns")
    cocotb.start_soon(clock.start())

    tb = SpiTestbench(dut)

    await tb.master.reset()

    # Test 10 random values
    for _ in range(10):
        tx_data = random.randint(0, 255)
        rx_data = random.randint(0, 255)

        await tb.slave.send_data(rx_data)
        received_data = await tb.master.send_data(tx_data)
        slave_received = await tb.slave.get_received_data()

        assert received_data == rx_data, \
            f"Master received wrong data: {received_data} != {rx_data}"
        assert slave_received == tx_data, \
            f"Slave received wrong data: {slave_received} != {tx_data}"


@cocotb.test()
async def test_timeout_handling(dut):
    """Test timeout handling"""
    clock = Clock(dut.clk, 10, units="ns")
    cocotb.start_soon(clock.start())

    tb = SpiTestbench(dut)

    await tb.master.reset()

    # Test with very short timeout
    with pytest.raises(TimeoutError):
        await tb.master.send_data(0x55, timeout=1)

    with pytest.raises(TimeoutError):
        await tb.slave.get_received_data(timeout=1)
