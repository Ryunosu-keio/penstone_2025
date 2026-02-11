import pandas as pd
import itertools
import os



grid_dicts_3 = {
    'brightness': {"0": 0, "1": 10, "2": 20, "3": 30},
    'contrast': {"0": 0.8, "1": 0.933, "2": 1.066, "3": 1.2},
    'gamma': {"0": 0.5, "1": 0.7, "2": 0.9, "3": 1.1},
    'sharpness': {"0": 0, "1": 0.33, "2": 0.66, "3": 1.0},
    # 'equalization': {"0": 4, "1": 13, "2": 22, "3": 32}
    'equalization': {"0": 3.9, "1": 12.9, "2": 21.9, "3": 32.1}
}


def search_image(df, params):
    for param in params:
        df = df[df[param] > float(params[param][0])]
        df = df[df[param] < float(params[param][1])]
    return df


def grid_num(num, param):
    grid_num_list = []
    if num == 0:
        grid_num_list.append(grid_dicts_3[param]["0"])
        grid_num_list.append(grid_dicts_3[param]["1"])
    elif num == 1:
        grid_num_list.append(grid_dicts_3[param]["1"])
        grid_num_list.append(grid_dicts_3[param]["2"])
    elif num == 2:
        grid_num_list.append(grid_dicts_3[param]["2"])
        grid_num_list.append(grid_dicts_3[param]["3"])
    return grid_num_list


def alphabet_paramname(alpha):
    if alpha == "g":
        return "gamma"
    elif alpha == "c":
        return "contrast"
    elif alpha == "s":
        return "sharpness"
    elif alpha == "b":
        return "brightness"
    elif alpha == "e":
        return "equalization"


def create_params(use_params, use_params_range):
    params_dict = {}
    for i in range(len(use_params)):
        param_name = alphabet_paramname(use_params[i])
        param_range = grid_num(
            int(use_params_range[i]), param_name)
        params_dict[param_name] = param_range
    return params_dict

def generate_combinations():
    param_options = ["g", "c", "s", "b", "e"]
    param_values = [0, 1, 2]

    # パラメータの組み合わせを生成
    param_combinations = itertools.combinations(param_options, 3)

    # 各組み合わせに対して0, 1, 2の値の組み合わせを生成
    for combination in param_combinations:
        for value_combination in itertools.product(param_values, repeat=3):
            yield combination, value_combination
            print(combination, value_combination)

def main():
    print("gamma", "contrast", "sharpness",  "brightness",  "equalization")
    # df = pd.read_excel("../data/final_part1/final_bright_add_modified.xlsx")
    df = pd.read_excel("../data/final_part1/add_contrast_sensitivity_features.xlsx")

    for combination, value_combination in generate_combinations():
        params = create_params(combination, value_combination)
        filtered_df = search_image(df.copy(), params)
        if not filtered_df.empty:
            image_df = filtered_df["image_name"]
            print(image_df)
            os.makedirs("../histogram/all_grids2", exist_ok=True)
            filename = f"../histogram/all_grids2/{combination}_{value_combination}.csv"

            filename = f"../histogram/all_grids2/{combination}_{value_combination}.csv"
            image_df.to_csv(filename)
            print(f"Generated {filename}")
        else:
            print(f"No results for combination {combination} with values {value_combination}")

if __name__ == "__main__":
    main()
