from adafruit_rfm9x import *
from machine import SPI, Pin, PWM, I2C
import time
from ADXL345 import ADXL345_I2C

# Lora
led = Pin(2)
CS = Pin(5, Pin.OUT)
RESET = Pin(27, Pin.OUT)
spi = SPI(2, baudrate=1000000, polarity=0, phase=0, bits=8, firstbit=0, sck=Pin(18), mosi=Pin(23), miso=Pin(19))
RADIO_FREQ_MHZ = 433.0
# Initialze RFM radio
rfm9x = RFM9x(spi, CS, RESET, RADIO_FREQ_MHZ)
rfm9x.tx_power = 23

# IMU
i2c = I2C(0, scl=Pin(22), sda=Pin(21))
imu = ADXL345_I2C(i2c)

# Piezo-speaker
piezo_pin = PWM(Pin(15))
piezo_pin.freq(440)
piezo_pin.duty(0)

# LED
red = Pin(13, Pin.OUT, value=0)
green = Pin(12, Pin.OUT, value=0)
blue = Pin(2, Pin.OUT, value=0)


# Button
button = Pin(14, Pin.IN, Pin.PULL_UP)


# Interrupt handler for button press
def button_pressed_handler(pin):
    rfm9x.send(bytes("Button gedrückt!\r\n", "utf-8"))
    print("Button gedrückt Nachricht gesendet!")


# Set up the button interrupt
button.irq(trigger=Pin.IRQ_FALLING, handler=button_pressed_handler)

print("Sent Hello World message!")
print("Waiting for packets...")

# Activate the piezo speaker for 5 seconds
piezo_pin.duty(400)
blue.value(1)
red.value(1)
time.sleep(1)

piezo_pin.duty(0)
blue.value(0)
red.value(0)

while True:
    packet = rfm9x.receive()
    # Optionally change the receive timeout from its default of 0.5 seconds:
    # packet = rfm9x.receive(timeout=5.0)
    # If no packet was received during the timeout, then None is returned.

    if packet is None:
        # Packet has not been received
        print("Received nothing! Listening again...")
    else:
        # Received a packet!
        print("Received (raw bytes): {0}".format(packet))
        # Decode to ASCII text and print it
        packet_text = str(packet, "ascii")
        print("Received (ASCII): {0}".format(packet_text))

        # Check if the received message is "Button gedrückt"
        if packet_text == "Button gedrückt!\r\n":
            red.value(1)  # Turn on the red LED
            green.value(1)  # Turn on the green LED
            piezo_pin.duty(512)
            time.sleep(1)
            red.value(0)  # Turn off the red LED
            green.value(0)  # Turn off the green LED
            piezo_pin.duty(0)

        # Read and print the RSSI (signal strength) of the last received message
        rssi = rfm9x.last_rssi
        print("Received signal strength: {0} dB".format(rssi))
