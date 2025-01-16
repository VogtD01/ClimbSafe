import math
import time
from machine import Pin, PWM, Timer
import status

def calculate_magnitude(x, y, z):
    """Berechnet die Magnitude des Beschleunigungsvektors."""
    return math.sqrt(x**2 + y**2 + z**2)

def anschalten(red, green, piezo_pin):
    """Funktion, um den Zustand "Gerät eingeschaltet" zu behandeln."""
    green.value(1)  # Grüne LED einschalten
    red.value(1)  # Rote LED einschalten
    piezo_pin.duty(512)  # Piezo aktivieren
    
    # Timer starten, um nach 1 Sekunde auszuschalten
    timer_f.init(mode=Timer.ONE_SHOT, period=1000, callback=lambda t: ausschalten(red, green, piezo_pin))

def drücken_nachricht(red, green, piezo_pin):
    """Funktion, was am eigenen ESP passiert wenn der Button gedrückt wird."""
    piezo_pin.duty(512)  # Piezo aktivieren
    red.value(0)
    green.value(1)
    # Timer starten, um Piezo nach 0.5 Sekunden auszuschalten
    timer_f.init(mode=Timer.ONE_SHOT, period=500, callback=lambda t: ausschalten(red, green, piezo_pin))

def button_nachricht(red, green, piezo_pin):
    """Funktion, um den Zustand "Button gedrückt" zu behandeln beim Empfänger."""
    status.fall_detected = False
    red.value(1)  # Rote LED einschalten
    green.value(1)  # Grüne LED einschalten
    piezo_pin.duty(512)  # Piezo aktivieren
    
    # Timer starten, um nach 1 Sekunde auszuschalten
    timer_f.init(mode=Timer.ONE_SHOT, period=1000, callback=lambda t: ausschalten(red, green, piezo_pin))

def ausschalten(red, green, piezo_pin):
    """Funktion, um LEDs und Piezo auszuschalten."""
    
    red.value(0)  # Rote LED ausschalten
    green.value(0)  # Grüne LED ausschalten
    piezo_pin.duty(0)  # Piezo deaktivieren

# Beispiel: Initialisierung des Timers
timer_f = Timer(0)

##############


def fall_sender(red, blue, piezo_pin):
    """Funktion, um den Zustand nach dem Sturz beim Sender zu behandeln.
    
    Diese Funktion aktiviert die rote und blaue LED sowie den Piezo-Summer.
    Nach 10
    Sekunden wird der Piezo-Summer aktiviert, wenn der Button nicht in der zeit gedrückt wurde."""

    start_time = time.time()
    status.fall_detected = True  # Zugriff über das Modul
    
    while status.fall_detected:  # Zugriff über das Modul
        red.value(1)
        
        if time.time() - start_time >= 10:
            piezo_pin.duty(500)

        time.sleep(0.1)

    ausschalten(red, blue, piezo_pin)
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
        blue.value(1)  # Blaue LED einschalten
        piezo_pattern(piezo_pin, duration=1, on_time=0.1, off_time=0.2)  # Kürzeres Muster

        time.sleep(0.1)  # Kurze Pause, um CPU-Last zu reduzieren

    ausschalten(red, blue, piezo_pin)  # LEDs und Piezo ausschalten

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
        piezo_pattern(piezo_pin, duration=0.8, on_time=0.4, off_time=0.4)  # Kürzeres Muster
        time.sleep(0.5)

        red.value(0)
        green.value(1)
        piezo_pin.duty(0)  # Piezo bleibt aktiv
        time.sleep(0.5)

    ausschalten(red, green, piezo_pin)  # LEDs und Piezo ausschalten

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