
# %%

import pandas as pd
import numpy as np

# %%

path = "../data/final_part1/final_majitetanomu.xlsx"
df = pd.read_excel(path)

grid_dicts_3 = {
    'brightness': {"0": 0, "1": 10, "2": 20, "3": 30},
    'contrast': {"0": 0.8, "1": 0.933, "2": 1.066, "3": 1.2},
    'gamma': {"0": 0.5, "1": 0.7, "2": 0.9, "3": 1.1},
    'sharpness': {"0": 0, "1": 0.33, "2": 0.66, "3": 1.0},
    'equalization': {"0": 4, "1": 13, "2": 22, "3": 32}
}

grid_dicts_5 = {
    'gamma': {"-1": 0.3, "0": 0.5, "1": 0.7, "2": 0.9, "3": 1.1, "4": 1.3},
    'contrast': {"-1": 0.66, "0": 0.8, "1": 0.933, "2": 1.066, "3": 1.2, "4": 1.33},
    'sharpness': {"-1": -0.33, "0": 0, "1": 0.33, "2": 0.66, "3": 1.0, "4": 1.33},
    'brightness': {"-1": -10, "0": 0, "1": 10, "2": 20, "3": 30, "4": 40},
    'equalization': {"-1": 0, "0": 4, "1": 13, "2": 22, "3": 32, "4": 40}
}


def final_exclude_red():
    path = "../data/final_part1/final_majitetanomu.xlsx"
    df = pd.read_excel(path)
    conditions = ((df["brightness"] == 0) & (df["equalization"] == 0)
                  & (df["gamma"] >= 0.7) & (df["gamma"] <= 0.9)
                  & (df["contrast"] >= 0.8) & (df["contrast"] <= 0.933)
                  & (df["sharpness"] >= 0.66) & (df["sharpness"] <= 1.0)
                  & (df["folder_name"] >= 18) & (df["folder_name"] <= 23)
                  )
    df_red_excluded = df.drop(df[conditions].index)
    df = df.drop(df[condition].index)

    print(df_red_excluded)

    df_red_excluded.to_excel(
        "../data/final_part1/final_majidetanomu_editted.xlsx")


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

# %%
# 境界を調整して、間違った赤をなくし、final_add_editted_border_adjusted.xlsxを生成


path = "../data/final_part1/final_add_editted.xlsx"
df = pd.read_excel(path)
print(df.loc[168, "sharpness"],
      df.loc[180, "gamma"],
      df.loc[464, "gamma"])

df.loc[168, "sharpness"] = 0.99
df.loc[180, "gamma"] = 0.71
df.loc[464, "gamma"] = 0.71

df.to_excel("../data/final_part1/final_add_editted_border_adjusted.xlsx")

# %%
# 3#gcsの赤グリッド、追加グリッド内の点分析


path = "../data/final_part1/final_add_editted_border_adjusted.xlsx"
df = pd.read_excel(path)

# gcs_red_1 = {"gamma": [0.7,0.9], "contrast": [0.8,0.93], "sharpness":[0.66, 1.0]}


conditions_wrong_red = ((df["gamma"] >= 0.5) & (df["gamma"] <= 0.7) & (df["contrast"] >= 0.8) & (
    df["contrast"] <= 0.933) & (df["sharpness"] >= 1.0) & (df["sharpness"] <= 1.33))
conditions_correct_red = ((df["gamma"] >= 0.7) & (df["gamma"] <= 0.9) & (df["contrast"] >= 0.8) & (
    df["contrast"] <= 0.933) & (df["sharpness"] >= 0.66) & (df["sharpness"] <= 1.0))

key = str(input("conditions_wrong_red : 1, conditions_correct_red :2"))
conditions_dic = {"1": conditions_wrong_red, "2": conditions_correct_red}
df2 = df[conditions_dic[key]]
if key == 1:
    print("wrong_red")
else:
    print("correct_red")
df2


