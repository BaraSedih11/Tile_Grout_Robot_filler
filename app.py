from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import serial
import time

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

# Adjust the serial port to match your Arduino
arduino = serial.Serial('/dev/ttyACM0', 9600, timeout=1)
time.sleep(2)  # Allow time for the Arduino to reset

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/command', methods=['POST'])
def send_command():
    data = request.get_json()
    command = data.get('command')
    
    if command:
        # Send the command to the Arduino
        arduino.write(f"{command}\n".encode())
        
        # Read the Arduino response
        response = arduino.readline().decode('utf-8').strip()
        
        # Return the Arduino response
        return jsonify({'response': response})
    else:
        return jsonify({'error': 'No command received'}), 400


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
