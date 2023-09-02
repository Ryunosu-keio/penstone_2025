import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import numpy as np
import pandas as pd
import itertools

use_file = input("どのファイルを図示しますか")

path = "../data/final_part1/" + use_file + ".xlsx"

# Load and preprocess the dataframe
df = pd.read_excel(path)
# columns_to_drop = ["Unnamed: 0.1", "フレーム数", "Unnamed: 0", "filename", "param1",
#                    "param1_value", "param2", "param2_value", "param3", "param3_value",
#                    "status", "image_name", "times", "figure"]
# df = df.drop(columns=columns_to_drop)

# Function to assign color based on diopter value percentile


def assign_color(value):
    if value <= df["diopter"].quantile(0.05):
        return 'red'
    elif value <= df["diopter"].quantile(0.90):
        return 'green'
    else:
        return 'blue'


# Grid definitions
grid_dicts = {
    'brightness': {"0": 0, "1": 10, "2": 20, "3": 30},
    'contrast': {"0": 0.8, "1": 0.933, "2": 1.066, "3": 1.2},
    'gamma': {"0": 0.5, "1": 0.7, "2": 0.9, "3": 1.1},
    'sharpness': {"0": 0, "1": 0.33, "2": 0.66, "3": 1.0},
    'equalization': {"0": 4, "1": 13, "2": 22, "3": 32}
}

colors = df["diopter"].apply(assign_color).tolist()

# Define axis colors
axis_colors = {
    'brightness': 'blue',
    'contrast': 'green',
    'gamma': 'red',
    'sharpness': 'purple',
    'equalization': 'cyan'
}

columns = ['gamma', 'contrast', 'sharpness', 'brightness', 'equalization']


def name_from_combination2(combinations_2):
    combi_names = []
    for combo in combinations_2:
        x, y = combo
        name = x + y
        combi_names.append(name)
    return combi_names


def name_from_combination3(combinations_3):
    combi_names = []
    for combo in combinations_3:
        x, y, z = combo
        name = x + y + z
        combi_names.append(name)
    return combi_names


combinations_2 = list(itertools.combinations(columns, 2))

# combinations_2 = name_from_combination2(combinations_2)

combinations_3 = list(itertools.combinations(columns, 3))

# combinations_3 = name_from_combination3(combinations_3)

combo_dict = {}

# add df column "use_features"
df["use_features"] = ["" for _ in range(len(df))]

df["color"] = colors

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
        df["equalization"][i] = 0.0
    df["use_features"][i] = use_features

# for combo in combinations_2:
#     x, y = combo
#     combo_name = x + y
#     df_combo = df[df["use_features"] == combo_name]
#     print(combo_name)
#     print(df_combo["use_features"])

#     fig = plt.figure()
#     ax = fig.add_subplot(111, projection='3d')
#     # colors = df_combo["diopter"].apply(assign_color).tolist()

#     ax.scatter(df_combo[x], df_combo[y],
#                c=df_combo["color"], s=30)

#     # Configure axes
#     for axis, axis_name, axis_color in [(ax.xaxis, x, axis_colors[x]),
#                                         (ax.yaxis, y, axis_colors[y])]:
#         axis.set_label_text(axis_name, color=axis_color)
#         axis.set_ticks(list(grid_dicts[axis_name].values()))
#         for tl in axis.get_ticklabels():
#             tl.set_color(axis_color)
#         axis._axinfo["grid"]['color'] = axis_color

#     plt.title(f'{x}, {y} 3D scatter plot')
#     plt.get_current_fig_manager().window.state('zoomed')
#     plt.show()

for combo in combinations_3:
    x, y, z = combo
    combo_name = x + y + z
    combo_name2 = x + y
    combo_name3 = y + z
    combo_name4 = x + z
    combo_list = [combo_name, combo_name2, combo_name3, combo_name4]
    df_combo = df[df["use_features"].isin(combo_list)]
    print(combo_name)
    print(df_combo["use_features"])

    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    # colors = df_combo["diopter"].apply(assign_color).tolist()

    ax.scatter(df_combo[x], df_combo[y], df_combo[z],
               c=df_combo["color"], s=30)

    # Configure axes
    for axis, axis_name, axis_color in [(ax.xaxis, x, axis_colors[x]),
                                        (ax.yaxis, y, axis_colors[y]),
                                        (ax.zaxis, z, axis_colors[z])]:
        axis.set_label_text(axis_name, color=axis_color)
        axis.set_ticks(list(grid_dicts[axis_name].values()))
        for tl in axis.get_ticklabels():
            tl.set_color(axis_color)
        axis._axinfo["grid"]['color'] = axis_color

    plt.title(f'{x}, {y}, {z} 3D scatter plot')
    plt.get_current_fig_manager().window.state('zoomed')
    plt.show()
