import pandas as pd
import cv2
import numpy as np
import matplotlib.pyplot as plt
import glob
import os
from tqdm import tqdm
import PIL.Image as Image
# stats.kurtosis()とstats.skew()をインポート
from scipy import stats
# colors.rgb_to_hsv()をインポート
import matplotlib.colors as colors
# hist_contrast_mosaic.pyから定義した関数をインポート
# from hist_contrast_mosaic import apply_mosaic, calculate_contrast, calculate_contrast_coefficients, create_contrast_histogram
# hist_skewnessから定義した関数をインポート
from hist_def_of_calculate_feature import calculate_sharpness_factor, calculate_contrast_luminance, calculate_skewness_of_luminance, calculate_edge_sobel
# from hist_noise import calculate_mse_psnr



def calculate_mse_psnr(image_path):
    #image_pathからアルファベット部分を取り出す
    image_fig = image_path.split("\\")[-1].split("_")[1]
    # print(image_path)
    # print(image_fig)
    # image_path_original = f"../pictures/transformed/roomDark_figureBright/{image_fig}.JPG"
    image_path_original = f"../pictures/transformed/roomBright_figureDark/{image_fig}.JPG"
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

    
    return mse, snr, psnr


def maskedByFigure(figure):
    image_path = '../pictures/transformed/roomDark_figureBright/' + str(figure) + '.JPG'
    image_figure = cv2.imread(image_path)
    # 画像をグレースケールに変換
    gray_image = cv2.cvtColor(image_figure, cv2.COLOR_BGR2GRAY)

    # 閾値を上げて再度しきい値処理を行う
    _, thresh_image = cv2.threshold(gray_image, 100, 255, cv2.THRESH_BINARY)

    # # マスキング処理を行う
    # high_masked_image = cv2.bitwise_and(
    #     gray_image, gray_image, mask=thresh_image)

    # # マスキング後の画像を表示する
    # plt.imshow(high_masked_image, cmap='gray')
    # plt.title('High Threshold Masked Image')
    # plt.axis('off')  # 軸をオフに
    # plt.show()
    return thresh_image


def show_image(image):
    plt.imshow(image, cmap='gray')
    plt.axis('off')  # 軸をオフに
    plt.show()


def calculate_contrast(threshold_image, gray_image):
    # 数字の部分と数字以外の部分の平均輝度を計算
    digit_brightness = np.mean(gray_image[threshold_image == 255])
    non_digit_brightness = np.mean(gray_image[threshold_image == 0])

    # 平均輝度の比を求める
    brightness_ratio = digit_brightness / non_digit_brightness

    digit_brightness, non_digit_brightness, brightness_ratio
    return digit_brightness, non_digit_brightness, brightness_ratio


# 画像を読み込んで、RGBヒストグラムとグレースケールのヒストグラムそれぞれに対してヒストグラムの尖度を計算する
def calculate_kurtosis(image_path):
    # 画像を読み込む
    img = Image.open(image_path)
    rgb_data = np.array(img)
    gray_data = np.array(img.convert("L"))

    # RGBそれぞれに対してヒストグラムを計算
    r_hist = np.histogram(rgb_data[:, :, 0], bins=256, range=(0, 255))[0]
    g_hist = np.histogram(rgb_data[:, :, 1], bins=256, range=(0, 255))[0]
    b_hist = np.histogram(rgb_data[:, :, 2], bins=256, range=(0, 255))[0]

    # グレースケールのヒストグラムを計算
    gray_hist = np.histogram(gray_data, bins=256, range=(0, 255))[0]

    # ヒストグラムの尖度を計算
    r_kurtosis = stats.kurtosis(r_hist)
    g_kurtosis = stats.kurtosis(g_hist)
    b_kurtosis = stats.kurtosis(b_hist)
    gray_kurtosis = stats.kurtosis(gray_hist)
    return r_kurtosis, g_kurtosis, b_kurtosis, gray_kurtosis

