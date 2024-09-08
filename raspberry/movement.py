import serial
import time

class Movement:
    def __init__(self, serial_port='/dev/ttyACM0', baud_rate=9600):
        self.arduino = serial.Serial(serial_port, baud_rate, timeout=1)
        self.arduino.flush()

    def send_command(self, command):
        print(f"Sending command: {command}")
        self.arduino.write(f"{command}\n".encode('utf-8'))
        self.arduino.flush()

        # Wait for the Arduino to send the "DONE" response
        response = ""
        # while True:
        response = self.arduino.readline().decode('utf-8')
        
        self.arduino.flush()
        if response == "DONE":  # Only print non-empty responses
            print(f"Arduino response: {response}")
          #      break
        

    def move_forward(self, distance_cm):
        self.send_command(f'MOVE_FORWARD {distance_cm}')

    def move_backward(self, distance_cm):
        self.send_command(f'MOVE_BACKWARD {distance_cm}')

    def rotate_right(self, angle_deg):
        self.send_command(f'ROTATE_RIGHT {angle_deg}')

    def rotate_left(self, angle_deg):
        self.send_command(f'ROTATE_LEFT {angle_deg}')

    def stop(self):
        self.send_command('STOP')
