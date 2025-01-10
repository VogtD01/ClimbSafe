from adafruit_rfm9x import *
from machine import SPI, Pin, PWM, I2C
import time
from ADXL345 import ADXL345_I2C

#Lora
led = Pin(2)
CS = Pin(5, Pin.OUT)
RESET = Pin(34, Pin.OUT)
spi = SPI(2, baudrate=1000000, polarity=0, phase=0, bits=8, firstbit=0, sck=Pin(18), mosi=Pin(23), miso=Pin(19))
RADIO_FREQ_MHZ = 433.0
# Initialze RFM radio
rfm9x = RFM9x(spi, CS, RESET, RADIO_FREQ_MHZ)
rfm9x.tx_power = 23

# IMU
i2c = I2C(0, scl=Pin(22), sda=Pin(21))  
imu = ADXL345_I2C(i2c)

# Piezo-speaker
piezo_pin = PWM(Pin(25))
piezo_pin.freq(440)  
piezo_pin.duty(0)  

# Led
red = Pin(13, Pin.OUT)
green = Pin(12, Pin.OUT)

# Button
button = Pin(14, Pin.IN, Pin.PULL_UP)


# Send a packet.  Note you can only send a packet up to 252 bytes in length.
# This is a limitation of the radio packet size, so if you need to send larger
# amounts of data you will need to break it into smaller send calls.  Each send
# call will wait for the previous one to finish before continuing.
rfm9x.send(bytes("Hello world!\r\n", "utf-8"))
print("Sent Hello World message!")

# Wait to receive packets. 
print("Waiting for packets...")

while True:
    packet = rfm9x.receive()
    # Optionally change the receive timeout from its default of 0.5 seconds:
    # packet = rfm9x.receive(timeout=5.0)
    # If no packet was received during the timeout then None is returned.

    # Send a packet every 5 seconds
    rfm9x.send(bytes("Hello world!\r\n", "utf-8"))
    print("Sent Hello World message!")
    time.sleep(5)
    
    if packet is None:
        # Packet has not been received
        led.value(0)
        print("Received nothing! Listening again...")
    else:
        # Received a packet!
        led.value(1)
        # Print out the raw bytes of the packet:
        print("Received (raw bytes): {0}".format(packet))
        # And decode to ASCII text and print it too.  Note that you always
        # receive raw bytes and need to convert to a text format like ASCII
        # if you intend to do string processing on your data.  Make sure the
        # sending side is sending ASCII data before you try to decode!
        packet_text = str(packet, "ascii")
        print("Received (ASCII): {0}".format(packet_text))
        # Also read the RSSI (signal strength) of the last received message and
        # print it.
        rssi = rfm9x.last_rssi
        print("Received signal strength: {0} dB".format(rssi))