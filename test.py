import cv2

# Open video capture
cap = cv2.VideoCapture('/dev/video0')

while True:
    # Capture frame-by-frame
    ret, frame = cap.read()
    if not ret:
        break

    # Display the resulting frame
    cv2.imshow('Video', frame)

    # Press 'q' to exit
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# When everything done, release the capture
cap.release()
cv2.destroyAllWindows()
