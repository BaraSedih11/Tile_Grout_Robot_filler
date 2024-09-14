import cv2
import numpy as np
from flask import Flask, request, jsonify, render_template, Response
import serial  # Serial communication with Arduino
import time
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes


# Set up the serial connection to Arduino
arduino = serial.Serial(port='/dev/ttyACM0', baudrate=9600, timeout=1)
arduino.flush()

# Movement commands using serial communication with Arduino
def send_serial_command(command, value=0):
    """Send a command over serial to the Arduino and wait for the 'DONE' response."""
    if arduino.is_open:
        # Write the command to the serial based on whether it has a value or not
        if command in ['APPLY', 'EMPTY', 'STOP']:
            arduino.write(f"{command}\n".encode())
            print(f"Sent command: {command}")
        else:
            arduino.write(f"{command} {value}\n".encode())
            print(f"Sent command: {command} {value}")
        
        # Wait for the 'DONE' response from Arduino
        while True:
            if arduino.in_waiting > 0:  # Check if there's incoming data in the serial buffer
                response = arduino.readline().decode().strip()  # Read the incoming serial data
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

        # Execute the command received from the client
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
        # Log the request to verify it's received
        print("Automatic mode request received")

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
        print(f"Error in automatic mode: {e}")
        return jsonify({"error": str(e)}), 400


# Automatic mode handler
def run_automatic_mode(tile_width, rows, columns, gaps):
        
    total_tile_width = tile_width + gaps # 40.25
    
    max_col_distance = (columns - 1) * total_tile_width  # 80.5
    max_row_distance = (rows - 1) * total_tile_width # 120.75
    
    for col in range(columns - 1):
        send_serial_command("MOVE_FORWARD", max_col_distance) # 80.5

        if col < columns - 1:
            rotate()
            send_serial_command("MOVE_FORWARD", max_row_distance) # 120.75
            rotate()
            
        send_serial_command("STOP")

    def rotate():
        send_serial_command("MOVE_BACKWARD", total_tile_width / 1.2) # 33.54
        send_serial_command("ROTATE_RIGHT", 97) # 90 deg
        send_serial_command("MOVE_BACKWARD", total_tile_width / 2) # 20
    
    
    print("Automatic mode completed")

if __name__ == '__main__':
    # Serve the application on port 5000
    app.run(host='0.0.0.0', port=5000)
