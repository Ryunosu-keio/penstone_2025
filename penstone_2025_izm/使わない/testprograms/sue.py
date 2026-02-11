import cv2
import numpy as np

def adjust_vibrance(filename, vibrance_scale):
    # Load the image
    img = cv2.imread(filename)
    
    # Convert the image to HSV
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    
    # Adjust the saturation channel
    hsv[:, :, 1] = hsv[:, :, 1] * vibrance_scale
    hsv[:, :, 1] = np.clip(hsv[:, :, 1], 0, 255)
    
    # Convert the image back to BGR
    img = cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)
    
    cv2.imwrite("photos/3_vibrance_0.5.jpg", img)

adjust_vibrance("photos/3.jpg", 0.5) # Increase vibrance by 20%
