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
blue = Pin(2, Pin.OUT, value=0) # LED am ESP32 zur kontrollle


# Button
button = Pin(14, Pin.IN, Pin.PULL_UP)

# Funktion für den Button-Interrupt
def button_pressed_handler(pin):

    """Funktion, die aufgerufen wird, wenn der Button gedrückt wird.
    
    Diese Funktion zählt die Anzahl der Button-Drücke innerhalb von 2 Sekunden
    und sendet entsprechende Nachrichten an den Empfänger.
    
    Einmaliges Drücken: "001", bedeutet "Button gedrückt"
    Doppelklick: "010" , bedeutet "Verletzung" """


    # Nachricht senden je nach Anzahl der Button-Drücke innerhalb von 2 Sekunden
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

        einmal_drücken_nachricht() #funktion was der esp eigene macht wenn der button gedrückt wurde

        
    else:
        # Nachricht senden: "001" für einmaliges Drücken
        fall_detected = False  # Beende den Fallzustand, wenn der Button gedrückt wird
        rfm9x.send(bytes([0b001]))
        print("Button gedrückt Nachricht gesendet!")

        zweimal_drücken_nachricht() #funktion was der esp eigene macht wenn der button zweimal gedrückt wurde



# Button-Interrupt hinzufügen
button.irq(trigger=Pin.IRQ_FALLING, handler=button_pressed_handler)

print("Sent Hello World message!")
print("Waiting for packets...")



#######################################################################################################

# Funktionen für die verschiedenen Nachrichten 
# sollten in die Funktions.py ausgelagert werden

def anschalten():
    """Funktion, um den Zustand "Gerät eingeschaltet" zu behandeln.
    
    Diese Funktion aktiviert die blaue LED und den Piezo-Summer für 1 Sekunde."""

    blue.value(1)  # Blaue LED einschalten
    red.value(1)  # Rote LED einschalten
    piezo_pin.duty(512)  # Piezo aktivieren
    time.sleep(1)  # 1 Sekunde warten
    blue.value(0)  # Blaue LED ausschalten
    red.value(0)  # Rote LED ausschalten
    piezo_pin.duty(0)  # Piezo deaktivieren

def einmal_drücken_nachricht():
    """Funktion, was am eigenen ESP passiert wenn der Button gedrückt wird. also nicht beim empfänger"""
            
    piezo_pin.duty(512)  # Piezo aktivieren
    time.sleep(0.5)   #damit mann merkt das der Button gedrückt wurde
    piezo_pin.duty(0)

def zweimal_drücken_nachricht():
    """Funktion, was am eigenen ESP passiert wenn der Button gedrückt wird"""
            
    piezo_pin.duty(512)  # Piezo aktivieren
    time.sleep(0.5)   #damit mann merkt das der Button gedrückt wurde
    piezo_pin.duty(0)


def button_nachricht():

    """Funktion, um den Zustand "Button gedrückt" zu behandeln beim empfänger.
    Diese Funktion aktiviert die rote und grüne LED sowie den Piezo-Summer für 1 Sekunde."""

    red.value(1)  # Rote LED einschalten
    green.value(1)  # Grüne LED einschalten
    piezo_pin.duty(512)  # Piezo aktivieren
    time.sleep(1)
    red.value(0)  # Rote LED ausschalten
    green.value(0)  # Grüne LED ausschalten
    piezo_pin.duty(0)  # Piezo deaktivieren


def fall_sender():
    """Funktion, um den Zustand nach dem Sturz beim Sender zu behandeln.
    
    Diese Funktion aktiviert die rote und blaue LED sowie den Piezo-Summer.
    Nach 10
    Sekunden wird der Piezo-Summer aktiviert, wenn der Button nicht in der zeit gedrückt wurde."""

    # LEDs aktivieren und Piezo erst
    # nach 10 Sekunden einschalten, falls der Button nicht gedrückt wird
    start_time = time.time()  # Startzeitpunkt erfassen

    while fall_detected:
        red.value(1)
        blue.value(1)

        # Wenn 10 Sekunden vergangen sind und der Zustand noch aktiv ist, Piezo einschalten
        if time.time() - start_time >= 10:
            piezo_pin.duty(200)

        time.sleep(0.1)  # Kurze Pause, um CPU-Last zu reduzieren

    # Zustand beendet, LEDs und Piezo ausschalten
    red.value(0)
    blue.value(0)
    piezo_pin.duty(0)
    

