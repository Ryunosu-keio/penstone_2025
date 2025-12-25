import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import numpy as np
import pandas as pd
import itertools

path = "../data/final_part1/final.xlsx"
# path = "../data/final_part1/final_all.xlsx"

# Load and preprocess the dataframe
df = pd.read_excel(path)
columns_to_drop = ["Unnamed: 0.1", "フレーム数", "Unnamed: 0", "filename", "param1", 
                   "param1_value", "param2", "param2_value", "param3", "param3_value", 
                   "status", "image_name", "times", "figure"]
df = df.drop(columns=columns_to_drop)

# Function to assign color based on diopter value percentile
def assign_color(value):
    if value <= df["diopter"].quantile(0.10):
        return 'red'
    else:
        return 'blue'

# Grid definitions
grid_dicts = {
    'brightness': {"0":0,"1":10,"2":20,"3":30},
    'contrast': {"0":0.8,"1":0.9,"2":1.0,"3":1.1},
    'gamma': {"0":0.5,"1":0.7,"2":0.9,"3":1.1},
    'sharpness': {"0":0.25,"1":0.5,"2":0.75,"3":1.0},
    'equalization': {"0":4,"1":13,"2":22,"3":32}
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
combinations = list(itertools.combinations(columns, 3))

for combo in combinations:
    x, y, z = combo

    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    ax.scatter(df[x], df[y], df[z], c=colors, s=30)

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
    # plt.get_current_fig_manager().window.state('zoomed')
    plt.show()
