import pandas as pd
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.pyplot as plt

# # df = pd.read_excel("../data/final_recent_dark/final_recent_dark_add_entropy_fft_color_skewgray2_michaelson_sf_mse.xlsx")
# # df = df[df["isred"] == "red"]
# # #xyz軸を列に指定して3次元プロット

# # # df = df[df["diopter"]]
# # x = df["sharpness_factor"]
# # y = df["squared_mean_contrast"] 
# # z = df["diopter"]

# # # print(x)
# # # print(y)
# # # print(z)

# # # fig = plt.figure()
# # # ax = fig.add_subplot(111, projection='3d')
# # # # ax = Axes3D(fig)
# # # ax.scatter(x, y, z)
# # # ax.set_xlabel("sharpness_factor")
# # # ax.set_ylabel("squared_mean_contrast")
# # # ax.set_zlabel("diopter")
# # # #近似平面



# # # plt.show()

# # #近似平面を作成

# # import numpy as np
# # from sklearn.linear_model import LinearRegression

# # # 線形回帰モデルを作成
# # model = LinearRegression()

# # # トレーニングデータを準備（x と y を組み合わせる）
# # XY = np.column_stack((x, y))

# # # モデルをトレーニング
# # model.fit(XY, z)

# # # x と y の値に基づいてグリッドを生成
# # x_range = np.linspace(x.min(), x.max(), 100)
# # y_range = np.linspace(y.min(), y.max(), 100)
# # xx, yy = np.meshgrid(x_range, y_range)

# # # グリッド上の予測値を計算
# # zz = model.predict(np.column_stack((xx.ravel(), yy.ravel()))).reshape(xx.shape)

# # # 3次元プロットと近似平面の表示
# # fig = plt.figure()
# # ax = fig.add_subplot(111, projection='3d')
# # ax.scatter(x, y, z, color='b')  # 元のデータをプロット
# # ax.plot_surface(xx, yy, zz, color='r', alpha=0.5)  # 近似平面をプロット

# # ax.set_xlabel("sharpness_factor")
# # ax.set_ylabel("squared_mean_contrast")
# # ax.set_zlabel("diopter")

# # plt.show()

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from sklearn.linear_model import LinearRegression

# # # データの読み込み
# # df = pd.read_excel("../data/final_recent_bright/final_recent_bright_add_entropy_skewgray2_michaelson_sf_mse_sf2.xlsx")
# df = pd.read_excel("../data/final_recent_dark/final_recent_dark_add_entropy_fft_color_skewgray2_michaelson_sf_mse_luminance_sobel_std_par_figure.xlsx")

# def regressor(df,x_feature,y_feature):
#     red_df = df[df["isred"] == "red"]
#     x_red = red_df[x_feature]
#     y_red = red_df[y_feature]
#     z_red = red_df["diopter"]
#     print(red_df)

#     # その他のデータポイントの選択
#     blue_df = df[df["isred"] != "red"]
#     x_blue = blue_df[x_feature]
#     y_blue = blue_df[y_feature]
#     z_blue = blue_df["diopter"]

#     # 線形回帰モデルを作成
#     model = LinearRegression()
#     XY = np.column_stack((df[x_feature], df[y_feature]))
#     model.fit(XY, df["diopter"])

#     # グリッド上の予測値を計算
#     x_range = np.linspace(df[x_feature].min(), df[x_feature].max(), 100)
#     y_range = np.linspace(df[y_feature].min(), df[y_feature].max(), 100)
#     xx, yy = np.meshgrid(x_range, y_range)
#     zz = model.predict(np.column_stack((xx.ravel(), yy.ravel()))).reshape(xx.shape)

#     # 3次元プロットと近似平面の表示
#     fig = plt.figure()
#     ax = fig.add_subplot(111, projection='3d')


#     # 青色のデータポイントをプロット
#     ax.scatter(x_blue, y_blue, z_blue, color='blue'#プロット小さくする
#                     , marker='o', s=1, alpha=0.5)
#     # 赤色のデータポイントをプロット
#     ax.scatter(x_red, y_red, z_red, color='r',#青の上から赤をプロット
#                 marker='o', edgecolors='k', s=15,zorder=2)

#     # 近似平面をプロット
#     ax.plot_surface(xx, yy, zz, color='cyan', alpha=0.5)
#     #近似平面の式
#     # plt.text(0.1 * plt.xlim()[1], 0.5 * plt.ylim()[1], f'z = {model.intercept_:.2f} + {model.coef_[0]:.2f}x + {model.coef_[1]:.2f}y', fontsize=12, s=10)

