from machine import Pin, SPI
from time import sleep, ticks_ms, ticks_diff

class RFM69:
    def __init__(self, spi, cs_pin, reset_pin, freq=433.0):
        self.spi = spi
        self.cs = cs_pin
        self.reset = reset_pin
        self.freq = freq
        self.cs.init(Pin.OUT, value=1)  # CS auf HIGH setzen
        self.reset.init(Pin.OUT, value=0)  # Reset auf LOW setzen
        self.init_radio()

    def init_radio(self):
        # Reset durchführen
        self.reset.value(1)
        sleep(0.01)
        self.reset.value(0)
        sleep(0.01)

        # Setze Frequenz und grundlegende Register
        self.write_register(0x01, 0x04)  # Sleep mode
        self.write_register(0x02, 0x00)  # Standby mode
        self.set_frequency(self.freq)
        self.write_register(0x11, 0x9F)  # Max Tx power
        self.write_register(0x19, 0x42)  # Set bitrate to 4.8 kbps
        self.write_register(0x25, 0x80)  # Set RSSI threshold
        self.write_register(0x29, 0xE4)  # Sync word
        self.write_register(0x2E, 0x88)  # Packet format

    def set_frequency(self, freq_mhz):
        freq = int((freq_mhz * 10**6) / 61.03515625)
        self.write_register(0x07, (freq >> 16) & 0xFF)
        self.write_register(0x08, (freq >> 8) & 0xFF)
        self.write_register(0x09, freq & 0xFF)

    def send(self, data):
        self.write_register(0x01, 0x0C)  # Transmit mode
        self.write_fifo(data)
        while not self.read_register(0x28) & 0x08:  # Wait for packet sent
            pass
        self.write_register(0x01, 0x04)  # Back to standby mode

    def receive(self, timeout=1.0):
        self.write_register(0x01, 0x10)  # Receive mode
        start = ticks_ms()  # Startzeit in Millisekunden
        while ticks_diff(ticks_ms(), start) < timeout * 1000:
            if self.read_register(0x28) & 0x04:  # PayloadReady
                return self.read_fifo()
        return None

    def write_fifo(self, data):
        self.cs.value(0)
        self.spi.write(bytearray([0x80] + list(data)))
        self.cs.value(1)

    def read_fifo(self):
        self.cs.value(0)
        self.spi.write(bytearray([0x00]))
        data = self.spi.read(64)  # Max packet size
        self.cs.value(1)
        return data

    def write_register(self, address, value):
        self.cs.value(0)
        self.spi.write(bytearray([address | 0x80, value]))
        self.cs.value(1)

    def read_register(self, address):
        self.cs.value(0)
        self.spi.write(bytearray([address & 0x7F]))
        result = self.spi.read(1)
        self.cs.value(1)
        return result[0]
