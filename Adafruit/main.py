from machine import SPI, Pin, PWM, I2C, Timer
from adafruit_rfm9x import *
from ADXL345 import ADXL345_I2C
import time
import functions as f # Importiere die ausgelagerten Funktionen
import status # Importiere die ausgelagerten Statusvariablen

# Lora Konfiguration
CS = Pin(5, Pin.OUT)  
RESET = Pin(27, Pin.OUT)
spi = SPI(2, baudrate=1000000, polarity=0, phase=0, bits=8, firstbit=0, sck=Pin(18), mosi=Pin(23), miso=Pin(19))
RADIO_FREQ_MHZ = 433.0

# Initialisiere RFM radio
rfm9x = RFM9x(spi, CS, RESET, RADIO_FREQ_MHZ)
rfm9x.tx_power = 23

#-------------------------------------------------------------------------------------------------------

# IMU Konfiguration
i2c = I2C(0, scl=Pin(22), sda=Pin(21)) # I2C-Verbindung
imu = ADXL345_I2C(i2c)

# Freier Fall Konfiguration
FALL_THRESHOLD = 0.35  # Schwellenwert für freien Fall (nahe 0 g in allen Achsen)


# LED Konfiguration
red = Pin(13, Pin.OUT )
green = Pin(12, Pin.OUT)
blue = Pin(2, Pin.OUT )  # LED am ESP32 zur Kontrolle

# Piezo-speaker
piezo_pin = PWM(Pin(15))
piezo_pin.freq(1000)
piezo_pin.duty(0)

# Button
button = Pin(14, Pin.IN, Pin.PULL_UP)

# Initialisiere Variablen für den Button-Interrupt
last_button_press_time = 0
button_press_count = 0



# Funktion für den Button-Interrupt
def button_pressed_handler(pin):
    """Funktion, die aufgerufen wird, wenn der Button gedrückt wird.
    
    Diese Funktion sendet eine Nachricht über das Funkmodul, wenn der Button gedrückt wird.
    Bei einem Doppelklick wird eine andere Nachricht gesendet."""

    global last_button_press_time, button_press_count
    current_time = time.ticks_ms()
    if time.ticks_diff(current_time, last_button_press_time) <= 2000:
        button_press_count += 1
    else:
        button_press_count = 1

    last_button_press_time = current_time

    if button_press_count == 2:
        rfm9x.send(bytes([0b010]))
        print("Doppelklick Nachricht gesendet!")
        f.drücken_nachricht(red, green, piezo_pin)
    else:
        status.fall_detected = False
        rfm9x.send(bytes([0b001]))
        print("Button gedrückt Nachricht gesendet!")
        f.drücken_nachricht(red, green, piezo_pin)


#####################################
# Interrupt-Handler für den Button


def debounce(pin):
	# Timer wird mit einer Verzögerung von 200ms gestartet. 
	# Nach Ablauf wird die callback Funktion "button_pressed_handler" aufgerufen
	timer.init(mode=Timer.ONE_SHOT, period=200, callback=button_pressed_handler)

# Hardware timer init.
timer = Timer(0)
timer1 = Timer(1)
###########################################################

# Button-Interrupt hinzufügen
button.irq(trigger=Pin.IRQ_FALLING, handler=debounce)


#--------------------------------------------------------------------------------------------------------------------
print("Sent Hello World message!")
print("Waiting for packets...")

# Ab hier der Hauptteil des Programms

f.anschalten(red, green, piezo_pin)  # Gerät einschalten


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
        
        blue.value(1)  # Blaue LED einschalten
        
        # Nachricht senden: "100" für freien Fall erkannt
        rfm9x.send(bytes([0b100]))
        print("Fall detected Nachricht gesendet!")
        f.fall_sender(red, blue, piezo_pin)  # Funktion für das Sendegerät nach einem Fall

    if packet is None:
        # Kein Paket empfangen
        print("Received nothing! Listening again...")
    else:
        # Ein Paket wurde empfangen
        print("Received (raw bytes): {0}".format(packet))

        # Paketinhalte analysieren (binäre Zustände)
        if packet[0] == 0b001:  # "001" entspricht "Button gedrückt"
            timer1.deinit() # Timer stoppen um fall_nachricht_empfänger zu verhindern
            f.button_nachricht(red, green, piezo_pin)  # Funktion für das Empfängergerät


        elif packet[0] == 0b100:  # "100" entspricht "Fall erkannt"
            red.value(1)

            # timer starten
            timer1.init(mode=Timer.ONE_SHOT, period=10000, callback=lambda t: f.fall_nachricht_empfänger(red, blue, piezo_pin))

        elif packet[0] == 0b010:  # "010" entspricht "Doppelklick, Verletzt"
            f.verletzt_nachricht_empfänger(red, green, piezo_pin)  # Funktion für das Empfängergerät bei Verletzung

