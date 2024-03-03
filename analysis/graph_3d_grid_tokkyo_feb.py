import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import pandas as pd
import itertools
import os
import numpy as np

use_file = "final_test2_mean2"
path = "../data/final_part1/" + use_file + ".xlsx"

# データフレームの読み込み
df = pd.read_excel(path)

# diopter値に基づいてマーカーを割り当てる関数
def assign_color(value):
    if value <= df["diopter"].quantile(0.05):
        return "o"
    elif value <= df["diopter"].quantile(0.90):
        return "^"
    else:
        return "x"


#縦線あり
def draw_cube(ax, x_range, y_range, z_range, color="black", n_lines=3):
    # 立方体の辺を描画
    for x in x_range:
        for y in y_range:
            ax.plot([x, x], [y, y], z_range, color=color)
    for x in x_range:
        for z in z_range:
            ax.plot([x, x], y_range, [z, z], color=color)
    for y in y_range:
        for z in z_range:
            ax.plot(x_range, [y, y], [z, z], color=color)

    # 各面に斜線を描画
    def draw_lines_on_face(p1, p2, p3, p4, n_lines=3):
        p1 = np.array(p1)
        p2 = np.array(p2)
        p3 = np.array(p3)
        p4 = np.array(p4)

        for i in range(n_lines):
            # t = i / float(n_lines)
            # start = p1 * (1 - t) + p2 * t
            # end = p3 * (1 - t) + p4 * t
            # ax.plot([start[0], end[0]], [start[1], end[1]], [start[2], end[2]], color=color)

            # start = p1 * (1 - i / n_lines) + p2 * (i / n_lines)
            # end = p3 * (1 - i / n_lines) + p4 * (i / n_lines)
            # ax.plot([start[0], end[0]], [start[1], end[1]], [start[2], end[2]], color="black")

             # 上辺のi番目の点
            start = p1 * (1 - i / n_lines) + p2 * (i / n_lines)
            # 下辺のi+1番目の点
            end = p3 * (1 - (i + 1) / n_lines) + p4 * ((i + 1) / n_lines)
            ax.plot([start[0], end[0]], [start[1], end[1]], [start[2], end[2]], color="black")


    # 各面の4つの頂点を計算
    vertices = [
        [x_range[0], y_range[0], z_range[0]],
        [x_range[1], y_range[0], z_range[0]],
        [x_range[1], y_range[1], z_range[0]],
        [x_range[0], y_range[1], z_range[0]],
        [x_range[0], y_range[0], z_range[1]],
        [x_range[1], y_range[0], z_range[1]],
        [x_range[1], y_range[1], z_range[1]],
        [x_range[0], y_range[1], z_range[1]]
    ]
    
    # 底面、上面、側面に斜線を描画
    draw_lines_on_face(vertices[0], vertices[1], vertices[3], vertices[2], n_lines)
    draw_lines_on_face(vertices[4], vertices[5], vertices[7], vertices[6], n_lines)
    for i in range(4):
        draw_lines_on_face(vertices[i], vertices[(i + 1) % 4], vertices[i + 4], vertices[(i + 1) % 4 + 4], n_lines)

#斜線なし
# def draw_cube(ax, x_range, y_range, z_range, color="black", linestyle="-"):
#     # 立方体の辺を描画
#     for x in x_range:
#         for y in y_range:
#             ax.plot([x, x], [y, y], z_range, color=color, linestyle=linestyle)
#     for x in x_range:
#         for z in z_range:
#             ax.plot([x, x], y_range, [z, z], color=color, linestyle=linestyle)
#     for y in y_range:
#         for z in z_range:
#             ax.plot(x_range, [y, y], [z, z], color=color, linestyle=linestyle)


