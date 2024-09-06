from flask import Flask, render_template, request, jsonify
import serial
import time
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Adjust the serial port to match your Arduino
arduino = serial.Serial('COM3', 9600, timeout=1)
time.sleep(2)  # Allow time for the Arduino to reset

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/command', methods=['POST'])
def send_command():
    data = request.get_json()
    command = data['command']
    
    # Send the command to the Arduino
    arduino.write(f"{command}\n".encode())
    
    # Read the Arduino response (optional)
    response = arduino.readline().decode('utf-8').strip()
    
    return jsonify({'response': response})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)