# %%
def refer_block():
    path = "../data/final_part1/final_test2_mean2.xlsx"
    # path = "../data/final_part1/final_ave_until17_fuck.xlsx"
    df = pd.read_excel(path)
    conditions_original = ((df["brightness"] == 0) & (df["equalization"] == 0)
                           & (df["gamma"] >= 0.5) & (df["gamma"] <= 0.7)
                           & (df["contrast"] >= 1.066) & (df["contrast"] <= 1.2)
                           & (df["sharpness"] >= 0.33) & (df["sharpness"] <= 0.66)
                           #    & (df["folder_name"] >= 2) & (df["folder_name"] <= 17)
                           )
    conditions_additional = ((df["brightness"] == 0) & (df["equalization"] == 0)
                             & (df["gamma"] >= 0.5) & (df["gamma"] <= 0.7)
                             & (df["contrast"] >= 1.066) & (df["contrast"] <= 1.2)
                             & (df["sharpness"] >= 0.33) & (df["sharpness"] <= 0.66)
                             #  & (df["folder_name"] >= 18) & (df["folder_name"] <= 23)
                             )
    df_refer_ori = df[conditions_original]
    df_refer_add = df[conditions_additional]
    print(df_refer_ori)
    print(df_refer_add)


refer_block()

# %%
gcs_red_1 = {"gamma": [0.7,0.9], "contrast": [
  0.8,0.933], "sharpness":[0.66, 1.0]}

gcs_1 = {"gamma": [0.7, 0.9], "contrast": [
    0.8, 0.93], "sharpness": [1.0, 1.33]}


gcs_2 = {"gamma": [0.7, 0.9], "contrast": [
    0.66, 0.8], "sharpness": [1.0, 1.33]}



gcs_3 = {"gamma": [0.7, 0.9], "contrast": [
    0.66, 0.8], "sharpness": [0.66, 1.0]}


gcs_red_2 = {"gamma": [0.9, 1.1], "contrast": [
    1.066, 1.2], "sharpness": [0.33, 0.66]}

gcs_4 = {"gamma": [0.9, 1.1], "contrast": [
    1.2, 1.333], "sharpness": [0.33, 0.66]}

gcs_5 = {"gamma": [1.1, 1.3], "contrast": [
    1.066, 1.2], "sharpness": [0.33, 0.66]}

gcs_6 = {"gamma": [1.1, 1.3], "contrast": [
    1.2, 1.333], "sharpness": [0.33, 0.66]}

gcs_void = {"gamma": [0.5, 0.7], "contrast": [
    0.8, 0.93], "sharpness": [0.66, 1.0]}


gcb_void = {"gamma": [0.7, 1.1], "contrast": [
    1.066, 1.2], "brightness": [20, 30]}


gse_red = {"gamma": [0.5, 0.7], "sharpness": [
    0.33, 0.66], "equalization": [13, 23]}

gse_1 = {"gamma": [0.3, 0.5], "sharpness": [
    0.33, 0.66], "equalization": [13, 23]}  # 追加


cse_red_1 = {"contrast": [0.933, 1.066], "sharpness": [
    0.666, 1.0], "equalization": [13, 23]}

cse_1 = {"contrast": [0.933, 1.066], "sharpness": [
    1.0, 1.333], "equalization": [13, 23]}

cse_red_2 = {"contrast": [0.933, 1.066], "sharpness": [
    0.333, 0.666], "equalization": [4, 13]}

cse_2 = {"contrast": [0.933, 1.066], "sharpness": [
    0.333, 0.666], "equalization": [1, 4]}

cse_red_3 = {"contrast": [1.066, 1.2], "sharpness": [
    0.333, 0.666], "equalization": [13, 23]}

cse_3 = {"contrast": [1.2, 1.333], "sharpness": [
    0.333, 0.666], "equalization": [13, 23]}


red_dics = [gcs_red_1, gcs_red_2, gse_red, cse_red_1, cse_red_2, cse_red_3]

