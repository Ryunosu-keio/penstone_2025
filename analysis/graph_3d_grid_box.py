from mpl_toolkits.mplot3d import Axes3D
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
import numpy as np
import pandas as pd
import itertools
import matplotlib.pyplot as plt
import os

# Function to calculate the average diopter in a grid cell


def calculate_grid_ratio(df, x_feature, y_feature, z_feature, x_range, y_range, z_range):
    filtered_df = df[(df[x_feature] >= x_range[0]) & (df[x_feature] <= x_range[1]) &
                    (df[y_feature] >= y_range[0]) & (df[y_feature] <= y_range[1]) &
                    (df[z_feature] >= z_range[0]) & (df[z_feature] <= z_range[1])]
    df_upper_quantiles = filtered_df[filtered_df["diopter"] <= quantiles["lower"]]
    df_lower_quantiles = filtered_df[filtered_df["diopter"] >= quantiles["upper"]]
    if len(filtered_df) == 0:
        return None, None, None
    upper_quantiles_ratio = len(df_upper_quantiles) / len(filtered_df)
    lower_quantiles_ratio = len(df_lower_quantiles) / len(filtered_df)
    return upper_quantiles_ratio, lower_quantiles_ratio, filtered_df

# Function to assign color based on the average diopter value in a grid cell


# Grid definitions
grid_dicts_3 = {
    'brightness': {"0": 0, "1": 10, "2": 20, "3": 30},
    'contrast': {"0": 0.8, "1": 0.933, "2": 1.066, "3": 1.2},
    'gamma': {"0": 0.5, "1": 0.7, "2": 0.9, "3": 1.1},
    'sharpness': {"0": 0, "1": 0.33, "2": 0.66, "3": 1.0},
    'equalization': {"0": 4, "1": 13, "2": 22, "3": 32}
}

grid_dicts_5 = {
    'gamma': {"-1": 0.20, "0": 0.49, "1": 0.7, "2": 0.9, "3": 1.11, "4": 1.3},
    'contrast': {"-1": 0.81, "0": 0.81, "1": 0.933, "2": 1.066, "3": 1.23, "4": 1.33},
    'sharpness': {"-1": -0.33, "0": -0.1, "1": 0.32, "2": 0.66, "3": 1.02, "4": 1.33},
    'brightness': {"-1": -10, "0": -0.1, "1": 10, "2": 20, "3": 31, "4": 40},
    'equalization': {"-1": 0, "0": 4, "1": 13, "2": 22, "3": 33, "4": 40}
}
# grid_dicts_5 = {
#     'gamma': {"-1": 0.19, "0": 0.49, "1": 0.7, "2": 0.9, "3": 1.11, "4": 1.3},
#     'contrast': {"-1": 0.65, "0": 0.79, "1": 0.933, "2": 1.066, "3": 1.21, "4": 1.33},
#     'sharpness': {"-1": -0.01, "0": -0.01, "1": 0.33, "2": 0.66, "3": 1.01, "4": 1.33},
#     'brightness': {"-1": -9, "0": -1, "1": 10, "2": 20, "3": 31, "4": 40},
#     'equalization': {"-1": -1, "0": 3, "1": 13, "2": 22, "3": 33, "4": 40}
# }
grids = {"3": grid_dicts_3, "5": grid_dicts_5}


def add_external_grid(ax, x_range, y_range, z_range, color='purple'):
    """Add an external grid to the plot."""

    # Define the vertices of the new cube (grid)
    vertices = [
        (x_range[0], y_range[0], z_range[0]),
        (x_range[0], y_range[1], z_range[0]),
        (x_range[1], y_range[0], z_range[0]),
        (x_range[1], y_range[1], z_range[0]),
        (x_range[0], y_range[0], z_range[1]),
        (x_range[0], y_range[1], z_range[1]),
        (x_range[1], y_range[0], z_range[1]),
        (x_range[1], y_range[1], z_range[1])
    ]

    # Define the 6 faces of the cube
    faces = [
        [vertices[0], vertices[1], vertices[5], vertices[4]],
        [vertices[7], vertices[6], vertices[2], vertices[3]],
        [vertices[0], vertices[1], vertices[3], vertices[2]],
        [vertices[7], vertices[6], vertices[4], vertices[5]],
        [vertices[7], vertices[3], vertices[1], vertices[5]],
        [vertices[0], vertices[4], vertices[6], vertices[2]]
    ]

    # Add the cube (grid) to the plot
    ax.add_collection3d(Poly3DCollection(
        faces, linewidths=1, edgecolors='gray', alpha=0.25, facecolors=color))

