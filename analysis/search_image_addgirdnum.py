import pandas as pd
import glob


#########各グリッドのcsvに平均dioとグリッド番号を付ける
# df = pd.read_excel("../data/final_part1/final_bright_add_modified.xlsx")
# print(-1)
# df_dark = pd.read_excel("../data/final_part2/darkfinal_modified.xlsx")
df_dark = pd.read_excel("../data/final_part1/add_contrast_sensitivity_features.xlsx")
# print(0.1)
df_par_grid_list = glob.glob("../histogram/all_grids/*.csv")
# print(0.2)

for i, df_par_grid in enumerate(df_par_grid_list):
    file_name = str(df_par_grid)
    print(file_name)
    df_par_grid = pd.read_csv(df_par_grid)
    df_par_grid = pd.merge(df_par_grid, df_dark[['image_name', 'diopter']], on='image_name', how='left')
    df_par_grid["average_diopter"] = df_par_grid["diopter"].mean()
    df_par_grid["grid_number"] =  i % 27
    print(df_par_grid)
    df_par_grid.to_csv(file_name)
