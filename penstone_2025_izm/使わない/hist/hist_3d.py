from mpl_toolkits.mplot3d import Axes3D
import matplotlib.pyplot as plt
import numpy as np
from PIL import Image

# 画像を読み込んでNumPy配列に変換
img1 = Image.open("../histogram/redpic_dark/スクリーンショット 2023-12-13 224354.png")
img_array = np.array(img1)

# 画像データを2次元配列に変換（ピクセル x RGB）
img_reshaped = img_array.reshape(-1, img_array.shape[2])

# 3Dヒストグラムの計算
# RGBの各チャンネルについて100ビンを使用
hist, edges = np.histogramdd(img_reshaped, bins=(100, 100, 100))

# 3Dヒストグラムのプロット
fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')

# ヒストグラムデータをプロットに適した形に変換
xpos, ypos, zpos = np.indices(np.array(hist.shape) + 1).reshape(3, -1)[:-1, :]
xpos = edges[0][xpos]
ypos = edges[1][ypos]
zpos = edges[2][zpos]

# ヒストグラムのビンの大きさ
dx = dy = dz = np.ones_like(zpos)

# ヒストグラムのビンの値
values = hist.ravel()

# 3Dヒストグラムをプロット
ax.bar3d(xpos, ypos, zpos, dx, dy, dz, values)
plt.show()
