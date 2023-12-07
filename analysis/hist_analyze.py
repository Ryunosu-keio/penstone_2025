#%%
import pandas as pd
from PIL import Image
import matplotlib.pyplot as plt
import numpy as np
import glob


bool = int(input("diopter小さいなら1,大きいなら2"))
if bool == 1:
    bool = True
    print("diopterいい画像")
elif bool ==2 :
    bool = False
    print("diopter悪い画像")

directory = int(input("明所なら1,暗所なら2"))
if directory == 1 :
    df = pd.read_excel("../data/final_part1/final_bright_add_modified.xlsx")
if directory == 2 :
      df = pd.read_excel("../data/final_part2/darkfinal_modified.xlsx")
    
df = df.sort_values(by="diopter",ascending = bool)

image_name = df["image_name"]
# image_path = f"../experiment_images/*/{image_name}"ばかめ
image_path = glob.glob("../experiment_images/*/*")


img_list = []
hist_list = []
# for i,image_name in df["image_name"]:
n= int(input("diopter上位何個見たいですか: "))
for i, image_name in enumerate(df["image_name"].head(n)):
    image_path = glob.glob("../experiment_images/*/" + image_name)[0]
    img = Image.open(image_path)
    img_list.append(img)
    # color_hist(image_path)ばかめ
    hist = np.asarray(Image.open(image_path).convert("RGB")).reshape(-1,3)
    hist_list.append(hist)

# 画像とヒストグラムを表示するためのサブプロットを作成
# plt.figure(figsize=(15, 6))  # 図のサイズは必要に応じて調整してください

for i in range(len(img_list)):
    print(str(i)+"枚目")
    # 画像を表示
    # plt.subplot(2, n, i + 1)  # 2行5列のサブプロットの上の行
    plt.figure(figsize=(15, 6))
    plt.subplot(1,2,1)
    plt.imshow(img_list[i])
    plt.axis('off')  # 軸を非表示にする

    # ヒストグラムを表示
    # plt.subplot(2, n, i+n+1)  # 2行5列のサブプロットの下の行
    plt.subplot(1,2,2)
    plt.hist(hist_list[i], color=["red", "green", "blue"], bins=128)
    plt.xlim(0, 255)

    plt.show()

# import math

# # img_listの長さに基づいて必要な行数を計算
# rows = math.ceil(len(img_list) / 5) * 2  # 2倍するのは画像とヒストグラムのため

# plt.figure(figsize=(25, 4 * rows))  # 図のサイズを調整

# for i in range(len(img_list)):
#     # 画像を表示
#     plt.subplot(rows, 5, i + 1)  # rows行5列のサブプロット
#     plt.imshow(img_list[i])
#     plt.axis('off')  # 軸を非表示にする

#     # ヒストグラムを表示
#     plt.subplot(rows, 5, i + 6)  # rows行5列のサブプロット、次の行
#     plt.hist(hist_list[i], color=["red", "green", "blue"], bins=128)
#     plt.xlim(0, 255)

# plt.show()

# %%
