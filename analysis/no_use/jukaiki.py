import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import glob
import os

def load_and_prepare_grid_data(path_pattern):
    df_paths = glob.glob(path_pattern)
    df_list = [pd.read_csv(df_path).dropna() for df_path in df_paths]
    df_grid = pd.concat(df_list, ignore_index=True).drop_duplicates(subset='image_name')
    return df_grid[['image_name']]  # ここでは、'image_name' 列のみを保持する

def merge_data(df_grid, df_main, key='image_name'):
    df_merged = pd.merge(df_grid, df_main, on=key, how='left')
    df_merged.drop_duplicates(subset=key, inplace=True)
    return df_merged

# def plot_correlations(xs, y, x_names):
#     corr = x.corrwith(y)
#     print(corr)
#     # for i in range(len(x.columns)):
#     #     plt.scatter(x.iloc[:, i], y)
#     #     plt.xlabel(x.columns[i])
#     #     plt.ylabel("diopter")
#     #     plt.show()
#     # 1×len(x.columns)のサブプロットで一度に表示
#     fig, axes = plt.subplots(1, len(x.columns), figsize=(20, 5))
#     for i in range(len(x.columns)):
#         axes[i].scatter(x.iloc[:, i], y)
#         axes[i].set_xlabel(x.columns[i])
#         axes[i].set_ylabel("diopter")
#         #相関係数を表示
#         axes[i].text(0.05, 0.9, f"r={corr[i]:.2f}", transform=axes[i].transAxes)
#         # タイトルとしてx_names[i] を表示
#         axes[i].set_title(x_names[i])
#     plt.show()
        
def plot_correlations(xs, y, x_titles):
    for x in xs:
        print(x)
        type(x)
        # xとyの相関係数を計算
        corr = x.corrwith(y)
        print(corr)

        # 1×len(x.columns)のサブプロットで一度に表示
        fig, axes = plt.subplots(1, len(x.columns), figsize=(18, 5))
        for i in range(len(x.columns)):
            axes[i].scatter(x.iloc[:, i], y)
            axes[i].set_xlabel(x.columns[i])
            axes[i].set_ylabel("diopter")
            #相関係数を表示
            axes[i].text(0.05, 0.9, f"r={corr[i]:.2f}", transform=axes[i].transAxes)
            # サブプロット全体のタイトルとしてx_names[i] を表示
            # fig.suptitle(x_titles[i])
        plt.show()

            



# メインのデータフレームを読み込む
df_main = pd.read_excel("../data/final_recent_dark/final_recent_dark.xlsx")

# Gridデータを読み込み、準備する
df_grid = load_and_prepare_grid_data("../histogram/red_grids/*.csv")
# df_grid = load_and_prepare_grid_data("../histogram/red_grids_dark/*.csv")
print("df_grid", df_grid)

# データをマージする
df_merged = merge_data(df_grid, df_main)
print("df_merged", df_merged)


# df_merged = pd.read_excel("../data/final_partw/final_dark_add_contrast_sensitivity_features.xlsx")

# # df_merged = df_merged[(df_merged[['param1', 'param2', 'param3']].isin(['contrast', 'sharpness', 'equalization'])).all(axis=1)]
# # df_merged = df_merged[(df_merged[['param1', 'param2', 'param3']].isin(['gamma', 'sharpness', 'equalization'])).all(axis=1)]
# df_merged = df_merged[(df_merged[['param1', 'param2', 'param3']].isin(['gamma', 'contrast', 'sharpness'])).all(axis=1)]

# df_merged = df_merged[df_merged["max_index"] != 245]

# yとXの定義（'diopter' 列が存在することが前提）
y = df_merged["diopter"]
x = df_merged[["gamma","contrast", "sharpness", "brightness", "equalization", "contrast_sensitivity",
                "digit_brightness", "non_digit_brightness", "brightness_ratio",
               "contrast_value", "contrast_sensitivity",
               "r_kurtosis", "g_kurtosis", "b_kurtosis", "gray_kurtosis",
               "r_skewness", "g_skewness", "b_skewness", "gray_skewness",
               "r_max_brightness", "g_max_brightness", "b_max_brightness", "gray_max_brightness",
               "max_index", "mode_index", "hist_contrast",
               "contrast_variation_coefficient", "squared_mean_contrast"]]


x_param = df_merged[["gamma", "contrast", "sharpness", "brightness", "equalization"]]
x_brightness = df_merged[["digit_brightness", "non_digit_brightness", "brightness_ratio"]]
x_contrast_coefficients = df_merged[["contrast_variation_coefficient", "squared_mean_contrast","contrast_value", "contrast_sensitivity"]]
x_kurtosis = df_merged[["r_kurtosis", "g_kurtosis", "b_kurtosis", "gray_kurtosis"]]
x_skewness = df_merged[["r_skewness", "g_skewness", "b_skewness", "gray_skewness"]]
x_max_brightness = df_merged[["r_max_brightness", "g_max_brightness", "b_max_brightness", "gray_max_brightness"]]
x_index = df_merged[["max_index", "mode_index"]]
x_w3c = df_merged[["brightness_w3c", "colorness_w3c"]]
# x_hist = df_merged[["hist_contrast"]]
# x_hist = df_merged["hist_contrast"] = df_merged["max_index"] / df_merged["mode_index"]

xs = [x_param, x_brightness, x_contrast_coefficients, x_kurtosis, x_skewness, x_max_brightness, x_index, x_w3c]
x_titles = ["param", "brightness", "contrast_coefficients", "kurtosis", "skewness", "max_brightness", "index", "w3c"]

for x, x_title in zip(xs, x_titles):
    print(x_title)
    plot_correlations(xs, y, x_titles)
    #画像をx_titlesの名前に合わせて保存
    #保存先ディレクトリをつくる
    # os.makedirs(f"../histogram/correlations/bright_bad/{x_title}", exist_ok=True)
    # plt.savefig(f"../histogram/correlations/bright_bad/{x_title}/{x_title}.png")
    # print("saved")
# 相関をプロットする
# plot_correlations(x_only, y)
