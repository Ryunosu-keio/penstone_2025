from mpl_toolkits.mplot3d import Axes3D
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
import numpy as np
import pandas as pd
import itertools
import matplotlib.pyplot as plt

# Function to calculate the average diopter in a grid cell


def calculate_grid_average(df, x_feature, y_feature, z_feature, x_range, y_range, z_range):
    filtered_df = df[(df[x_feature] >= x_range[0]) & (df[x_feature] < x_range[1]) &
                     (df[y_feature] >= y_range[0]) & (df[y_feature] < y_range[1]) &
                     (df[z_feature] >= z_range[0]) & (df[z_feature] < z_range[1])]
    return filtered_df['diopter'].mean()

# Function to assign color based on the average diopter value in a grid cell


def assign_grid_color(value, overall_mean):
    if value is None:
        return 'gray'  # No data in this grid cell
    if value > overall_mean:
        return 'red'
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
#############################################################################################
# grid_dicts =  {
#     'gamma': {"-1": 0.3, "0": 0.5, "1": 0.7, "2": 0.9, "3": 1.1, "4": 1.3},
#     'contrast': {"-1": 0.66, "0": 0.8, "1": 0.933, "2": 1.066, "3": 1.2, "4": 1.33},
#     'sharpness': {"-1": -0.33, "0": 0, "1": 0.33, "2": 0.66, "3": 1.0, "4": 1.33},
#     'brightness': {"-1": -10, "0": 0, "1": 10, "2": 20, "3": 30, "4": 40},
#     'equalization': {"-1": 0, "0": 4, "1": 13, "2": 22, "3": 32, "4": 40}
# }

############################################################################################

# Feature combinations
columns = ['gamma', 'contrast', 'sharpness', 'brightness', 'equalization']
combinations_3 = list(itertools.combinations(columns, 3))

# Plotting the 3D scatter plot with grid averages for the first combination as an example


# Function to plot 3D scatter plot with transparent colored grids


def plot_3d_grid_color(df, x_feature, y_feature, z_feature, grid_dicts, quantiles, grid_num):
    x_values = np.linspace(min(grid_dicts[x_feature].values()), max(
        grid_dicts[x_feature].values()), grid_num+1)
    y_values = np.linspace(min(grid_dicts[y_feature].values()), max(
        grid_dicts[y_feature].values()), grid_num+1)
    z_values = np.linspace(min(grid_dicts[z_feature].values()), max(
        grid_dicts[z_feature].values()), grid_num+1)

    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')

    for i in range(grid_num):
        for j in range(grid_num):
            for k in range(grid_num):
                x_range = (x_values[i], x_values[i + 1])
                y_range = (y_values[j], y_values[j + 1])
                z_range = (z_values[k], z_values[k + 1])

                grid_avg = calculate_grid_average(
                    df, x_feature, y_feature, z_feature, x_range, y_range, z_range)

                # Determine the color based on quantiles
                if grid_avg is not None:
                    if grid_avg >= quantiles['upper']:
                        color = 'blue'
                    elif grid_avg <= quantiles['lower']:
                        color = 'red'
                    else:
                        color = 'green'

                    # Draw a transparent cube
                    r = [x_range[0], x_range[1]]
                    s = [y_range[0], y_range[1]]
                    t = [z_range[0], z_range[1]]
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

    ax.set_xlabel(x_feature)
    ax.set_ylabel(y_feature)
    ax.set_zlabel(z_feature)
    plt.title(f"{x_feature}, {y_feature}, {z_feature} (Colored Grids)")
    plt.show()


# path = "../data/final_part1/final_test2_mean2.xlsx"

#########################################################
data = input("図示するエクセルデータを選んでください")
path = "../data/final_part1/"+ data + ".xlsx"
#########################################################

df = pd.read_excel(path)

# Calculate 10th and 90th percentile values for the diopter
quantiles = {
    'upper': df['diopter'].quantile(0.9),
    'lower': df['diopter'].quantile(0.1)
}

# Plotting the 3D scatter plot with transparent colored grids for the first combination as an example
plot_3d_grid_color(df, combinations_3[0][0], combinations_3[0]
                   [1], combinations_3[0][2], grid_dicts, quantiles, grid_num=3)

# Plotting the 3D scatter plots with transparent colored grids for the remaining combinations
# Skip the first combination as it was already plotted
for combo in combinations_3[1:]:
    plot_3d_grid_color(df, combo[0], combo[1], combo[2], grid_dicts, quantiles, grid_num=3)
