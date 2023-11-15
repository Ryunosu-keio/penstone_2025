import pandas as pd

grid_dicts_3 = {
    'brightness': {"0": 0, "1": 10, "2": 20, "3": 30},
    'contrast': {"0": 0.8, "1": 0.933, "2": 1.066, "3": 1.2},
    'gamma': {"0": 0.5, "1": 0.7, "2": 0.9, "3": 1.1},
    'sharpness': {"0": 0, "1": 0.33, "2": 0.66, "3": 1.0},
    'equalization': {"0": 4, "1": 13, "2": 22, "3": 32}
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


if __name__ == "__main__":
    print("gamma", "contrast", "sharpness",  "brightness",  "equalization")
    param1_num = input("Enter param num: ")
    param2_num = input("Enter param num: ")
    param3_num = input("Enter param num: ")
    use_params = [param1_num, param2_num, param3_num]
    param1_range = input("Enter param lowrange: ")
    param2_range = input("Enter param lowrange: ")
    param3_range = input("Enter param lowrange: ")
    use_params_range = [param1_range, param2_range, param3_range]
    params = create_params(use_params, use_params_range)
    df = pd.read_excel("../data/final_part2/darkfinal_modified.xlsx")
    df = search_image(df, params)
    image_df = df["image_name"]
    print(image_df)
