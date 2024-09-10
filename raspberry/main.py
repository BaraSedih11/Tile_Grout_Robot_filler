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
    control = Control(sensors=sensors, movement=movement)

    try:
        for row in range(NUM_ROWS):
            for col in range(NUM_COLS):
                control.forward(TOTAL_WIDTH)
                time.sleep(2)

                if col == NUM_COLS - 1 and row < NUM_ROWS - 1:
                    if row % 2 == 0:
                        control.turn_right(90)
                    else:
                        control.turn_left(90)
                    control.forward(TOTAL_WIDTH)
                    time.sleep(2)
        control.stop()
    except KeyboardInterrupt:
        print("Program interrupted")
    finally:
        control.cleanup()
        GPIO.cleanup()

if __name__ == "__main__":
    if len(sys.argv) > 1:
        command = sys.argv[1]
        if command == "AUTOMATIC" and len(sys.argv) > 2:
            params = json.loads(sys.argv[2])
            width = params.get("width", 40)  # Default to 40 if not provided
            rows = params.get("rows", 2)  # Default to 2 if not provided
            columns = params.get("columns", 3)  # Default to 3 if not provided
            gaps = params.get("gaps", 2)  # Default to 2 if not provided
            run_automatic_mode(width, rows, columns, gaps)
        else:
            print(f"Unknown command or missing parameters: {command}")
    else:
        print("No command provided")
