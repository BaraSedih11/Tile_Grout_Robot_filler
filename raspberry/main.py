import sys
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

    # Initialize movement class (which communicates with Arduino)
    movement = Movement()

    # Initialize control class
    control = Control(None, movement)  # No sensors are needed

    # Example of sending a command to the movement class in automatic mode
    for row in range(NUM_ROWS):
        for col in range(NUM_COLS):
            movement.move_forward(TOTAL_WIDTH)
            time.sleep(1)  # Simulate time taken to move
        movement.move_to_next_row()

def handle_manual_command(command):
    # GPIO.setmode(GPIO.BCM)
    # GPIO.setwarnings(False)

    # Initialize movement class (which communicates with Arduino)
    movement = Movement()

    # Initialize control class
    control = Control(None, movement)  # No sensors are needed for manual mode

    try:
        if "MOVE_FORWARD" in command:
            print(command)
            distance = int(command.split()[1])
            control.forward(distance)
        elif "MOVE_BACKWARD" in command:
            distance = int(command.split()[1])
            control.backward(distance)
        elif "ROTATE_LEFT" in command:
            angle = int(command.split()[1])
            control.turn_left(angle)
        elif "ROTATE_RIGHT" in command:
            angle = int(command.split()[1])
            control.turn_right(angle)
        elif command == "STOP":
            control.stop()
        else:
            print(f"Unknown command: {command}")
    except Exception as e:
        print(f"Error executing command: {e}")
    finally:
        control.cleanup()
        GPIO.cleanup()

if __name__ == "__main__":
    if len(sys.argv) > 1:
        command = sys.argv[1]

        # If the command is for automatic mode, handle it
        if command == "AUTOMATIC" and len(sys.argv) > 2:
            params = json.loads(sys.argv[2])
            width = params.get("width", 40)  # Default to 40 if not provided
            rows = params.get("rows", 2)  # Default to 2 if not provided
            columns = params.get("columns", 3)  # Default to 3 if not provided
            gaps = params.get("gaps", 2)  # Default to 2 if not provided
            run_automatic_mode(width, rows, columns, gaps)
        # Handle manual mode commands
        else:
            handle_manual_command(command)
    else:
        print("No command provided")
