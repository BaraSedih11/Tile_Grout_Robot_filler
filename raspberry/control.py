# import time
# import RPi.GPIO as GPIO

class Control:
    def __init__(self, sensors, movement):
        self.sensors = sensors
        self.movement = movement
        self.distance_threshold = 25.0  # Threshold in cm for stopping at obstacles

    def forward(self, distance_cm):
        print(f"Moving forward {distance_cm} cm")
        self.movement.move_forward(distance_cm)

    def backward(self, distance_cm):
        print(f"Moving backward {distance_cm} cm")
        self.movement.move_backward(distance_cm)

    def turn_right(self, angle_deg):
        print(f"Turning right {angle_deg} degrees")
        self.movement.rotate_right(angle_deg)

    def turn_left(self, angle_deg):
        print(f"Turning left {angle_deg} degrees")
        self.movement.rotate_left(angle_deg)

    def stop(self):
        print("Sending command: STOP")
        self.movement.stop()

    def cleanup(self):
        self.movement.stop()
        # GPIO.cleanup()

