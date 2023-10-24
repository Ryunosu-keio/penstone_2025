import itertools
import numpy as np
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
from mpl_toolkits.mplot3d import Axes3D
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

params = ["gamma", "contrast", "sharpness",  "brightness",  "equalization"]
combinations_3 = list(itertools.combinations(params, 3))


def calculateCorr(df):
    corr = df["diopter"].corr(df["timeFromDisplay_std"])
    print(corr)


def scatter(df, param1="diopter", param2="timeFromDisplay_std"):
    plt.scatter(df[param1], df[param2])
    plt.show()

# Function to calculate the average diopter in a grid cell


def calculate_grid_ratio(df, x_feature, y_feature, z_feature, x_range, y_range, z_range):
    quantiles = {
        'upper': df['timeFromDisplay_std'].quantile(0.8),
        'lower': df['timeFromDisplay_std'].quantile(0.2)
    }
    filtered_df = df[(df[x_feature] >= x_range[0]) & (df[x_feature] < x_range[1]) &
                     (df[y_feature] >= y_range[0]) & (df[y_feature] < y_range[1]) &
                     (df[z_feature] >= z_range[0]) & (df[z_feature] < z_range[1])]
    df_upper_quantiles = filtered_df[filtered_df['timeFromDisplay_std']
                                     <= quantiles["lower"]]
    df_lower_quantiles = filtered_df[filtered_df['timeFromDisplay_std']
                                     >= quantiles["upper"]]
    if len(filtered_df) == 0:
        return None, None
    upper_quantiles_ratio = len(df_upper_quantiles) / len(filtered_df)
    lower_quantiles_ratio = len(df_lower_quantiles) / len(filtered_df)
    return upper_quantiles_ratio, lower_quantiles_ratio

# Function to assign color based on the average diopter value in a grid cell


# Grid definitions
grid_dicts = {
    'brightness': {"0": 0, "1": 10, "2": 20, "3": 30},
    'contrast': {"0": 0.8, "1": 0.933, "2": 1.066, "3": 1.2},
    'gamma': {"0": 0.5, "1": 0.7, "2": 0.9, "3": 1.1},
    'sharpness': {"0": 0, "1": 0.33, "2": 0.66, "3": 1.0},
    'equalization': {"0": 4, "1": 13, "2": 22, "3": 32}
}


def plot_3d_grid_color(df, x_feature, y_feature, z_feature, grid_dicts):
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

                grid_ratio_upper, grid_ratio_lower = calculate_grid_ratio(
                    df, x_feature, y_feature, z_feature, x_range, y_range, z_range)

                # Determine the color based on quantiles
                if grid_ratio_upper is not None:
                    if grid_ratio_upper >= 0.6:
                        color = 'red'
                    # elif grid_ratio_lower >= 0.5:
                    #     color = 'blue'
                    else:
                        color = 'blue'
                else:
                    color = "blue"

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


def searchPareto(data):
    # Sort the data by 'diopter' in ascending order
    sorted_data = data.sort_values(by='diopter')

    # Initialize an empty list to store pareto optimal points
    pareto_points = []

    # Check each point to see if it's pareto optimal
    for i, row in sorted_data.iterrows():
        is_pareto_optimal = True
        for j, compare_row in sorted_data.iterrows():
            # If there exists a point that has both values less than the current point,
            # then the current point is not pareto optimal
            if compare_row['diopter'] <= row['diopter'] and compare_row['timeFromDisplay_std'] < row['timeFromDisplay_std']:
                is_pareto_optimal = False
                break
        if is_pareto_optimal:
            pareto_points.append(row)

    # Convert the list of pareto optimal points to a DataFrame
    pareto_df = pd.DataFrame(pareto_points)
    pareto_df.to_csv("../data/emr_button_pareto.csv", index=False)
    # Print the pareto optimal points
    print(pareto_df)


def main():
    df = pd.read_csv("../data/all_integrated_emr_button_removeNan.csv")
    dio_divide(df)
    # scatter(df)
    # calculateCorr(df)
    # df = pd.read_excel("../data/onlytest.xlsx")
    # df = df.dropna()
    # df = df[df["diopter"] != 0]
    # df = df[df["timeFromDisplay_std"] != 0]

    # df.to_csv("../data/all_integrated_emr_button_removeNan.csv", index=False)
    # sns.heatmap(df.corr())
    # plt.show()
    # for param in params:
    #     scatter(df, param1=param)
    # scatter(df)

    # Calculate 10th and 90th percentile values for the diopter

    # # Plotting the 3D scatter plot with transparent colored grids for the first combination as an example
    # plot_3d_grid_color(df, combinations_3[0][0], combinations_3[0]
    #                    [1], combinations_3[0][2], grid_dicts)

    # # Plotting the 3D scatter plots with transparent colored grids for the remaining combinations
    # # Skip the first combination as it was already plotted
    # for combo in combinations_3[1:]:
    #     plot_3d_grid_color(df, combo[0], combo[1],
    #                        combo[2], grid_dicts)

    # # # Extract the Pareto optimal points
    # # pareto_points = df[df.apply(lambda x: is_pareto_optimal(x, df), axis=1)]
    # # print(pareto_points)
    # # print(pareto_points[['diopter', 'timeFromDisplay_std']])
    # # searchPareto(df)


def dio_divide(df):
    df_1 = df[(df["diopter"] <= 2.0) & (df["diopter"] >= 1.0)]
    df_2 = df[(df["diopter"] <= 3.0) & (df["diopter"] >= 2.0)]
    df_3 = df[(df["diopter"] <= 4.0) & (df["diopter"] >= 3.0)]
    df_4 = df[df["diopter"] >= 4.0]
    df_1_mean = df_1["timeFromStart"].mean()
    df_2_mean = df_2["timeFromStart"].mean()
    df_3_mean = df_3["timeFromStart"].mean()
    df_4_mean = df_4["timeFromStart"].mean()
    print(df_1_mean)
    print(df_2_mean)
    print(df_3_mean)
    print(df_4_mean)


if __name__ == "__main__":
    main()
