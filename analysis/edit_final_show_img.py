# final_recent_dark_add_entropy.xlsxの任意の列を昇順または降順にして、image_pathを参照して画像を表示する

#必要なライブラリのインポート
import pandas as pd
import cv2
import matplotlib.pyplot as plt
import numpy as np
import glob
import os
from tqdm import tqdm
from PIL import Image
import matplotlib.pyplot as plt
import pandas as pd
from PIL import Image
import os


# ユーザー入力を受け取るための関数
def get_user_input():
    try:
        min_value = float(input("最小値を入力してください: "))
        max_value = float(input("最大値を入力してください: "))
        return min_value, max_value
    except ValueError:
        print("数値を入力してください。")
        return None, None


# 一度に表示する画像の枚数をユーザー入力で設定するための関数
def get_number_of_images_to_display():
    try:
        num_images = int(input("一度に表示する画像の枚数(5の倍数): "))
        return num_images
    except ValueError:
        print("整数を入力してください。")
        return 20  # デフォルト値

# 画像とラベルを表示する関数（更新版）
# def display_images_with_labels_and_title(image_paths, labels, colors, num_images_per_display):
#     total_displays = len(image_paths) // num_images_per_display + int(len(image_paths) % num_images_per_display != 0)
    
#     # 20枚ごとに画像を表示
#     for i in range(0, len(image_paths), num_images_per_display):
#         current_display = i // num_images_per_display + 1
#         plt.figure(figsize=(10, 20))  # 図のサイズを設定
#         plt.suptitle(f"{current_display}/{total_displays}")  # タイトルを設定

#         for j, (path, label, color) in enumerate(zip(image_paths[i:i + num_images_per_display], labels[i:i + num_images_per_display], colors[i:i + num_images_per_display])):
#             if os.path.exists(path):
#                 img = Image.open(path)
#                 plt.subplot(int(num_images_per_display/5), 5, j + 1)  # 縦に画像を並べる
#                 plt.imshow(img)
#                 label = round(label, 3)
#                 plt.text(10, 10, str(label), color=color, fontsize=12, ha='left', va='top',
#                          bbox=dict(facecolor='white', alpha=0.5))
#                 plt.axis('off')
                
#             else:
#                 plt.subplot(num_images_per_display, 1, j + 1)
#                 plt.text(0.5, 0.5, 'Image not found', ha='center', va='center')
#                 plt.axis('off')
#         plt.show()


import os
import matplotlib.pyplot as plt
from PIL import Image

def display_images_with_labels_and_title(image_paths, labels, colors, hists, num_images_per_display):
    total_displays = len(image_paths) // num_images_per_display + int(len(image_paths) % num_images_per_display != 0)
    
    for i in range(0, len(image_paths), num_images_per_display):
        current_display = i // num_images_per_display + 1
        plt.figure(figsize=(20, 20))  # 図のサイズを設定
        plt.suptitle(f"{current_display}/{total_displays}")  # タイトルを設定

        display_images = image_paths[i:i + num_images_per_display]
        display_labels = labels[i:i + num_images_per_display]
        display_colors = colors[i:i + num_images_per_display]
        display_hists = hists[i:i + num_images_per_display]

        for j, (path, label, color, hist) in enumerate(zip(display_images, display_labels, display_colors, display_hists)):
            if os.path.exists(path):
                img = Image.open(path)
                plt.subplot(int(num_images_per_display/5), 10, j*2 + 1)  # 画像を表示するサブプロット
                plt.imshow(img)
                label = round(label, 3)
                plt.text(10, 10, str(label), color=color, fontsize=12, ha='left', va='top',
                         bbox=dict(facecolor='black', alpha=0.5))
                plt.axis('off')

                plt.subplot(int(num_images_per_display/5), 10, j*2 + 2)  # ヒストグラムを表示するサブプロット
                # for channel, color in zip(hist, ['r', 'g', 'b']):
                #     plt.plot(channel, color=color)

                plt.hist(hist, color=["red", "green", "blue"], bins=128)
                plt.axis('on')
            else:
                plt.subplot(int(num_images_per_display/5), 10, j*2 + 1)
                plt.text(0.5, 0.5, 'Image not found', ha='center', va='center')
                plt.axis('off')

        plt.show()

# この関数を呼び出す
# display_images_with_labels_and_title(image_paths, labels, colors, hists, num_images_per_display)


# データフレームのフィルタリングと画像表示を行う関数
def display_filtered_images(df, column):
    min_value, max_value = get_user_input()
    num_images_per_display = get_number_of_images_to_display()

    if min_value is not None and max_value is not None:
        # データフレームを指定された範囲でフィルタリング
        filtered_df = df[(df[column] >= min_value) & (df[column] <= max_value)]
        image_paths = filtered_df['image_path'].tolist()
        labels = filtered_df[column].tolist()
        colors = filtered_df['isred'].tolist()
        
        # ヒストグラムを計算
        hists = []
        for image_path in image_paths:
            img = Image.open(image_path)
            hist = np.asarray(img.convert("RGB")).reshape(-1, 3)
            hists.append(hist)

        # フィルタリングされた画像とラベルを表示
        display_images_with_labels_and_title(image_paths, labels, colors,hists, num_images_per_display)
    else:
        print("入力が正しくありません。")



# サンプルのデータフレームを読み込みます
df = pd.read_excel("../data/final_recent_dark/final_recent_dark_add_entropy.xlsx")
df = df.sort_values("entropy_gray", ascending=False)
df = df[df["isred"] == "red"]


df["figure"] = df["figure"].astype(str)
df = df.sort_values("figure", ascending=True)
# df = df[df["figure"] == "B"]



image_paths = df['image_path'].tolist()
entropy_gray = df['entropy_gray'].tolist()
display_filtered_images(df, 'entropy_gray')


