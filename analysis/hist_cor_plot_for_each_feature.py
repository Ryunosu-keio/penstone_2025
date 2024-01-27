import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import os



def plot_cor_for_each_feature(df, y_feature, feature_list, bright_or_dark="bright"):
    # 相関係数を計算
    for feature in feature_list:
        correlation = df[y_feature].corr(df[feature])
        print(f"{feature} : {correlation:.2f}")
        correlation = df[y_feature].corr(df[feature])

        # 散布図の作成
        
        plt.figure(figsize=(10, 6))
        # for color in ['red', 'blue']:
        #     subset = df[df['isred'] == color]
        #     plt.scatter(subset[feature], subset[y_feature], color=color, marker='o', label=f'color = {color}')
        # 青の点だけ先にプロット
        plt.scatter(df[df['isred'] == 'blue'][feature], df[df['isred'] == 'blue'][y_feature], color='blue', marker='o', label='color = blue')
        # 赤の点をzorderを使って青の点より上にプロット
        plt.scatter(df[df['isred'] == 'red'][feature], df[df['isred'] == 'red'][y_feature], color='red', marker='o', label='color = red', zorder=2)

        plt.xlabel(feature)
        plt.ylabel(y_feature)
        plt.title(f'Scatter Plot of {y_feature} vs Image Feature')
        plt.legend()

        # 相関係数を左上に表示
        # plt.text(0.1 * plt.xlim()[1], 0.9 * plt.ylim()[1], f'Correlation: {correlation:.2f}', fontsize=12)
        #相関係数を四角形で囲って凡例の下に表示
        plt.text(0.1*plt.xlim()[1], 0.9* plt.ylim()[1], f'Correlation: r= {correlation:.2f}', fontsize=12, bbox=dict(facecolor='white', alpha=0.5))   
        # os make directory
        # os.makedirs("../scatter_plot", exist_ok=True)
        # plt.savefig(f"../scatter_plot/{feature}.png")
        # plt.show()
        #画像をx_titlesの名前に合わせて保存
        # scatter_plotに保存
        os.makedirs(f"../scatter_plot/{bright_or_dark}", exist_ok=True)
        # plt.savefig(f"../scatter_plot/{bright_or_dark}/{feature}.png")
        save = input("save?(y/n)")
        if save == "y":
            plt.savefig(f"../scatter_plot/{bright_or_dark}/{feature}.png")
            print("saved")
        elif save == "n":
            print("not saved")
        


# y = df_merged["diopter"]
# feature_list = ["gamma","contrast", "sharpness", "brightness", "equalization", "contrast_sensitivity",
#                 "digit_brightness", "non_digit_brightness", "brightness_ratio",
#                "contrast_value", "contrast_sensitivity",
#                "r_kurtosis", "g_kurtosis", "b_kurtosis", "gray_kurtosis",
#                "r_skewness", "g_skewness", "b_skewness", "gray_skewness",
#                "r_max_brightness", "g_max_brightness", "b_max_brightness", "gray_max_brightness",
#                "max_index", "mode_index", "hist_contrast",
#                "contrast_variation_coefficient", "squared_mean_contrast"]

feature_list = [
                "digit_brightness", "non_digit_brightness", "brightness_ratio",
               "contrast_value", "contrast_sensitivity",
               "r_max_brightness", "g_max_brightness", "b_max_brightness", "gray_max_brightness",
               "max_index", "mode_index", "hist_contrast",
               "contrast_variation_coefficient", "squared_mean_contrast"]


brightness_list = ["digit_brightness", "non_digit_brightness", "brightness_ratio"]
w3c_list = ["brightness_w3c", "colorness_w3c"]
skewness_kurtosis_list = ["r_kurtosis", "g_kurtosis", "b_kurtosis", "gray_kurtosis","r_skewness", "g_skewness", "b_skewness", "gray_skewness"]
skewness2_list =["gray_skewness2"]
max_list = ["r_max_brightness", "g_max_brightness", "b_max_brightness", "gray_max_brightness"]
contrast_list = ["contrast_value", "contrast_sensitivity", "hist_contrast", "contrast_variation_coefficient", "squared_mean_contrast"]
entropy_list = ["entropy_gray", "entropy_rgb"]
fft_list = ["avg_diff", "max_diff", "avg_diff_low_freq", "avg_diff_high_freq"]
button_list = ["timeFromDisplay_std"]



# df = df[df["isred"] == "red"]
#異なるdiff_listの中のdfの列の差をとって新しい列を作る
# for i in range(len(diff_list)):
#     for j in range(i+1, len(diff_list)):
#         df[f"{diff_list[i]}-{diff_list[j]}"] = df[diff_list[i]]-df[diff_list[j]]
#         # df[f"abs_{diff_list[i]}_{diff_list[j]}"] = df[diff_list[i]]-df[diff_list[j]]


# if __name__ == '__main__':
#     for i in range(len(diff_list)):
#         for j in range(i+1, len(diff_list)):
#             # plot_cor_for_each_feature(df, y_feature="diopter", feature_list=[f"{diff_list[i]}-{diff_list[j]}"])
#             plot_cor_for_each_feature(df, y_feature="diopter", feature_list=diff_list)    

# df["freq_ratio"] = df["avg_diff_low_freq"]/df["avg_diff_high_freq"]


# num_list = df["num"].unique().tolist()
# #num_listを昇順にする
# num_list.sort()
# print(num_list)

# for num in num_list:
#     df_num = df[df["num"] == num]
#     print(num)
#     plot_cor_for_each_feature(df_num, y_feature="diopter", feature_list=diff_list)



df = pd.read_excel("../data/final_recent_bright/final_recent_bright_add_entropy_skewgray_michaelson_sf.xlsx")
# df = pd.read_excel("../data/final_recent_dark/final_recent_dark_add_entropy_fft.xlsx")

plot_cor_for_each_feature(df, y_feature="diopter", feature_list=["sharpness_factor"], bright_or_dark="bright")
