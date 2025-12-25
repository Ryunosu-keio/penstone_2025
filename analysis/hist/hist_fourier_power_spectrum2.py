# from PIL import Image
# import numpy as np
# from scipy.fft import fft2, fftshift
# import matplotlib.pyplot as plt

# # 画像を読み込む関数
# def load_image(file_path):
#     img = Image.open(file_path)
#     img_gray = img.convert('L')  # グレースケールに変換
#     img_array = np.array(img_gray)  # NumPy配列に変換
#     return img_array

# # 極座標系でのスペクトル分析を行う関数
# def convert_to_polar_spectrum(image_array):
#     fft_result = fft2(image_array)
#     fft_shifted = fftshift(fft_result)  # FFT結果を中心にシフト
#     magnitude_spectrum = np.abs(fft_shifted)  # マグニチュードスペクトルを計算
#     maxRadius = min(image_array.shape) // 2
#     maxTheta = 360  # 0-359度
#     # 極座標変換用の配列を初期化
#     Pr = np.zeros(maxRadius)
#     Pt = np.zeros(maxTheta)
#     ny, nx = image_array.shape
#     center_x, center_y = nx // 2, ny // 2

#     # 極座標系でのスペクトラム計算
#     for y in range(ny):
#         for x in range(nx):
#             # 中心からの相対位置を計算
#             rel_x = x - center_x
#             rel_y = y - center_y
#             # 極座標変換
#             rr = int(np.sqrt(rel_x**2 + rel_y**2))
#             th = int(np.arctan2(rel_y, rel_x) * 180.0 / np.pi) % maxTheta
#             # スペクトル値を累積
#             if rr < maxRadius:
#                 Pr[rr] += magnitude_spectrum[y, x]
#                 Pt[th] += magnitude_spectrum[y, x]
#                 # print("rr,th",rr, th)
#                 # print("magnitude_spectrum[y, x]",magnitude_spectrum[y, x])
#                 # print("Pr[rr], Pt[th]",Pr[rr], Pt[th])

#     # スペクトルの平滑化と正規化
#     aPr = np.convolve(Pr, np.ones(3)/3, mode='same')
#     aPt = np.convolve(Pt, np.ones(3)/3, mode='same')
#     aPr /= np.max(aPr)
#     aPt /= np.max(aPt)

#     return aPr, aPt

# # 画像を読み込む
# image_path = '../photos/煉瓦壁1-1.jpg'
# image_array = load_image(image_path)

# # 極座標系でのスペクトル分析を実行
# polar_radius, polar_theta = convert_to_polar_spectrum(image_array)

# # 結果をプロット
# plt.figure(figsize=(12, 6))
# plt.subplot(1, 2, 1)
# plt.plot(polar_radius)
# plt.title('Polar Spectrum - Radius')
# plt.xlabel('Radius')
# plt.ylabel('Amplitude')
# # 両対数グラフにする
# plt.yscale('log')
# plt.xscale('log')



# plt.subplot(1, 2, 2)
# plt.plot(polar_theta)
# plt.title('Polar Spectrum - Theta')
# plt.xlabel('Theta')
# plt.ylabel('Amplitude')
# # #両対数グラフにする
# # plt.yscale('log')
# # plt.xscale('log')

# plt.tight_layout()
# plt.show()


from scipy.fft import fft2, fftshift
from scipy import ndimage
import matplotlib.pyplot as plt
import numpy as np
from PIL import Image
import glob

#画像を中心に合わせて2の累乗にリサイズ


def resize_to_power_of_two(image_path):
    # 画像を読み込む
    img = Image.open(image_path)
    width, height = img.size

    # 2の累乗に最も近いサイズを求める
    new_size = 2**np.floor(np.log2(min(width, height))).astype(int)
    left = (width - new_size) // 2
    top = (height - new_size) // 2
    right = (width + new_size) // 2
    bottom = (height + new_size) // 2

    # 画像を中央から切り抜く
    img_cropped = img.crop((left, top, right, bottom))
    #　画像のdpiを取得
    dpi = int(img.info['dpi'][0])
    
    img_cropped.save("../photos/2Npic.jpg")
    print(dpi, new_size)
    return img_cropped, new_size, dpi



