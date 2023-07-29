import cv2
import numpy as np

def equalize_hist_color(filename):
    # Load the image
    img = cv2.imread(filename)
    
    # Convert the image to YUV color space
    img_yuv = cv2.cvtColor(img, cv2.COLOR_BGR2YUV)
    
    # Apply histogram equalization to the Y channel
    img_yuv[:,:,0] = cv2.equalizeHist(img_yuv[:,:,0])
    
    # Convert the image back to BGR color space
    img_eq = cv2.cvtColor(img_yuv, cv2.COLOR_YUV2BGR)
    
    cv2.imwrite("photos/3_equalized_color.jpg", img_eq)

equalize_hist_color("photos/3.jpg")  # Equalize histogram of the color image