######################################################################################################################


# Feature combinations
columns = ['gamma', 'contrast', 'sharpness', 'brightness', 'equalization']
combinations_3 = list(itertools.combinations(columns, 3))

# Plotting the 3D scatter plot with grid averages for the first combination as an example


grids_to_remove = []
# grids_to_remove = [f"Grid_{i}_{j}_{k}" for i in range(5) for j in range(5) for k in range(5)]
# for i in range(5):
#     grids_to_remove.remove(f"Grid_{i}_{0}_{0}")
print(grids_to_remove)

# Function to plot 3D scatter plot with transparent colored grids


def plot_3d_grid_color(df, x_feature, y_feature, z_feature, quantiles, grid_num):
    grid_dicts = grids[str(grid_num)]

    # x_values = np.linspace(min(grid_dicts[x_feature].values()), max(
    #     grid_dicts[x_feature].values()), grid_num+1)
    # y_values = np.linspace(min(grid_dicts[y_feature].values()), max(
    #     grid_dicts[y_feature].values()), grid_num+1)
    # z_values = np.linspace(min(grid_dicts[z_feature].values()), max(
    #     grid_dicts[z_feature].values()), grid_num+1)

    x_values = list(grid_dicts[x_feature].values())
    y_values = list(grid_dicts[y_feature].values())
    z_values = list(grid_dicts[z_feature].values())

    # print(x_values, y_values, z_values)

    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')

    for i in range(grid_num):
        for j in range(grid_num):
            for k in range(grid_num):
                x_range = (x_values[i], x_values[i + 1])
                y_range = (y_values[j], y_values[j + 1])
                z_range = (z_values[k], z_values[k + 1])

                grid_ratio_upper, grid_ratio_lower, filtered_df = calculate_grid_ratio(
                    df, x_feature, y_feature, z_feature, x_range, y_range, z_range)
                print("xyz_features")
                print(x_feature, y_feature, z_feature)
                print("xyz_values")
                print(x_values, y_values, z_values)
                print("params")
                if filtered_df is not None:
                    print(filtered_df["param1"].unique())
                    print(filtered_df["param2"].unique())
                    print(filtered_df["param3"].unique())
                # Determine the color based on quantiles 
                #for good
                if grid_ratio_upper is not None: 
                    if grid_ratio_upper >= 0.66:#defaultは0.6
                        color = 'red'
                        print(color)
                    # elif grid_ratio_upper >= 0.5:
                    #     color = 'red'
                    else:
                        color = 'blue'
                # if grid_ratio_lower is not None: 
                        # for bad
                #     if grid_ratio_lower >= 0.4:
                #         color = 'orange'
                #     # elif grid_ratio_upper >= 0.6:
                #     #     color = 'red'
                #     else:
                #         color = 'blue'

                    

                    # Draw a transparent cube
                    r = [x_range[0], x_range[1]]
                    s = [y_range[0], y_range[1]]
                    t = [z_range[0], z_range[1]]

                    print(r, s, t)

                    # filtered_df["isorange"] = color
                    # filtered_df["x_feature"] = x_feature
                    # filtered_df["y_feature"] = y_feature
                    # filtered_df["z_feature"] = z_feature

                    # filtered_df["x_range0", "x_range1"] = [x_range[0], x_range[1]]
                    # filtered_df["y_range0", "y_range1"] = [y_range[0], y_range[1]]
                    # filtered_df["z_range0", "z_range1"] = [z_range[0], z_range[1]]


                    # if filtered_df is not None:
                    #     print("filtered_df")
                    #     print(filtered_df)
                    #     df.loc[filtered_df.index, "color"] = color
                    #     df.loc[filtered_df.index, "x_feature"] = x_feature
                    #     df.loc[filtered_df.index, "y_feature"] = y_feature
                    #     df.loc[filtered_df.index, "z_feature"] = z_feature

                    #     df.loc[filtered_df.index, "x_range0"] = x_range[0]
                    #     df.loc[filtered_df.index, "x_range1"] = x_range[1]
                    #     df.loc[filtered_df.index, "y_range0"] = y_range[0]
                    #     df.loc[filtered_df.index, "y_range1"] = y_range[1]
                    #     df.loc[filtered_df.index, "z_range0"] = z_range[0]
                    #     df.loc[filtered_df.index, "z_range1"] = z_range[1]
                    #     print("##################################")

                    #     print(df.loc[filtered_df.index])

                    #     print("df.loc[filtered_df.index]")
                    #     print(df.loc[filtered_df.index])
                            





                    for l in itertools.product(*[r, s, t]):
                        # Plot corner points for debugging
                        ax.scatter(*l, alpha=0, c=color)

                    # Define the vertices that compose each of the 6 faces
                    vertices = [(x_range[0], y_range[0], z_range[0]),
                                (x_range[0], y_range[1], z_range[0]),
                                (x_range[1], y_range[0], z_range[0]),
                                (x_range[1], y_range[1], z_range[0]),
                                (x_range[0], y_range[0], z_range[1]),
                                (x_range[0], y_range[1], z_range[1]),
                                (x_range[1], y_range[0], z_range[1]),
                                (x_range[1], y_range[1], z_range[1])]

                    # Create the 6 faces of the cube
                    faces = [[vertices[0], vertices[1], vertices[5], vertices[4]],
                                [vertices[7], vertices[6], vertices[2], vertices[3]],
                                [vertices[0], vertices[1], vertices[3], vertices[2]],
                                [vertices[7], vertices[6], vertices[4], vertices[5]],
                                [vertices[7], vertices[3], vertices[1], vertices[5]],
                                [vertices[0], vertices[4], vertices[6], vertices[2]]]

                    # Draw cube faces
                    ax.add_collection3d(Poly3DCollection(
                        faces, linewidths=1, edgecolors='gray', alpha=0.25, facecolors=color))

    ax.set_xlabel(x_feature, fontsize=14)
    ax.set_ylabel(y_feature, fontsize=14)
    ax.set_zlabel(z_feature, fontsize=14)
    ax.tick_params(axis='both', which='major', labelsize=14)
    




    # ディレクトリがなければ作成
    if directory_number == "1":
        os.makedirs(f"../grid_pic/bright_{data}", exist_ok=True)
        plt.title(f"{x_feature}, {y_feature}, {z_feature} (bright)")
        plt.savefig(f"../grid_pic/bright_{data}/{x_feature}_{y_feature}_{z_feature}_bright.png")
        print("saved")

    if directory_number == "2":
        os.makedirs(f"../grid_pic/dark_0.66{data}", exist_ok=True)
        # plt.title(f"{x_feature}, {y_feature}, {z_feature} (dark)")
        plt.savefig(f"../grid_pic/dark_0.66{data}/{x_feature}_{y_feature}_{z_feature}_dark_0.66.png")
        print("saved")
    plt.show()
    
    
