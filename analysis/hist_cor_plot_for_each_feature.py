import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import os



def plot_cor_for_each_feature(df, y_feature, feature_list):
    # 相関係数を計算
    for feature in feature_list:
        correlation = df[y_feature].corr(df[feature])
        print(f"{feature} : {correlation:.2f}")
        correlation = df[y_feature].corr(df[feature])

        # 散布図の作成
        
        plt.figure(figsize=(10, 6))
        for color in ['red', 'blue']:
            subset = df[df['isred'] == color]
            plt.scatter(subset[feature], subset[y_feature], color=color, marker='o', label=f'color = {color}')
        plt.xlabel(feature)
        plt.ylabel(y_feature)
        plt.title(f'Scatter Plot of {y_feature} vs Image Feature')
        plt.legend()

        # 相関係数を左上に表示
        # plt.text(0.1 * plt.xlim()[1], 0.9 * plt.ylim()[1], f'Correlation: {correlation:.2f}', fontsize=12)
        #相関係数を四角形で囲って凡例の下に表示
        plt.text(0.75*plt.xlim()[1], 0.9* plt.ylim()[1], f'Correlation: r= {correlation:.2f}', fontsize=12, bbox=dict(facecolor='white', alpha=0.5))   
        # os make directory
        # os.makedirs("../scatter_plot", exist_ok=True)
        # plt.savefig(f"../scatter_plot/{feature}.png")
        plt.show()
        #画像をx_titlesの名前に合わせて保存
        #scatter_plotに保存
        # os.makedirs(f"../scatter_plot/{feature}", exist_ok=True)
        # plt.savefig(f"../scatter_plot/{feature}/{feature}.png")
        


# y = df_merged["diopter"]
# feature_list = ["gamma","contrast", "sharpness", "brightness", "equalization", "contrast_sensitivity",
#                 "digit_brightness", "non_digit_brightness", "brightness_ratio",
#                "contrast_value", "contrast_sensitivity",
#                "r_kurtosis", "g_kurtosis", "b_kurtosis", "gray_kurtosis",
#                "r_skewness", "g_skewness", "b_skewness", "gray_skewness",
#                "r_max_brightness", "g_max_brightness", "b_max_brightness", "gray_max_brightness",
#                "max_index", "mode_index", "hist_contrast",
#                "contrast_variation_coefficient", "squared_mean_contrast"]

# feature_list = [
#                 "digit_brightness", "non_digit_brightness", "brightness_ratio",
#                "contrast_value", "contrast_sensitivity",
#                "r_max_brightness", "g_max_brightness", "b_max_brightness", "gray_max_brightness",
#                "max_index", "mode_index", "hist_contrast",
#                "contrast_variation_coefficient", "squared_mean_contrast", "brightness_w3c", "colorness_w3c", "entropy_gray", "entropy_rgb"]

# feature_list = ["entropy_gray", "entropy_rgb"]

df = pd.read_excel("../data/final_recent_dark/final_recent_dark_add_entropy.xlsx")

if __name__ == '__main__':
    plot_cor_for_each_feature(df, y_feature="entropy_gray", feature_list=["gamma", "contrast", "sharpness", "brightness", "equalization", "contrast_sensitivity", "digit_brightness", "non_digit_brightness", "brightness_ratio", "contrast_value", "contrast_sensitivity", "r_kurtosis", "g_kurtosis", "b_kurtosis", "gray_kurtosis", "r_skewness", "g_skewness", "b_skewness", "gray_skewness", "r_max_brightness", "g_max_brightness", "b_max_brightness", "gray_max_brightness", "max_index", "mode_index", "hist_contrast", "contrast_variation_coefficient", "squared_mean_contrast", "brightness_w3c", "colorness_w3c", "entropy_gray", "entropy_rgb"])