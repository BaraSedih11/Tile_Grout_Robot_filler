from sensors import Sensors
from movement import Movement
from control import Control
import RPi.GPIO as GPIO
import time

# Define grid dimensions and tile properties
TILE_WIDTH = 40  # cm
GAP_WIDTH = 2    # cm
TOTAL_WIDTH = TILE_WIDTH + GAP_WIDTH  # Total width to move per tile

NUM_ROWS = 2
NUM_COLS = 3

if __name__ == "__main__":
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)

    # Initialize sensors (ultrasonic sensor pins)
    sensors = Sensors(trig_pin=24, echo_pin=23)  # Adjust GPIO pins for TRIG and ECHO

    # Initialize movement class (which communicates with Arduino)
    movement = Movement()

    # Initialize control class
    control = Control(sensors=sensors, movement=movement)

    try:
        time.sleep(2)        # Ensure there is enough time for the movement to finish
        # first line
        control.forward(82)  # Move forward 80 cm
        time.sleep(4)        # Ensure there is enough time for the movement to finish
        control.stop()
        time.sleep(1)
        control.backward(15)  # Move backward 15 cm
        time.sleep(2)         # Wait for movement to complete
        control.stop()
        time.sleep(1)
        control.turn_right(194)  # Turn right 180 degrees
        time.sleep(5)          # Wait for rotation to complete (longer for 180 degrees)
        control.stop()
        time.sleep(1)
        control.forward(17)  # Move forward 17 cm
        time.sleep(2)        # Wait for movement to complete
        control.stop()
        time.sleep(1)
        control.turn_left(97)  # Turn left 90 degrees
        time.sleep(4)          # Wait for rotation to complete
        control.stop()

        time.sleep(2)        # Ensure there is enough time for the movement to finish
        # Second line
        control.forward(113)  # Move forward 110 cm
        time.sleep(8)         # Wait for movement to complete
        control.stop()
        time.sleep(1)
        control.backward(18)  # Move backward 15 cm
        time.sleep(2)         # Wait for movement to complete
        control.stop()
        time.sleep(1)
        control.turn_right(194)  # Turn right 180 degrees
        time.sleep(8)          # Wait for rotation to complete
        control.stop()
        time.sleep(1)
        control.forward(17)  # Move forward 17 cm
        time.sleep(2)        # Wait for movement to complete
        control.stop()
        time.sleep(1)
        control.turn_left(97)  # Turn left 90 degrees
        time.sleep(3)          # Wait for rotation to complete

        # After finishing the sequence, stop the robot
        control.stop()
        time.sleep(1)
        
        
        # control.forward(42)
        # Start at the bottom left of the grid (Tile 1, Row 1)
        # for row in range(NUM_ROWS):
        #     for col in range(NUM_COLS):
        #         # Move forward by one tile (42 cm)
        #         control.forward(TOTAL_WIDTH)

        #         # At the end of the row, turn to the next row
        #         if col == NUM_COLS - 1:
        #             if row < NUM_ROWS - 1:
        #                 # If it's not the last row, move to the next row
        #                 if row % 2 == 0:
        #                     # If it's an even row, turn left and move up)
        #                     # control.forward(10)
        #                     control.turn_right(90)
        #                     control.forward(TOTAL_WIDTH)
        #                 else:
        #                     # If it's an odd row, turn right and move up
        #                     # control.forward(10)
        #                     control.turn_left(90)
        #                     control.forward(TOTAL_WIDTH)
        #         else:
        #             # Continue moving forward in the same row
        #             control.forward(TOTAL_WIDTH)

        # # After finishing the grid, stop the robot
        # control.stop()
    except KeyboardInterrupt:
        print("Program interrupted")
    finally:
        control.cleanup()
        GPIO.cleanup()
