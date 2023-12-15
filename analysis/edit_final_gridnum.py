


##########平均dioとグリッド番号をfinalに追加


import pandas as pd
import glob

# df_dark データフレームの読み込み
df_dark = pd.read_excel("../data/final_part2/darkfinal_modified.xlsx")

# 新しい列の初期化
df_dark['average_diopter_combined'] = pd.NA
df_dark['grid_number_combined'] = pd.NA

# df_par_grid のCSVファイルのリストを取得
df_par_grid_list = glob.glob("../histogram/all_grids_dark/*.csv")

# 各 df_par_grid CSVファイルに対してループ処理
for df_par_grid_file in df_par_grid_list:
    # CSVファイルを読み込む
    df_par_grid = pd.read_csv(df_par_grid_file)

    # 各行に対する処理
    for _, row in df_par_grid.iterrows():
        image_name = row['image_name']
        average_diopter = row['average_diopter']
        grid_number = row['grid_number']

        # df_dark で対応する行を見つけて値を更新
        df_dark.loc[df_dark['image_name'] == image_name, 'average_diopter_combined'] = average_diopter
        df_dark.loc[df_dark['image_name'] == image_name, 'grid_number_combined'] = grid_number

# 結果を保存
df_dark.to_excel("../data/final_part2/darkfinal_with_combined_data2.xlsx", index=False)
