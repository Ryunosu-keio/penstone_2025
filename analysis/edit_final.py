
#%%

import pandas as pd
import numpy as np


path = "../data/final_part1/final_add.xlsx"
df = pd.read_excel(path)

grid_dicts_3 = {
    'brightness': {"0": 0, "1": 10, "2": 20, "3": 30},
    'contrast': {"0": 0.8, "1": 0.933, "2": 1.066, "3": 1.2},
    'gamma': {"0": 0.5, "1": 0.7, "2": 0.9, "3": 1.1},
    'sharpness': {"0": 0, "1": 0.33, "2": 0.66, "3": 1.0},
    'equalization': {"0": 4, "1": 13, "2": 22, "3": 32}
}

grid_dicts_5 =  {
    'gamma': {"-1": 0.3, "0": 0.5, "1": 0.7, "2": 0.9, "3": 1.1, "4": 1.3},
    'contrast': {"-1": 0.66, "0": 0.8, "1": 0.933, "2": 1.066, "3": 1.2, "4": 1.33},
    'sharpness': {"-1": -0.33, "0": 0, "1": 0.33, "2": 0.66, "3": 1.0, "4": 1.33},
    'brightness': {"-1": -10, "0": 0, "1": 10, "2": 20, "3": 30, "4": 40},
    'equalization': {"-1": 0, "0": 4, "1": 13, "2": 22, "3": 32, "4": 40}
}

def final_exclude_red():
    path = "../data/final_part1/final_add.xlsx"
    df = pd.read_excel(path)  
    conditions = ((df["brightness"] == 0) & (df["equalization"] == 0)  
            & (df["gamma"] >= 0.7) & (df["gamma"] <= 0.9)
            & (df["contrast"] >= 0.8) & (df["contrast"] <= 0.93)
            & (df["sharpness"] >= 0.66) & (df["sharpness"] <= 1.0)
            & (df["folder_name"] >= 18) & (df["folder_name"] <= 23)
            )
    df_red_excluded = df.drop(df[conditions].index)
    print(df_red_excluded)

    df_red_excluded.to_excel("../data/final_part1/final_add_editted.xlsx")

final_exclude_red()




# def plot_3d_grid_color(df, x_feature, y_feature, z_feature, grid_dicts, grid_num):
#     x_values = np.linspace(min(grid_dicts[x_feature].values()), max(
#         grid_dicts[x_feature].values()), grid_num+1)
#     y_values = np.linspace(min(grid_dicts[y_feature].values()), max(
#         grid_dicts[y_feature].values()), grid_num+1)
#     z_values = np.linspace(min(grid_dicts[z_feature].values()), max(
#         grid_dicts[z_feature].values()), grid_num+1)
#     print("gamma:",x_values,"contrast:",y_values,"sharpness:",z_values)

#     # red_x = (x_values[0],x_values[1]) #0.5 0.7
#     # red_y = (y_values[2],y_values[3])
#     # red_z = (z_values[4],z_values[5])

#     red_x = (grid_dicts_5[x_feature]["-1"],grid_dicts_5[x_feature]["0"]) #0.5 0.7
#     red_y = (grid_dicts_5[y_feature]["1"],grid_dicts_5[y_feature]["2"])
#     red_z = (grid_dicts_5[z_feature]["3"],grid_dicts_5[z_feature]["4"])
#     print(red_x,red_y,red_z)
#     conditions = ( (df["gamma"] >= red_x[0]) & (df["gamma"] <= red_x[1])
#             & (df["contrast"] >= red_y[0]) & (df["contrast"] <= red_y[1])
#             & (df["sharpness"] >= red_z[0]) & (df["sharpness"] <= red_z[1])
#             ) 
#     df = df[conditions]
#     print(df)

#%%
#################### 境界を調整して、間違った赤をなくし、final_add_editted_border_adjusted.xlsxを生成

import pandas as pd
import numpy as np

path = "../data/final_part1/final_add_editted.xlsx"
df = pd.read_excel(path)
print(df.loc[168,"sharpness"],
df.loc[180,"gamma"],
df.loc[464,"gamma"])

df.loc[168,"sharpness"]=0.99
df.loc[180,"gamma"]=0.71
df.loc[464,"gamma"]=0.71

df.to_excel("../data/final_part1/final_add_editted_border_adjusted.xlsx")

#%%
######################3#gcsの赤グリッド、追加グリッド内の点分析

import pandas as pd
import numpy as np

path = "../data/final_part1/final_add_editted_border_adjusted.xlsx"
df = pd.read_excel(path)

# gcs_red_1 = {"gamma": [0.7,0.9], "contrast": [0.8,0.93], "sharpness":[0.66, 1.0]}

conditions_wrong_red = ((df["gamma"] >= 0.5) & (df["gamma"] <= 0.7) & (df["contrast"] >= 0.8) & (df["contrast"] <= 0.933) & (df["sharpness"] >= 1.0) & (df["sharpness"] <= 1.33))
conditions_correct_red = ((df["gamma"]>=0.7) & (df["gamma"]<=0.9) & (df["contrast"]>=0.8) & (df["contrast"] <=0.933) & (df["sharpness"]>=0.66) & (df["sharpness"]<=1.0))
key = str(input("conditions_wrong_red : 1, conditions_correct_red :2"))
conditions_dic = {"1":conditions_wrong_red, "2": conditions_correct_red}
df2 = df[conditions_dic[key]]
if key ==1:
    print("wrong_red")
else:
    print("correct_red")
df2
# %%
import pandas as pd
import numpy as np

path = "../data/final_part1/final_add_editted_border_adjusted.xlsx"
df = pd.read_excel(path)

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


gse_red = {"gamma":[0.5,0.7],"sharpness":[0.33,0.66],"equalization":[13,23]}

gse_1 = {"gamma":[0.3,0.5],"sharpness":[0.33,0.66],"equalization":[13,23]}#######追加


cse_red_1 = {"contrast":[0.933,1.066],"sharpness":[0.666,1.0],"equalization":[13,23]}

cse_1 =  {"contrast":[0.933,1.066],"sharpness":[1.0,1.333],"equalization":[13,23]}

cse_red_2 = {"contrast":[0.933,1.066],"sharpness":[0.333,0.666],"equalization":[4,13]}

cse_2 = {"contrast":[0.933,1.066],"sharpness":[0.333,0.666],"equalization":[1,4]}

cse_red_3 = {"contrast":[1.066,1.2],"sharpness":[0.333,0.666],"equalization":[13,23]}

cse_3 = {"contrast":[1.2,1.333],"sharpness":[0.333,0.666],"equalization":[13,23]}


red_dics = [gcs_red_1, gcs_red_2, gse_red, cse_red_1, cse_red_2, cse_red_3]



condition= pd.Series([True] * 3)

# 各キー（フィーチャー名）に対して、条件式を生成


for dic in red_dics:
    for key, values in dic.items():
        condition = ((df[key] >= values[0]) & (df[key] <= values[1]) & (df["folder_name"] >= 18) & (df["folder_name"] <= 23))
        df = df.drop(df[condition].index)

df


#     conditions.append(condition)
# print(conditions)

# # 全ての条件を結合して、一つの条件式を生成
# combined_condition = conditions[0]
# for cond in conditions[1:]:
#     combined_condition = combined_condition & cond
#     combined_condition

# conditions = []
# for dic in param_dics:
#     conditions.append(create_conditions(df, dic))
#     print(conditions)

# conditions_correct_red = create_conditions(df, gcs_red_1)
# print(conditions_correct_red)

# %%