# 画像を読み込んで、RGBヒストグラムとグレースケールのヒストグラムそれぞれに対してヒストグラムの歪度を計算する
# def calculate_skewness(image_path):
    # 画像を読み込む
    img = Image.open(image_path)
    rgb_data = np.array(img)
    gray_data = np.array(img.convert("L"))

    # RGBそれぞれに対してヒストグラムを計算
    r_hist = np.histogram(rgb_data[:, :, 0], bins=256, range=(0, 255))[0]
    g_hist = np.histogram(rgb_data[:, :, 1], bins=256, range=(0, 255))[0]
    b_hist = np.histogram(rgb_data[:, :, 2], bins=256, range=(0, 255))[0]

    # グレースケールのヒストグラムを計算
    gray_hist = np.histogram(gray_data, bins=256, range=(0, 255))[0]

    # ヒストグラムの歪度を計算
    r_skewness = stats.skew(r_hist)
    g_skewness = stats.skew(g_hist)
    b_skewness = stats.skew(b_hist)
    gray_skewness = stats.skew(gray_hist)
    return r_skewness, g_skewness, b_skewness, gray_skewness


def calculate_skewness2(image_path):
    image = Image.open(image_path)
    image_gray = image.convert('L')
    image_gray = np.asarray(image_gray)
    skewness_gray = stats.skew(image_gray.flatten())
    # print("skewness_gray: ", skewness_gray)

    return skewness_gray


def calculate_michaelson_contrast(image_path):
    # 画像ファイルを読み込み
    image = Image.open(image_path)

    # 画像をグレースケールに変換
    gray_image = image.convert("L")

    # NumPy配列に変換
    image_data = np.array(gray_image)

    # ヒストグラムを計算
    histogram, _ = np.histogram(image_data, bins=256, range=(0, 255))

    # 頻度が0でない輝度のビンを見つける
    non_zero_bins = np.where(histogram > 0)[0]

    # 最小値と最大値を取得
    min_brightness = non_zero_bins[0]
    max_brightness = non_zero_bins[-1]

    michaelson_contrast = (max_brightness-min_brightness)/(max_brightness+min_brightness)

    # print("non_zero_bins", non_zero_bins)
    # print("len(non_zero_bins)", len(non_zero_bins))
    # print("min_brightness, max_brightness", min_brightness, max_brightness)
    # print("michaelson_contrast", michaelson_contrast)

    # print("頻度が0でない最小の輝度値:", min_brightness)
    # print("頻度が0でない最大の輝度値:", max_brightness)

    #読み込んだ画像を閉じる
    image.close()

    return michaelson_contrast

# ヒストグラムに対して大津の閾値を求める
def calculate_otsu_threshold(image_path):
    # 画像を読み込んでグレースケールに変換
    img = Image.open(image_path).convert("L")
    hist = np.histogram(np.array(img), bins=256, range=(0, 256))[0]

    # 総ピクセル数
    total = hist.sum()

    # クラス間分散を最大にする閾値を見つける
    sumB = 0
    wB = 0
    maximum = 0.0
    sum1 = np.cumsum(hist)
    for i in range(256):
        wB += hist[i]
        if wB == 0:
            continue
        wF = total - wB
        if wF == 0:
            break

        sumB += i * hist[i]
        mB = sumB / wB
        mF = (sum1[i] - sumB) / wF
        between = wB * wF * (mB - mF) ** 2

        if between > maximum:
            threshold = i
            maximum = between

    return threshold

# ヒストグラムに対して大津の閾値を求め、その閾値で2値化した画像を返す
def otsu_binarization(image):
    # ヒストグラムの計算
    hist = cv2.calcHist([image], [0], None, [256], [0, 256])
    hist = hist.flatten()

    # 大津の閾値を計算
    threshold = calculate_otsu_threshold(hist)

    # 大津の閾値で2値化
    _, binary_image = cv2.threshold(image, threshold, 255, cv2.THRESH_BINARY)
    return binary_image

