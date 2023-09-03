import pandas as pd
import os
import glob
import matplotlib.pyplot as plt
import numpy as np


def graph_average_image(file_name):
    df = pd.read_excel("../data/final_part1/" + file_name + ".xlsx")
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

    # dio_dictをcsvに出力
    df_dio_dict = pd.DataFrame(dio_dict)
    df_dio_dict.to_csv("../data/final_part1/dio_dict.csv", index=False)

    print(dio_dict)
    # print(new_df)
    new_df = new_df.reset_index(drop=True)
    new_df.to_excel("../data/final_part1/" +
                    file_name + "_mean.xlsx", index=False)


if __name__ == "__main__":
    file_name = input("file_name: ")
    graph_average_image(file_name)
