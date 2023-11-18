
import pandas as pd
import matplotlib.pyplot as plt
from itertools import combinations

df = pd.read_excel("../data/final_part2/add_contrast.xlsx")
df = df[df["hist_bright"] < 40]

# 判定する基準のカラム
criteria_columns = ['gamma', 'brightness', 'contrast', 'sharpness', 'equalization']

# 5つのパラメータから3つを選ぶすべての組み合わせを生成
combinations_of_criteria = list(combinations(criteria_columns, 3))

# 各組み合わせに対してフィルタリングを行う
for combination in combinations_of_criteria:
    print(combination)
    # 組み合わせの中で、3つの基準すべてが0でない行をフィルタリング
    filtered_df = df[(df[list(combination)] != 0).all(axis=1)]

    # 散布図のプロット
    plt.scatter(filtered_df["brightness_ratio"], filtered_df["diopter"])
    plt.xlabel("brightness_ratio")
    plt.ylabel("diopter")
    plt.title(f"Combination: {combination}")
    plt.show()

