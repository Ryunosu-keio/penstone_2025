import numpy as np
import matplotlib.pyplot as plt
from PIL import Image
import os
import glob
import pandas as pd
from tqdm import tqdm





def make_list_fft(df):
    figs = df["figure"].tolist()
    image_paths = df["image_path"].tolist()

    # 加工画像の元画像のリスト
    fig_paths = []
    img_original_list = []
    for i in range(len(figs)):
        fig_paths.append("../pictures/transformed/roomDark_figureBright/"+str(figs[i])+".JPG")
        img_original_list.append(Image.open("../pictures/transformed/roomDark_figureBright/"+str(figs[i])+".JPG"))

    # 加工画像のリスト
    img_list = []
    for i in range(len(image_paths)):
        img_list.append(Image.open(image_paths[i]))
    
    return fig_paths, image_paths,img_original_list, img_list



def compute_fft(image):
    # Convert to grayscale
    gray_image = image.convert('L')
    # Convert to numpy array
    image_array = np.asarray(gray_image)
    # Compute the 2-dimensional FFT
    fft_array = np.fft.fft2(image_array)
    # Shift the zero frequency component to the center of the spectrum
    fft_shifted = np.fft.fftshift(fft_array)
    # Compute magnitude spectrum
    magnitude_spectrum = 20 * np.log(np.abs(fft_shifted))
    return magnitude_spectrum

# Function to compare the FFTs and find differences
def compare_ffts(fft1, fft2):
    # Compute the difference in FFTs
    fft_diff = np.abs(fft1 - fft2)
    # Find the average difference
    avg_diff = np.mean(fft_diff)
    # Find the maximum difference
    max_diff = np.max(fft_diff)
    return fft_diff, avg_diff, max_diff


# Function to quantify the differences in low and high frequency bands
def quantify_frequency_bands(fft_diff):
    # Dimensions of the FFT difference image
    h, w = fft_diff.shape
    # Find the center of the image
    center_x, center_y = w // 2, h // 2

    # Define radius for low frequency band (arbitrary choice of w/4 for demonstration)
    radius_low_freq = w // 4

    # Create a mask for low frequency band (center circle of the image)
    y, x = np.ogrid[:h, :w]
    low_freq_mask = (x - center_x)**2 + (y - center_y)**2 <= radius_low_freq**2

    # Apply mask to get low frequency differences
    low_freq_diff = fft_diff * low_freq_mask
    # Calculate the average difference in low frequency band
    avg_diff_low_freq = np.mean(low_freq_diff[low_freq_mask])

    # Mask for high frequency band is the complement of the low frequency mask
    high_freq_mask = ~low_freq_mask
    # Apply mask to get high frequency differences
    high_freq_diff = fft_diff * high_freq_mask
    # Calculate the average difference in high frequency band
    avg_diff_high_freq = np.mean(high_freq_diff[high_freq_mask])

    return avg_diff_low_freq, avg_diff_high_freq



avg_diff_list = []
max_diff_list = []
avg_diff_low_freq_list = []
avg_diff_high_freq_list = []

df = pd.read_excel("../data/final_recent_dark/final_recent_dark_add_entropy.xlsx")
fig_paths,image_paths,img_original_list, img_list = make_list_fft(df)

# Compute the FFT for both images
for i in tqdm(range(len(img_list))):
    img1 = img_original_list[i]
    img2 = img_list[i]

    fft1 = compute_fft(img1)
    fft2 = compute_fft(img2)

    # Get the FFT difference and stats
    fft_diff, avg_diff, max_diff = compare_ffts(fft1, fft2)

    avg_diff_list.append(avg_diff)
    max_diff_list.append(max_diff)


    # Plot the difference in FFTs
    # plt.figure(figsize=(6, 6))
    # plt.imshow(fft_diff, cmap='hot', interpolation='nearest')
    # plt.colorbar()
    # plt.title('Difference in FFT Magnitude Spectrum')
    # plt.axis('off')
    # plt.show()


    # Quantify the differences in low and high frequency bands
    avg_diff_low_freq, avg_diff_high_freq = quantify_frequency_bands(fft_diff)

    avg_diff_low_freq_list.append(avg_diff_low_freq)
    avg_diff_high_freq_list.append(avg_diff_high_freq)

    # print("fig_paths[i]",fig_paths[i])
    # print("image_paths[i]",image_paths[i])
    # print("avg_diff",avg_diff , "max_diff", max_diff)#################ここ平均と最大
    # print("avg_diff_low_freq",avg_diff_low_freq, "avg_diff_high_freq", avg_diff_high_freq)#################ここ低周波と高周波

    # 画像がもはや必要なくなったので、リソースを解放します
    img1.close()
    img2.close()


df["avg_diff"] = avg_diff_list
df["max_diff"] = max_diff_list
df["avg_diff_low_freq"] = avg_diff_low_freq_list
df["avg_diff_high_freq"] = avg_diff_high_freq_list
df.to_excel("../data/final_recent_dark/final_recent_dark_add_entropy_fft.xlsx")








# #####################################
# # Re-define the quantify_frequency_bands function to include the center points
# def quantify_frequency_bands(fft_diff, w, h):
#     # Find the center of the image
#     center_x, center_y = w // 2, h // 2

#     # Define radius for low frequency band (arbitrary choice of w/4 for demonstration)
#     radius_low_freq = w // 4

#     # Create a mask for low frequency band (center circle of the image)
#     y, x = np.ogrid[:h, :w]
#     low_freq_mask = (x - center_x)**2 + (y - center_y)**2 <= radius_low_freq**2

#     # Apply mask to get low frequency differences
#     low_freq_diff = fft_diff * low_freq_mask
#     # Calculate the average difference in low frequency band
#     avg_diff_low_freq = np.mean(low_freq_diff[low_freq_mask])

#     # Mask for high frequency band is the complement of the low frequency mask
#     high_freq_mask = ~low_freq_mask
#     # Apply mask to get high frequency differences
#     high_freq_diff = fft_diff * high_freq_mask
#     # Calculate the average difference in high frequency band
#     avg_diff_high_freq = np.mean(high_freq_diff[high_freq_mask])

#     return avg_diff_low_freq, avg_diff_high_freq

# # Apply sharpness adjustment to both images
# # sharpness_value = 2
# # img1_sharp = adjust_sharpness(img1, sharpness_value)
# # img2_sharp = adjust_sharpness(img2, sharpness_value)

# # Compute the FFT for the sharpened images
# # fft1_sharp = compute_fft(img1_sharp)
# # fft2_sharp = compute_fft(img2_sharp)

# fft1=img1
# fft2=img2
# # Dimensions of the FFT difference image
# h, w = fft_diff.shape

# # Recompute the average differences in low and high frequency bands with the sharpened images
# avg_diff_low_freq_sharp1, avg_diff_high_freq_sharp1 = quantify_frequency_bands(fft1, w, h)
# avg_diff_low_freq_sharp2, avg_diff_high_freq_sharp2 = quantify_frequency_bands(fft2, w, h)

# # Calculate the differences between the sharpened images
# diff_low_freq_sharp = avg_diff_low_freq_sharp2 - avg_diff_low_freq_sharp1
# diff_high_freq_sharp = avg_diff_high_freq_sharp2 - avg_diff_high_freq_sharp1

# diff_low_freq_sharp, diff_high_freq_sharp
