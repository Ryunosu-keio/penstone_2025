import cv2
import cv2
from PIL import Image
import numpy as np
import matplotlib.pyplot as plt
import glob
import os
import time

def apply_blur(filename, blur_size):
    # Load the image
    img = cv2.imread(filename)
    
    # Apply Gaussian blur
    img = cv2.GaussianBlur(img, (blur_size, blur_size), 0)
    
    cv2.imwrite("photos/3_blur.jpg", img)

apply_blur("photos/3.jpg", 5)  # Apply blur with kernel size of 5


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


# Increase hue by 0.1
adjust_hue("photos/3.jpg", 18)




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


adjust_contrast("photos/3_slide_30.jpg", 1.5)  # Increase contrast by 50%

# equalize_gauss
def equalize_hist_color_smoothed(filename):
    # Load the image
    img = cv2.imread(filename)
    
    # Convert the image to YUV color space
    img_yuv = cv2.cvtColor(img, cv2.COLOR_BGR2YUV)
    
    # Apply histogram equalization to the Y channel
    img_yuv[:,:,0] = cv2.equalizeHist(img_yuv[:,:,0])
    
    # Convert the image back to BGR color space
    img_eq = cv2.cvtColor(img_yuv, cv2.COLOR_YUV2BGR)
    
    # Apply Gaussian blur
    img_smoothed = cv2.GaussianBlur(img_eq, (5, 5), 0)
    
    cv2.imwrite("photos/3_equalized_color_smoothed.jpg", img_smoothed)

equalize_hist_color_smoothed("photos/3.jpg")  # Equalize histogram of the color image and apply Gaussian blur

def adjust_gamma(image, gamma=1.0):
    invGamma = 1.0 / gamma
    table = np.array([((i / 255.0) ** invGamma) * 255 for i in np.arange(0, 256)]).astype("uint8")
    return cv2.LUT(image, table)


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

slide_brightness("photos/3.jpg", 30)  # Slide brightness by 50


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

stretch_brightness("photos/3.jpg")  # Stretch brightness

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

stretch_brightness_clip("photos/3.jpg", 0.01, 0.99)  # Stretch brightness

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

stretch_rgb_clahe("photos/3.jpg")  # Stretch brightness in RGB using CLAHE

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

stretch_rgb("photos/3.jpg")  # Stretch brightness in RGB


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
