import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from mpl_toolkits.mplot3d import Axes3D
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
# from matplotlib.colors import Normalize, ScalarMappable
# from matplotlib.cm import viridis
import itertools

# grid_dicts_3 辞書
grid_dicts_3 = {
    'brightness': {"0": 0, "1": 10, "2": 20, "3": 30},
    'contrast': {"0": 0.8, "1": 0.933, "2": 1.066, "3": 1.2},
    'gamma': {"0": 0.5, "1": 0.7, "2": 0.9, "3": 1.1},
    'sharpness': {"0": 0, "1": 0.33, "2": 0.66, "3": 1.0},
    'equalization': {"0": 4, "1": 13, "2": 22, "3": 32}
}

# データの読み込み
# df = pd.read_excel("../data/final_part2/darkfinal_with_combined_data2.xlsx")
df = pd.read_excel("../data/final_recent_dark/final_recent_dark.xlsx")
# 3次元グラフにグリッドを追加し、各グリッド内のaverage_diopterの値を表示する関数
def plot_3d_with_grids(df, x_feature, y_feature, z_feature):
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')

    # グリッドの定義を取得
    x_grid = list(grid_dicts_3[x_feature].values())
    y_grid = list(grid_dicts_3[y_feature].values())
    z_grid = list(grid_dicts_3[z_feature].values())

    # # データの値に基づいて色を設定するための正規化
    # norm = Normalize(vmin=df['average_diopter_combined'].min(), vmax=df['average_diopter_combined'].max())
    # mappable = ScalarMappable(norm=norm, cmap=viridis)

    # グリッドごとに処理
    for i in range(len(x_grid)-1):
        for j in range(len(y_grid)-1):
            for k in range(len(z_grid)-1):
                x_range = [x_grid[i], x_grid[i+1]]
                y_range = [y_grid[j], y_grid[j+1]]
                z_range = [z_grid[k], z_grid[k+1]]

                # グリッド内のデータをフィルタリング
                grid_data = df[
                    (df[x_feature] >= x_range[0]) & (df[x_feature] < x_range[1]) &
                    (df[y_feature] >= y_range[0]) & (df[y_feature] < y_range[1]) &
                    (df[z_feature] >= z_range[0]) & (df[z_feature] < z_range[1])
                ]

                # 平均値を計算（存在する場合）
                if not grid_data.empty:
                    # avg_diopter = grid_data['average_diopter_combined'].iloc[0]
                    count =  grid_data['average_diopter_combined'].count()

                    # グリッドの中心座標
                    center_x, center_y, center_z = np.mean(x_range), np.mean(y_range), np.mean(z_range)

                    # 色を決定
                    # color = mappable.to_rgba(avg_diopter)
                    # if avg_diopter < 2.81:
                    #     color = "red"
                    # elif avg_diopter < 3:
                    #     color = "green"
                    # elif avg_diopter < 3.2:
                    #     color = "yellow"
                    # else:
                    #     color = "blue"
                    
                    #サイズを決定
                    if count == 1:
                        size = 50
                    if count < 10:
                        size = 10
                    elif count < 20:
                        size = 15
                    elif count < 30:
                        size = 20
                    elif count < 40:
                        size = 25
                    else:
                        size = 30


                    # グリッドを描画
                    ax.scatter(center_x, center_y, center_z,s=50, cmap='viridis', c=count, alpha=0.5)
                    # ax.text(center_x, center_y, center_z, f'{avg_diopter:.2f}', color='black')
                    ax.text(center_x, center_y, center_z, f'{count}', fontsize=size, color='black')

    ax.set_xlabel(x_feature)
    ax.set_ylabel(y_feature)
    ax.set_zlabel(z_feature)
    # plt.colorbar(mappable, ax=ax, label='Average Diopter')
    plt.title('3D Grids with Average Diopter Values')
    plt.show()


#パラメータの組み合わせをつくる
columns = ['gamma', 'contrast', 'sharpness', 'brightness', 'equalization']
combinations_3 = list(itertools.combinations(columns, 3))
print(combinations_3)
for combo in combinations_3:
    x, y, z = combo
    plot_3d_with_grids(df, x, y, z)
    
