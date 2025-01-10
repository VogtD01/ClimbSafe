from adafruit_rfm9x import *
from machine import SPI, Pin, PWM, I2C
import time
from ADXL345 import ADXL345_I2C
import math

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

def calculate_magnitude(x, y, z):
    """Berechnet die Magnitude des Beschleunigungsvektors."""
    return math.sqrt(x**2 + y**2 + z**2)

# Schwellenwert für freien Fall (nahe 0 g in allen Achsen)
FALL_THRESHOLD = 0.35  # g-Wert, anpassbar

# Variable, um zu speichern, ob ein freier Fall erkannt wurde
fall_detected = False


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
    # Nachricht senden: "001" für "Button gedrückt"
    rfm9x.send(bytes([0b001]))
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



###################################

def button_nachricht():
    red.value(1)  # Rote LED einschalten
    green.value(1)  # Grüne LED einschalten
    piezo_pin.duty(512)  # Piezo aktivieren
    time.sleep(1)
    red.value(0)  # Rote LED ausschalten
    green.value(0)  # Grüne LED ausschalten
    piezo_pin.duty(0)  # Piezo deaktivieren

def fall_nachricht():

    red.value(1)  # Rote LED einschalten
    blue.value(1)  # Blaue LED einschalten
    piezo_pin.duty(512)  # Piezo aktivieren
    time.sleep(5)
    red.value(0)  # Rote LED ausschalten
    blue.value(0)  # Blaue LED ausschalten
    piezo_pin.duty(0)  # Piezo deaktivieren
###############################

while True:
    # Empfange ein Paket mit den RFM9x-Funkmodul
    packet = rfm9x.receive()

    # Lese die Beschleunigungswerte
    x = imu.xValue / 256  # Werte in g umwandeln (Division anpassen, falls nötig)
    y = imu.yValue / 256
    z = imu.zValue / 256

    # Berechne die Magnitude (Betrag des Beschleunigungsvektors)
    magnitude = calculate_magnitude(x, y, z)

    # Prüfe auf freien Fall anhand eines Schwellenwerts
    if magnitude < FALL_THRESHOLD:
        fall_detected = True
        blue.value(1)  # Blaue LED einschalten
        time.sleep(5)  # LED für 5 Sekunden anlassen
        blue.value(0)  # Blaue LED ausschalten

        # Nachricht senden: "100" für freien Fall erkannt
        rfm9x.send(bytes([0b100]))
        print("Fall detected Nachricht gesendet!")

    if packet is None:
        # Kein Paket empfangen
        print("Received nothing! Listening again...")
    else:
        # Ein Paket wurde empfangen
        print("Received (raw bytes): {0}".format(packet))

        # Paketinhalte analysieren (binäre Zustände)
        if packet[0] == 0b001:  # "001" entspricht "Button gedrückt"
            
            button_nachricht()
        

        elif packet[0] == 0b100:  # "100" entspricht "Fall erkannt"

            fall_nachricht()


        # Signalstärke (RSSI) des empfangenen Pakets auslesen und ausgeben
        rssi = rfm9x.last_rssi
        print("Received signal strength: {0} dB".format(rssi))
