import numpy as np
import matplotlib.pyplot as plt
from scipy.fft import fft2, fftshift
from scipy.optimize import curve_fit
from PIL import Image
import glob

def load_image(image_path):
    """画像をグレースケールで読み込む"""
    image = Image.open(image_path).convert('L')
    return np.asarray(image)

def calculate_psd2d(image):
    """2D フーリエ変換とパワースペクトル密度(PSD)の計算"""
    f_transform = fft2(image)
    f_shifted = fftshift(f_transform)
    psd2d = np.abs(f_shifted)**2
    return psd2d

def fit_power_law(freqs, psd):
    """1/f^αのパワーローにフィットさせ、αを求める"""
    # フィットさせる関数の定義 (1/f^alpha)
    def model_func(f, alpha):
        return 1 / f**alpha

    # 0を除外して対数を取る
    log_freqs = np.log(freqs[freqs > 0])
    log_psd = np.log(psd[freqs > 0])
    print(freqs.shape)
    print(psd1d.shape)

    # フィットさせる
    popt, pcov = curve_fit(model_func, log_freqs, log_psd)
    alpha = popt[0]
    return alpha

def plot_psd(freqs, psd, alpha):
    """パワースペクトル密度をプロット"""
    plt.figure(figsize=(10, 6))
    plt.loglog(freqs, psd, label="PSD")
    plt.loglog(freqs, 1/freqs**alpha, label=f"Fit with alpha = {alpha:.2f}")
    plt.xlabel('Frequency')
    plt.ylabel('PSD')
    plt.legend()
    plt.show()

# 画像の読み込み
image_path = 'path_to_your_image.jpg'  # 画像パスを指定
image_path = "../experiment_images/101_1/1_3_brightness23.072_gamma1.092_sharpness0.325.jpg"
image = load_image(image_path)

# 2D フーリエ変換とパワースペクトル密度の計算
psd2d = calculate_psd2d(image)
freqs = np.fft.fftfreq(image.shape[0])

# パワースペクトル密度を1次元に変換
psd1d = psd2d.mean(axis=0)

# 1/f^αにフィットさせてαを求める
alpha = fit_power_law(freqs, psd1d)

# 結果のプロット
plot_psd(freqs, psd1d, alpha)

print(f"Estimated alpha: {alpha}")

# # -*- coding: utf-8 -*-
# import numpy as np
# import matplotlib.pyplot as plt

# # データのパラメータ
# N = 256            # サンプル数
# dt = 0.01          # サンプリング間隔
# f1, f2 = 10, 20    # 周波数
# t = np.arange(0, N*dt, dt)  # 時間軸
# freq = np.linspace(0, 1.0/dt, N)  # 周波数軸

# # 信号を生成（周波数10の正弦波+周波数20の正弦波+ランダムノイズ）
# f = np.sin(2*np.pi*f1*t) + np.sin(2*np.pi*f2*t) + 0.3 * np.random.randn(N)

# # 高速フーリエ変換
# F = np.fft.fft(f)

# # 振幅スペクトルを計算
# Amp = np.abs(F)

# # パワースペクトルの計算（振幅スペクトルの二乗）
# Pow = Amp ** 2

# # グラフ表示
# plt.figure()
# plt.rcParams['font.family'] = 'Times New Roman'
# plt.rcParams['font.size'] = 17
# plt.subplot(121)
# plt.plot(t, f, label='f(n)')
# plt.xlabel("Time", fontsize=20)
# plt.ylabel("Signal", fontsize=20)
# plt.grid()
# leg = plt.legend(loc=1, fontsize=25)
# leg.get_frame().set_alpha(1)
# plt.subplot(122)
# plt.plot(freq, Pow, label='|F(k)|')
# plt.xlabel('Frequency', fontsize=20)
# plt.ylabel('Amplitude', fontsize=20)
# plt.grid()
# leg = plt.legend(loc=1, fontsize=25)
# leg.get_frame().set_alpha(1)
# plt.show()