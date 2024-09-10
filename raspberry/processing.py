import cv2
from flask import Flask, request, jsonify, Response
import numpy as np

app = Flask(__name__)

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

@app.route('/check-gap', methods=['GET'])
def check_gap():
    frame = capture_frame()
    processing = Processing()
    edges = processing.preprocess_image(frame)
    gap_detected = processing.detect_gap(edges)
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

@app.route('/command', methods=['POST'])
def command():
    data = request.json
    command = data.get('command')
    # Process command here (e.g., send to Arduino)
    # For example, you can send the command to Arduino using serial communication
    # Return a response
    return jsonify(response="DONE")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5050)
