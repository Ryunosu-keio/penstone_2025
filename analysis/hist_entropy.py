import cv2
import matplotlib.pyplot as plt
import numpy as np
import glob

# 画像の読み込み
# path = glob.glob("../pictures/transformed/roomDark_figureBright/*.JPG")
path = glob.glob("../experiment_images/101_0/*.jpg")

for i in range(len(path)):
    print(path[i])
    img = cv2.imread(path[i])
    # img = cv2.imread('./img_data/lena_gray.jpg') #ファイルのバスは適宜変えてください
    height, width, _ = img.shape

    # ヒストグラム（各色の画素数）の算出
    histgram = [0]*256
    for i in range(height):
        for j in range(width):
            histgram[img[i, j, 0]] += 1

    # エントロピーの算出
    size = height * width
    entropy = 0

    for i in range(256):
        # レベルiの出現確率p
        p = histgram[i]/size
        if p == 0:
            continue
        entropy -= p*np.log2(p)

    plt.imshow(img)
    print('エントロピー：{}'.format(entropy))
