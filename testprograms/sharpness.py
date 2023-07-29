import cv2
import numpy as np

def adjust_sharpness(img, sharpness_factor):
    # Gaussian blur
    blurred = cv2.GaussianBlur(img, (0, 0), sharpness_factor)
    
    # Add weighted original and blurred
    sharpened = cv2.addWeighted(img, 1.5, blurred, -0.5, 0)
    return sharpened

def apply_sharpness(filename, sharpness_factor):
    # Load the image
    img = cv2.imread(filename)
    
    # Adjust sharpness
    img = adjust_sharpness(img, sharpness_factor)
    
    cv2.imwrite("photos/3_sharpness.jpg", img)

apply_sharpness("photos/3.jpg", 21) # Adjust sharpness with factor of 5
