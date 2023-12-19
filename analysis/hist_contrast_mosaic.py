import matplotlib.pyplot as plt
from PIL import Image
import numpy as np

def apply_mosaic(image, block_size):
    img_array = np.array(image)
    for i in range(0, img_array.shape[0], block_size):
        for j in range(0, img_array.shape[1], block_size):
            img_array[i:i+block_size, j:j+block_size] = np.mean(img_array[i:i+block_size, j:j+block_size], axis=(0, 1))
    return Image.fromarray(img_array.astype('uint8'))

def calculate_contrast(mosaic_image, block_size):
    img_array = np.array(mosaic_image)
    contrast_values = []

    for i in range(0, img_array.shape[0] - block_size + 1, block_size):
        for j in range(0, img_array.shape[1] - block_size + 1, block_size):
            block = img_array[i:i+block_size, j:j+block_size]
            neighbors = [
                img_array[max(i-dy, 0):min(i+block_size-dy, img_array.shape[0]), 
                          max(j-dx, 0):min(j+block_size-dx, img_array.shape[1])]
                for dy in range(-block_size, block_size+1, block_size)
                for dx in range(-block_size, block_size+1, block_size)
                if (dx != 0 or dy != 0) and (0 <= i-dy < img_array.shape[0]-block_size) and (0 <= j-dx < img_array.shape[1]-block_size)
            ]
            contrasts = [np.abs(block - neighbor[:block.shape[0], :block.shape[1]]).mean() for neighbor in neighbors if neighbor.size == block.size]
            contrast = np.mean(contrasts) if contrasts else 0
            contrast_values.append(contrast)

    return contrast_values


def create_contrast_histogram(image_path, block_size):
    image = Image.open(image_path)
    mosaic_image = apply_mosaic(image, block_size)
    contrast_values = calculate_contrast(mosaic_image, block_size)
    histogram, bins = np.histogram(contrast_values, bins=30, range=(0, 255))
    return histogram



def calculate_contrast_coefficients(histogram):
    # ヒストグラムの値から平均コントラストと標準偏差を計算
    mean_contrast = np.mean(histogram)
    std_contrast = np.std(histogram)

    # コントラスト変動係数を計算（平均コントラストで標準偏差を割る）
    contrast_variation_coefficient = std_contrast / mean_contrast if mean_contrast != 0 else 0

    # 二乗平均コントラストを計算（値を二乗し、その平均の平方根を取る）
    squared_mean_contrast = np.sqrt(np.mean(histogram**2))

    return contrast_variation_coefficient, squared_mean_contrast


# 使用例
import glob

image_path = glob.glob("../experiment_images/110_0/*")  # 画像のパス

for image_path in image_path:
    block_size = 32 # ブロックサイズ
    histogram = create_contrast_histogram(image_path, block_size)
    #histogramをmatplotlibで表示
    # plt.bar(range(len(histogram)), histogram)
    # plt.show()
    # print(histogram)

    # 統計量の計算
    contrast_variation_coefficient, squared_mean_contrast = calculate_contrast_coefficients(histogram)
    # print("コントラスト変動係数:", contrast_variation_coefficient)
    # print("二乗平均コントラスト:", squared_mean_contrast)


# def calcuate_contrast_features(image_path, block_size):
#     # ヒストグラムの計算
#     histogram = create_contrast_histogram(image_path, block_size)

#     # 統計量の計算
#     contrast_variation_coefficient, squared_mean_contrast = calculate_contrast_coefficients(histogram)

#     return contrast_variation_coefficient, squared_mean_contrast

