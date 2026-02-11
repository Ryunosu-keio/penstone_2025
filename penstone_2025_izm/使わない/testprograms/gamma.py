import cv2
import numpy as np
import matplotlib.pyplot as plt
from PIL import Image

def adjust_gamma(image, gamma=1.0):
    invGamma = 1.0 / gamma
    table = np.array([((i / 255.0) ** invGamma) * 255 for i in np.arange(0, 256)]).astype("uint8")
    return cv2.LUT(image, table)

def color_hist(filename):
    img = np.asarray(Image.open(filename).convert("RGB")).reshape(-1,3)
    plt.hist(img, color=["red", "green", "blue"], bins=128)
    # plt.show()
    plt.xlim(0, 255)
    plt.savefig('histogram/3_gamma0.5_hist.png')

# Load image
image = cv2.imread('photos/3.jpg')

# Apply gamma correction and save output
gamma_corrected = adjust_gamma(image, gamma=0.5)
cv2.imwrite('photos/3_gamma0.5.jpg', gamma_corrected)

color_hist("photos/3_gamma0.5.jpg")  # Show histogram of the modified image