#斜線あり
# def draw_hatch_lines_on_plane(ax, plane, start_point, end_point, fixed_value, delta, angle):
#     """
#     指定された平面に斜線を描画する関数。
#     ax: 描画対象のAxes3Dオブジェクト。
#     plane: 'xy', 'yz', 'xz' のいずれかを指定。
#     start_point, end_point: 斜線を描画する範囲を定義する始点と終点の座標。
#     fixed_value: 固定される軸の値。
#     delta: 斜線間の間隔。
#     angle: 斜線の方向。
#     """
#     if plane == 'xy':
#         z = fixed_value
#         for x in np.arange(start_point[0], end_point[0], delta):
#             for y in np.arange(start_point[1], end_point[1], delta):
#                 ax.plot([x, x + angle[0]], [y, y + angle[1]], [z, z], color="black")
#     elif plane == 'yz':
#         x = fixed_value
#         for y in np.arange(start_point[0], end_point[0], delta):
#             for z in np.arange(start_point[1], end_point[1], delta):
#                 ax.plot([x, x], [y, y + angle[0]], [z, z + angle[1]], color="black")
#     elif plane == 'xz':
#         y = fixed_value
#         for x in np.arange(start_point[0], end_point[0], delta):
#             for z in np.arange(start_point[1], end_point[1], delta):
#                 ax.plot([x, x + angle[0]], [y, y], [z, z + angle[1]], color="black")



def get_grid_ranges(value, grid_values):
    ranges = []
    for i in range(len(grid_values) - 1):
        if grid_values[i] <= value <= grid_values[i + 1]:
            ranges.append((grid_values[i], grid_values[i + 1]))
    return ranges




# グリッド定義
grid_dicts = {
    'brightness': {"0": 0, "1": 10, "2": 20, "3": 30},
    'contrast': {"0": 0.8, "1": 0.933, "2": 1.066, "3": 1.2},
    'gamma': {"0": 0.5, "1": 0.7, "2": 0.9, "3": 1.1},
    'sharpness': {"0": 0, "1": 0.33, "2": 0.66, "3": 1.0},
    'equalization': {"0": 4, "1": 13, "2": 22, "3": 32}
}


axis_colors = {
    'brightness': 'black',
    'contrast': 'black',
    'gamma': 'black',
    'sharpness': 'black',
    'equalization': 'black'
}

markers = df["diopter"].apply(assign_color).tolist()
columns = ['gamma', 'contrast', 'sharpness', 'brightness', 'equalization']
combinations_3 = list(itertools.combinations(columns, 3))


df["use_features"] = ["" for _ in range(len(df))]
# 他の列の値を更新
for i in range(len(df)):
    use_features = ""
    if df["gamma"][i] != 0:
        use_features += "gamma"
    else:
        df["gamma"][i] = 1.0

    if df["contrast"][i] != 0:
        use_features += "contrast"
    else:
        df["contrast"][i] = 1.0

    if df["sharpness"][i] != 0:
        use_features += "sharpness"
    else:
        df["sharpness"][i] = 0.0

    if df["brightness"][i] != 0:
        use_features += "brightness"
    else:
        df["brightness"][i] = 0.0

    if df["equalization"][i] != 0:
        use_features += "equalization"
    else:
        df["equalization"][i] = 4.0
    df["use_features"][i] = use_features

df["marker"] = markers



