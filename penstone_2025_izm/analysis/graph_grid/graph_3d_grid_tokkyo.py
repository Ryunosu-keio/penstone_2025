

####################以下特許用########################
####################以下特許用########################
####################以下特許用########################
####################以下特許用########################
####################以下特許用########################
####################以下特許用########################


# Iterate over combinations and create 3D scatter plots again with the updated grid_dicts
# Importing necessary libraries
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import numpy as np
import pandas as pd
import itertools

# # Load and preprocess the dataframe
# file_path = '/mnt/data/final_test2.xlsx'  # Updated file path with the uploaded file
path = "../data/final_part1/final_test2.xlsx"
df = pd.read_excel(path)

# # Function to assign marker based on diopter value percentile
def assign_marker(value):
    if value <= df["diopter"].quantile(0.05):
        return 'o'  # Circle as red
    elif value <= df["diopter"].quantile(0.90):
        return '^'  # Triangle as blue
    else:
        return 's'  # Square as green

# # Applying the function to assign markers
markers = df["diopter"].apply(assign_marker).tolist()

# # Grid definitions
grid_dicts = {
    'brightness': {"0": 0, "1": 10, "2": 20, "3": 30},
    'contrast': {"0": 0.8, "1": 0.933, "2": 1.066, "3": 1.2},
    'gamma': {"0": 0.5, "1": 0.7, "2": 0.9, "3": 1.1},
    'sharpness': {"0": 0, "1": 0.33, "2": 0.66, "3": 1.0},
    'equalization': {"0": 4, "1": 13, "2": 22, "3": 32}
}

# # Define axis colors (for simplicity, using black for all)
# axis_colors = {feature: 'black' for feature in ['brightness', 'contrast', 'gamma', 'sharpness', 'equalization']}

# # Define the columns to use
columns = ['gamma', 'contrast', 'sharpness', 'brightness', 'equalization']

# # Define combinations of 3 features
combinations_3 = list(itertools.combinations(columns, 3))

# Add 'use_features' column to the dataframe
df["use_features"] = df.apply(lambda row: ''.join([feature for feature in columns if row[feature] != 0]), axis=1)

# Iterate over combinations and create 3D scatter plots
for combo in combinations_3:
    x, y, z = combo
    df_combo = df[df["use_features"].str.contains(x) & df["use_features"].str.contains(y) & df["use_features"].str.contains(z)]

    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')

    # Scatter plot with different markers
    for m in set(markers):
        ax.scatter(df_combo[x][df_combo["diopter"].apply(assign_marker) == m],
                   df_combo[y][df_combo["diopter"].apply(assign_marker) == m],
                   df_combo[z][df_combo["diopter"].apply(assign_marker) == m],
                   marker=m)

    # Configure axes
    for axis, axis_name in [(ax.xaxis, x), (ax.yaxis, y), (ax.zaxis, z)]:
        axis.set_label_text(axis_name)
        axis.set_ticks(list(grid_dicts[axis_name].values()))
        axis._axinfo["grid"]['color'] = 'grey'  # Set grid color to grey for better visibility

    plt.title(f'{x}, {y}, {z} 3D scatter plot')
    plt.show()

