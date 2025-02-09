from machine import Pin
import time

button = Pin(14, Pin.IN, Pin.PULL_UP)

while True:
    if button.value() == 0:
        print("Button gedrückt!")
    else:
        print("Button nicht gedrückt!")
    time.sleep(0.1)
