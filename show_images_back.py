
import os
import time
from PIL import Image
import matplotlib.pyplot as plt

def display_images(folder_path, delay):
    # フォルダ内のファイル名を取得し、アルファベット順にソート
    image_files = sorted(os.listdir(folder_path))

    # 画像表示のためのfigureとaxesを生成
    fig, ax = plt.subplots()
    for image_file in image_files:
        # ファイルが画像であることを確認
        if image_file.lower().endswith(('.png', '.jpg', '.jpeg')):
            image_path = os.path.join(folder_path, image_file)
            img = Image.open(image_path)

            # 画像を表示
            ax.imshow(img)
            plt.axis('off')  # 軸の非表示

            # 画像のタイトルをファイル名にする
            plt.title("")
            
            # 画像を表示
            plt.pause(delay)  # ここで一時停止すると、図が表示されます

            # クリアー画像
            ax.cla()

    plt.close()

# 使用例
display_images('experiment_images/',2.5)