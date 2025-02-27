from machine import SPI, Pin, PWM, I2C, Timer
from adafruit_rfm9x import *
from ADXL345 import ADXL345_I2C
import time
import functions as f # Importiere die ausgelagerten Funktionen
import status # Importiere die ausgelagerten Statusvariablen

# Lora Konfiguration
CS = Pin(5, Pin.OUT) # Chip-Select-Pin
RESET = Pin(27, Pin.OUT) # Reset-Pin
spi = SPI(2, baudrate=1000000, polarity=0, phase=0, bits=8, firstbit=0, sck=Pin(18), mosi=Pin(23), miso=Pin(19)) # SPI-Verbindung
RADIO_FREQ_MHZ = 433.0 # Funkfrequenz in MHz

rfm9x = RFM9x(spi, CS, RESET, RADIO_FREQ_MHZ) # Erstellung eines RFM9x-Objekts
rfm9x.tx_power = 23 # Sendeleistung auf 23 Dezibel-Milliwatt (dBm) einstellen

# IMU Konfiguration
i2c = I2C(0, scl=Pin(22), sda=Pin(21)) # I2C-Verbindung
imu = ADXL345_I2C(i2c)

# LED Konfiguration
red = Pin(13, Pin.OUT )
green = Pin(12, Pin.OUT)

# Piezo-speaker Konfiguration
piezo_pin = PWM(Pin(15))
piezo_pin.freq(1000)
piezo_pin.duty(0)

# Button Konfiguration
button = Pin(14, Pin.IN, Pin.PULL_UP)

# Initialisiere Variablen 
last_button_press_time = 0 
button_press_count = 0

fall_threshold = 0.35  # Schwellenwert für freien Fall (nahe 0 g in allen Achsen)

# Timer initialisieren
timer_debounce = Timer(0)
timer_sturz = Timer(1)

# Funktion für den Button-Interrupt
def button_pressed_handler(pin):
    """Funktion, die aufgerufen wird, wenn der Button gedrückt wird.
    
    Diese Funktion sendet eine Nachricht über das Funkmodul, wenn der Button gedrückt wird.
    Bei einem Doppelklick wird eine andere Nachricht gesendet."""

    global last_button_press_time, button_press_count

    # Prüfe, ob der Button innerhalb von 2 Sekunden erneut gedrückt wurde
    current_time = time.ticks_ms()
    if time.ticks_diff(current_time, last_button_press_time) <= 2000:
        button_press_count += 1
    else:
        button_press_count = 1

    last_button_press_time = current_time # Aktualisiere die Zeit

    # Sende entsprechende Nachricht basierend auf der Anzahl der Button-Drücke
    if button_press_count == 2:
        rfm9x.send(bytes([0b010]))
        print("Doppelklick Nachricht gesendet!")

    else:
        status.fall_detected = False
        rfm9x.send(bytes([0b001]))
        print("Button gedrückt Nachricht gesendet!")
    
    f.drücken_nachricht(red, green, piezo_pin) # Hinweis für das Sendegerät, dass der Button gedrückt wurde

# Funktion für den Button-Debounce
def debounce(pin):
    '''Funktion, um den Button-Interrupt zu entprellen.
    Diese Funktion startet einen Timer, um den Button-Interrupt zu entprellen und die Button-Pressed-Handler-Funktion aufzurufen.'''
	
    timer_debounce.init(mode=Timer.ONE_SHOT, period=200, callback=button_pressed_handler)

# Button-Interrupt hinzufügen
button.irq(trigger=Pin.IRQ_FALLING, handler=debounce)

#-------------------------------------------------------------Hauptschleife------------------------------------------------------------------------


f.anschalten(red, green, piezo_pin)  # Testfunktion für die LEDs und den Piezo-Summer

print("Waiting for packets...")

while True:
    # Empfange ein Paket mit den RFM9x-Funkmodul
    packet = rfm9x.receive()

    # Beschleunigungswerte auslesen
    x = imu.xValue / 256  # Werte in g umwandeln
    y = imu.yValue / 256
    z = imu.zValue / 256

    # Berechne die Magnitude (Betrag des Beschleunigungsvektors)
    beschleunigung = f.beschleunigungsvektor_berechnen(x, y, z)

    # Prüfe auf freien Fall anhand eines Schwellenwerts
    if beschleunigung < fall_threshold:
        
        rfm9x.send(bytes([0b100])) # Nachricht senden: "100" für freien Fall erkannt
        print("Fall detected Nachricht gesendet!")

        f.fall_sender(red, piezo_pin)  # Hinweis für das Sendegerät, dass ein Fall erkannt wurde

    # Prüfe, ob ein Paket empfangen wurde
    if packet is None:
        # Kein Paket empfangen
        print("Received nothing! Listening again...")

    else:
        # Ein Paket wurde empfangen
        print("Received (raw bytes): {0}".format(packet))

        # Paketinhalte analysieren (binäre Zustände)
        if packet[0] == 0b001:  # "001" entspricht "Button gedrückt"
            timer_sturz.deinit() # Timer stoppen um fall_nachricht_empfänger zu verhindern
            f.button_nachricht(red, green, piezo_pin)  # Hinweis für das Empfängergerät, dass der Button gedrückt wurde

        elif packet[0] == 0b100:  # "100" entspricht "Fall erkannt"
            red.value(1)

            # Timer starten, um nach 10 Sekunden eine Nachricht an den Empfänger zu senden
            timer_sturz.init(mode=Timer.ONE_SHOT, period=10000, callback=lambda t: f.fall_nachricht_empfänger(red, piezo_pin))

        elif packet[0] == 0b010:  # "010" entspricht "Doppelklick, Verletzt"
            f.verletzt_nachricht_empfänger(red, green, piezo_pin)  # Hinweis für den Empfänger, dass der Benutzer verletzt ist

