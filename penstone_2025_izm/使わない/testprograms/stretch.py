from PIL import Image
import numpy as np
import cv2
import matplotlib.pyplot as plt

def stretch_brightness_clip(filename, lower_freq=0.01, upper_freq=0.99):
    # Load the image
    img = Image.open(filename)
    img_np = np.array(img)

    # Convert the image to HSV
    hsv = cv2.cvtColor(img_np, cv2.COLOR_RGB2HSV)

    # Calculate the histogram and CDF of the V channel
    hist, bins = np.histogram(hsv[:,:,2].flatten(), bins=256, range=[0,256])
    cdf = hist.cumsum()

    # Normalize the CDF
    cdf = cdf / float(cdf[-1])

    # Find the histogram bins where the CDF is just below the lower/upper threshold
    v_min = np.searchsorted(cdf, lower_freq)
    v_max = np.searchsorted(cdf, upper_freq)

    # Stretch the V channel using the new min and max
    hsv[:,:,2] = np.clip((hsv[:,:,2] - v_min) / (v_max - v_min) * 255, 0, 255)

    # Convert the image back to RGB
    img_np = cv2.cvtColor(hsv, cv2.COLOR_HSV2RGB)

    # Convert back to uint8
    img = Image.fromarray(img_np.astype('uint8'))

    img.save("photos/3_stretch_clip.jpg")  # Save the modified image
    return img

def color_hist(filename):
    img = np.asarray(Image.open(filename).convert("RGB")).reshape(-1,3)
    plt.hist(img, color=["red", "green", "blue"], bins=128)
    plt.show()

stretch_brightness_clip("photos/3.jpg", 0.01, 0.99)  # Stretch brightness

color_hist("photos/3_stretch_clip.jpg")  # Show histogram of the modified image