# 画像を読み込んで、RGBヒストグラムとグレースケールのヒストグラムそれぞれに対して大津の閾値を計算する
def calculate_otsu_thresholds(image_path):
    # 画像を読み込む
    img = Image.open(image_path)
    rgb_data = np.array(img)
    gray_data = np.array(img.convert("L"))

    # RGBそれぞれに対してヒストグラムを計算
    r_hist = np.histogram(rgb_data[:, :, 0], bins=256, range=(0, 255))[0]
    g_hist = np.histogram(rgb_data[:, :, 1], bins=256, range=(0, 255))[0]
    b_hist = np.histogram(rgb_data[:, :, 2], bins=256, range=(0, 255))[0]

    # グレースケールのヒストグラムを計算
    gray_hist = np.histogram(gray_data, bins=256, range=(0, 255))[0]

    # ヒストグラムに対して大津の閾値を計算
    r_threshold = calculate_otsu_threshold(r_hist)
    g_threshold = calculate_otsu_threshold(g_hist)
    b_threshold = calculate_otsu_threshold(b_hist)
    gray_threshold = calculate_otsu_threshold(gray_hist)
    return r_threshold, g_threshold, b_threshold, gray_threshold

# 画像を読み込んで、RGBヒストグラムとグレースケールのヒストグラムそれぞれに対して大津の閾値で2値化した画像を返す
def otsu_binarizations(image_path):
    # 画像を読み込む
    img = Image.open(image_path)
    rgb_data = np.array(img)
    gray_data = np.array(img.convert("L"))

    # RGBそれぞれに対してヒストグラムを計算
    r_hist = np.histogram(rgb_data[:, :, 0], bins=256, range=(0, 255))[0]
    g_hist = np.histogram(rgb_data[:, :, 1], bins=256, range=(0, 255))[0]
    b_hist = np.histogram(rgb_data[:, :, 2], bins=256, range=(0, 255))[0]

    # グレースケールのヒストグラムを計算
    gray_hist = np.histogram(gray_data, bins=256, range=(0, 255))[0]

    # ヒストグラムに対して大津の閾値で2値化
    r_binary_image = otsu_binarization(rgb_data[:, :, 0])
    g_binary_image = otsu_binarization(rgb_data[:, :, 1])
    b_binary_image = otsu_binarization(rgb_data[:, :, 2])
    gray_binary_image = otsu_binarization(gray_data)
    return r_binary_image, g_binary_image, b_binary_image, gray_binary_image

# 画像を読み込んで、hsvヒストグラムを計算する
def calculate_hsv_histogram(image_path):
    # 画像を読み込む
    img = Image.open(image_path)
    rgb_data = np.array(img)

    # RGBからHSVに変換
    hsv_data = colors.rgb_to_hsv(rgb_data / 255.0)

    # HSVヒストグラムを計算
    h_hist = np.histogram(hsv_data[:, :, 0], bins=256, range=(0, 1))[0]
    s_hist = np.histogram(hsv_data[:, :, 1], bins=256, range=(0, 1))[0]
    v_hist = np.histogram(hsv_data[:, :, 2], bins=256, range=(0, 1))[0]
    return h_hist, s_hist, v_hist

# hsvヒストグラムの尖度、歪度を計算する
def calculate_hsv_kurtosis_and_skewness(image_path):
    # HSVヒストグラムを計算
    h_hist, s_hist, v_hist = calculate_hsv_histogram(image_path)

    # ヒストグラムの尖度を計算
    h_kurtosis = stats.kurtosis(h_hist)
    s_kurtosis = stats.kurtosis(s_hist)
    v_kurtosis = stats.kurtosis(v_hist)

    # ヒストグラムの歪度を計算
    h_skewness = stats.skew(h_hist)
    s_skewness = stats.skew(s_hist)
    v_skewness = stats.skew(v_hist)
    return h_kurtosis, s_kurtosis, v_kurtosis, h_skewness, s_skewness, v_skewness

