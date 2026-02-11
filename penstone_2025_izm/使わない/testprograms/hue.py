from PIL import Image
import numpy as np
import cv2
import matplotlib.pyplot as plt

def adjust_hue(filename, delta):
    # Load the image
    img = Image.open(filename)
    img_np = np.array(img)  # No need to convert to float and scale

    # Convert the image to HSV
    hsv = cv2.cvtColor(img_np, cv2.COLOR_RGB2HSV)

    # Adjust the hue
    hsv[:,:,0] = (hsv[:,:,0] + delta) % 180  # Hue is in range [0, 180]

    # Convert the image back to RGB
    img_np = cv2.cvtColor(hsv, cv2.COLOR_HSV2RGB)  # Output is uint8

    # No need to convert back to uint8 and scale
    img = Image.fromarray(img_np)

    img.save("photos/3_hue18.jpg")  # Save the modified image
    return img


def color_hist(filename):
    img = np.asarray(Image.open(filename).convert("RGB")).reshape(-1,3)
    plt.hist(img, color=["red", "green", "blue"], bins=128)
    # plt.show()
    plt.xlim(0, 255)
    plt.savefig('histogram/hue18_hist.png')

# Increase hue by 0.1
adjust_hue("photos/3.jpg", 18)

# Decrease hue by 0.1
# adjust_hue("original.jpg", -0.1)
