import matplotlib.pyplot as plt
from PIL import Image
import numpy as np
import matplotlib.colors as colors
import glob


# image_path = glob.glob("../pictures/transformed/roomDark_figureBright/*.jpg")[0]
# def plot_hsv_histogram(image_path):
#     # 画像を読み込む
#     img = Image.open(image_path)
#     rgb_data = np.array(img)

#     # RGBからHSVに変換
#     hsv_data = colors.rgb_to_hsv(rgb_data / 255.0)

#     # HSVヒストグラムをプロット
#     fig, axes = plt.subplots(1, 3, figsize=(15, 5))
#     labels = ['Hue', 'Saturation', 'Value']
#     for i in range(3):
#         axes[i].hist(hsv_data[:, :, i].flatten(), bins=256, range=(0, 1))
#         axes[i].set_title(labels[i])

#     plt.tight_layout()
#     plt.show()

# plot_hsv_histogram(image_path)import matplotlib.pyplot as plt
import matplotlib.pyplot as plt
import numpy as np
from PIL import Image
import matplotlib.colors as colors
import pandas as pd
import glob

def plot_hsv_histograms_for_images(csv_list):
    nrows = 7
    ncols = 8

    fig, axes = plt.subplots(nrows=nrows, ncols=ncols, figsize=(ncols * 5, nrows * 5))

    for i, csv_path in enumerate(csv_list):
        # CSVファイルから画像名を読み込む
        df = pd.read_csv(csv_path)

        # dfの長さを確認し、iが範囲内にあるか確認
        if i < len(df):
            image_name = df["image_name"].iloc[i]
            image_path = glob.glob("../experiment_images/*/" + image_name)[0]

            img = Image.open(image_path)
            rgb_data = np.array(img)

            hsv_data = colors.rgb_to_hsv(rgb_data / 255.0)

            row_index = i % nrows
            col_index_base = 0 if i < len(csv_list) / 2 else 4

            ax_img = axes[row_index, col_index_base]
            ax_img.imshow(img)
            ax_img.axis('off')

            labels = ['Hue', 'Saturation', 'Value']
            for j in range(3):
                ax_hist = axes[row_index, col_index_base + j + 1]
                ax_hist.hist(hsv_data[:, :, j].flatten(), bins=256, range=(0, 1))
                ax_hist.set_title(labels[j])

    plt.tight_layout()
    plt.show()

csv_list = glob.glob
