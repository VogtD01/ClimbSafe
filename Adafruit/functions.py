import math
import time
from machine import Pin, PWM
#import main
import status

# fall_detected = main.fall_detected <--------------------------------------------------------------------------------------------

def calculate_magnitude(x, y, z):
    """Berechnet die Magnitude des Beschleunigungsvektors."""
    return math.sqrt(x**2 + y**2 + z**2)

def anschalten(red, blue, piezo_pin):
    """Funktion, um den Zustand "Gerät eingeschaltet" zu behandeln.
    
    Diese Funktion aktiviert die blaue LED und den Piezo-Summer für 1 Sekunde."""
    
    blue.value(1)  # Blaue LED einschalten
    red.value(1)  # Rote LED einschalten
    piezo_pin.duty(512)  # Piezo aktivieren
    time.sleep(1)  # 1 Sekunde warten
    blue.value(0)  # Blaue LED ausschalten
    red.value(0)  # Rote LED ausschalten
    piezo_pin.duty(0)  # Piezo deaktivieren

def einmal_drücken_nachricht(piezo_pin):
    """Funktion, was am eigenen ESP passiert wenn der Button gedrückt wird."""
    piezo_pin.duty(512)  # Piezo aktivieren
    time.sleep(0.5)   #damit man merkt, dass der Button gedrückt wurde
    piezo_pin.duty(0)

def zweimal_drücken_nachricht(piezo_pin):
    """Funktion, was am eigenen ESP passiert wenn der Button zweimal gedrückt wird."""
    piezo_pin.duty(512)  # Piezo aktivieren
    time.sleep(0.5)   #damit man merkt, dass der Button gedrückt wurde
    piezo_pin.duty(0)

def button_nachricht(red, green, piezo_pin):
    """Funktion, um den Zustand "Button gedrückt" zu behandeln beim Empfänger.
    Diese Funktion aktiviert die rote und grüne LED sowie den Piezo-Summer für 1 Sekunde."""
    red.value(1)  # Rote LED einschalten
    green.value(1)  # Grüne LED einschalten
    piezo_pin.duty(512)  # Piezo aktivieren
    time.sleep(1)
    red.value(0)  # Rote LED ausschalten
    green.value(0)  # Grüne LED ausschalten
    piezo_pin.duty(0)  # Piezo deaktivieren


##############


def fall_sender(red, blue, piezo_pin):
    """Funktion, um den Zustand nach dem Sturz beim Sender zu behandeln.
    
    Diese Funktion aktiviert die rote und blaue LED sowie den Piezo-Summer.
    Nach 10
    Sekunden wird der Piezo-Summer aktiviert, wenn der Button nicht in der zeit gedrückt wurde."""

    start_time = time.time()
    while status.fall_detected:  # Zugriff über das Modul
        red.value(1)
        blue.value(1)

        if time.time() - start_time >= 10:
            piezo_pin.duty(200)

        time.sleep(0.1)

    red.value(0)
    blue.value(0)
    piezo_pin.duty(0)
############

def fall_nachricht_empfänger(red, blue, piezo_pin):
    """Funktion, um den Zustand "Fall erkannt" zu behandeln.
    
    Diese Funktion aktiviert die rote und blaue LED sowie den Piezo-Summer.
    Nach 10
    Sekunden wird der Piezo-Summer aktiviert, wenn der Button nicht in der zeit gedrückt wurde."""

    # LEDs aktivieren und Piezo erst nach 10 Sekunden einschalten, falls der Button nicht gedrückt wird

    # global fall_detected<--------------------------------------------------------------------------------------------
    status.fall_detected = True
    start_time = time.time()  # Startzeitpunkt erfassen

    while status.fall_detected:
        red.value(1)  # Rote LED einschalten
        blue.value(1)  # Blaue LED einschalten

        # Wenn 10 Sekunden vergangen sind und der Zustand noch aktiv ist, Piezo einschalten
        if time.time() - start_time >= 10:
            piezo_pattern(piezo_pin, duration=1, on_time=0.1, off_time=0.2)  # Kürzeres Muster

        time.sleep(0.1)  # Kurze Pause, um CPU-Last zu reduzieren

    # Zustand beendet, LEDs und Piezo ausschalten
    red.value(0)  # Rote LED ausschalten
    blue.value(0)  # Blaue LED ausschalten
    piezo_pin.duty(0)  # Piezo deaktivieren

def verletzt_nachricht_empfänger(red, green, piezo_pin):
    """Funktion, um den Zustand "Verletzung erkannt" zu behandeln.
    
    Diese Funktion aktiviert die rote und grüne LED  sowie den Piezo-Summer.
    Die LEDs und der Piezo-Summer wechseln sich alle 0,5 Sekunden ab, bis der button gedrückt wird wird."""

    # LEDs und Piezo aktivieren, bis der Zustand beendet wird

    # global fall_detected<--------------------------------------------------------------------------------------------
    status.fall_detected = True

    while status.fall_detected:
        red.value(1)
        green.value(0)
        piezo_pattern(piezo_pin, duration=10, on_time=0.4, off_time=0.4)  # Kürzeres Muster
        time.sleep(0.5)

        red.value(0)
        green.value(1)
        piezo_pin.duty(0)  # Piezo bleibt aktiv
        time.sleep(0.5)

    # Zustand beendet, LEDs und Piezo ausschalten
    red.value(0)
    green.value(0)
    piezo_pin.duty(0)


def piezo_pattern(piezo_pin, duration=10, on_time=0.5, off_time=0.5):
    """
    Erzeugt ein akustisches Muster für den Piezo-Lautsprecher.

    Args:
        piezo_pin (PWM): Der Pin, der den Piezo steuert.
        duration (float): Gesamtdauer des Musters in Sekunden.
        on_time (float): Dauer, für die der Piezo eingeschaltet bleibt (Sekunden).
        off_time (float): Dauer, für die der Piezo ausgeschaltet bleibt (Sekunden).
    """
    start_time = time.time()
    while time.time() - start_time < duration:
        piezo_pin.duty(512)  # Piezo aktivieren
        time.sleep(on_time)  # Zeit für Ton
        piezo_pin.duty(0)    # Piezo deaktivieren
        time.sleep(off_time)  # Pause