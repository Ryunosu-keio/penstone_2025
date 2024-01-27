#元画像と比較した、各画素の輝度値の差の二乗の平均を求める

from PIL import Image
import numpy as np
from skimage import io
from skimage.metrics import structural_similarity as ssim
import matplotlib.pyplot as plt


def calculate_mse_psnr(image1, image2):
    # 画像を読み込む
    img1 = Image.open(image1)
    img2 = Image.open(image2)

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

# 画像ファイルのパスをここに入れてください
image1_path = 'path_to_your_first_image.jpg'
image2_path = 'path_to_your_second_image.jpg'

# MSEを計算
mse, psnr = calculate_mse_psnr(image1_path, image2_path)
print(f"平均二乗誤差（MSE）: {mse}")
print(f"ピーク信号対雑音比（PSNR）: {psnr}")


def calculate_ssim(image1, image2):
    # 画像を読み込む
    img1 = io.imread(image1, as_gray=True)
    img2 = io.imread(image2, as_gray=True)

    # SSIMを計算
    score, diff = ssim(img1, img2, full=True)
    print(f"SSIM: {score}")

    # 差分画像を表示
    plt.imshow(diff, cmap='gray')
    plt.title('Difference Image')
    plt.show()

# 画像ファイルのパスをここに入れてください
image1_path = 'path_to_your_first_image.jpg'
image2_path = 'path_to_your_second_image.jpg'

# SSIMを計算
calculate_ssim(image1_path, image2_path)


