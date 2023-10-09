from mpl_toolkits.mplot3d import Axes3D
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
import numpy as np
import pandas as pd
import itertools
import matplotlib.pyplot as plt

# Function to calculate the average diopter in a grid cell


def calculate_grid_ratio(df, x_feature, y_feature, z_feature, x_range, y_range, z_range):
    filtered_df = df[(df[x_feature] >= x_range[0]) & (df[x_feature] <= x_range[1]) &
                     (df[y_feature] >= y_range[0]) & (df[y_feature] <= y_range[1]) &
                     (df[z_feature] >= z_range[0]) & (df[z_feature] <= z_range[1])]
    df_upper_quantiles = filtered_df[filtered_df["diopter"]
                                     <= quantiles["lower"]]
    if len(filtered_df) == 0:
        return None
    upper_quantiles_ratio = len(df_upper_quantiles) / len(filtered_df)
    return upper_quantiles_ratio
    # return filtered_df['diopter'].mean()

# Function to assign color based on the average diopter value in a grid cell


# def assign_grid_color(value, overall_mean):
#     if value is None:
#         return 'gray'  # No data in this grid cell
#     if value > overall_mean:
#         return 'red'
#     else:
#         return 'blue'


# Grid definitions
grid_dicts = {
    'brightness': {"0": 0, "1": 10, "2": 20, "3": 30},
    'contrast': {"0": 0.8, "1": 0.933, "2": 1.066, "3": 1.2},
    'gamma': {"0": 0.5, "1": 0.7, "2": 0.9, "3": 1.1},
    'sharpness': {"0": 0, "1": 0.33, "2": 0.66, "3": 1.0},
    'equalization': {"0": 4, "1": 13, "2": 22, "3": 32}
}

# Feature combinations
columns = ['gamma', 'contrast', 'sharpness', 'brightness', 'equalization']
combinations_3 = list(itertools.combinations(columns, 3))

# Plotting the 3D scatter plot with grid averages for the first combination as an example


# Function to plot 3D scatter plot with transparent colored grids


def plot_3d_grid_color(df, x_feature, y_feature, z_feature, grid_dicts, quantiles):
    x_values = np.linspace(min(grid_dicts[x_feature].values()), max(
        grid_dicts[x_feature].values()), 4)
    y_values = np.linspace(min(grid_dicts[y_feature].values()), max(
        grid_dicts[y_feature].values()), 4)
    z_values = np.linspace(min(grid_dicts[z_feature].values()), max(
        grid_dicts[z_feature].values()), 4)

    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')

    for i in range(3):
        for j in range(3):
            for k in range(3):
                x_range = (x_values[i], x_values[i + 1])
                y_range = (y_values[j], y_values[j + 1])
                z_range = (z_values[k], z_values[k + 1])

                upper_quantiles_ratio = calculate_grid_ratio(
                    df, x_feature, y_feature, z_feature, x_range, y_range, z_range)

                # Determine the color based on quantiles
                if upper_quantiles_ratio is not None:
                    if upper_quantiles_ratio >= 0.6:
                        color = 'red'
                    else:
                        color = 'blue'

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


path = "../data/final_part1/final_test2_mean2.xlsx"

df = pd.read_excel(path)

# Calculate 10th and 90th percentile values for the diopter
quantiles = {
    'upper': df['diopter'].quantile(0.9),
    'lower': df['diopter'].quantile(0.1)
}

# Plotting the 3D scatter plot with transparent colored grids for the first combination as an example
plot_3d_grid_color(df, combinations_3[0][0], combinations_3[0]
                   [1], combinations_3[0][2], grid_dicts, quantiles)

# Plotting the 3D scatter plots with transparent colored grids for the remaining combinations
# Skip the first combination as it was already plotted
for combo in combinations_3[1:]:
    plot_3d_grid_color(df, combo[0], combo[1], combo[2], grid_dicts, quantiles)

print(quantiles["upper"], quantiles["lower"])
