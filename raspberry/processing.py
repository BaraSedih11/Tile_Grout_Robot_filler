import cv2
import numpy as np

class Processing:
    def preprocess_image(self, image):
        # Convert to grayscale if the image is not already
        if len(image.shape) == 2:
            gray = image
        else:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        # Apply Gaussian blur to reduce noise
        blurred = cv2.GaussianBlur(gray, (3, 3), 0)

        # Use Canny edge detection to find edges
        edges = cv2.Canny(blurred, 50, 150, apertureSize=3)

        return edges

    def detect_gap(self, edges):
        # Detect lines using Hough Line Transform
        lines = cv2.HoughLinesP(edges, 1, np.pi/180, threshold=50, minLineLength=20, maxLineGap=5)

        if lines is None:
            return False

        # Look for a vertical black gap (around 2 cm wide)
        for line in lines:
            x1, y1, x2, y2 = line[0]
            # Check if the line is approximately vertical and its length matches the expected gap size
            if abs(x2 - x1) < 10 and abs(y2 - y1) > 10:  # Vertical line
                return True

        return False
