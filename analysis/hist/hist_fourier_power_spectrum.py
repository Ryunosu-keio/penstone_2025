
import matplotlib.pyplot as plt
from scipy.fft import fftshift, fft2
import numpy as np



def create_dummy_image(size):
    """ ダミー画像（シンプルなグレースケールのグラデーション）を作成する """
    img = np.zeros((size, size), dtype=np.uint8)
    for i in range(size):
        img[:, i] = i * 255 // size
    return img

def calc_power_spectrum(img_array):
    """ 画像のパワースペクトルを計算する """
    fft_result = fft2(img_array)
    fft_shifted = fftshift(fft_result)  # 中心を原点にシフト
    magnitude_spectrum = 20 * np.log(np.abs(fft_shifted))  # マグニチュードスペクトルを計算
    return magnitude_spectrum

# ダミー画像の生成とFFT実行
dummy_size = 256
dummy_image = create_dummy_image(dummy_size)
power_spectrum = calc_power_spectrum(dummy_image)


def convert_to_polar_and_smooth(si, maxRadius, maxTheta):
    nx, ny = si.shape
    Pr = np.zeros(maxRadius)
    Pt = np.zeros(maxTheta)

    # 極座標系でのスペクトラム計算
    for j in range(ny // 2 + 10):
        for i in range(nx):
            x = i - nx // 2
            y = ny // 2 - j
            rr = int(np.sqrt(x*x + y*y) + 0.5)
            th = int(np.arctan2(y, x) * 180.0 / np.pi + 0.5)
            if rr < maxRadius and th >= 0 and th < maxTheta:
                Pr[rr] += si[i, j]
                Pt[th] += si[i, j]

    # スペクトルの平滑化
    aPr = np.zeros(maxRadius)
    aPt = np.zeros(maxTheta)
    aPr[0] = (Pr[0] + Pr[1]) / 2.0
    aPt[0] = (Pt[0] + Pt[1]) / 2.0
    aPr[-1] = (Pr[-2] + Pr[-1]) / 2.0
    aPt[-1] = (Pt[-2] + Pt[-1]) / 2.0

    for i in range(1, maxRadius - 1):
        aPr[i] = (Pr[i-1] + Pr[i] + Pr[i+1]) / 3.0

    for i in range(1, maxTheta - 1):
        aPt[i] = (Pt[i-1] + Pt[i] + Pt[i+1]) / 3.0

    # スペクトラムの正規化
    aPr /= np.max(aPr)
    aPt /= np.max(aPt)

    return aPr, aPt

# ダミー画像のパワースペクトルデータを使用して極座標変換をテスト
maxRadius = dummy_size // 2
maxTheta = 360  # 0-359度
polar_r, polar_theta = convert_to_polar_and_smooth(power_spectrum, maxRadius, maxTheta)

# 結果のプロット
plt.figure(figsize=(12, 6))
plt.subplot(1, 2, 1)
plt.plot(polar_r)
plt.title('Polar Spectrum - Radius')
plt.xlabel('Radius')
plt.ylabel('Amplitude')
plt.subplot(1, 2, 2)
plt.plot(polar_theta)
plt.title('Polar Spectrum - Theta')
plt.xlabel('Theta')
plt.ylabel('Amplitude')
plt.show()

