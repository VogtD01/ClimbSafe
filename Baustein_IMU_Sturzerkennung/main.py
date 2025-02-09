#main

from machine import Pin, I2C, PWM
from ADXL345 import ADXL345_I2C
import time
import math

# Initialisiere I2C und den IMU-Sensor
i2c = I2C(0, scl=Pin(22), sda=Pin(21))  # I2C-Bus initialisieren
imu = ADXL345_I2C(i2c)

# LED konfigurieren
led1 = Pin(2, Pin.OUT)

# Button konfigurieren (GPIO 14)
button = Pin(14, Pin.IN, Pin.PULL_UP)  # Pull-Up-Widerstand aktivieren

# Piezo-Lautsprecher konfigurieren (GPIO 15)
piezo = PWM(Pin(15))  # PWM-Signal für Tonerzeugung
piezo.freq(1000)  # Standardfrequenz (1 kHz)
piezo.duty(0)   # Piezo ausschalten

# Schwellenwert für freien Fall (nahe 0 g in allen Achsen)
FALL_THRESHOLD = 0.35  

# Variable, um zu speichern, ob ein freier Fall erkannt wurde
fall_detected = False

def calculate_magnitude(x, y, z):
    """Berechnet die Magnitude des Beschleunigungsvektors."""
    return math.sqrt(x**2 + y**2 + z**2)

while True:
    if not fall_detected:  # Nur prüfen, wenn freier Fall noch nicht erkannt wurde
        # Lese die Beschleunigungswerte
        x = imu.xValue / 256  
        y = imu.yValue / 256
        z = imu.zValue / 256

        # Berechne die Magnitude
        magnitude = calculate_magnitude(x, y, z)
        print("Magnitude1:", magnitude)

        # Prüfe auf freien Fall
        if magnitude < FALL_THRESHOLD:
            fall_detected = True
            led1.value(1)   # LED1 einschalten

            # Piezo-Lautsprecher dauerhaft aktivieren
            piezo.duty(512)  # 50% Duty-Cycle für hörbaren Ton

    else:
        # Überprüfe, ob der Button gedrückt wurde
        if button.value() == 0:  # Button gedrückt (LOW)
            fall_detected = False  # Reset des Fall-Detektionsstatus
            print("Reset fall detection.")
            led1.value(0)  
            piezo.duty(0) 
        else:
            print("Fall detected!")
            # Piezo-Lautsprecher für 1 Sekunde aktivieren
            piezo.duty(512)
            led1.value(1)
            time.sleep(1)
            piezo.duty(0)


    # Kurze Verzögerung, um den Sensor nicht zu überlasten
    time.sleep(0.1)


