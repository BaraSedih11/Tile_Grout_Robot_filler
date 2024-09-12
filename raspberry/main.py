import sys
import time
import json
import requests  # Correct import for requests

from movement import Movement
from control import Control
# import RPi.GPIO as GPIO

def run_automatic_mode(width, rows, columns, gaps):
    TILE_WIDTH = width
    GAP_WIDTH = gaps
    TOTAL_WIDTH = TILE_WIDTH + GAP_WIDTH

    NUM_ROWS = rows
    NUM_COLS = columns

    movement = Movement()

    for row in range(NUM_ROWS):
        for col in range(NUM_COLS):
            movement.move_forward(TOTAL_WIDTH)
            gap_detected = check_gap_status()
            if not gap_detected:
                print("Deviation detected, stopping.")
                movement.stop()
                break
            time.sleep(1)
        movement.move_to_next_row()

def check_gap_status():
    # Call the API to check for gap detection
    response = requests.get("http://localhost:5050/check-gap")
    result = response.json()
    return result['gapDetected']

def handle_manual_command(command, value=None):
    # GPIO.setmode(GPIO.BCM)
    # GPIO.setwarnings(False)

    # Initialize movement class (which communicates with Arduino)
    movement = Movement()

    # Initialize control class
    control = Control(None, movement)  # No sensors are needed for manual mode
    try:
        if command == "MOVE_FORWARD":
            control.forward(value)
        elif command == "MOVE_BACKWARD":
            control.backward(value)
        elif command == "ROTATE_LEFT":
            control.turn_left(value)
        elif command == "ROTATE_RIGHT":
            control.turn_right(value)
        elif command == "STOP":
            control.stop()
        else:
            print(f"Unknown command: {command}")
    except Exception as e:
        print(f"Error executing command: {e}")
    # finally:
        # control.cleanup()
        # GPIO.cleanup()

if __name__ == "__main__":
    if len(sys.argv) > 1:
        command = sys.argv[1]

        # Check if it's a manual command with an optional distance/angle
        if command in ["MOVE_FORWARD", "MOVE_BACKWARD", "ROTATE_LEFT", "ROTATE_RIGHT"]:
            # Ensure a distance or angle is provided for these commands
            if len(sys.argv) > 2:
                value = int(sys.argv[2])
                handle_manual_command(command, value)
            else:
                print(f"Error: {command} requires a value (distance or angle).")
        elif command == "STOP":
            handle_manual_command(command)
        elif command == "AUTOMATIC" and len(sys.argv) > 2:
            params = json.loads(sys.argv[2])
            width = params.get("width", 40)  # Default to 40 if not provided
            rows = params.get("rows", 2)  # Default to 2 if not provided
            columns = params.get("columns", 3)  # Default to 3 if not provided
            gaps = params.get("gaps", 2)  # Default to 2 if not provided
            run_automatic_mode(width, rows, columns, gaps)
        else:
            print("Unknown command or insufficient arguments.")