# 3D散布図の描画と立方体の描画
for combo in combinations_3:
    x, y, z = combo
    df_combo = df[df["use_features"].isin([x + y + z, x + y, y + z, x + z])]
    o_points = df_combo[df_combo["diopter"].apply(assign_color) == 'o']

    import matplotlib.pyplot as plt
    import tkinter as tk

    # フルスクリーンの解像度を取得
    root = tk.Tk()
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    root.destroy()

    # 解像度に基づいてフィギュアサイズを設定
    dpi = 100  # 例として100 dpiを使用
    figsize = (screen_width / dpi, screen_height / dpi)
    fig = plt.figure(figsize=figsize, dpi=dpi)
    ax = fig.add_subplot(111, projection='3d')

    # すべてのマーカーを持つ点をプロットし、diopterの値を横に表示
    for m in set(markers):
        points = df_combo[df_combo["diopter"].apply(assign_color) == m]
        ax.scatter(points[x], points[y], points[z], marker=m, color="black" if m == 'o' else "black", s=70 if m == 'o' else 10)
        
        # 各点の横にdiopterの値を表示
        for index, point in points.iterrows():
            ax.text(point[x], point[y], point[z], str(round(point["diopter"],2)), 
                    color="black", fontsize=15 if m == 'o' else 8,
                    bbox=dict(facecolor='white', alpha=0.5) if m == 'o' else None)
    # 各 'o' マーカーの点に対する立方体の描画
    x_values = sorted(grid_dicts[x].values())
    y_values = sorted(grid_dicts[y].values())
    z_values = sorted(grid_dicts[z].values())

    for index, row in o_points.iterrows():
        x_ranges = get_grid_ranges(row[x], x_values)
        y_ranges = get_grid_ranges(row[y], y_values)
        z_ranges = get_grid_ranges(row[z], z_values)

        for x_range in x_ranges:
            for y_range in y_ranges:
                for z_range in z_ranges:
                    draw_cube(ax, x_range, y_range, z_range)

    # # 各 'o' マーカーの点に対する立方体の描画（斜線付き）
    # for index, row in o_points.iterrows():
    #     x_ranges = get_grid_ranges(row[x], x_values)
    #     y_ranges = get_grid_ranges(row[y], y_values)
    #     z_ranges = get_grid_ranges(row[z], z_values)

    #     for x_range in x_ranges:
    #         for y_range in y_ranges:
    #             for z_range in z_ranges:
    #                 draw_cube(ax, x_range, y_range, z_range, color="black", n_lines=6)
    #                 print(x_range, y_range, z_range)
    #                 # 立方体のサイズ定義
    #                 # x_start, x_end = x_ranges[0], x_ranges[1]
    #                 # y_start, y_end = y_ranges[0], y_ranges[1]
    #                 # z_start, z_end = z_ranges[0], z_ranges[1]

    #                 x_start, x_end = x_range
    #                 y_start, y_end = y_range
    #                 z_start, z_end = z_range
    #                 # 例: 底面、上面、側面に斜線を描画
    #                 delta = 3
    #                 draw_hatch_lines_on_plane(ax, 'xy', [x_start, y_start], [x_end, y_end], z_start, delta, [1, 1])
    #                 draw_hatch_lines_on_plane(ax, 'xy', [x_start, y_start], [x_end, y_end], z_end, delta, [1, -1])
    #                 draw_hatch_lines_on_plane(ax, 'yz', [y_start, z_start], [y_end, z_end], x_start, delta, [1, 1])
    #                 draw_hatch_lines_on_plane(ax, 'yz', [y_start, z_start], [y_end, z_end], x_end, delta, [1, -1])
    #                 draw_hatch_lines_on_plane(ax, 'xz', [x_start, z_start], [x_end, z_end], y_start, delta, [1, 1])
    #                 draw_hatch_lines_on_plane(ax, 'xz', [x_start, z_start], [x_end, z_end], y_end, delta, [1, -1])

        # # 軸ラベルの設定
        # ax.set_xlabel('X Axis')
        # ax.set_ylabel('Y Axis')
        # ax.set_zlabel('Z Axis')
        # ax.set_xlim([x_start, x_end])
        # ax.set_ylim([y_start, y_end])
        # ax.set_zlim([z_start, z_end])
        # plt.show()

    # 軸の設定
    for axis, axis_name in [(ax.xaxis, x), (ax.yaxis, y), (ax.zaxis, z)]:
        axis.set_label_text(axis_name, color='black')
        axis.set_ticks(list(grid_dicts[axis_name].values()))
        for tl in axis.get_ticklabels():
            tl.set_color('black')
        axis._axinfo["grid"]['color'] = 'black'

    plt.title(f'{x}, {y}, {z} 3D scatter plot')
    os.makedirs("../grid_pic/tokkyo/slash3", exist_ok=True)
    plt.savefig(f"../grid_pic/tokkyo/slash3/{x}_{y}_{z}.png",dpi=dpi)
    # plt.show()


