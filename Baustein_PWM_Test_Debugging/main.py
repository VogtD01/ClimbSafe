import time
from machine import Pin, PWM

led_pin = Pin(15, Pin.OUT)
led_pin1 = Pin(2, Pin.OUT)
pwm = PWM(led_pin)
pwm1 = PWM(led_pin1)
pwm.freq(1000)
pwm1.freq(1000)

# Funktion zum Dimmen der LEDs
def dim_led():
    # erhöhe Helligkeit
    for duty in range(0, 1024, 10):
        pwm.duty(duty)
        pwm1.duty(duty)
        time.sleep(0.05)
    
    # verringere Helligkeit
    for duty in range(1023, -1, -10):
        pwm.duty(duty)
        pwm1.duty(duty)
        time.sleep(0.05)

while True:

    dim_led()
    print("LED dimming cycle complete!")