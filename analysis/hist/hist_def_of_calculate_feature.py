import cv2
import numpy as np
from scipy.stats import skew
from PIL import Image
from scipy import stats
import matplotlib.pyplot as plt
import glob
import os
from tqdm import tqdm



# # # Load the image

# path = '../experiment_images/0824_rb_fd_29/*.jpg'
# files = glob.glob(path)

# # from PIL import Image
# # import numpy as np

# # # 画像ファイルを読み込み
# # image = Image.open("path_to_your_image.jpg")

# # # 画像をグレースケールに変換
# # gray_image = image.convert("L")

# # # NumPy配列に変換
# # image_data = np.array(gray_image)

# # # ヒストグラムを計算
# # histogram, _ = np.histogram(image_data, bins=256, range=(0, 255))

# # # 頻度が0でない輝度のビンを見つける
# # non_zero_bins = np.where(histogram > 0)[0]

# # # 最小値と最大値を取得
# # min_brightness = non_zero_bins[0]
# # max_brightness = non_zero_bins[-1]

# # print("頻度が0でない最小の輝度値:", min_brightness)
# # print("頻度が0でない最大の輝度値:", max_brightness)




# # pilでグレースケール画像のskewnessを計算
# # image = Image.open('../pictures/transformed/roomBright_figureDark/0.JPG')
# # image_gray = image.convert('L')
# # image_gray = np.asarray(image_gray)
# # skewness_gray = skew(image_gray.flatten())


# def calculate_michaelson_contrast(image_path):
#     # 画像ファイルを読み込み
#     image = Image.open(image_path)

#     # 画像をグレースケールに変換
#     gray_image = image.convert("L")

#     # NumPy配列に変換
#     image_data = np.array(gray_image)

#     # ヒストグラムを計算
#     histogram, _ = np.histogram(image_data, bins=256, range=(0, 255))

#     # 頻度が0でない輝度のビンを見つける
#     non_zero_bins = np.where(histogram > 0)[0]

#     # 最小値と最大値を取得
#     min_brightness = non_zero_bins[0]
#     max_brightness = non_zero_bins[-1]

#     michaelson_contrast = (max_brightness-min_brightness)/(max_brightness+min_brightness)

#     print("non_zero_bins", non_zero_bins)
#     print("len(non_zero_bins)", len(non_zero_bins))
#     print("min_brightness, max_brightness", min_brightness, max_brightness)
#     print("michaelson_contrast", michaelson_contrast)

#     # print("頻度が0でない最小の輝度値:", min_brightness)
#     # print("頻度が0でない最大の輝度値:", max_brightness)

#     return michaelson_contrast

# for path in files:
#     calculate_michaelson_contrast(path)


#画像を読み込んで中心を変えずに1024pixelにリサイズする
#

def resize_to_power_of_two(image_path):
    # 画像を読み込む
    img = Image.open(image_path)
    #画像を表示
    # img.show()
    width, height = img.size

    # 2の累乗に最も近いサイズを求める
    # new_size = 2**np.floor(np.log2(min(width, height))).astype(int)
    new_size = 600
    left = (width - new_size) // 2
    top = (height - new_size) // 2
    right = (width + new_size) // 2
    bottom = (height + new_size) // 2

    # 画像を中央から切り抜く
    img_cropped = img.crop((left, top, right, bottom))
    #　画像のdpiを取得
    # dpi = int(img.info['dpi'][0])
    
    img_cropped.save("../photos/2Npic.jpg")
    # print(dpi, new_size)
    return img_cropped

# pics = glob.glob("../pictures/transformed/roomDark_figureBright/*.JPG")
# for i,pic in enumerate(pics):
#     img_cropped = resize_to_power_of_two(pic)
#     img_cropped_gray = img_cropped.convert('L')
#     img_cropped_gray = np.asarray(img_cropped_gray)
#     print(img_cropped_gray)
#     print(img_cropped_gray.shape)
    # print(img_cropped_gray.mean())

    # #画像を保存
    # os.makedirs("../photos/pic_square_dark", exist_ok=True)
    # img_cropped.save(f"../photos/pic_square_dark/{i}.jpg")



