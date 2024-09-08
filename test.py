import cv2

# Try to open the camera using V4L2
camera = cv2.VideoCapture(0, cv2.CAP_V4L2)

if not camera.isOpened():
    print("Error: Could not open video stream from the camera.")
    exit()
