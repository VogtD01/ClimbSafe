from machine import Pin, SPI
from time import sleep
from rfm69 import RFM69

# Pin-Belegung
CS = Pin(5, Pin.OUT)       # Chip Select
RESET = Pin(22, Pin.OUT)   # Reset
SCK = 18                   # SPI Clock
MOSI = 23                  # SPI Data Out
MISO = 19                  # SPI Data In

# Frequenz (433 MHz oder 915 MHz)
FREQ = 433.0

# SPI initialisieren
spi = SPI(1, baudrate=5000000, polarity=0, phase=0, sck=Pin(SCK), mosi=Pin(MOSI), miso=Pin(MISO))

# RFM69 initialisieren
radio = RFM69(spi, CS, RESET, FREQ)

print("RFM69 Sender bereit!")

while True:
    print("Warte auf Empfang...")
    message = "Hello world!\r\n"
    radio.send(bytes(message, "utf-8"))
    print("Gesendet: Hallo Welt!")
    sleep(1)
