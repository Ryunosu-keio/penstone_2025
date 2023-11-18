import pandas as pd
import cv2
import numpy as np
import matplotlib.pyplot as plt
import glob


def maskedByFigure(figure):
    image_path = '/mnt/data/' + str(figure) + '.JPG'
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


def calculate(threshold_image, gray_image):
    # 数字の部分と数字以外の部分の平均輝度を計算
    digit_brightness = np.mean(gray_image[threshold_image == 255])
    non_digit_brightness = np.mean(gray_image[threshold_image == 0])

    # 平均輝度の比を求める
    brightness_ratio = digit_brightness / non_digit_brightness

    digit_brightness, non_digit_brightness, brightness_ratio
    return [digit_brightness, non_digit_brightness, brightness_ratio]


def contrast_to_df(path):
    image_path = '/mnt/data/3.JPG'

    image = cv2.imread(image_path)
