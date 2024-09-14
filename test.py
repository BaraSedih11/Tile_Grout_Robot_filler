from flask import Flask, Response
import subprocess
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes


def generate_video():
    # Use subprocess to call libcamera-vid and stream MJPEG
    cmd = [
        'libcamera-vid',
        '-t', '0',  # Unlimited duration
        '--width', '640',  # Width of the video
        '--height', '480',  # Height of the video
        '--framerate', '30',  # Frame rate
        '--codec', 'mjpeg',  # Use MJPEG codec
        '-o', '-'  # Output to stdout
    ]
    process = subprocess.Popen(cmd, stdout=subprocess.PIPE, bufsize=10**8)

    try:
        while True:
            # Read the MJPEG stream
            data = process.stdout.read(1024)
            if not data:
                break
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + data + b'\r\n')
    except GeneratorExit:
        process.terminate()
        process.wait()

@app.route('/video_feed')
def video_feed():
    return Response(generate_video(), mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
