from machine import Pin, I2C, PWM
from ADXL345 import ADXL345_I2C
import time
import math

# Initialisiere I2C und den IMU-Sensor
i2c = I2C(0, scl=Pin(22), sda=Pin(21))  # Passen Sie die Pins ggf. an Ihre Hardware an
imu = ADXL345_I2C(i2c)

# LED konfigurieren
led = Pin(13, Pin.OUT)
led1 = Pin(2, Pin.OUT)

# Piezo-Lautsprecher konfigurieren (GPIO 25)
piezo = PWM(Pin(25))  # PWM-Signal für Tonerzeugung
piezo.freq(1000)  # Standardfrequenz (1 kHz)

# Schwellenwert für freien Fall (nahe 0 g in allen Achsen)
FALL_THRESHOLD = 0.2  # g-Wert, anpassbar

# Variable, um zu speichern, ob ein freier Fall erkannt wurde
fall_detected = False

piezo.duty(0)   # Piezo ausschalten

def calculate_magnitude(x, y, z):
    """Berechnet die Magnitude des Beschleunigungsvektors."""
    return math.sqrt(x**2 + y**2 + z**2)

while True:
    if not fall_detected:  # Nur prüfen, wenn freier Fall noch nicht erkannt wurde
        # Lese die Beschleunigungswerte
        x = imu.xValue / 256  # Werte in g umwandeln (Division anpassen, falls nötig)
        y = imu.yValue / 256
        z = imu.zValue / 256

        # Berechne die Magnitude
        magnitude = calculate_magnitude(x, y, z)
        print("Magnitude:", magnitude)

        # Prüfe auf freien Fall
        if magnitude < FALL_THRESHOLD:
            fall_detected = True
            led.value(1)  # LED einschalten
            led1.value(1)   # LED1 einschalten
            
            # Piezo-Lautsprecher aktivieren
            piezo.duty(512)  # 50% Duty-Cycle für hörbaren Ton
            time.sleep(1)   # Ton für 1 Sekunde
            piezo.duty(0)   # Piezo ausschalten

    # Kurze Verzögerung, um den Sensor nicht zu überlasten
    time.sleep(0.1)