# 画像を読み込んで、RGBヒストグラムとグレースケールのヒストグラムそれぞれに対してヒストグラムの平均輝度を計算する
def calculate_brightness(image_path):
    # 画像を読み込む
    img = Image.open(image_path)
    rgb_data = np.array(img)
    gray_data = np.array(img.convert("L"))

    # RGBそれぞれに対してヒストグラムを計算
    r_hist = np.histogram(rgb_data[:, :, 0], bins=256, range=(0, 255))[0]
    g_hist = np.histogram(rgb_data[:, :, 1], bins=256, range=(0, 255))[0]
    b_hist = np.histogram(rgb_data[:, :, 2], bins=256, range=(0, 255))[0]

    # グレースケールのヒストグラムを計算
    gray_hist = np.histogram(gray_data, bins=256, range=(0, 255))[0]

    # ヒストグラムの平均輝度を計算
    r_brightness = np.mean(r_hist)
    g_brightness = np.mean(g_hist)
    b_brightness = np.mean(b_hist)
    gray_brightness = np.mean(gray_hist)
    return r_brightness, g_brightness, b_brightness, gray_brightness

# 画像を読み込んで、RGBヒストグラムとグレースケールのヒストグラムそれぞれに対してヒストグラムの最大輝度を計算する
def calculate_max_brightness(image_path):
    # 画像を読み込む
    img = Image.open(image_path)
    rgb_data = np.array(img)
    gray_data = np.array(img.convert("L"))

    # RGBそれぞれに対してヒストグラムを計算
    r_hist = np.histogram(rgb_data[:, :, 0], bins=256, range=(0, 255))[0]
    g_hist = np.histogram(rgb_data[:, :, 1], bins=256, range=(0, 255))[0]
    b_hist = np.histogram(rgb_data[:, :, 2], bins=256, range=(0, 255))[0]

    # グレースケールのヒストグラムを計算
    gray_hist = np.histogram(gray_data, bins=256, range=(0, 255))[0]

    # ヒストグラムの最大輝度を計算
    r_max_brightness = np.argmax(r_hist)
    g_max_brightness = np.argmax(g_hist)
    b_max_brightness = np.argmax(b_hist)
    gray_max_brightness = np.argmax(gray_hist)
    return r_max_brightness, g_max_brightness, b_max_brightness, gray_max_brightness

# 画像の最大輝度、最頻輝度を計算し、その比率を計算する
def calculate_max_mode_contrast(image_path):
    image = cv2.imread(image_path)
    # 画像をグレースケールに変換
    gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # ヒストグラムの計算
    hist = cv2.calcHist([gray_image], [0], None, [256], [0, 256])
    hist = hist.flatten()[10:]
    print("len(hsit): ", len(hist))
    # print("hist: ", hist)

    # 最大輝度値の取得
    non_zero_indices = np.nonzero(hist)[0]  # 0でない要素のインデックスを取得
    max_index = non_zero_indices[-1]  # 最大のインデックスを取得    
    mode_index = int(np.argmax(hist)) +10
    hist_contrast = mode_index / max_index
    # max_brightness = np.argmax(hist)
    print("max_index: ", max_index)
    print("mode_index: ", mode_index)
    print("hist_contrast: ", hist_contrast)
    # print("peak index: ", peak_index)
    return max_index, mode_index, hist_contrast

# 画像のコントラストヒストグラムの特徴量を計算する
# def calcuate_contrast_features(image_path, block_size):
#     # ヒストグラムの計算
#     histogram = create_contrast_histogram(image_path, block_size)

#     # 統計量の計算
#     contrast_variation_coefficient, squared_mean_contrast = calculate_contrast_coefficients(histogram)

#     return contrast_variation_coefficient, squared_mean_contrast

# グレースケール画像のエントロピーを計算する
def calculate_entropy_gray(image_path):
    # 画像を読み込む
    img = Image.open(image_path)
    gray_data = np.array(img.convert("L"))

    # ヒストグラムの計算
    hist = np.histogram(gray_data, bins=256, range=(0, 255))[0]

    # 総ピクセル数
    total = hist.sum()

    # エントロピーの計算
    entropy_gray = 0
    for i in range(256):
        p = hist[i] / total
        if p == 0:
            continue
        entropy_gray -= p * np.log2(p)
    return entropy_gray

