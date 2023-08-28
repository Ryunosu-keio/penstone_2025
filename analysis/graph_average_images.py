import pandas as pd
import os
import glob
import matplotlib.pyplot as plt
import numpy as np

df = pd.read_excel("../data/final_part1/final.xlsx")
print(df)

# df["diopter"] のデータの種類を全て取得
image_list = df["image_name"].unique().tolist()

dio_dict = {}
for image in image_list:
    df_dio = df[df["image_name"] == image]
    df_dio = df_dio.reset_index(drop=True)

    mean = df_dio["diopter"].mean()
    std = df_dio["diopter"].std()
    dio_dict[image] = [mean, std, len(df_dio)]
    df_mean = df_dio.mean()
    df_mean = df_mean.to_frame().T

    if not "new_df" in locals():
        new_df = df_mean.copy()
    else:
        new_df = pd.concat([df_mean, new_df], axis=0)

# dio_dictのmeanが小さい順に並び替え
dio_dict = sorted(dio_dict.items(), key=lambda x: x[1][0])

print(dio_dict)
print(new_df)
new_df = new_df.reset_index(drop=True)
new_df.to_excel("../data/final_part1/final_mean.xlsx", index=False)
