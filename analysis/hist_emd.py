
from scipy.stats import wasserstein_distance
import numpy as np
from PIL import Image
import matplotlib.pyplot as plt
import os
import glob
import pandas as pd
# from scipy.stats import wasserstein_distance
# import pandas as pd
# import numpy as np
# from PIL import Image
# import matplotlib.pyplot as plt
# import os


def show_histograms(df):
    # 画像のパスを取得
    image_path = df['image_path'].tolist()
    fgure_list = df['figure'].tolist()

    hist_list = []
    # 画像を読み込み、ヒストグラムを表示
    for path in image_path:
        if os.path.exists(path):
            img = Image.open(path)
            img = img.resize((1920, 1080))
            # plt.imshow(img)
            # plt.show()
            # hist = np.asarray(img.convert("RGB")).reshape(-1, 3)
            hist = np.asarray(img.convert("L"))
            hist_list.append(hist)
        #     plt.hist(hist, color=["red", "green", "blue"], bins=128)
        #     plt.show()
            
        else:
            print("画像が見つかりません。")
    return hist_list, fgure_list


# #image_pathsを引数にして、画像のヒストグラムを計算する関数


df = pd.read_excel("../data/final_recent_dark/final_recent_dark_add_entropy.xlsx")
df = df[df["isred"]=="red"]


hist_list,figure_list = show_histograms(df)





# # Earth Mover's Distance (EMD)を計算します
# for i in range(len(hist_list)):
#     for j in range(len(hist_list)):
#         hist1 = hist_list[i]
#         hist2 = hist_list[j]
#         emd = wasserstein_distance(hist1, hist2)
#         #hist1とhist2を表示
#         plt.subplot(1, 2, 1)
#         plt.imshow(hist1)
#         plt.subplot(1, 2, 2)
#         plt.imshow(hist2)
#         plt.text(10, 10, str(emd), color="white", fontsize=12, ha='left', va='top',
#                  bbox=dict(facecolor='black', alpha=0.5))
#         print("Earth Mover's Distance (EMD):", emd)
#         print("figure1:",figure_list[i])



def compute_histogram(image):
    # グレースケール画像のヒストグラムを計算
    histogram, _ = np.histogram(image, bins=256, range=(0, 256))
    return histogram

# Earth Mover's Distance (EMD) を計算
for i in range(len(hist_list)):
    for j in range(i + 1, len(hist_list)):  # 重複を避けるため j は i + 1 から始める
        img1 = hist_list[i]
        img2 = hist_list[j]

        hist1 = compute_histogram(img1)
        hist2 = compute_histogram(img2)

        emd = wasserstein_distance(hist1, hist2)

        # hist1 と hist2 のヒストグラムを表示
        plt.figure(figsize=(12, 6))
        plt.subplot(1, 2, 1)
        plt.imshow(img1, cmap='gray')
        plt.title(f"Image {i}")

        plt.subplot(1, 2, 2)
        plt.imshow(img2, cmap='gray')
        plt.title(f"Image {j}")

        plt.suptitle(f"Earth Mover's Distance (EMD): {emd:.2f}")
        plt.show()

        print("Earth Mover's Distance (EMD):", emd)
        print("Image:", figure_list[i], "vs", figure_list[j])