# 画像データの周辺画素との輝度差の平均値を計算する関数

# def delta_hist_by_pic(img):
#     # #画像をグレースケールに変換
#     img = img.convert('L')
#     size = img.size

#     # 画像データをNumPy配列に変換
#     img_array = np.array(img)
#     H, W = img_array.shape
#     diff_img = np.zeros((H, W), dtype=np.float64)

#     # 画像の端は処理しないためループは1から開始し、H-1, W-1で終了
#     for y in range(1, H-1):
#         for x in range(1, W-1):
#             # 中心画素と8近傍との輝度差の絶対値を計算し、平均をとる
#             diff = 0
#             for j in range(-1, 2):
#                 for i in range(-1, 2):
#                     if i == 0 and j == 0:
#                         continue  # 中心画素自身との差は計算しない
#                     diff += abs(int(img_array[y, x]) - int(img_array[y + j, x + i]))
#             diff_img[y, x] = diff / 8.0
    
#     # エッジを除いた画像の中心部分だけを返す
#     return diff_img[1:H-1, 1:W-1]
    

# def delta_hist(image_path):
#     img = Image.open(image_path)
#     delta = delta_hist_by_pic(img)
#     return delta

# # ガウシアンフィルタを適用する関数
# def gaussian_filtered_hist(image_path):
#     # 画像をグレースケールで読み込む
#     img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    
#     # ガウシアンフィルタを適用 (5x5のカーネルサイズを使用)
#     gaussian_filtered_array = cv2.GaussianBlur(img, (5, 5), 0)
#     gaussian_filtered_img = Image.fromarray(gaussian_filtered_array)

#     gaussian_hist = delta_hist_by_pic(gaussian_filtered_img)

#     return gaussian_hist



# # 画像を読み込む
# def sharpness_factor(image_path):
#     img_size = Image.open(image_path).size
#     pixel = img_size[0] * img_size[1]
#     # 輝度差の平均値を計算
#     delta = delta_hist(image_path)
#     gaussian = gaussian_filtered_hist(image_path)

#     # ヒストグラムを計算 (0-255の範囲で256ビン)
#     histogram, bins = np.histogram(delta.flatten(), bins=256, range=(0, 255))
#     gaussian_histogram, bins = np.histogram(gaussian.flatten(), bins=256, range=(0, 255))

#     #binごとにdelta-gaussianの絶対値を計算
#     diff_histogram = abs(histogram - gaussian_histogram)

#     # diff_histogramの和を全画素数で割る
#     # diff_histogram = diff_histogram / delta.size

#     # diff_histogramの要素の和
#     sum_diff_histogram = sum(diff_histogram)
#     sharpness_factor = sum_diff_histogram / pixel

#     print("diff_histogram", diff_histogram)
#     print("sum_diff_histogram", sum_diff_histogram)
#     print("pixel", pixel)
#     print(" sharpness_factor",  sharpness_factor)
#     return sharpness_factor

# image_path= "../photos/2Npic.jpg"
# sharpness_factor(image_path)



from PIL import Image
import cv2
import numpy as np

def delta_hist_by_pic(img_array):
    
    H, W = img_array.shape
    diff_img = np.zeros((H, W), dtype=np.float64)

    # 画像の端は処理しないためループは1から開始し、H-1, W-1で終了
    # for y in tqdm(range(1, H-1)):
    for y in range(1, H-1):
        for x in range(1, W-1):
            # 中心画素と8近傍との輝度差の絶対値を計算し、平均をとる
            diff = 0
            for j in range(-1, 2):
                for i in range(-1, 2):
                    if i == 0 and j == 0:
                        continue  # 中心画素自身との差は計算しない
                    diff += abs(int(img_array[y, x]) - int(img_array[y + j, x + i]))
            diff_img[y, x] = diff / 8.0
    
    # エッジを除いた画像の中心部分だけを返す
    return diff_img[1:H-1, 1:W-1]
    

