from flask import Flask, Response, render_template_string
import cv2

app = Flask(__name__)

def gen_frames():
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Error: Could not open video device.")
        return  # Exit if the camera cannot be accessed
    
    while True:
        success, frame = cap.read()
        if not success:
            print("Error: Failed to capture frame.")
            break
        else:
            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

@app.route('/')
def index():
    # Render a simple HTML page that displays the video feed
    return render_template_string('''
        <html>
            <head>
                <title>Video Stream</title>
            </head>
            <body>
                <h1>Live Video Stream</h1>
                <img src="{{ url_for('video_feed') }}" alt="Video Feed">
            </body>
        </html>
    ''')

@app.route('/video_feed')
def video_feed():
    return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
