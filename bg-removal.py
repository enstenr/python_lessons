import cv2
import numpy as np

# Load the image
image = cv2.imread("1000008455.jpg")

# Convert BGR to BGRA (adds alpha channel)
image_bgra = cv2.cvtColor(image, cv2.COLOR_BGR2BGRA)

# Define green color range (tweak if needed)
lower_green = np.array([35, 100, 100])    # Lower bound of green in BGR
upper_green = np.array([85, 255, 255])    # Upper bound of green in BGR

# Convert image to HSV for better color filtering
hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
mask = cv2.inRange(hsv, lower_green, upper_green)

# Set alpha = 0 (transparent) where green is detected
image_bgra[mask > 0, 3] = 0

# Save result
cv2.imwrite("output_transparent.png", image_bgra)

