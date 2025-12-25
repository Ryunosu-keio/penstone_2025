from PIL import Image
import numpy as np
import matplotlib.pyplot as plt
import glob

def load_image(image_path):
    # 画像をグレースケールで読み込み
    image = Image.open(image_path).convert('L')
    return np.array(image)

def fourier_transform(image_array):
    # 2次元フーリエ変換
    f_transform = np.fft.fft2(image_array)
    # ゼロ周波数成分を中央にシフト
    f_shift = np.fft.fftshift(f_transform)
    # スペクトルの対数スケールを取得
    magnitude_spectrum = 20 * np.log(np.abs(f_shift))
    return magnitude_spectrum

def plot_spectrum(magnitude_spectrum, title):
    plt.imshow(magnitude_spectrum, cmap='gray')
    plt.title(title)
    plt.colorbar()
    plt.show()

# 画像のパスを取得
image_paths = glob.glob("../pictures/transformed/roomDark_figureBright/*")  # 画像ファイルへのパス
# image_pathsの長さに基づいて、matplotlibで表示するための行列の大きさを決定
nrows = 3
ncols = 3
fig, axes = plt.subplots(nrows, ncols, figsize=(ncols * 5, nrows * 5))
axes = axes.ravel()  # axes配列を1次元に変換

# 各画像に対してフーリエ変換を実行し、結果をプロット
for idx, path in enumerate(image_paths):
    image_array = load_image(path)
    magnitude_spectrum = fourier_transform(image_array)

    # 対応するサブプロットに画像を表示
    ax = axes[idx]
    ax.imshow(magnitude_spectrum, cmap='gray')
    ax.set_title(f"Magnitude Spectrum of {path.split('/')[-1]}")
    ax.axis('off')  # 軸の表示をオフにする

plt.tight_layout()
plt.show()