def calculate_sharpness_factor(image_path):
    # 画像を一度だけ読み込む
    img_0 = Image.open(image_path)

    #画像を表示
    # img.show()
    width, height = img_0.size

    # 2の累乗に最も近いサイズを求める
    # new_size = 2**np.floor(np.log2(min(width, height))).astype(int)
    new_size = 600
    left = (width - new_size) // 2
    top = (height - new_size) // 2
    right = (width + new_size) // 2
    bottom = (height + new_size) // 2

    # 画像を中央から切り抜く
    img_0 = img_0.crop((left, top, right, bottom))
    # img_0.show()

    img_gray = img_0.convert('L')
    #numpy配列に変換
    img = np.array(img_gray)
    img_size = img_0.size
    pixel = img_size[0] * img_size[1]

    # 輝度差の平均値を計算
    delta = delta_hist_by_pic(img)

    # ガウシアンフィルタを適用
    img_gaussian = cv2.GaussianBlur(np.array(img), (5, 5), 0)

    gaussian = delta_hist_by_pic(img_gaussian)

    # ヒストグラムの計算と差の計算
    # histogram = np.histogram(delta.flatten(), bins=256, range=(0, 255))[0]
    # gaussian_histogram = np.histogram(gaussian.flatten(), bins=256, range=(0, 255))[0]

    #deltaの累積ヒストグラムを計算

    cumulative = np.cumsum(delta.flatten())
    histogram = np.histogram(cumulative, bins=256, range=(0, 255))[0]
    #gaussianの累積ヒストグラムを計算
    cumulative_gaussian = np.cumsum(gaussian.flatten())
    gaussian_histogram = np.histogram

    diff_histogram = abs(histogram - gaussian_histogram)

    # シャープネスファクターの計算
    sum_diff_histogram = sum(diff_histogram)
    sharpness_factor = sum_diff_histogram / pixel

    # print("diff_histogram", diff_histogram)
    # print("sum_diff_histogram", sum_diff_histogram)
    # print("pixel", pixel)
    # print(" sharpness_factor",  sharpness_factor)


    return sharpness_factor





import cv2
import numpy as np
import matplotlib.pyplot as plt
import glob

# 画像を読み込み、グレースケールに変換
# path = "../pictures/transformed/roomBright_figureDark/*.JPG"
# path = "../pictures/transformed/roomDark_figureBright/*.JPG"
# path = "../experiment_images/101_0/*_1_*.jpg"
import cv2
import numpy as np
import matplotlib.pyplot as plt
import glob  # globモジュールをインポート
def calculate_edge_sobel(path):
    image = cv2.imread(path, cv2.IMREAD_GRAYSCALE)

    # メディアンフィルタを適用
    # image = cv2.medianBlur(image, 3)
    # ソーベルフィルタを適用
    sobelx = cv2.Sobel(image, cv2.CV_64F, 1, 0, ksize=3)
    sobely = cv2.Sobel(image, cv2.CV_64F, 0, 1, ksize=3)

    # エッジ強度を計算
    edge_magnitude = np.sqrt(sobelx**2 + sobely**2)

    # エッジ強度の平均値を計算
    average_edge_strength = np.mean(edge_magnitude)
    # print("Average edge strength: ", average_edge_strength)

    # オリジナル画像とエッジ画像、およびヒストグラムを表示
    # plt.figure(figsize=(15, 10))
    # plt.subplot(2, 2, 1)
    # plt.imshow(image, cmap='gray')
    # plt.title('Original Image')
    # plt.axis("off")

    # plt.subplot(2, 2, 2)
    # plt.hist(image.ravel(), bins=256, range=[0,256])
    # plt.title('Histogram for Original Image')

    # plt.subplot(2, 2, 3)
    # plt.imshow(edge_magnitude, cmap='gray')
    # plt.title('Edge Magnitude')
    # plt.axis("off")

    # plt.subplot(2, 2, 4)
    # plt.hist(edge_magnitude.ravel(), bins=256, range=[0,256])
    # plt.title('Histogram for Edge Magnitude')

    # plt.show()

    return average_edge_strength