#     ax.set_xlabel(x_feature)
#     ax.set_ylabel(y_feature)
#     ax.set_zlabel("diopter")

#     plt.show()

lists = ["brightness_ratio","squared_mean_contrast","sharpness_factor"]
# for i in range(len(lists)):
#     for j in range(i+1,len(lists)):
#         regressor(df,lists[i],lists[j])


#listsのうち３つえらんでmatplotlib３次元プロット
# for i in range(len(lists)):
#     for j in range(i+1,len(lists)):
#         for k in range(j+1,len(lists)):
#             # データの読み込み
#             df = pd.read_excel("../data/final_recent_dark/final_recent_dark_add_entropy_fft_color_skewgray2_michaelson_sf_mse_luminance_sobel_std_par_figure.xlsx")
#             red_df = df[df["isred"] == "red"]
#             blue_df = df[df["isred"] != "red"]
#             x = df[lists[i]]
#             y = df[lists[j]]
#             z = df[lists[k]]

#             #3要素に対して線形回帰
#             model = LinearRegression()
#             XY = np.column_stack((df[lists[i]], df[lists[j]]))
#             model.fit(XY, df[lists[k]])

#             # グリッド上の予測値を計算
#             x_range = np.linspace(df[lists[i]].min(), df[lists[i]].max(), 100)
#             y_range = np.linspace(df[lists[j]].min(), df[lists[j]].max(), 100)
#             xx, yy = np.meshgrid(x_range, y_range)
#             zz = model.predict(np.column_stack((xx.ravel(), yy.ravel()))).reshape(xx.shape)



#             #3次元プロット
#             fig = plt.figure()
#             ax = fig.add_subplot(111, projection='3d')
#             #blue_dfを青でプロット
#             ax.scatter(blue_df[lists[i]], blue_df[lists[j]], blue_df[lists[k]], color='b', s=1)
#             #red_dfを赤でプロット
#             ax.scatter(red_df[lists[i]], red_df[lists[j]], red_df[lists[k]], color='r',zorder=2, edgecolors='k', s=15)
#             ax.set_xlabel(lists[i])
#             ax.set_ylabel(lists[j])
#             ax.set_zlabel(lists[k])



#             plt.show()
            



            

# #listの中身の散布図行列を作成
# # import seaborn as sns
# # sns.pairplot(df[lists])
# # plt.show()

#seaborn使わずにmatplotlibで散布図行列を作成
# import itertools

# df = pd.read_excel("../data/final_recent_dark/final_recent_dark_add_entropy_fft_color_skewgray2_michaelson_sf_mse_luminance_sobel_std_par_figure.xlsx")
# fig, axes = plt.subplots(nrows=6, ncols=6, figsize=(15, 15))
# for i, j in itertools.combinations(range(6), 2):
#     axes[i, j].scatter(df[lists[i]], df[lists[j]],s=1)
#     axes[i, j].set_xlabel(lists[i])
#     axes[i, j].set_ylabel(lists[j])
# plt.show()


import pandas as pd
import matplotlib.pyplot as plt
import itertools

# データの読み込み
# df = pd.read_excel("../data/final_recent_dark/final_recent_dark_add_entropy_fft_color_skewgray2_michaelson_sf_mse_luminance_sobel_std_par_figure.xlsx")

df = pd.read_excel("../data/final_recent_bright/final_recent_bright_add_entropy_skewgray2_michaelson_sf_mse_sf2.xlsx")
# lists = ['var1', 'var2', 'var3', 'var4', 'var5', 'var6']

# 6x6のサブプロットを作成
fig, axes = plt.subplots(nrows=3, ncols=3, figsize=(10, 10))
plt.subplots_adjust(hspace=0.4, wspace=0.4)

# 各変数の組み合わせに対して散布図を描画
for i, j in itertools.combinations(range(3), 2):
    ax = axes[i, j]

    #赤と青に分けてプロット
    red_df = df[df["isred"] == "red"]
    blue_df = df[df["isred"] != "red"]
    ax.scatter(blue_df[lists[i]], blue_df[lists[j]], s=1)
    ax.scatter(red_df[lists[i]], red_df[lists[j]], s=1,color='r')
    #相関係数を表示
    # ax.text(0.1 * plt.xlim()[1], 0.5 * plt.ylim()[1], f'Correlation: {df[lists[i]].corr(df[lists[j]]):.2f}', fontsize=12, s=10)
    print(f'Correlation: {df[lists[i]].corr(df[lists[j]]):.2f}')
    ax.set_xlabel(lists[i])
    ax.set_ylabel(lists[j])

    # 上三角形の部分のサブプロットを非表示にする
    axes[j, i].set_visible(False)

plt.show()


            