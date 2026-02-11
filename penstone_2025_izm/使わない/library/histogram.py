from PIL import Image
import matplotlib.pyplot as plt
import numpy as np

def color_hist(filename):
    img = np.asarray(Image.open(filename).convert("RGB")).reshape(-1,3)
    plt.hist(img, color=["red", "green", "blue"], bins=128)
    plt.show()
    plt.xlim(0, 255)
    # plt.savefig('histogram/original_hist.png')


color_hist("../histogram/redpic_dark/スクリーンショット 2023-12-13 224354.png")



def gray_hist(filename):
    # 画像をグレースケールに変換し、NumPy配列に変換
    img_gray = np.asarray(Image.open(filename).convert("L"))

    # グレースケール画像のヒストグラムをプロット
    plt.hist(img_gray.ravel(), bins=128, color='gray')

    # x軸の範囲を0から255に設定
    plt.xlim(0, 255)
    plt.show()
    # plt.savefig('histogram/grayscale_hist.png')

# 関数を実行
gray_hist("../histogram/redpic_dark/スクリーンショット 2023-12-13 224354.png")