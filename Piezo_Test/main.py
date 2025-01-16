import machine
import time

# Set up the piezo on pin 15 with PWM
piezo = machine.PWM(machine.Pin(15))
piezo.freq(1000)  # Set frequency to 1000 Hz

# Function to test the piezo with PWM
def test_piezo():
    for _ in range(10):
        piezo.duty(512)  # Set duty cycle to 50%
        time.sleep(0.5)
        piezo.duty(0)  # Turn off the piezo
        time.sleep(0.5)

# Run the test
test_piezo()
print("Piezo test complete!")