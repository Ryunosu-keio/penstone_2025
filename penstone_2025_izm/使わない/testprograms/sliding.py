from PIL import Image
import matplotlib.pyplot as plt
import numpy as np
import cv2

def slide_brightness(filename, shift):
    # Load the image
    img = Image.open(filename)
    img_np = np.array(img).astype('float32') / 255.0  # Convert to float32 and scale to 0-1

    # Convert the image to HSV
    hsv = cv2.cvtColor(img_np, cv2.COLOR_RGB2HSV)

    # Add the shift to the V channel (V channel is also scaled to 0-1)
    hsv[:,:,2] = hsv[:,:,2] + shift / 255.0

    # Clip the V channel
    hsv[:,:,2] = np.clip(hsv[:,:,2], 0, 1)

    # Convert the image back to RGB
    img_np = cv2.cvtColor(hsv, cv2.COLOR_HSV2RGB)  # Output is also 0-1 float32

    # Convert back to uint8 and scale to 0-255
    img = Image.fromarray(np.round(img_np * 255).astype('uint8'))

    img.save("photos/3_slide_30.jpg")  # Save the modified image
    return img

def color_hist(filename):
    img = np.asarray(Image.open(filename).convert("RGB")).reshape(-1,3)
    plt.hist(img, color=["red", "green", "blue"], bins=128)
    # plt.show()
    plt.xlim(0, 255)
    plt.savefig('histogram/slide_30_hist.png')

slide_brightness("photos/3.jpg", 30)  # Slide brightness by 50
color_hist("photos/3_slide_30.jpg")  # Show histogram of the modified image