red_dics_name = ["gcs_red_1", "gcs_red_2", "gse_red", "cse_red_1", "cse_red_2", "cse_red_3"]


path = "../data/final_part1/final_add_editted.xlsx"
df = pd.read_excel(path)

for dic in red_dics:
    condition = pd.Series([True] * len(df), index=df.index)
    for key, values in dic.items():
        condition &= ((df[key] >= values[0]) & (df[key] <= values[1]))
    condition &= (df["folder_name"] >= 18) & (df["folder_name"] <= 23)
    df = df.drop(df[condition].index)
df.to_excel("../data/final_part1/final_majidetanomu_editted2.xlsx")


condition= pd.Series([True] * len(df))
for key, values in gcs_red_2.items():
    condition &= ((df[key] >= values[0]) & (df[key] <= values[1]) )
df = df[condition]
df.to_csv("../data/final_part1/final_gcs_red_2.csv")
# df.to_excel("../data/final_part1/final_red/"+ red_dics_name +".xlsx")       
#     conditions.append(condition)_
# print(conditions)
#%%
from itertools import combinations, product

adjust_params = {
    "brightness": [0, 30],  
    "contrast": [0.8, 1.2],
    "gamma": [0.5, 1.1],
    "sharpness": [0, 1.0],
    "equalization": [4, 32]
}

# 3つのキーの組み合わせを取得
three_key_combinations = list(combinations(adjust_params.keys(), 3))

# 各キーに対する値のリストを3分割する関数
def split_into_three(r):
    return [(round(r[0] + (r[1] - r[0]) * i/3, 2), round(r[0] + (r[1] - r[0]) * (i+1)/3, 2)) for i in range(3)]

all_combinations = []

# 3つのキーのそれぞれの組み合わせに対して処理
for comb in three_key_combinations:
    ranges = [split_into_three(adjust_params[key]) for key in comb]
    
    # 3つのキーのそれぞれの3分割したリストのすべての組み合わせを作成
    for values in product(*ranges):
        dic = {comb[i]: values[i] for i in range(3)}
        all_combinations.append(dic)

# 結果を表示
for comb in all_combinations:
    print(comb)



# %%import openpyxl
import os

def replace_content(source_file, target_file):
    # ソースファイルからワークブックをロード
    source_wb = openpyxl.load_workbook(source_file)
    
    # ターゲットファイルからワークブックをロード
    target_wb = openpyxl.load_workbook(target_file)

    # ターゲットのワークブックの全てのシートを削除
    for sheet in target_wb.sheetnames:
        del target_wb[sheet]

    # ソースのワークブックからシートをコピーしてターゲットのワークブックに追加
    for sheet_name in source_wb.sheetnames:
        source_sheet = source_wb[sheet_name]
        target_sheet = target_wb.create_sheet(sheet_name)

        for row in source_sheet:
            for cell in row:
                target_sheet[cell.coordinate].value = cell.value

    # ターゲットファイルを上書き保存
    target_wb.save(target_file)

# パスの修正
base_dir = "../imageCreationExcel/back"
source_folder = f"{base_dir}/101"

# mapping_files = {
#     "101_0.xlsx": "_0.xlsx",
#     "101_1.xlsx": "_1.xlsx",
#     "101_10.xlsx": "_10.xlsx",
#     "101_11.xlsx": "_11.xlsx"
# }

mapping_files = {
    "101_0.xlsx": "_0.xlsx"
}
for i in range(102, 103):
    target_folder = f"{base_dir}/{i}"
    for source_name, target_suffix in mapping_files.items():
        source_file_path = os.path.join(source_folder, source_name)
        target_file_path = os.path.join(target_folder, f"{i}{target_suffix}")

        if os.path.exists(source_file_path) and os.path.exists(target_file_path):
            replace_content(source_file_path, target_file_path)
        else:
            print(f"Warning: {source_file_path} or {target_file_path} does not exist!")

print("Process Completed.")

# %%
