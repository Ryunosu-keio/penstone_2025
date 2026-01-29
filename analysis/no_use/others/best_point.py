import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import os
# import japanize_matplotlib




# def plot_cor_for_each_feature(df, y_feature, feature_list, folder_name, bright_or_dark="bright"):
#     # 相関係数を計算
#     # for feature in feature_list:
#     #     correlation = df[y_feature].corr(df[feature])
#     #     print(f"{feature} : {correlation:.2f}")
#     #     correlation = df[y_feature].corr(df[feature])

#     #     # 散布図の作成
        
#     #     plt.figure(figsize=(10, 6))
#     #     # for color in ['red', 'blue']:
#     #     #     subset = df[df['isred'] == color]
#     #     #     plt.scatter(subset[feature], subset[y_feature], color=color, marker='o', label=f'color = {color}')
#     #     # 青の点だけ先にプロット
#     #     plt.scatter(df[df['isred'] == 'blue'][feature], df[df['isred'] == 'blue'][y_feature], color='blue', marker='o', label='color = blue')
        
#     #     # 赤の点をzorderを使って青の点より上にプロット
#     #     plt.scatter(df[df['isred'] == 'red'][feature], df[df['isred'] == 'red'][y_feature], color='red', marker='o', label='color = red', zorder=2)
#     #     #赤の点のうち、timeFromDisplayが1.39以下の点をプロット

#     #     #青の点の重心をプロット
#     #     plt.scatter(df[df['isred'] == 'blue'][feature].mean(), df[df['isred'] == 'blue'][y_feature].mean(), 
#     #                 color='#1f77b4', marker='x', label='center of blue', edgecolors='white', linewidths=5, zorder=3, s=100)
#     #     # 赤の点の重心をプロット
#     #     plt.scatter(df[df['isred'] == 'red'][feature].mean(), df[df['isred'] == 'red'][y_feature].mean(), 
#     #                 color='red', marker='x', label='center of red', edgecolors='white', linewidths=5, zorder=4, s=100)
        
#         #赤と青の重心のxy座標を取得
#         blue_x = df[df['isred'] == 'blue'][feature].mean()
#         blue_y = df[df['isred'] == 'blue'][y_feature].mean()
#         red_x = df[df['isred'] == 'red'][feature].mean()
#         red_y = df[df['isred'] == 'red'][y_feature].mean()
#         # #blue_x, blue_y を軸上に表示
#         # plt.annotate(f'({blue_x:.2f}, {blue_y:.2f})', xy=(blue_x, blue_y), xytext=(blue_x, blue_y+0.5), fontsize=12, color='#1f77b4', zorder=5)
#         # #red_x, red_y を軸上に表示
#         # plt.annotate(f'({red_x:.2f}, {red_y:.2f})', xy=(red_x, red_y), xytext=(red_x, red_y+0.5), fontsize=12, color='red', zorder=6)



#         df = df[df["isred"] == "red"]
#         x_plot_list = df["sharpness_factor"].values.tolist()
#         y_plot_list = df["squared_mean_contrast"].values.tolist()

#         #df内の赤の点のうち、赤の重心からの距離潤にソート
#         distance_list = []
#         for x, y in zip(x_plot_list, y_plot_list):
#             distance = np.sqrt((x-red_x)**2 + (y-red_y)**2)
#             distance_list.append(distance)
        
#         df["distance"] = distance_list

#         df = df.sort_values("distance")
#         print(df[["image_name"],["diopter"]])
        



# # plot_cor_for_each_feature(df=df, y_feature="diopter", feature_list=["sobel_std_par_figure"], folder_name="necessary_s18_bdsame",bright_or_dark="bright")










        
#         # import scipy.stats as stats


#         # plt.xlabel(f"{feature}({bright_or_dark})",fontsize=18)
#         # plt.ylabel(y_feature,fontsize=18)
#         # #軸の数値のサイズ
#         # plt.tick_params(labelsize=18)
#         # # plt.title(f'Scatter Plot of {y_feature} vs Image Feature({bright_or_dark})')
#         # plt.legend()

    
#         # # folder_name = str(feature_list).split("_")[0]
#         # os.makedirs(f"../scatter_plot/{bright_or_dark}/{folder_name}", exist_ok=True)
#         # # plt.savefig(f"../scatter_plot/{bright_or_dark}/{folder_name}/{feature}.png")
#         # # print("saved")
#         # # plt.show()



# #################################################################################################################################################################

# feature_list = ["digit_brightness", "non_digit_brightness", "brightness_ratio",
#                 "contrast_value", "contrast_sensitivity",
#                 "r_max_brightness", "g_max_brightness", "b_max_brightness", "gray_max_brightness",
#                 "max_index", "mode_index", "hist_contrast",
#                 "contrast_variation_coefficient", "squared_mean_contrast"]


# # brightness_list = ["digit_brightness", "non_digit_brightness", "brightness_ratio"]
# # w3c_list = ["brightness_w3c", "colorness_w3c"]
# # skewness_kurtosis_list = ["r_kurtosis", "g_kurtosis", "b_kurtosis", "gray_kurtosis","r_skewness", "g_skewness", "b_skewness", "gray_skewness"]
# # skewness2_list =["gray_skewness2"]
# # max_list = ["r_max_brightness", "g_max_brightness", "b_max_brightness", "gray_max_brightness"]
# # contrast_list = ["contrast_value", "contrast_sensitivity", "hist_contrast", "contrast_variation_coefficient", "squared_mean_contrast"]
# # entropy_list = ["entropy_gray", "entropy_rgb"]
# # fft_list = ["avg_diff", "max_diff", "avg_diff_low_freq", "avg_diff_high_freq"]
# # button_list = ["timeFromDisplay_std"]
# # sharpness_factor2_list = ["sharpness_factor2"]
# # luminance_list = ["contrast_luminance","skewness_luminance"]
# # folder_lists =[brightness_list, w3c_list, skewness_kurtosis_list, skewness2_list, max_list, contrast_list, entropy_list, fft_list, button_list]