# path = "../data/final_part1/final_test2_mean2.xlsx"
    # df.to_excel("../data/final_recent_dark/final_recent_dark_add_entropy_fft_color.xlsx")

#########################################################
directory_number = str(input("明所なら1、暗所なら2"))
# data = input("図示するエクセルデータを選んでください")
data = "final_recent_dark_add_entropy_fft"
path = "../data/final_part" + directory_number + "/" + data + ".xlsx"
path = "../data/final_recent_dark/final_recent_dark_add_entropy_fft.xlsx"
grid_num = int(input("gridの数を入力してください（3or5):"))
#########################################################

df = pd.read_excel(path)

# Calculate 10th and 90th percentile values for the diopter
if directory_number == "1":
    quantiles = {
        'upper': df['diopter'].quantile(0.9),
        'lower': df['diopter'].quantile(0.1) #明所の時こっち
    }
if directory_number == "2":
    quantiles = {
        'upper': 3.9094741816716603,
        'lower': 2.562485021528731 #暗所の時こっち  
    }

# Plotting the 3D scatter plot with transparent colored grids for the first combination as an example
# plot_3d_grid_color(df, combinations_3[0][0], combinations_3[0][1], combinations_3[0][2], quantiles, grid_num)

# Plotting the 3D scatter plots with transparent colored grids for the remaining combinations
# Skip the first combination as it was already plotted
for combo in combinations_3:
    plot_3d_grid_color(df, combo[0], combo[1], combo[2], quantiles, grid_num)


# final_test2_mean2 penstone提出 穴空いてるけど採用
# final_add 追加実験分
# final_add_editted 追加実験分-追加実験のgcsの赤グリッド点

# darkfinal 暗所実験分
# final_recent_dark_add_entropy_fftでも同じ赤になるのでおけ