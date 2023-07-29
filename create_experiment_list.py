import glob
import random
import pandas as pd

original_images = glob.glob("testpic/*.jpg")

adjust_params = {
    "brightness": [0, 60], # パラメーターの値を入れる
    "contrast": [0.8,1.2],
    "gamma": [0.5,1.1],
    "sharpness":[0, 1.0],
    "equalization":[0,32]
}

condition_list = []
for i in range(50):
    image = random.choice(original_images)
    filename = image.split("/")[-1]
    # filename = filename.split(".")[0]
    selected_parameters = {}
    # random choice from adjust_params by 2~3
    selected_parameters_keys = random.sample(list(adjust_params.keys()), random.randint(2,3))
    # create dataframe [filename, param1, param1_value, param2, param2_value, param3, param3_value]
    for key in selected_parameters_keys:
        selected_parameters[key] = random.uniform(adjust_params[key][0], adjust_params[key][1])
    if len(selected_parameters_keys) == 2:
        condition_list.append([filename, selected_parameters_keys[0], selected_parameters[selected_parameters_keys[0]], selected_parameters_keys[1], selected_parameters[selected_parameters_keys[1]], "None", "None"])
    else:
        condition_list.append([filename, selected_parameters_keys[0], selected_parameters[selected_parameters_keys[0]], selected_parameters_keys[1], selected_parameters[selected_parameters_keys[1]], selected_parameters_keys[2], selected_parameters[selected_parameters_keys[2]]])
df = pd.DataFrame(condition_list, columns=["filename", "param1", "param1_value", "param2", "param2_value", "param3", "param3_value"])
print(df)
df.to_excel("imageCreationExcel/sample2.xlsx", index=False)
