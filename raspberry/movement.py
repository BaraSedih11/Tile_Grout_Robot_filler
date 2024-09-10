import serial
import time

class Movement:
    def __init__(self, serial_port='/dev/ttyACM0', baud_rate=115200):
        self.arduino = serial.Serial(serial_port, baud_rate, timeout=1)
        self.arduino.flush()

    def send_command(self, command):
        print(f"Sending command: {command}")
        self.arduino.flushInput()  # Flush input buffer
        self.arduino.write(f"{command}\n".encode('utf-8'))
        self.arduino.flush()
        time.sleep(0.1)  # Add a small delay
        print("Command Sent")
        # Wait for the Arduino to send the "DONE" response
        response = self.arduino.readline().decode('utf-8').strip()
        if response:
            print(f"Arduino response: {response}")

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