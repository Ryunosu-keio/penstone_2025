from PIL import Image
import matplotlib.pyplot as plt
import numpy as np
import cv2

def stretch_rgb_clahe(filename):
    # Load the image
    img = Image.open(filename)
    img_np = np.array(img).astype('float32') / 255.0  # Convert to float32 and scale to 0-1

    # Initialize CLAHE
    clahe = cv2.createCLAHE(clipLimit=2, tileGridSize=(8,8))

    # Perform histogram equalization on each channel
    for i in range(3):
        img_np[:,:,i] = clahe.apply((img_np[:,:,i] * 255).astype('uint8')) / 255.0

    # Convert back to uint8 and scale to 0-255
    img = Image.fromarray(np.round(img_np * 255).astype('uint8'))

    img.save("photos/3_stretch_rgb_clahe.jpg")  # Save the modified image
    return img

def color_hist(filename):
    img = np.asarray(Image.open(filename).convert("RGB")).reshape(-1,3)
    plt.hist(img, color=["red", "green", "blue"], bins=128)
    # plt.show()
    plt.xlim(0, 255)
    plt.savefig("histogram/3_stretch_rgb_clahe_hist.jpg")

stretch_rgb_clahe("photos/3.jpg")  # Stretch brightness in RGB using CLAHE
color_hist("photos/3_stretch_rgb_clahe.jpg")  # Show histogram of the modified image
