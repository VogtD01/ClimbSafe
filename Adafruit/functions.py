import math
import time
from machine import Pin, PWM



def calculate_magnitude(x, y, z):
    """Berechnet die Magnitude des Beschleunigungsvektors."""
    return math.sqrt(x**2 + y**2 + z**2)

def button_nachricht():
    red.value(1)  # Rote LED einschalten
    green.value(1)  # Grüne LED einschalten
    piezo_pin.duty(512)  # Piezo aktivieren
    time.sleep(1)
    red.value(0)  # Rote LED ausschalten
    green.value(0)  # Grüne LED ausschalten
    piezo_pin.duty(0)  # Piezo deaktivieren