import pandas as pd
import glob
import os
import natsort

# files = glob.glob("../data/integrated_adjust/*/*.csv")
# folders = glob.glob("../data/integrated_adjust/*")
# # output_dir = "../data/integrated_adjust/"
# # if not os.path.exists(output_dir):
# #     os.mkdir(output_dir)
# files = natsort.natsorted(files)
# folders = natsort.natsorted(folders)


# for file in files:
#     file_name = file.split("\\")[-1].split(".")[0] 
#     # df_file =pd.DataFrame() 
#     # for folder in folders:
#     # folder_name = folder.split("\\")[-1]
#     # path = "../data/integrated/"+ folder_name + "/"+ file_name +".csv"   
#     df = pd.read_csv(file)
#     # df[] = df_folder["diopter"]
#     df = df[df["diopter"] < 2]
#     print(f"タスク番号{file_name}")
#     # (print(df_file))
#     # すべての値が0.45以上である行を取得
#     mask = (df_file <= 2.22).all(axis=1)
#     # 上記の条件にマッチするインデックスをリストに変換
#     result_df = df_file[mask]
#     print(result_df)

path = "../data/final_part1/final.xlsx"

df = pd.read_excel(path)

df = df[df["diopter"] < 2]

print(df)
