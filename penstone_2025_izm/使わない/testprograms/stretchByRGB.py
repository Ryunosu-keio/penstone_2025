from PIL import Image
import matplotlib.pyplot as plt
import numpy as np
import cv2

def stretch_rgb(filename):
    # Load the image
    img = Image.open(filename)
    img_np = np.array(img).astype('float32') / 255.0  # Convert to float32 and scale to 0-1

    # Perform histogram equalization on each channel
    for i in range(3):
        img_np[:,:,i] = cv2.equalizeHist((img_np[:,:,i] * 255).astype('uint8')) / 255.0

    # Convert back to uint8 and scale to 0-255
    img = Image.fromarray(np.round(img_np * 255).astype('uint8'))

    img.save("photos/3_stretch_rgb.jpg")  # Save the modified image
    return img

def color_hist(filename):
    img = np.asarray(Image.open(filename).convert("RGB")).reshape(-1,3)
    plt.hist(img, color=["red", "green", "blue"], bins=128)
    plt.show()

stretch_rgb("photos/3.jpg")  # Stretch brightness in RGB
color_hist("photos/3_stretch_rgb.jpg")  # Show histogram of the modified image
