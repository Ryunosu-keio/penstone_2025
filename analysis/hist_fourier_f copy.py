# # Load the necessary packages
# import numpy as np
# import matplotlib.pyplot as plt
# from scipy.fft import fft2, fftshift
# from scipy.optimize import curve_fit
# from PIL import Image
# import glob
# from sklearn.linear_model import LinearRegression



# def analyze_image_fft(image_array):
#     # Perform 2D Fourier Transform on the image
#     f_transform = fftshift(fft2(image_array))

#     # Calculate the Power Spectrum
#     power_spectrum = np.abs(f_transform)**2

#     # Create meshgrid of frequency domain
#     freq_x = np.fft.fftfreq(image_array.shape[1])
#     freq_y = np.fft.fftfreq(image_array.shape[0])
#     freq_x, freq_y = np.meshgrid(freq_x, freq_y)
#     radius = np.sqrt(freq_x**2 + freq_y**2).flatten()
    
#     # Get the indices to sort by radius
#     indices = np.argsort(radius)
#     radius = radius[indices]
#     sorted_power_spectrum = power_spectrum.flatten()[indices]

#     # Only take non-zero frequencies to avoid log(0) issues
#     non_zero_mask = radius > 0
#     radius = radius[non_zero_mask]
#     print(radius)
#     sorted_power_spectrum = sorted_power_spectrum[non_zero_mask]

#     # Convert to log scale for both axes
#     log_radius = np.log10(radius)
#     log_power_spectrum = np.log10(sorted_power_spectrum)
    
#     # Linear regression on the log-log scale data
#     model = LinearRegression()
#     model.fit(log_radius.reshape(-1, 1), log_power_spectrum.reshape(-1, 1))
#     slope = model.coef_[0][0]
#     r_squared = model.score(log_radius.reshape(-1, 1), log_power_spectrum.reshape(-1, 1))
    
#     # # Plotting the Power Spectrum and its linear fit
#     # plt.figure(figsize=(10, 6))
#     # plt.scatter(log_radius, log_power_spectrum, label="Power Spectrum", s=1)
#     # plt.plot(log_radius, model.intercept_[0] + slope * log_radius, label="Linear Fit", color='red')
#     # plt.xlabel("Log(Spatial Frequency)")
#     # plt.ylabel("Log(Power Spectrum)")
#     # plt.title("Log-Log Plot of Power Spectrum with Linear Fit")
#     # plt.legend()
#     # plt.show()
    
#     # Plotting the Power Spectrum and its linear fit with adjusted x-axis
#     plt.figure(figsize=(10, 6))
#     plt.scatter(10**log_radius, 10**log_power_spectrum, label="Power Spectrum", s=1)  # Adjust x-values
#     plt.plot(10**log_radius, 10**model.intercept_[0] + slope * log_radius, label="Linear Fit", color='red')  # Adjust x-values
#     plt.xscale('log')  # Set x-axis to logarithmic scale
#     plt.yscale('log')  # Set y-axis to logarithmic scale
#     plt.xlabel("Spatial Frequency (10^n)")
#     plt.ylabel("Power Spectrum (10^n)")
#     plt.title("Log-Log Plot of Power Spectrum with Linear Fit")
#     plt.legend()
#     plt.show()

#     return slope, r_squared

# # Load the image
# # image_path = "../experiment_images/101_1/1_3_brightness23.072_gamma1.092_sharpness0.325.jpg"
# # image_path = "../photos/2015-11-landscape-free-photo42.jpg"
# image_path = "../photos/wood-texture_00058.jpg"
# # image_path = "../photos/Lake-Kawaguchiko-Mount-Fuji-and-cherry-blossoms-typical-landscape-of-spring-in-Japan.jpg"
# image = Image.open(image_path).convert('L')
# image_array = np.asarray(image)
# # Resizing the image to a smaller resolution to reduce computational load
# # image_small = image_array[::4, ::4]

# # Apply the Fourier transform analysis on the resized image array and plot the graph
# slope, r_squared = analyze_image_fft(image_array)
# slope, r_squared

import numpy as np
import matplotlib.pyplot as plt
from scipy.fft import fft2, fftshift
from PIL import Image

def analyze_image_fft(image_array):
    # Perform 2D Fourier Transform on the image
    f_transform = fftshift(fft2(image_array))

    # Calculate the Power Spectrum
    power_spectrum = np.abs(f_transform)**2

    # Create meshgrid of frequency domain
    freq_x = np.fft.fftfreq(image_array.shape[1])
    freq_y = np.fft.fftfreq(image_array.shape[0])
    freq_x, freq_y = np.meshgrid(freq_x, freq_y)
    radius = np.sqrt(freq_x**2 + freq_y**2)

    # Flatten and sort the radius and power spectrum values
    radius_flat = radius.flatten()
    power_flat = power_spectrum.flatten()
    indices = np.argsort(radius_flat)  # Sort by radius
    radius_sorted = radius_flat[indices]
    power_sorted = power_flat[indices]

    # Bin the radius and average the power in each bin to get radial distribution
    radial_dist, radial_edges = np.histogram(radius_sorted, bins=200, weights=power_sorted)
    count, _ = np.histogram(radius_sorted, bins=200)  # Count number of values in each bin
    radial_dist /= count  # Average the power

    # Plotting the Radial Distribution
    plt.figure(figsize=(10, 6))
    radial_centers = (radial_edges[:-1] + radial_edges[1:]) / 2  # Compute the center of the bins
    plt.plot(radial_centers, radial_dist)
    plt.xscale('log')  # Set x-axis to logarithmic scale
    plt.yscale('log')  # Set y-axis to logarithmic scale
    plt.xlabel("Spatial Frequency (cycles per pixel)")
    plt.ylabel("Average Power")
    plt.title("Radial Distribution of Power Spectrum")
    plt.show()

# Load the image
image_path = "../experiment_images/101_1/1_3_brightness23.072_gamma1.092_sharpness0.325.jpg"
image = Image.open(image_path).convert('L')
image_array = np.asarray(image)

# Apply the Fourier transform analysis on the image array and plot the graph
analyze_image_fft(image_array)
