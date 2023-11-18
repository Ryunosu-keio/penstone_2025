#%%
import pandas as pd
import matplotlib.pyplot as plt

df = pd.read_excel("updated_dataframe.xlsx")
filtered_df = df[df["hist_bright"] > 50]

plt.scatter(filtered_df["hist_bright"],filtered_df["diopter"])
plt.xlabel("hist_bright")
plt.ylabel("diopter")
plt.title("Scatter Plot of hist_bright vs diopter")
plt.show()


#%%
import pandas as pd
import matplotlib.pyplot as plt
from PIL import Image
import numpy as np



def color_hist(filename):
    img = np.asarray(Image.open(filename).convert("RGB")).reshape(-1,3)
    plt.hist(img, color=["red", "green", "blue"], bins=128)
    plt.show()

df = pd.read_excel("updated_dataframe.xlsx")
filtered_df = df[df["hist_bright"] > 50]

for index, row in filtered_df.iterrows():
    image_path = row["image_path"]
    try:
        # 画像の読み込み
        image = Image.open(image_path)

        # 画像の表示
        plt.imshow(image)
        plt.axis("off")
        plt.show()

        color_hist(image_path)

        # 対応する数値の出力
        # 実際の列名に合わせて "a", "b", "c" を置き換える
        print(f"diopter: {row['diopter']}")
        print(f"hist_bright: {row['hist_bright']}")
        print(f"gamma:{row['gamma']}")
        print(f"contrast:{row['contrast']}")
        print(f"sharpness:{row['sharpness']}")
        print(f"brightness:{row['brightness']}")
        print(f"equalization:{row['equalization']}")
    except FileNotFoundError:
            print(f"ファイルが見つかりません: {image_path}")
    except KeyError as e:
        print(f"列が存在しません: {e}")
# %%
