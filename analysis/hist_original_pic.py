import matplotlib.pyplot as plt
from PIL import Image
import numpy as np
import glob

from edit_final_add_features import calculate_entropy_gray


# 画像ファイルパスのリスト
image_paths = glob.glob("../pictures/transformed/roomDark_figureBright/*.jpg")

# 画像の数に合わせてサブプロットを作成
nrows = 7  # 各行に2つのペア（画像とヒストグラム）が配置される
ncols = 4 # 合計14枚の画像と14枚のヒストグラム
fig, axes = plt.subplots(nrows, ncols, figsize=(20, 10))

# 画像とヒストグラムを配置
for i in range(len(image_paths)):
    col_index_img = (i // nrows) * 2
    col_index_hist = col_index_img + 1

    # 画像を表示
    ax_img = axes[i % nrows, col_index_img]
    img = Image.open(image_paths[i])
    ax_img.imshow(img)
    ax_img.axis('off')  # 軸は非表示に

    # ヒストグラムを表示
    ax_hist = axes[i % nrows, col_index_hist]
    hist = np.asarray(img.convert("RGB")).reshape(-1, 3)
    ax_hist.hist(hist, bins=256, range=(0, 255), color=["red", "green", "blue"])
    ax_hist.axis('on')  # ヒストグラムの軸は表示

    entropy = calculate_entropy_gray(image_paths[i])
   
    entropy = round(entropy, 3)
    #entropyを画像の左上に表示
    ax_img.text(10, 10, str(entropy), color="white", fontsize=12, ha='left', va='top',
                 bbox=dict(facecolor='black', alpha=0.5))
    
    

# プロットを表示
plt.tight_layout()
# 表示したプロットを保存
# plt.savefig("../histogram/hist_original.pdf")
plt.show()
