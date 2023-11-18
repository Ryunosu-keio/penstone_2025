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


def contrast_to_df(df):
    for index, row in tqdm(df.iterrows()):
        # image_path = row["image_path"]
        try:
            image_name = row["image_name"]
            # print(image_path)
            image_path = glob.glob("../experiment_images/*/" + image_name)[0]
            print(image_path)
            image_figure = row["figure"]
            # print(image_figure)
            image = cv2.imread(image_path)
            # 画像をグレースケールに変換
            gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            # show_image(gray_image)
            threshold_image = maskedByFigure(image_figure)
            digit_brightness, non_digit_brightness, brightness_ratio = calculate_contrast(
                threshold_image, gray_image)
            df.loc[index, "digit_brightness"] = digit_brightness
            df.loc[index, "non_digit_brightness"] = non_digit_brightness
            df.loc[index, "brightness_ratio"] = brightness_ratio
        except IndexError :
            pass
    df = df.dropna()
    return df


if __name__ == "__main__":
    path = "../data/final_part1/final_bright_add_modified.xlsx"
    df = pd.read_excel(path)
    #明るいとき
    df = df[df["figure"] != "Q"]
    df = df[df["figure"] != "J"]
    df = df[df["image_name"] != "33_7_brightness19.0_sharpness0.85_gamma0.99.jpg"]
    df = df[df["image_name"] != "36_9_sharpness0.28_equalization24.0.jpg"]
    df = df[df["image_name"] != "20_I_gamma0.65_sharpness0.12_equalization9.4.jpg"]
    df = df[df["image_name"] != "32_2_contrast1.1_sharpness0.65_equalization5.8.jpg"]
    df = df[df["image_name"] != "10_S_brightness16.0_gamma0.8.jpg"]
    df = df[df["image_name"] != "1_E_sharpness0.28_contrast0.84_equalization16.0.jpg"]
    df = df[df["image_name"] != "18_2_gamma0.87_sharpness0.79_equalization29.0.jpg"]



    df = contrast_to_df(df)
    df.to_excel("../data/final_part1/add_contrast.xlsx", index=False)
