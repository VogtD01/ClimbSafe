#main_interruppts

### funktioniert noch nicht

from machine import Pin, I2C, PWM, Timer
from ADXL345 import ADXL345_I2C
import math

# Initialisiere I2C und den IMU-Sensor
i2c = I2C(0, scl=Pin(22), sda=Pin(21))  # Passen Sie die Pins ggf. an Ihre Hardware an
imu = ADXL345_I2C(i2c)

# LED konfigurieren
led = Pin(2, Pin.OUT)

# Button konfigurieren (GPIO 12)
button = Pin(12, Pin.IN, Pin.PULL_UP)  # Pull-Up aktiviert für stabilen High-Zustand

# Piezo-Lautsprecher konfigurieren (GPIO 25)
piezo = PWM(Pin(25))
piezo.freq(1000)  # Standardfrequenz (1 kHz)
piezo.duty(0)  # Piezo ausschalten

# Schwellenwert für freien Fall (nahe 0 g in allen Achsen)
FALL_THRESHOLD = 0.3  # g-Wert, anpassbar

# Variable, um zu speichern, ob ein freier Fall erkannt wurde
fall_detected = False

# Timer-Objekte für Piezo und LED
piezo_timer = Timer()
led_timer = Timer()

def calculate_magnitude(x, y, z):
    """Berechnet die Magnitude des Beschleunigungsvektors."""
    return math.sqrt(x**2 + y**2 + z**2)

def reset_fall_detection(timer):
    """Resettet den Fall-Detektionsstatus."""
    global fall_detected
    fall_detected = False
    led.value(0)
    piezo.duty(0)
    print("Reset fall detection.")

def button_interrupt(pin):
    """Interrupt-Funktion für den Button."""
    global fall_detected
    if fall_detected:
        reset_fall_detection(None)

def handle_fall():
    """Aktiviert LED und Piezo bei freiem Fall."""
    global fall_detected
    fall_detected = True
    led.value(1)
    piezo.duty(512)
    print("Fall detected!")
    
    # Starte Timer, um Piezo und LEDs nach 1 Sekunde auszuschalten
    piezo_timer.init(mode=Timer.ONE_SHOT, period=1000, callback=reset_fall_detection)

# Button-Interrupt aktivieren
button.irq(trigger=Pin.IRQ_FALLING, handler=button_interrupt)

while True:
    if not fall_detected:
        # Lese die Beschleunigungswerte
        x = imu.xValue / 256  # Werte in g umwandeln (Division anpassen, falls nötig)
        y = imu.yValue / 256
        z = imu.zValue / 256

        # Berechne die Magnitude
        magnitude = calculate_magnitude(x, y, z)
        print("Magnitude:", magnitude)

        # Prüfe auf freien Fall
        if magnitude < FALL_THRESHOLD:
            handle_fall()
