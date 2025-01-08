import time
from machine import Pin

led_pin = Pin(2, Pin.OUT)

while 1:
    print('Congratulation, the setup works, you are a genius10')

    time.sleep(0.2)
    led_pin.on()

    time.sleep(1)
    led_pin.off()
     