


import cv2
import numpy as np
import matplotlib.pyplot as plt
import glob

# 画像を読み込み、グレースケールに変換
import cv2
import numpy as np
import matplotlib.pyplot as plt
import glob

def calculate_edge_sobel(image_path):
    image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    
    # ソーベルフィルタを適用
    sobelx = cv2.Sobel(image, cv2.CV_64F, 1, 0, ksize=3)
    sobely = cv2.Sobel(image, cv2.CV_64F, 0, 1, ksize=3)
    
    # エッジ強度を計算
    edge_magnitude = np.sqrt(sobelx**2 + sobely**2)

    # 図を作成してサブプロットを追加
    fig, axs = plt.subplots(1, 3, figsize=(15, 5))
    axs[0].imshow(image, cmap='gray')
    axs[0].set_title('Original Image')
    axs[0].axis('off')

    axs[1].imshow(np.abs(sobelx) + np.abs(sobely), cmap='gray')
    axs[1].set_title('Sobel Edge Detection')
    axs[1].axis('off')

    axs[2].hist(edge_magnitude.ravel(), bins=100, rwidth=0.8)
    axs[2].set_title('Edge Magnitude Histogram')

    plt.show()

    # エッジ強度の平均値を計算
    average_edge_strength = np.mean(edge_magnitude)
    print("Average edge strength: ", average_edge_strength)
    return average_edge_strength

# 画像パスのリストを取得
image_paths = glob.glob("../experiment_images/101_0/*_1_*.jpg")

# 各画像に対して処理を実行
for path in image_paths:
    calculate_edge_sobel(path)


# df = pd.read_excel("../data/final_recent_bright/final_recent_bright_add_entropy_skewgray2_michaelson_sf_mse_sf2_luminance_sobel.xlsx")
# df = pd.read_excel("../data/final_recent_dark/final_recent_dark_add_entropy_skewgray2_michaelson_sf_mse_sf2_luminance_sobel.xlsx")
# def std_sobel(df):
#     df["sobel_std_par_figure"] = np.nan

#     figure_list = df["figure"].values
#     figure_list = figure_list.tolist()

#     for figure in figure_list:
#         #figureごとにsobel_std_figureを計算
#         df = df[df["figure"] == figure]
#         mean = df["edge_sobel"].mean()
#         std = df["edge_sobel"].std()
#         df["sobel_std_par_figure"] = (df["edge_sobel"] - mean) / std

#     #計算したsobel_std_figureをdfに追加
#     df.to_excel("../data/final_recent_bright/final_recent_bright_add_entropy_skewgray2_michaelson_sf_mse_sf2_luminance_sobel_std_par_figure.xlsx", index=False)