# # need_list = ["gray_skewness2", "digit_brightness", "squared_mean_contrast", "michaelson_contrast", "contrast_luminance","skewness_luminance","sharpness_factor"]
# need_list = ["skewness_luminance","digit_brightness", "brightness_ratio", "squared_mean_contrast", "contrast_luminance","sharpness_factor"]
# #diffあとでやる
# ###################################################################################################################################################################


# # df = pd.read_excel("../data/final_recent_bright/final_recent_bright_add_entropy_skewgray2_michaelson_sf_mse_sf2_luminance_sobel_std_par_figure.xlsx")
# # # df = pd.read_excel("../data/final_recent_dark/final_recent_dark_add_entropy_fft_color_skewgray2_michaelson_sf_mse_luminance.xlsx")

# # # df = pd.read_excel("../data/final_recent_dark/final_recent_dark_add_entropy_fft_button_without104105.xlsx")#################timeFromDisplay_std用
# # # df = pd.read_excel("../data/final_recent_dark/final_recent_dark_add_entropy_fft_color_skewgray2_michaelson_sf_mse_left.xlsx")########赤追加
# # # df_time = pd.read_excel("../data/final_recent_dark/final_recent_dark_add_entropy_skewgray2_michaelson_sf_mse_button700.xlsx")
# # # df_time = df_time[df_time["timeFromDisplay"] < 1.39]

# # plot_cor_for_each_feature(df=df, y_feature="diopter", feature_list=["sobel_std_par_figure"], folder_name="necessary_s18_bdsame",bright_or_dark="bright")





# # df = pd.read_excel("../data/final_recent_dark/final_recent_dark_add_entropy_fft_color_skewgray2_michaelson_sf_mse_luminance_sobel_std_par_figure.xlsx")

# # plot_cor_for_each_feature(df=df, y_feature="diopter", feature_list=["edge_sobel"], folder_name="necessary_s18_bdsame",bright_or_dark="dark")

# # # "necessary_s18_bdsame"の中の画像をfeatureごとにhconcatして保存
# # import cv2
# # import glob
# # path_bright = "../scatter_plot/bright/necessary_s18_bdsame2/"
# # path_dark = "../scatter_plot/dark/necessary_s18_bdsame2/"
# # path_list_bright = glob.glob(path_bright + "*")
# # path_list_dark = glob.glob(path_dark + "*")

# # for path_b, path_d in zip(path_list_bright, path_list_dark):
# #     img_b = cv2.imread(path_b)
# #     img_d = cv2.imread(path_d)
# #     img = cv2.vconcat([img_b, img_d])
# #     print(img)
# #     os.makedirs("../scatter_plot/necessary_s18_bdsamev", exist_ok=True)
# #     #imgを保存
# #     # cv2.imwrite("../scatter_plot/necessary_s18_bdsame/af.png", img)
# #     print(path_b.split('/')[-1])
# #     cv2.imwrite("../scatter_plot/necessary_s18_bdsamev/" + path_b.split('\\')[-1] + ".png", img)






# df = pd.read_excel("../data/final_recent_bright/final_recent_bright_add_entropy_skewgray2_michaelson_sf_mse_sf2_luminance_sobel_std_par_figure.xlsx")
df = pd.read_excel("../data/final_recent_dark/final_recent_dark_add_entropy_fft_color_skewgray2_michaelson_sf_mse_luminance_sobel_std_par_figure.xlsx")
feature = "skewness_luminance"
y_feature = "brightness_ratio"



#赤と青の重心のxy座標を取得
blue_x = df[df['isred'] == 'blue'][feature].mean()
blue_y = df[df['isred'] == 'blue'][y_feature].mean()
red_x = df[df['isred'] == 'red'][feature].mean()
red_y = df[df['isred'] == 'red'][y_feature].mean()
# #blue_x, blue_y を軸上に表示
# plt.annotate(f'({blue_x:.2f}, {blue_y:.2f})', xy=(blue_x, blue_y), xytext=(blue_x, blue_y+0.5), fontsize=12, color='#1f77b4', zorder=5)
# #red_x, red_y を軸上に表示
# plt.annotate(f'({red_x:.2f}, {red_y:.2f})', xy=(red_x, red_y), xytext=(red_x, red_y+0.5), fontsize=12, color='red', zorder=6)



df = df[df["isred"] == "red"]
x_plot_list = df["skewness_luminance"].values.tolist()
y_plot_list = df["brightness_ratio"].values.tolist()

#df内の赤の点のうち、赤の重心からの距離潤にソート
distance_list = []
for x, y in zip(x_plot_list, y_plot_list):
    distance = np.sqrt((x-red_x)**2 + (y-red_y)**2)
    distance_list.append(distance)

df["distance"] = distance_list

df = df.sort_values("distance")
df = df[["image_name","diopter","distance"]]

# df.to_excel("../data/final_recent_bright/final_recent_bright_gravity.xlsx")

df.to_excel("../data/final_recent_dark/final_recent_dark_gravity3.xlsx")
