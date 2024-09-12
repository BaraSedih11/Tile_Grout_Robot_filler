import sys
import time
import json
import cv2
import numpy as np
import requests
from flask import Flask, request, jsonify, Response

app = Flask(__name__)

# Movement and Control classes (formerly from movement.py and control.py)
class Movement:
    def __init__(self):
        self.position = 0  # Placeholder for actual movement logic

    def move_forward(self, distance_cm):
        print(f"Moving forward {distance_cm} cm")
        self.position += distance_cm

    def move_backward(self, distance_cm):
        print(f"Moving backward {distance_cm} cm")
        self.position -= distance_cm

    def rotate_right(self, angle_deg):
        print(f"Rotating right {angle_deg} degrees")

    def rotate_left(self, angle_deg):
        print(f"Rotating left {angle_deg} degrees")

    def stop(self):
        print("Stopping robot")

    def move_to_next_row(self):
        print("Moving to the next row")


# Image processing and gap detection logic (formerly from processing.py)
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


# Flask API Routes (formerly from processing.py)
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


# Command handler (merging logic from main.py)
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


def handle_manual_command(command, value=None):
    movement = Movement()

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
        print(f"Unknown command: {command}")


if __name__ == "__main__":
    if len(sys.argv) > 1:
        command = sys.argv[1]

        # Manual movement commands
        if command in ["MOVE_FORWARD", "MOVE_BACKWARD", "ROTATE_LEFT", "ROTATE_RIGHT"]:
            if len(sys.argv) > 2:
                value = int(sys.argv[2])
                handle_manual_command(command, value)
            else:
                print(f"Error: {command} requires a value (distance or angle).")
        elif command == "STOP":
            handle_manual_command(command)
        # Automatic mode
        elif command == "AUTOMATIC" and len(sys.argv) > 2:
            params = json.loads(sys.argv[2])
        else:
            print("Unknown command or insufficient arguments.")

    # Start Flask server for gap detection
    app.run(host='0.0.0.0', port=5050)
