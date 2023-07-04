from PIL import Image
import numpy as np
import cv2
import matplotlib.pyplot as plt

def stretch_brightness(filename):
    # Load the image
    img = Image.open(filename)
    img_np = np.array(img)

    # Convert the image to HSV
    hsv = cv2.cvtColor(img_np, cv2.COLOR_RGB2HSV)

    # Stretch the V channel
    v_min, v_max = np.min(hsv[:,:,2]), np.max(hsv[:,:,2])
    hsv[:,:,2] = ((hsv[:,:,2] - v_min) / (v_max - v_min)) * 255

    # Convert the image back to RGB
    img_np = cv2.cvtColor(hsv, cv2.COLOR_HSV2RGB)

    # Convert back to uint8
    img = Image.fromarray(img_np.astype('uint8'))

    img.save("photos/3_stretch.jpg")  # Save the modified image
    return img

def color_hist(filename):
    img = np.asarray(Image.open(filename).convert("RGB")).reshape(-1,3)
    plt.hist(img, color=["red", "green", "blue"], bins=128)
    plt.show()

stretch_brightness("photos/3.jpg")  # Stretch brightness

color_hist("photos/3_stretch.jpg")  # Show histogram of the modified image
