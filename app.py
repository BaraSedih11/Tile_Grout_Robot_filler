from picamera2 import Picamera2
import cv2
import numpy as np
from flask import Flask, request, jsonify, render_template, Response
import serial  # Serial communication with Arduino
import time
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Initialize Picamera2
picam2 = Picamera2()
picam2.configure(picam2.create_preview_configuration(main={"format": 'XRGB8888', "size": (640, 480)}))
picam2.start()

# A flag to stop the video thread
video_running = True

# Set up the serial connection to Arduino
arduino = serial.Serial(port='/dev/ttyACM0', baudrate=9600, timeout=1)
arduino.flush()

# Movement commands using serial communication with Arduino
def send_serial_command(command):
    """Send a command over serial to the Arduino and wait for the 'DONE' response."""
    if arduino.is_open:
        
        arduino.write(f"{command}\n".encode())
        print(f"Sent command: {command}")
        
        while True:
            if arduino.in_waiting > 0:  # Check if there's incoming data in the serial buffer
                response = arduino.readline().decode().strip()
                print(f"Arduino response: {response}")
                if response == "DONE":  # Exit the loop if 'DONE' is received
                    break
            time.sleep(0.1)  # Add a small delay to avoid excessive CPU usage in the loop
    else:
        print("Serial port not open")

# Image processing and gap detection logic (camera input)
class Processing:
    def preprocess_image(self, image):
        if len(image.shape) == 2:
            gray = image
        else:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Apply a bilateral filter to preserve edges
        filtered = cv2.bilateralFilter(gray, 9, 75, 75)
        
        # Apply Canny edge detection
        edges = cv2.Canny(filtered, 50, 150, apertureSize=3)
        
        # Perform morphological operations to enhance edges
        kernel = np.ones((3, 3), np.uint8)
        edges = cv2.dilate(edges, kernel, iterations=1)
        edges = cv2.erode(edges, kernel, iterations=1)
        
        return edges

    def detect_gap(self, edges):
        # Refine line detection parameters
        lines = cv2.HoughLinesP(edges, 1, np.pi/180, threshold=100, minLineLength=30, maxLineGap=10)
        if lines is None:
            return False, None
        
        frame_center = 320  # Assuming frame width is 640
        center_xs = []
        for line in lines:
            x1, y1, x2, y2 = line[0]
            if abs(x2 - x1) < 10 and abs(y2 - y1) > 20:  # Detect mostly vertical lines
                center_x = (x1 + x2) // 2
                center_xs.append(center_x)
        
        if not center_xs:
            return False, None
        
        # Use the average center of detected lines to correct the path
        average_center_x = int(np.mean(center_xs))
        return True, average_center_x


def capture_frame():
    frame = picam2.capture_array()
    # Extract only RGB channels from the XRGB8888 format
    frame = frame[:, :, :3]  # Extract RGB ignoring the alpha channel
    return frame

def check_gap_status():
    frame = capture_frame()
    processing = Processing()
    edges = processing.preprocess_image(frame)
    gap_detected, center_x = processing.detect_gap(edges)
    return gap_detected, center_x

# Serve the frontend
@app.route('/')
def index():
    return render_template('index.html')

# Flask API Routes
@app.route('/check-gap', methods=['GET'])
def check_gap():
    gap_detected, _ = check_gap_status()
    return jsonify(gapDetected=gap_detected)

@app.route('/video_feed')
def video_feed():
    return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

def gen_frames():
    while video_running:
        frame = capture_frame()
        if frame is None:
            print("Error: Failed to capture frame.")
            break
        else:
            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

    picam2.stop()
    cv2.destroyAllWindows()

# Route to handle manual commands from the UI
@app.route('/command', methods=['POST'])
def command():
    try:
        data = request.get_json()
        print("Received data:", data)
        command = data.get('command')
        
        send_serial_command(command)

        return jsonify({"response": f"Command {command} executed"})

    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route('/automatic-mode', methods=['POST'])
def automatic_mode():
    try:
        print("Automatic mode request received")
        data = request.get_json()
        print("Received data for automatic mode:", data)

        width = data.get('width', 40)
        rows = data.get('rows', 2)
        columns = data.get('columns', 3)
        gaps = data.get('gaps', 2)

        run_automatic_mode(width, rows, columns, gaps)

        return jsonify({"response": "Automatic mode initiated"})

    except Exception as e:
        print(f"Error in automatic mode: {e}")
        return jsonify({"error": str(e)}), 400

# Automatic mode handler with path correction
def run_automatic_mode(tile_width, rows, columns, gaps):
    total_tile_width = tile_width + gaps  # Total width including gaps
    max_col_distance = (columns - 1) * total_tile_width  # Maximum column distance
    max_row_distance = (rows - 1) * total_tile_width  # Maximum row distance
    step_size = 10  # Define a smaller step size for movement

    def move_in_steps(total_distance):
        # Move in smaller increments, correcting path between steps
        remaining_distance = total_distance
        while remaining_distance > 0:
            move_distance = min(step_size, remaining_distance)
            send_serial_command(f"MOVE_FORWARD {move_distance}")
            correct_path()
            remaining_distance -= move_distance

    def correct_path():
        # Correct path based on camera feedback
        gap_detected, center_x = check_gap_status()
        if gap_detected:
            frame_center = 320  # Assuming frame width is 640
            offset = center_x - frame_center
            print(f"Path correction needed, offset: {offset}")
            
            # Proportional control for more accurate rotation
            if abs(offset) > 20:  # Set a smaller threshold for correction
                rotation_angle = min(10, max(2, int(abs(offset) / 10)))  # Adjust rotation based on offset size
                if offset > 0:
                    send_serial_command(f"ROTATE_RIGHT {rotation_angle}")  # Adjust right
                else:
                    send_serial_command(f"ROTATE_LEFT {rotation_angle}")  # Adjust left


    def rotate():
        send_serial_command(f"MOVE_BACKWARD {total_tile_width / 1.25}")  # 32.2
        send_serial_command(f"ROTATE_RIGHT {97}")  # 90 deg
        send_serial_command(f"MOVE_BACKWARD {total_tile_width / 3.5}")  # 23

    for col in range(columns - 1):
        move_in_steps(max_col_distance)

        if col < columns - 1:
            rotate()
            move_in_steps(max_row_distance)
            rotate()
            
        send_serial_command("STOP")
    
    print("Automatic mode completed")


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