# 画像のエントロピーを計算する
def calculate_entropy_rgb(image_path):
    # img = Image.open(image_path)
    img = cv2.imread(image_path)
    # img = cv2.imread('./img_data/lena_gray.jpg') #ファイルのバスは適宜変えてください
    height, width, _ = img.shape

    # ヒストグラム（各色の画素数）の算出
    histgram = [0]*256
    for i in range(height):
        for j in range(width):
            histgram[img[i, j, 0]] += 1

    # エントロピーの算出
    size = height * width
    entropy_rgb = 0

    for i in range(256):
        # レベルiの出現確率p
        p = histgram[i]/size
        if p == 0:
            continue
        entropy_rgb -= p*np.log2(p)

    # plt.imshow(img)
    # print('エントロピー：{}'.format(entropy))
    return entropy_rgb


# 上記の関数を使って、画像の特徴量を計算し、dfに格納する
def calculate_features(df):
    for index, row in tqdm(df.iterrows(), total=len(df)):
        # image_path = row["image_path"]
        try:
            image_name = row["image_name"]
            # print(image_path)
            image_path = glob.glob("../experiment_images/*/" + image_name)[0]
            


            ####追加したい列#################################################################################################################
            # image_pathにたいして上記の関数を使って、画像の特徴量を計算し、dfに格納する
            # r_kurtosis, g_kurtosis, b_kurtosis, gray_kurtosis = calculate_kurtosis(image_path)
            # r_skewness, g_skewness, b_skewness, gray_skewness = calculate_skewness(image_path)
            # r_threshold, g_threshold, b_threshold, gray_threshold = calculate_otsu_thresholds(image_path)
            # r_binary_image, g_binary_image, b_binary_image, gray_binary_image = otsu_binarizations(image_path)
            # h_kurtosis, s_kurtosis, v_kurtosis, h_skewness, s_skewness, v_skewness = calculate_hsv_kurtosis_and_skewness(image_path)
            # r_brightness, g_brightness, b_brightness, gray_brightness = calculate_brightness(image_path)
            # r_max_brightness, g_max_brightness, b_max_brightness, gray_max_brightness = calculate_max_brightness(image_path)
            # max_index, mode_index, hist_contrast = calculate_max_mode_contrast(image_path)
            # contrast_variation_coefficient, squared_mean_contrast = calcuate_contrast_features( image_path, block_size=32)
            ####追加したい列：新規####################################################################################################################

            # entropy_gray = calculate_entropy_gray(image_path)
            # entropy_rgb = calculate_entropy_rgb(image_path)
            # skewness_gray2 = calculate_skewness2(image_path)
            # michaelson_contrast = calculate_michaelson_contrast(image_path)
            # sharpness_factor_value = calculate_sharpness_factor(image_path)
            # mse, snr, psnr = calculate_mse_psnr(image_path)
            # sharpness_factor2 = calculate_sharpness_factor(image_path)
            # contrast_luminance = calculate_contrast_luminance(image_path)
            # skewness_luminance = calculate_skewness_of_luminance(image_path)
            edge_sobel = calculate_edge_sobel(image_path)
            # print("done")


            ###実際に追加###################################################################################################################
            # df.loc[index, "r_kurtosis"] = r_kurtosis
            # df.loc[index, "g_kurtosis"] = g_kurtosis
            # df.loc[index, "b_kurtosis"] = b_kurtosis
            # df.loc[index, "gray_kurtosis"] = gray_kurtosis

            # df.loc[index, "r_skewness"] = r_skewness
            # df.loc[index, "g_skewness"] = g_skewness
            # df.loc[index, "b_skewness"] = b_skewness
            # df.loc[index, "gray_skewness"] = gray_skewness

            # df.loc[index, "r_threshold"] = r_threshold
            # df.loc[index, "g_threshold"] = g_threshold
            # df.loc[index, "b_threshold"] = b_threshold
            # df.loc[index, "gray_threshold"] = gray_threshold

            # df.loc[index, "h_kurtosis"] = h_kurtosis
            # df.loc[index, "s_kurtosis"] = s_kurtosis
            # df.loc[index, "v_kurtosis"] = v_kurtosis

            # df.loc[index, "h_skewness"] = h_skewness
            # df.loc[index, "s_skewness"] = s_skewness
            # df.loc[index, "v_skewness"] = v_skewness

            # df.loc[index, "r_brightness"] = r_brightness
            # df.loc[index, "g_brightness"] = g_brightness
            # df.loc[index, "b_brightness"] = b_brightness
            # df.loc[index, "gray_brightness"] = gray_brightness

            # df.loc[index, "r_max_brightness"] = r_max_brightness
            # df.loc[index, "g_max_brightness"] = g_max_brightness
            # df.loc[index, "b_max_brightness"] = b_max_brightness
            # df.loc[index, "gray_max_brightness"] = gray_max_brightness

            # df.loc[index, "max_index"] = max_index
            # df.loc[index, "mode_index"] = mode_index
            # df.loc[index, "hist_contrast"] = hist_contrast
            
            # df.loc[index, "contrast_variation_coefficient"] = contrast_variation_coefficient
            # df.loc[index, "squared_mean_contrast"] = squared_mean_contrast
            ###実際に追加：新規####################################################################################################################
            # df.loc[index, "entropy_gray"] = entropy_gray
            # df.loc[index, "entropy_rgb"] = entropy_rgb
            # df.loc[index, "gray_skewness2"] = skewness_gray2
            # df.loc[index, "michaelson_contrast"] = michaelson_contrast
            # df.loc[index, "sharpness_factor"] = sharpness_factor_value
            # df.loc[index, "mse"] = mse
            # df.loc[index, "snr"] = snr
            # df.loc[index, "psnr"] = psnr
            # df.loc[index, "sharpness_factor2"] = sharpness_factor2
            # df.loc[index, "contrast_luminance"] = contrast_luminance
            # df.loc[index, "skewness_luminance"] = skewness_luminance
            df.loc[index, "edge_sobel"] = edge_sobel


            
            ####################################################################################################################################
    
            # image = cv2.imread(image_path)
            # gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            # image_figure = row["figure"]
            # threshold_image = maskedByFigure(image_figure)
            # digit_brightness, non_digit_brightness, brightness_ratio = calculate_contrast(
            #     threshold_image, gray_image)
            # df.loc[index, "digit_brightness"] = digit_brightness
            # df.loc[index, "non_digit_brightness"] = non_digit_brightness
            # df.loc[index, "brightness_ratio"] = brightness_ratio
        except IndexError :
            print("pass")
            pass
    df = df.dropna()
    return df


def main():
    df = pd.read_excel("../data/final_recent_bright/final_recent_bright_add_entropy_skewgray2_michaelson_sf_mse_sf2_luminance.xlsx")
    # df = pd.read_excel("../data/final_recent_dark/final_recent_dark_add_entropy_fft_color_skewgray2_michaelson_sf_mse.xlsx")

    df = calculate_features(df)

    df.to_excel("../data/final_recent_bright/final_recent_bright_add_entropy_skewgray2_michaelson_sf_mse_sf2_luminance_sobel.xlsx")
    # df.to_excel("../data/final_recent_dark/final_recent_dark_add_entropy_fft_color_skewgray2_michaelson_sf_mse_luminance.xlsx")
    print(df)

    df = pd.read_excel("../data/final_recent_dark/final_recent_dark_add_entropy_fft_color_skewgray2_michaelson_sf_mse_luminance.xlsx")
    df = calculate_features(df)
    df.to_excel("../data/final_recent_dark/final_recent_dark_add_entropy_fft_color_skewgray2_michaelson_sf_mse_luminance_sobel.xlsx")
    print(df)
if __name__ == "__main__":
    main()




