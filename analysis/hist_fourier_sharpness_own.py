import cv2
import numpy as np
from matplotlib import pyplot as plt
from PIL import Image


# 画像をグレースケールで読み込むPIL
image = Image.open('../pictures/transformed/roomDark_figureBright/2.JPG')
# image = Image.open("../photos/2015-11-landscape-free-photo42.jpg")
image_gray = image.convert('L')

image2 = Image.open("../experiment_images/103_7/40_2_contrast0.888_sharpness0.066_equalization13.838.jpg")
image2_gray = image2.convert('L')


# image = cv2.imread('../pictures/transformed/roomDark_figureBright/T.JPG')
# image_gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
# image2 = cv2.imread("../experiment_images/101_0/4_T_brightness28.468_contrast0.864_sharpness0.767.jpg")
# image2_gray = cv2.cvtColor(image2, cv2.COLOR_BGR2GRAY)


def fourier(image_gray):
    # 画像をnumpy配列に変換
    image_gray = np.asarray(image_gray)

    f = np.fft.fft2(image_gray)
    fshift = np.fft.fftshift(f)

    # 画像のサイズを取得
    rows, cols = image_gray.shape
    crow, ccol = rows // 2, cols // 2

    # ガウシアンマスクを作成（低周波フィルタ）
    # sigma = 30  # ガウス関数の標準偏差
    # x = np.linspace(-ccol, ccol, cols)
    # y = np.linspace(-crow, crow, rows)
    # x, y = np.meshgrid(x, y)
    # gaussian_mask = np.exp(- (x**2 + y**2) / (2 * sigma**2))


    #円形のマスクを作成
    x = np.linspace(-ccol, ccol, cols)
    y = np.linspace(-crow, crow, rows)
    x, y = np.meshgrid(x, y)
    r = np.sqrt(x**2 + y**2)
    gaussian_mask = np.zeros((rows, cols))
    gaussian_mask[r < 30] = 1

    # マスクを適用して低周波成分を取り出す
    fshift_lowpass = fshift * gaussian_mask

    # マスクを反転して高周波成分を取り出す
    gaussian_mask_inv = 1 - gaussian_mask
    fshift_highpass = fshift * gaussian_mask_inv

    # 画像に戻す
    img_lowpass = np.fft.ifftshift(fshift_lowpass)
    img_lowpass = np.fft.ifft2(img_lowpass)
    img_lowpass = np.abs(img_lowpass)

    img_highpass = np.fft.ifftshift(fshift_highpass)
    img_highpass = np.fft.ifft2(img_highpass)
    img_highpass = np.abs(img_highpass)

    return img_lowpass, img_highpass


img_lowpass, img_highpass = fourier(image_gray)
img_lowpass2, img_highpass2 = fourier(image2_gray)
# 結果を表示
plt.figure(figsize=(20, 10))

plt.subplot(241), plt.imshow(image)
plt.title('Original Image'), plt.axis('off')

plt.subplot(242), plt.imshow(image_gray, cmap='gray')
plt.title('Gray Image'), plt.axis('off')

plt.subplot(243), plt.imshow(img_lowpass, cmap='gray')
plt.title('Low-pass Filtered Image'), plt.axis('off')

plt.subplot(244), plt.imshow(img_highpass, cmap='gray')
plt.title('High-pass Filtered Image'), plt.axis('off')

plt.subplot(245), plt.imshow(image2, cmap='gray')
plt.title('Original Image'), plt.axis('off')

plt.subplot(246), plt.imshow(image2_gray, cmap='gray')
plt.title('Gray Image'), plt.axis('off')

plt.subplot(247), plt.imshow(img_lowpass2, cmap='gray')
plt.title('Low-pass Filtered Image'), plt.axis('off')

plt.subplot(248), plt.imshow(img_highpass2, cmap='gray')
plt.title('High-pass Filtered Image'), plt.axis('off')


plt.show()