def fall_nachricht_empfänger():

    """Funktion, um den Zustand "Fall erkannt" zu behandeln.
    
    Diese Funktion aktiviert die rote und blaue LED sowie den Piezo-Summer.
    Nach 10
    Sekunden wird der Piezo-Summer aktiviert, wenn der Button nicht in der zeit gedrückt wurde."""


    # LEDs aktivieren und Piezo erst nach 10 Sekunden einschalten, falls der Button nicht gedrückt wird
    global fall_detected
    fall_detected = True
    start_time = time.time()  # Startzeitpunkt erfassen

    while fall_detected:
        red.value(1)  # Rote LED einschalten
        blue.value(1)  # Blaue LED einschalten

        # Wenn 10 Sekunden vergangen sind und der Zustand noch aktiv ist, Piezo einschalten
        if time.time() - start_time >= 10:
            piezo_pin.duty(512)  # Piezo aktivieren

        time.sleep(0.1)  # Kurze Pause, um CPU-Last zu reduzieren

    # Zustand beendet, LEDs und Piezo ausschalten
    red.value(0)  # Rote LED ausschalten
    blue.value(0)  # Blaue LED ausschalten
    piezo_pin.duty(0)  # Piezo deaktivieren

def verletzt_nachricht_empfänger():

    """Funktion, um den Zustand "Verletzung erkannt" zu behandeln.
    
    Diese Funktion aktiviert die rote und grüne LED sowie den Piezo-Summer.
    Die LEDs und der Piezo-Summer wechseln sich alle 0,5 Sekunden ab, bis der button gedrückt wird wird."""

    # LEDs und Piezo aktivieren, bis der Zustand beendet wird
    global fall_detected
    fall_detected = True

    while fall_detected:
        red.value(1)
        green.value(0)
        piezo_pin.duty(512)  # Piezo aktivieren
        time.sleep(0.5)

        red.value(0)
        green.value(1)
        piezo_pin.duty(0)  # Piezo bleibt aktiv
        time.sleep(0.5)

    # Zustand beendet, LEDs und Piezo ausschalten
    red.value(0)
    green.value(0)
    piezo_pin.duty(0)

# Initialisiere Variablen für den Button-Interrupt
last_button_press_time = 0
button_press_count = 0

##################################################################################################################

#################################################################################################################

# Ab hier der Hauptteil des Programms

anschalten() # Gerät einschalten

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
        fall_sender() #funktion was das sende gerät macht wenn ein fall erkannt wurde

    if packet is None:
        # Kein Paket empfangen
        print("Received nothing! Listening again...")
    else:
        # Ein Paket wurde empfangen
        print("Received (raw bytes): {0}".format(packet))

        # Paketinhalte analysieren (binäre Zustände)
        if packet[0] == 0b001:  # "001" entspricht "Button gedrückt"
            button_nachricht() #funktion was der empfänger macht wenn der button gedrückt wurde
        
        elif packet[0] == 0b100:  # "100" entspricht "Fall erkannt"
            fall_nachricht_empfänger() #funktion was der empfänger macht wenn ein fall erkannt wurde

        elif packet[0] == 0b010:  # "010" entspricht "Doppelklick, Verletzt"
            verletzt_nachricht_empfänger() #funktion was der empfänger macht wenn ein verletzung erkannt wurde


        # Signalstärke (RSSI) des empfangenen Pakets auslesen und ausgeben
        rssi = rfm9x.last_rssi
        print("Received signal strength: {0} dB".format(rssi))
