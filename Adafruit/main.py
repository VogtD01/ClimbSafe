from machine import SPI, Pin, PWM, I2C
from adafruit_rfm9x import *
from ADXL345 import ADXL345_I2C
import time
import math
import functions as f # Importiere die ausgelagerten Funktionen

# Lora
led = Pin(2)
CS = Pin(5, Pin.OUT)
RESET = Pin(27, Pin.OUT)
spi = SPI(2, baudrate=1000000, polarity=0, phase=0, bits=8, firstbit=0, sck=Pin(18), mosi=Pin(23), miso=Pin(19))
RADIO_FREQ_MHZ = 433.0
# Initialisiere RFM radio
rfm9x = RFM9x(spi, CS, RESET, RADIO_FREQ_MHZ)
rfm9x.tx_power = 23

# IMU
i2c = I2C(0, scl=Pin(22), sda=Pin(21))
imu = ADXL345_I2C(i2c)

# LED
red = Pin(13, Pin.OUT, value=0)
green = Pin(12, Pin.OUT, value=0)
blue = Pin(2, Pin.OUT, value=0)  # LED am ESP32 zur Kontrolle

# Piezo-speaker
piezo_pin = PWM(Pin(15))
piezo_pin.freq(440)
piezo_pin.duty(0)

# Schwellenwert für freien Fall (nahe 0 g in allen Achsen)
FALL_THRESHOLD = 0.35  # g-Wert, anpassbar

# Variable, um zu speichern, ob ein freier Fall erkannt wurde
fall_detected = False

# Button
button = Pin(14, Pin.IN, Pin.PULL_UP)

# Funktion für den Button-Interrupt
def button_pressed_handler(pin):
    """Funktion, die aufgerufen wird, wenn der Button gedrückt wird."""
    global fall_detected, last_button_press_time, button_press_count
    current_time = time.time()
    if current_time - last_button_press_time <= 2:
        button_press_count += 1
    else:
        button_press_count = 1

    last_button_press_time = current_time

    if button_press_count == 2:
        # Nachricht senden: "010" für zweimaliges Drücken innerhalb von 3 Sekunden
        rfm9x.send(bytes([0b010]))
        print("Doppelklick Nachricht gesendet!")
        f.zweimal_drücken_nachricht(piezo_pin)  # Funktion für das zweimalige Drücken
    else:
        # Nachricht senden: "001" für einmaliges Drücken
        fall_detected = False  # Beende den Fallzustand, wenn der Button gedrückt wird
        rfm9x.send(bytes([0b001]))
        print("Button gedrückt Nachricht gesendet!")
        f.einmal_drücken_nachricht(piezo_pin)  # Funktion für das einmalige Drücken


# Initialisiere Variablen für den Button-Interrupt
last_button_press_time = 0
button_press_count = 0


# Button-Interrupt hinzufügen
button.irq(trigger=Pin.IRQ_FALLING, handler=button_pressed_handler)

print("Sent Hello World message!")
print("Waiting for packets...")

# Ab hier der Hauptteil des Programms

f.anschalten(red, blue, piezo_pin)  # Gerät einschalten


while True:
    # Empfange ein Paket mit den RFM9x-Funkmodul
    packet = rfm9x.receive()

    # Lese die Beschleunigungswerte
    x = imu.xValue / 256  # Werte in g umwandeln (Division anpassen, falls nötig)
    y = imu.yValue / 256
    z = imu.zValue / 256

    # Berechne die Magnitude (Betrag des Beschleunigungsvektors)
    magnitude = f.calculate_magnitude(x, y, z)

    # Prüfe auf freien Fall anhand eines Schwellenwerts
    if magnitude < FALL_THRESHOLD:
        fall_detected = True
        blue.value(1)  # Blaue LED einschalten
        time.sleep(5)  # LED für 5 Sekunden anlassen
        blue.value(0)  # Blaue LED ausschalten

        # Nachricht senden: "100" für freien Fall erkannt
        rfm9x.send(bytes([0b100]))
        print("Fall detected Nachricht gesendet!")
        f.fall_sender(red, blue, piezo_pin, fall_detected)  # Funktion für das Sendegerät nach einem Fall

    if packet is None:
        # Kein Paket empfangen
        print("Received nothing! Listening again...")
    else:
        # Ein Paket wurde empfangen
        print("Received (raw bytes): {0}".format(packet))

        # Paketinhalte analysieren (binäre Zustände)
        if packet[0] == 0b001:  # "001" entspricht "Button gedrückt"
            f.button_nachricht(red, green, piezo_pin)  # Funktion für das Empfängergerät

        elif packet[0] == 0b100:  # "100" entspricht "Fall erkannt"
            f.fall_nachricht_empfänger(red, blue, piezo_pin, fall_detected)  # Funktion für das Empfängergerät nach einem Fall

        elif packet[0] == 0b010:  # "010" entspricht "Doppelklick, Verletzt"
            f.verletzt_nachricht_empfänger(red, green, piezo_pin, fall_detected)  # Funktion für das Empfängergerät bei Verletzung

        # Signalstärke (RSSI) des empfangenen Pakets auslesen und ausgeben
        rssi = rfm9x.last_rssi
        print("Received signal strength: {0} dB".format(rssi))