import os
import sys
import json
import time
import cv2
import numpy as np
from flask import Flask, request, jsonify, render_template, Response
import serial  # Serial communication with Arduino

app = Flask(__name__)

# Set up the serial connection to Arduino
# Make sure the port and baudrate match the ones used by your Arduino
arduino = serial.Serial(port='COM3', baudrate=9600, timeout=1)

# Movement commands using serial communication with Arduino
def send_serial_command(command):
    """Send a command over serial to the Arduino."""
    if arduino.is_open:
        arduino.write(f"{command}\n".encode())
        print(f"Sent command: {command}")
    else:
        print("Serial port not open")

# Movement class to wrap serial commands
class Movement:
    def move_forward(self, distance_cm):
        send_serial_command(f"MOVE_FORWARD {distance_cm}")

    def move_backward(self, distance_cm):
        send_serial_command(f"MOVE_BACKWARD {distance_cm}")

    def rotate_right(self, angle_deg):
        send_serial_command(f"ROTATE_RIGHT {angle_deg}")

    def rotate_left(self, angle_deg):
        send_serial_command(f"ROTATE_LEFT {angle_deg}")

    def stop(self):
        send_serial_command("STOP")

    def move_to_next_row(self):
        send_serial_command("MOVE_NEXT_ROW")


# Image processing and gap detection logic (camera input)
class Processing:
    def preprocess_image(self, image):
        if len(image.shape) == 2:
            gray = image
        else:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        blurred = cv2.GaussianBlur(gray, (3, 3), 0)
        edges = cv2.Canny(blurred, 50, 150, apertureSize=3)
        return edges

    def detect_gap(self, edges):
        lines = cv2.HoughLinesP(edges, 1, np.pi/180, threshold=50, minLineLength=20, maxLineGap=5)
        if lines is None:
            return False
        for line in lines:
            x1, y1, x2, y2 = line[0]
            if abs(x2 - x1) < 10 and abs(y2 - y1) > 10:
                return True
        return False


def capture_frame():
    cap = cv2.VideoCapture(0)  # 0 for default camera
    ret, frame = cap.read()
    cap.release()
    return frame

def check_gap_status():
    frame = capture_frame()
    processing = Processing()
    edges = processing.preprocess_image(frame)
    gap_detected = processing.detect_gap(edges)
    return gap_detected

# Serve the frontend
@app.route('/')
def index():
    return render_template('index.html')

# Flask API Routes
@app.route('/check-gap', methods=['GET'])
def check_gap():
    gap_detected = check_gap_status()
    return jsonify(gapDetected=gap_detected)


@app.route('/video_feed')
def video_feed():
    def generate():
        cap = cv2.VideoCapture(0)  # 0 for default camera
        while True:
            ret, frame = cap.read()
            _, jpeg = cv2.imencode('.jpg', frame)
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + jpeg.tobytes() + b'\r\n')
        cap.release()

    return Response(generate(), mimetype='multipart/x-mixed-replace; boundary=frame')


# Route to handle manual commands from the UI
@app.route('/command', methods=['POST'])
def command():
    try:
        # Log the incoming request body for debugging
        data = request.get_json()
        print("Received data:", data)  # Check the received data structure

        # Ensure that 'command' is present in the request body
        command = data.get('command')
        value = data.get('value', 0)

        print("Command:", command)
        print("Value:", value)

        if not command:
            return jsonify({"error": "Missing 'command' in request"}), 400

        movement = Movement()  # Instantiate Movement class

        # Execute the command received from the client
        if command == "MOVE_FORWARD":
            movement.move_forward(value)
        elif command == "MOVE_BACKWARD":
            movement.move_backward(value)
        elif command == "ROTATE_LEFT":
            movement.rotate_left(value)
        elif command == "ROTATE_RIGHT":
            movement.rotate_right(value)
        elif command == "STOP":
            movement.stop()
        else:
            return jsonify({"error": "Unknown command"}), 400

        return jsonify({"response": f"Command {command} executed"})

    except Exception as e:
        return jsonify({"error": str(e)}), 400


# New Route for Automatic Mode
@app.route('/automatic-mode', methods=['POST'])
def automatic_mode():
    try:
        # Get parameters for automatic mode from request
        data = request.get_json()
        print("Received data for automatic mode:", data)

        width = data.get('width', 40)
        rows = data.get('rows', 2)
        columns = data.get('columns', 3)
        gaps = data.get('gaps', 2)

        # Run the automatic mode with the given parameters
        run_automatic_mode(width, rows, columns, gaps)

        return jsonify({"response": "Automatic mode initiated"})

    except Exception as e:
        return jsonify({"error": str(e)}), 400


# Automatic mode handler
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

if __name__ == '__main__':
    # Serve the application on port 5000
    app.run(host='0.0.0.0', port=5000)
