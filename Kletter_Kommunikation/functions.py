import math
import time
from machine import Pin, PWM, Timer
import status

# Initialisierung des Timers
timer_f = Timer(0)

def beschleunigungsvektor_berechnen(x, y, z):
    """Berechnet die Magnitude des Beschleunigungsvektors."""
    return math.sqrt(x**2 + y**2 + z**2)

def anschalten(red, green, piezo_pin):
    """Funktion, um den Zustand "Gerät eingeschaltet" zu behandeln."""
    green.value(1)  
    red.value(1)
    piezo_pin.duty(512)
    
    # Timer starten, um nach 1 Sekunde auszuschalten
    timer_f.init(mode=Timer.ONE_SHOT, period=1000, callback=lambda t: ausschalten(red, green, piezo_pin))

def drücken_nachricht(green, piezo_pin):
    """Funktion, was am eigenen ESP passiert wenn der Button gedrückt wird."""
    piezo_pin.duty(512)
    green.value(1)

    # Timer starten, um Piezo nach 0.5 Sekunden auszuschalten
    timer_f.init(mode=Timer.ONE_SHOT, period=500, callback=lambda t: ausschalten(None, green, piezo_pin))

def button_nachricht(green, piezo_pin):
    """Funktion, um den Zustand "Button gedrückt" zu behandeln beim Empfänger."""
    status.fall_detected = False
 
    green.value(1)
    piezo_pin.duty(512)
    
    # Timer starten, um nach 1 Sekunde auszuschalten
    timer_f.init(mode=Timer.ONE_SHOT, period=1000, callback=lambda t: ausschalten(None, green, piezo_pin))

def ausschalten(red, green, piezo_pin):
    """Callback-Funktion, um die LEDs und den Piezo-Speaker auszuschalten."""

    if red is not None:
        red.value(0)
    if green is not None:
        green.value(0)
    if piezo_pin is not None:
        piezo_pin.duty(0)

#---------------------------------------Funktionen für den Fall-Status-----------------------------------------------------------------------------

def fall_sender(red, piezo_pin):
    """Funktion, um den Zustand nach dem Sturz beim Sender zu behandeln.
    
    Diese Funktion aktiviert die rote LED sowie den Piezo-Speaker nach 10s.
    """

    start_time = time.time()
    status.fall_detected = True  
    
    # LEDs und Piezo aktivieren, bis der Zustand beendet wird
    while status.fall_detected:
        red.value(1)
        
        if time.time() - start_time >= 10:
            piezo_pin.duty(500)

        time.sleep(0.1)

    ausschalten(red, None, piezo_pin)

def fall_nachricht_empfänger(red, piezo_pin):
    """Funktion, um den Zustand 'Fall erkannt' zu behandeln."""
    
    def check_fall_status(timer):
        """Prüft den Status 'fall_detected' regelmäßig."""
        if not status.fall_detected:  # Wenn `fall_detected` False ist
            timer.deinit()  # Timer stoppen
            ausschalten(red, None,  piezo_pin)  # LEDs und Piezo ausschalten
            print("Fall beendet. Status zurückgesetzt.")
        else:
            # LEDs aktivieren und Piezo-Muster abspielen
            piezo_pin.duty(500)  # Kürzeres Muster

    # Status auf True setzen und Timer starten
    status.fall_detected = True
    timer_f.init(mode=Timer.PERIODIC, period=100, callback=check_fall_status)  # Alle 100 ms prüfen


    
def verletzt_nachricht_empfänger(red, green, piezo_pin):
    """Funktion, um den Zustand "Verletzung erkannt" zu behandeln.
    
    Diese Funktion aktiviert die rote und grüne LED  sowie den Piezo-Summer.
    Die LEDs und der Piezo-Summer wechseln sich alle 0,5 Sekunden ab, bis der button gedrückt wird wird."""

    # LEDs und Piezo aktivieren, bis der Zustand beendet wird

    status.fall_detected = True

    while status.fall_detected:
        red.value(1)
        green.value(0)
        piezo_pin.duty(512)
        time.sleep(0.3)

        red.value(0)
        green.value(1)
        piezo_pin.duty(0)  # Piezo bleibt aktiv
        time.sleep(0.3)

    ausschalten(red, green, piezo_pin)  # LEDs und Piezo ausschalten

