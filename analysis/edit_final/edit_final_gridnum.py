
# #%%

# ##########平均dioとグリッド番号をfinalに追加


# import pandas as pd
# import glob

# # df_dark データフレームの読み込み
# # df_dark = pd.read_excel("../data/final_part2/darkfinal_with_combined_data3.xlsx")

# df_dark = pd.read_excel("../data/final_part1/add_contrast_sensitivity_features.xlsx")


# # 新しい列の初期化
# df_dark['average_diopter_combined'] = pd.NA
# df_dark['grid_number_combined'] = pd.NA
# df_dark["red_or_blue"] = pd.NA

# # df_par_grid のCSVファイルのリストを取得
# df_par_grid_list = glob.glob("../histogram/all_grids/*.csv")

# # 各 df_par_grid CSVファイルに対してループ処理
# for df_par_grid_file in df_par_grid_list:
#     # CSVファイルを読み込む
#     df_par_grid = pd.read_csv(df_par_grid_file)

#     # 各行に対する処理
#     for _, row in df_par_grid.iterrows():
#         image_name = row['image_name']
#         average_diopter = row['average_diopter']
#         grid_number = row['grid_number']

#         # # df_dark で対応する行を見つけて値を更新
#         df_dark.loc[df_dark['image_name'] == image_name, 'average_diopter_combined'] = average_diopter
#         df_dark.loc[df_dark['image_name'] == image_name, 'grid_number_combined'] = grid_number
#         # df_dark.loc[df_dark['image_name'] == image_name, 'is_red'] = "red"
#         # df_dark.loc[df_dark['image_name'] != image_name, 'is_red'] = "blue"


# # 結果を保存
# # df_dark.to_excel("../data/final_part2/darkfinal_with_combined_data4.xlsx", index=False)
# df_dark.to_excel("../data/final_recent_bright/final_recent_bright_add_gridnum.xlsx", index=False)


#l; %%

############dfにグリッドの色を追加
import pandas as pd
import glob

# df_dark データフレームの読み込み
# df_dark = pd.read_excel("../data/final_part2/darkfinal_with_combined_data3.xlsx")
df_dark = pd.read_excel("../data/final_part1/add_contrast_sensitivity_features.xlsx")

# 新しい列の初期化
df_dark['isred'] = "blue"  # 初期値として "blue" を設定

# df_par_grid のCSVファイルのリストを取得
df_par_grid_list = glob.glob("../histogram/red_grids/*.csv")
# df_par_grid_listをconcatで結合
df_par_grid = pd.concat([pd.read_csv(f) for f in df_par_grid_list], ignore_index=True)  
print(df_par_grid)
# # 全てのファイルに対して処理
# for df_par_grid_file in df_par_grid_list:
#     # CSVファイルを読み込む
#     df_par_grid = pd.read_csv(df_par_grid_file)
# image_name のリストを取得
image_names = df_par_grid['image_name'].unique()
print(image_names)
# 一致する行を "red" に更新
df_dark.loc[df_dark['image_name'].isin(image_names), 'isred'] = "red"
# 一致しない行を"blue"に更新
# df_dark.loc[~df_dark['image_name'].isin(image_names), 'isred'] = "blue"

# 結果を保存
# df_dark.to_excel("../data/final_part2/darkfinal_with_combined_data4.xlsx", index=False)
df_dark.to_excel("../data/final_recent_bright/final_recent_bright_add_.xlsx", index=False)

# # %%
# import pandas as pd
# import glob

# # データフレームの読み込み
# df_dark = pd.read_excel("../data/final_part1/add_contrast_sensitivity_features.xlsx")

# # 新しい列の初期化
# df_dark['average_diopter_combined'] = pd.NA
# df_dark['grid_number_combined'] = pd.NA
# df_dark['is_red'] = "blue"  # 初期値として "blue" を設定

# # df_par_grid のCSVファイルのリストを取得（全グリッド）
# df_par_grid_list_all = glob.glob("../histogram/all_grids2/*.csv")

# # 各 df_par_grid CSVファイルに対してループ処理（全グリッド）
# for df_par_grid_file in df_par_grid_list_all:
#     df_par_grid = pd.read_csv(df_par_grid_file)
#     for _, row in df_par_grid.iterrows():
#         image_name = row['image_name']
#         average_diopter = row['average_diopter']
#         grid_number = row['grid_number']
#         df_dark.loc[df_dark['image_name'] == image_name, 'average_diopter_combined'] = average_diopter
#         df_dark.loc[df_dark['image_name'] == image_name, 'grid_number_combined'] = grid_number

# # df_par_grid のCSVファイルのリストを取得（赤グリッド）
# df_par_grid_list_red = glob.glob("../histogram/red_grids_dark/*.csv")
# df_par_grid_red = pd.concat([pd.read_csv(f) for f in df_par_grid_list_red], ignore_index=True)
# image_names_red = df_par_grid_red['image_name'].unique()

# # 一致する行を "red" に更新
# df_dark.loc[df_dark['image_name'].isin(image_names_red), 'is_red'] = "red"

# # 結果を保存
# df_dark.to_excel("../data/final_recent_bright/final_recent_bright_add_combined.xlsx", index=False)

# # %%
