import pandas as pd
import cv2
import numpy as np
import matplotlib.pyplot as plt
import glob
import os
from tqdm import tqdm


def maskedByFigure(figure):
    image_path = '../pictures/transformed/roomDark_figureBright/' + \
        str(figure) + '.JPG'
    image_figure = cv2.imread(image_path)
    # 画像をグレースケールに変換
    gray_image = cv2.cvtColor(image_figure, cv2.COLOR_BGR2GRAY)

    # 閾値を上げて再度しきい値処理を行う
    _, thresh_image = cv2.threshold(gray_image, 220, 255, cv2.THRESH_BINARY)

    # # マスキング処理を行う
    # high_masked_image = cv2.bitwise_and(
    #     gray_image, gray_image, mask=thresh_image)

    # # マスキング後の画像を表示する
    # plt.imshow(high_masked_image, cmap='gray')
    # plt.title('High Threshold Masked Image')
    # plt.axis('off')  # 軸をオフに
    # plt.show()
    return image_figure, thresh_image


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


def calculate_contrast_w3c(threshold_image, image_figure):
    # w3cの定義に従って明度差と色差を計算
    digit_brightness_red = np.mean(image_figure[threshold_image == 255], axis=0)[0]
    digit_brightness_green = np.mean(image_figure[threshold_image == 255], axis=0)[1]
    digit_brightness_blue = np.mean(image_figure[threshold_image == 255], axis=0)[2]

    non_digit_brightness_red = np.mean(image_figure[threshold_image == 0], axis=0)[0]
    non_digit_brightness_green = np.mean(image_figure[threshold_image == 0], axis=0)[1]
    non_digit_brightness_blue = np.mean(image_figure[threshold_image == 0], axis=0)[2]

    #w3cの明度差の定義に従って計算
    brightness_w3c = 0.299 * abs(digit_brightness_red-non_digit_brightness_red) + 0.587 * abs(digit_brightness_green-non_digit_brightness_green) + 0.114 * abs(digit_brightness_blue-non_digit_brightness_blue)
    
    #w3cの色差の定義に従って計算
    colorness_w3c= abs(digit_brightness_red-non_digit_brightness_red) + abs(digit_brightness_green-non_digit_brightness_green) + abs(digit_brightness_blue-non_digit_brightness_blue)

    return brightness_w3c, colorness_w3c

def contrast_to_df(df):
    for index, row in tqdm(df.iterrows()):
        # image_path = row["image_path"]
        try:
            image_name = row["image_name"]
            # print(image_path)
            image_path = glob.glob("../experiment_images/*/" + image_name)[0]
            print(image_path)
            # image_figure = row["figure"]
            figure = row["figure"]
            # print(image_figure)
            image = cv2.imread(image_path)
            # 画像をグレースケールに変換
            gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            # show_image(gray_image)
            # threshold_image = maskedByFigure(image_figure)
            image_figure, threshold_image = maskedByFigure(figure)
            # digit_brightness, non_digit_brightness, brightness_ratio = calculate_contrast(
            #     threshold_image, gray_image)
            # df.loc[index, "digit_brightness"] = digit_brightness
            # df.loc[index, "non_digit_brightness"] = non_digit_brightness
            # df.loc[index, "brightness_ratio"] = brightness_ratio

            brightness_w3c, colorness_w3c = calculate_contrast_w3c(
                threshold_image, image_figure)
            print(brightness_w3c, colorness_w3c)
            df.loc[index, "brightness_w3c"] = brightness_w3c
            df.loc[index, "colorness_w3c"] = colorness_w3c
            print("done")
        except IndexError :
            print("pass")
            pass
    df = df.dropna()
    return df


if __name__ == "__main__":
    path = "../data/final_part2/darkfinal_with_combined_data4.xlsx"
    df = pd.read_excel(path)
    #明るいとき
    # df = df[df["figure"] != "Q"]
    # df = df[df["figure"] != "J"]
    # df = df[df["image_name"] != "33_7_brightness19.0_sharpness0.85_gamma0.99.jpg"]
    # df = df[df["image_name"] != "36_9_sharpness0.28_equalization24.0.jpg"]
    # df = df[df["image_name"] != "20_I_gamma0.65_sharpness0.12_equalization9.4.jpg"]
    # df = df[df["image_name"] != "32_2_contrast1.1_sharpness0.65_equalization5.8.jpg"]
    # df = df[df["image_name"] != "10_S_brightness16.0_gamma0.8.jpg"]
    # df = df[df["image_name"] != "1_E_sharpness0.28_contrast0.84_equalization16.0.jpg"]
    # df = df[df["image_name"] != "18_2_gamma0.87_sharpness0.79_equalization29.0.jpg"]



    df = contrast_to_df(df)
    print(df)
    df.to_excel("../data/final_recent_dark/final_recent_dark.xlsx", index=False)
