import cv2
from PIL import Image
import numpy as np
import matplotlib.pyplot as plt

def adjust_contrast(filename, scale):
    # Load the image
    img = Image.open(filename)
    img_np = np.array(img)

    # Convert the image to HSV
    hsv = cv2.cvtColor(img_np, cv2.COLOR_RGB2HSV)

    # Adjust contrast in the V channel
    hsv[:,:,2] = cv2.convertScaleAbs(hsv[:,:,2], alpha=scale)

    # Convert the image back to RGB
    img_np = cv2.cvtColor(hsv, cv2.COLOR_HSV2RGB)

    # Convert back to uint8
    img = Image.fromarray(img_np.astype('uint8'))

    img.save("photos/3_slide30_contrast_1.5.jpg")  # Save the modified image
    return img

def color_hist(filename):
    img = np.asarray(Image.open(filename).convert("RGB")).reshape(-1,3)
    plt.hist(img, color=["red", "green", "blue"], bins=128)
    # plt.show()
    plt.xlim(0, 255)
    plt.savefig('histogram/slide30_contrast_hist_1.5.png')

adjust_contrast("photos/3_slide_30.jpg", 1.5)  # Increase contrast by 50%

color_hist("photos/3_slide30_contrast_1.5.jpg")  # Show histogram of the modified image