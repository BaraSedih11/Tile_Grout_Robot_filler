import sys
import json
from sensors import Sensors
from movement import Movement
from control import Control
import RPi.GPIO as GPIO
import time

def run_automatic_mode(width, rows, columns, gaps):
    TILE_WIDTH = width  # Use the passed width
    GAP_WIDTH = gaps  # Use the passed gaps
    TOTAL_WIDTH = TILE_WIDTH + GAP_WIDTH  # Total width to move per tile

    NUM_ROWS = rows  # Use the passed number of rows
    NUM_COLS = columns  # Use the passed number of columns

    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)

    # Initialize sensors (ultrasonic sensor pins)
    sensors = Sensors(trig_pin=24, echo_pin=23)  # Adjust GPIO pins for TRIG and ECHO

    # Initialize movement class (which communicates with Arduino)
    movement = Movement()

    # Initialize control class
    control = Control(sensors, movement)

    # Example of sending a command to the movement class
    for row in range(NUM_ROWS):
        for col in range(NUM_COLS):
            movement.move_forward(TOTAL_WIDTH)
            time.sleep(1)  # Simulate time taken to move
        movement.move_to_next_row()

if __name__ == "__main__":
    # Example usage
    run_automatic_mode(10, 5, 5, 2)