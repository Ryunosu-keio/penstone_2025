import glob
import random
import pandas as pd

savefile = input("保存するファイル名を入力してください")

original_images = glob.glob("testpic/*.jpg")

# adjust_params = {
#     "brightness": [0, 30], # パラメーターの値を入れる
#     "contrast": [0.8,1.2],
#     "gamma": [0.5,1.1],
#     "sharpness":[0, 1.0],
#     "equalization":[4,32]
# }

#################################################################################################################
# adjust_params_cse_0 = {
#     "contrast": [0.933,1.066],
#     "sharpness":[0.33, 0.66],
#     "equalization":[4,13.33]
# }

# adjust_params_gcs_0 = {
#     "gamma": [0.7,0.9],
#     "contrast": [0.8,0.93],
#     "sharpness":[0.66, 1.0]
# }

# cse_1 = {"contrast": [0.933,1.066],"sharpness":[0.33, 0.66],"equalization":[0,4]}

# cse_2 = {"contrast": [1.2,1.333], "sharpness":[0.33, 0.66], "equalization":[13.33,22.66]}

# cse_void = {"contrast": [1.066,1.2], "sharpness":[0.33, 0.66], "equalization":[22.66,32]}


gcs_red_1 = {"gamma": [0.7,0.9], "contrast": [0.8,0.93], "sharpness":[0.66, 1.0]}

gcs_1 = {"gamma": [0.7,0.9], "contrast": [0.8,0.93], "sharpness":[1.0, 1.33]}

gcs_2 = {"gamma": [0.7,0.9], "contrast": [0.66,0.8], "sharpness":[1.0, 1.33]}

gcs_3 = {"gamma": [0.7,0.9], "contrast": [0.66,0.8], "sharpness":[0.66, 1.0]}


gcs_red_2 = {"gamma": [0.9,1.1], "contrast": [1.066,1.2], "sharpness":[0.33, 0.66]}

gcs_4 = {"gamma": [0.9,1.1], "contrast": [1.2,1.333], "sharpness":[0.33, 0.66]}

gcs_5 = {"gamma": [1.1,1.3], "contrast": [1.066,1.2], "sharpness":[0.33, 0.66]}

gcs_6 = {"gamma": [1.1,1.3], "contrast": [1.2,1.333], "sharpness":[0.33, 0.66]}

gcs_void = {"gamma": [0.5,0.7], "contrast": [0.8,0.93], "sharpness":[0.66, 1.0]}


gcb_void = {"gamma": [0.7,1.1], "contrast": [1.066,1.2], "brightness":[20,30]}


gse = {"gamma":[0.3,0.7],"sharpness":[0.33,0.66],"equalization":[13.33,22.66]}

cse_1 = {"contrast":[0.933,1.066],"sharpness":[0.666,1.333],"equalization":[13.33,22.66]}

cse_2 = {"contrast":[0.933,1.066],"sharpness":[0.333,0.666],"equalization":[0,13.33]}

cse_3 = {"contrast":[1.066,1.333],"sharpness":[0.333,0.666],"equalization":[13.33,22.66]}

param_dics = [gcs_red_1,gcs_1,gcs_2,gcs_3,gcs_red_2,gcs_4,gcs_5,gcs_6,gcs_void,gcb_void,gse,cse_1,cse_2,cse_3]

#################################################################################################################
condition_list = []
for i in range(50):
    image = random.choice(original_images)
    if "/" in image :
        filename = image.split("/")[-1]
        filename = "testpic/" + filename
    else:
        filename = image.split("\\")[-1]
        filename = "testpic\\" + filename
    # filename = filename.split(".")[0]
    selected_parameters = {}


    # random choice from adjust_params by 2~3
    # selected_parameters_keys = random.sample(list(adjust_params.keys()), random.randint(2,3))

##############################################################################################################################
    selected_param_dic = random.choice(param_dics)
    selected_parameters_keys = list(selected_param_dic.keys())
##############################################################################################################################

    # Check if 'equalization' is selected and move it to the end
    if "equalization" in selected_parameters_keys:
        selected_parameters_keys.remove("equalization")
        selected_parameters_keys.append("equalization")
    # create dataframe [filename, param1, param1_value, param2, param2_value, param3, param3_value]
    for key in selected_parameters_keys:
        # selected_parameters[key] = random.uniform(adjust_params[key][0], adjust_params[key][1])
        
##################################################################################################################################################
        selected_parameters[key] = random.uniform(selected_param_dic[key][0], selected_param_dic[key][1])
##################################################################################################################################################
    if len(selected_parameters_keys) == 2:
        condition_list.append([filename, selected_parameters_keys[0], selected_parameters[selected_parameters_keys[0]], selected_parameters_keys[1], selected_parameters[selected_parameters_keys[1]], "None", "None"])
    else:
        condition_list.append([filename, selected_parameters_keys[0], selected_parameters[selected_parameters_keys[0]], selected_parameters_keys[1], selected_parameters[selected_parameters_keys[1]], selected_parameters_keys[2], selected_parameters[selected_parameters_keys[2]]])
df = pd.DataFrame(condition_list, columns=["filename", "param1", "param1_value", "param2", "param2_value", "param3", "param3_value"])
print(df)
df.to_excel("imageCreationExcel/" + savefile  + ".xlsx", index=False)
print(condition_list)