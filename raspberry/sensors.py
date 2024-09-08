import time
import RPi.GPIO as GPIO
import collections

class Sensors:
    def __init__(self, trig_pin, echo_pin):
        self.TRIG_PIN = trig_pin
        self.ECHO_PIN = echo_pin
        self.distance = 0.0
        self.distance_history = collections.deque(maxlen=3)
        self.setup()

    def setup(self):
        GPIO.setwarnings(False)
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.TRIG_PIN, GPIO.OUT)
        GPIO.setup(self.ECHO_PIN, GPIO.IN)

    def measure_distance(self):
        # Ensure TRIG is low before starting
        GPIO.output(self.TRIG_PIN, False)
        time.sleep(0.025)

        # Send a short pulse to trigger the sensor
        GPIO.output(self.TRIG_PIN, True)
        time.sleep(0.00001)
        GPIO.output(self.TRIG_PIN, False)

        pulse_start = time.time()
        pulse_end = time.time()

        # Wait for the pulse to start
        while GPIO.input(self.ECHO_PIN) == 0:
            pulse_start = time.time()
            if time.time() - pulse_start > 0.02:  # Timeout after 20ms
                return None

        # Wait for the pulse to end
        while GPIO.input(self.ECHO_PIN) == 1:
            pulse_end = time.time()
            if time.time() - pulse_start > 0.02:  # Timeout after 20ms
                return None

        # Calculate the pulse duration
        pulse_duration = pulse_end - pulse_start
        new_distance = pulse_duration * 17150  # Convert to distance (cm)
        new_distance = round(new_distance, 2)
        new_distance *= 250
	
        if new_distance <= 0 or new_distance > 400:  # Typical range limit for HC-SR04
            return None

        # Add the new distance reading to the history
        self.distance_history.append(new_distance)

        # Calculate the moving average of the distance readings
        self.distance = sum(self.distance_history) / len(self.distance_history)

        return self.distance