def calculate_mse_psnr(image_path):
    #image_pathからアルファベット部分を取り出す
    image_fig = image_path.split("/")[-1].split(".")[1]
    print(image_fig)
    image_path_original = f"../pictures/transformed/roomDark_figureBright/{image_fig}.JPG"
    # 画像を読み込む
    img1 = Image.open(image_path)
    img2 = Image.open(image_path_original)

    # 画像を同じサイズにリサイズ
    if img1.size != img2.size:
        img2 = img2.resize(img1.size)
    
    # 画像をNumPy配列に変換
    arr1 = np.array(img1)
    arr2 = np.array(img2)
    
    #　元画像の分散を計算
    var1 = np.var(arr1)


    # 平均二乗誤差を計算
    mse = np.mean((arr1 - arr2) ** 2)

    #snrを計算
    snr =10*np.log10(var1/mse)

    psnr = 10*np.log10(255**2/mse)

    
    return snr, psnr



# def calculate_ssim(image1, image2):
#     # 画像を読み込む
#     img1 = io.imread(image1, as_gray=True)
#     img2 = io.imread(image2, as_gray=True)

#     # SSIMを計算
#     score, diff = ssim(img1, img2, full=True)
#     print(f"SSIM: {score}")

#     # 差分画像を表示
#     plt.imshow(diff, cmap='gray')
#     plt.title('Difference Image')
#     plt.show()


# MSEを計算
# # mse, psnr = calculate_mse_psnr(image1_path, image2_path)
# print(f"平均二乗誤差（MSE）: {mse}")
# print(f"ピーク信号対雑音比（PSNR）: {psnr}")



# if __name__ == "__main__":
#     sf_list = []
#     image_paths = "../experiment_images/101_0/*"
#     x = ["1","2","8","I","T","P","0"]
#     for x in x:
#         paths = glob.glob(image_paths+"*_"+x+"_*.jpg")
#         for path in paths[:5]:
#             print(x)

#             sf = calculate_edge_sobel(path)
#             sf_list.append(sf)









# # ヒストグラムを計算 (0-255の範囲で256ビン)
# histogram, bins = np.histogram(diff_image_data.flatten(), bins=256, range=(0, 255))



# # ヒストグラムをプロット
# plt.figure(figsize=(10, 5))
# plt.bar(bins[:-1], histogram, width=bins[1]-bins[0], color='black')
# plt.title('Brightness Difference Histogram')
# plt.xlabel('Brightness Difference')
# plt.ylabel('Frequency')
# plt.xlim(0, 255)  # x軸の表示範囲を0-255に限定
# plt.grid(axis='y')
# plt.show()



def calculate_contrast_luminance(image_path):
    img = Image.open(image_path)
    #lab変換
    img_lab = img.convert('LAB')
    img_lab = np.asarray(img_lab)
    #L成分のみ取り出し
    img_L = img_lab[:,:,0]
    #平均輝度
    L_mean = img_L.mean()
    #最大輝度と最小輝度
    L_max = img_L.max()
    L_min = img_L.min()
    #コントラスト
    contrast_luminance = (L_max - L_min) / L_mean
    #元画像とL成分の画像とそれらのヒストグラムを表示
    plt.figure(figsize=(15, 5))
    plt.subplot(1, 4, 1)
    plt.imshow(img)
    plt.title('Original Image')
    plt.axis('off')
    plt.subplot(1, 4, 2)
    plt.imshow(img_L, cmap='gray')
    plt.title('L Component')
    plt.axis('off')
    plt.subplot(1, 4, 4)
    plt.hist(img_L.flatten(), bins=256, range=(0, 255), color='black')
    plt.title('Histogram(Luminance)')
    plt.xlabel('Brightness')
    plt.ylabel('Frequency')
    # 元画像のヒストグラム
    plt.subplot(1, 4, 3)
    plt.hist(img_L.flatten(), bins=256, range=(0, 255), color='black')
    plt.title('Histogram(RGB)')
    plt.grid()
    plt.show()

    return contrast_luminance

def calculate_skewness_of_luminance(image_path):
    img = Image.open(image_path)
    #lab変換
    img_lab = img.convert('LAB')
    img_lab = np.asarray(img_lab)
    #L成分のみ取り出し
    img_L = img_lab[:,:,0]
    #歪度
    L_skewness = skew(img_L.flatten())
    return L_skewness

path = glob.glob("../experiment_images/101_0/*.jpg")
x = calculate_skewness_of_luminance(path[0])
f