# def image_to_2N(image_path):
#     # 画像の読み込み
#     img = Image.open(image_path).convert('L')
#     img_array = np.array(img)
#     # 2の累乗にリサイズ
#     size_image = 2 ** int(np.log2(min(img_array.shape[0], img_array.shape[1]))+1)
#     img = img.resize((size_image, size_image))
#     img.show()
#     img_array = np.array(img)

#     return img_array, size_image

def calc_polar_spectra(img_cropped, size_image, dpi, max_radius, max_theta):

    img_cropped_gray = img_cropped.convert('L')
    img_array = np.array(img_cropped_gray)
    # FFTを実行してパワースペクトルを計算
    fft_result = fft2(img_array)
    fft_shifted = fftshift(fft_result)
    #直流成分を除去
    # fft_shifted[size_image//2, size_image//2] = 0
    magnitude_spectrum = np.abs(fft_shifted)
    # magnitude_spectrum = 20 * np.log(np.abs(fft_shifted))

    # 初期化
    Pr = np.zeros(max_radius)
    Pt = np.zeros(max_theta)
    Pf = np.zeros(max_radius)

    # 極座標系でのスペクトル計算
    center_x, center_y = size_image // 2, size_image // 2
    for y in range(1,int(size_image/4)):
        for x in range(1,int(size_image/4)):
            rel_x = x - center_x
            rel_y = center_y - y  # 画像の座標系を反転
            rr = int(np.sqrt(rel_x**2 + rel_y**2)+0.5)
            th = int((np.arctan2(rel_y, rel_x) * 180.0 / np.pi)+0.5) % max_theta
            if rr < max_radius:
                Pr[rr] += magnitude_spectrum[y, x]
                Pt[th] += magnitude_spectrum[y, x]
    
    for rr in range(len(Pf)):
        # Pf[rr] = (96/(5.12*256))*rr
        Pf[rr] = (float(dpi/2.54)/(size_image/2))*rr

    # スペクトルの平滑化
    # aPr = ndimage.uniform_filter1d(Pr, size=3)
    # aPt = ndimage.uniform_filter1d(Pt, size=3)
    # スペクトルの平滑化と正規化
    aPr = np.convolve(Pr, np.ones(3)/3, mode='same')
    aPt = np.convolve(Pt, np.ones(3)/3, mode='same')

    # 正規化
    aPr /= np.max(aPr)
    aPt /= np.max(aPt) 

    # プロット
    fig, ax = plt.subplots(1, 3, figsize=(12, 6))
    ax[0].plot(aPr)
    ax[0].set_title('Polar Spectrum - Radius')
    ax[0].set_xlabel('Radius')
    ax[0].set_ylabel('Amplitude')

    ax[1].plot(aPt)
    ax[1].set_title('Polar Spectrum - Theta')
    ax[1].set_xlabel('Theta')
    ax[1].set_ylabel('Amplitude')


    # aPrとPfの両対数グラフにする
    ax[2].plot(Pf, aPr)
    ax[2].set_title('Polar Spectrum - frequency log-log')
    ax[2].set_xlabel('Frequency')
    ax[2].set_ylabel('Amplitude')
    ax[2].set_xscale('log')
    ax[2].set_yscale('log')
    # 対数軸の罫線を引く
    ax[2].grid(which='both')
    #対数軸の範囲
    ax[2].set_xlim(1, 100)


    plt.show()


# 画像パスとパラメータ

# image_path = '../photos/simasin.jpg'
# image_path = glob.glob("../experiment_images/105_0/*.jpg")[23]
image_path = "../photos/煉瓦壁1-1.jpg"

# 画像を2のN乗にリサイズ（中心から切り抜き）
img_resized, size_image,dpi = resize_to_power_of_two(image_path)

# リサイズした画像を表示
img_resized.show()

# img_array, size_image = image_to_2N(image_path)


max_radius = size_image // 2  # 最大半径
max_theta = 360  # 最大角度

# 極座標スペクトルの計算とプロット

calc_polar_spectra(img_resized, size_image, dpi, max_radius, max_theta)