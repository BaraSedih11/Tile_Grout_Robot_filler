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
arduino = serial.Serial(port='/dev/ttyACM1', baudrate=9600, timeout=1)
arduino.flush()

# Movement commands using serial communication with Arduino
def send_serial_command(command, value=0):
    """Send a command over serial to the Arduino and wait for the 'DONE' response."""
    if arduino.is_open:
        if command in ['APPLY', 'EMPTY', 'STOP']:
            arduino.write(f"{command}\n".encode())
            print(f"Sent command: {command}")
        else:
            arduino.write(f"{command} {value}\n".encode())
            print(f"Sent command: {command} {value}")
        
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
        blurred = cv2.GaussianBlur(gray, (3, 3), 0)
        edges = cv2.Canny(blurred, 50, 150, apertureSize=3)
        return edges

    def detect_gap(self, edges):
        lines = cv2.HoughLinesP(edges, 1, np.pi/180, threshold=50, minLineLength=20, maxLineGap=5)
        if lines is None:
            return False, None
        for line in lines:
            x1, y1, x2, y2 = line[0]
            if abs(x2 - x1) < 10 and abs(y2 - y1) > 10:
                center_x = (x1 + x2) // 2
                return True, center_x
        return False, None

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
        value = data.get('value', 0)

        if not command:
            return jsonify({"error": "Missing 'command' in request"}), 400

        if command == "MOVE_FORWARD":
            send_serial_command("MOVE_FORWARD", value)
        elif command == "MOVE_BACKWARD":
            send_serial_command("MOVE_BACKWARD", value)
        elif command == "ROTATE_LEFT":
            send_serial_command("ROTATE_LEFT", value)
        elif command == "ROTATE_RIGHT":
            send_serial_command("ROTATE_RIGHT", value)
        elif command == "MOVE_FRONT":
            send_serial_command("MOVE_FRONT", value)
        elif command == "APPLY":
            send_serial_command("APPLY")
        elif command == "EMPTY":
            send_serial_command("EMPTY")
        elif command == "STOP":
            send_serial_command("STOP")
        else:
            return jsonify({"error": "Unknown command"}), 400

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
    total_tile_width = tile_width + gaps  # 40.25
    max_col_distance = (columns - 1) * total_tile_width  # 80.5
    max_row_distance = (rows - 1) * total_tile_width  # 120.75
    
    def rotate():
        send_serial_command("MOVE_BACKWARD", total_tile_width / 1.25)  # 32.2
        send_serial_command("ROTATE_RIGHT", 97)  # 90 deg
        send_serial_command("MOVE_BACKWARD", total_tile_width / 3.5)  # 23

    def correct_path():
        # Correct path based on camera feedback
        gap_detected, center_x = check_gap_status()
        if gap_detected:
            frame_center = 320  # Assuming frame width is 640
            offset = center_x - frame_center
            print(f"Path correction needed, offset: {offset}")
            if abs(offset) > 50:  # If the deviation is significant
                if offset > 0:
                    send_serial_command("ROTATE_RIGHT", 5)  # Adjust right
                else:
                    send_serial_command("ROTATE_LEFT", 5)  # Adjust left

    for col in range(columns - 1):
        send_serial_command("MOVE_FORWARD", max_col_distance)  # 80.5
        correct_path()

        if col < columns - 1:
            rotate()
            send_serial_command("MOVE_FORWARD", max_row_distance)  # 120.75
            correct_path()
            rotate()
            
        send_serial_command("STOP")
    
    print("Automatic mode completed")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
