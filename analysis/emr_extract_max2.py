import matplotlib.pyplot as plt
import glob
import pandas as pd
import os
import natsort


def emr_extract_max(files, output_path, max_limit=10, min_limit=1.5):
    # for fi in range(1):
    #     file = files[fi]
    for file in files:
        t = 0
        df = pd.read_csv(file)
        # nanを0にする
        df = df.fillna(0)
        start = df['番号'][0]
        df['両眼.注視Z座標[mm]'] = 1000/df['両眼.注視Z座標[mm]']
        # df['両眼.注視Z座標[mm]'] = 1000/df['両眼.注視Z座標[mm]']
        # 両岸.注視Z座標[mm]が10以上の値を0にする
        for i in range(len(df)):
            if df['両眼.注視Z座標[mm]'][i] > max_limit or df['両眼.注視Z座標[mm]'][i] < min_limit:
                df['両眼.注視Z座標[mm]'][i] = 0
        diop_list = []
        for i in range(len(df)):
            key = i + t
            try:
                if df['両眼.注視Z座標[mm]'][key] > min_limit:
                    df_sorted = df.iloc[key:key+240,
                                        :].sort_values('両眼.注視Z座標[mm]', ascending=True)
                    df_sorted = df_sorted.reset_index(drop=True)
                    print(df_sorted)
                    df_sorted = df_sorted[df_sorted["両眼.注視Z座標[mm]"] != 0]
                    df_sorted = df_sorted.reset_index(drop=True)
                    print(len(df_sorted))
                    lower_10_percentile = df_sorted["両眼.注視Z座標[mm]"].quantile(
                        0.20)
                    higher_10_percentile = df_sorted["両眼.注視Z座標[mm]"].quantile(
                        0.90)
                    print(lower_10_percentile)
                    df_sorted = df_sorted[df_sorted["両眼.注視Z座標[mm]"]
                                          >= lower_10_percentile]
                    df_sorted = df_sorted[df_sorted["両眼.注視Z座標[mm]"]
                                          <= higher_10_percentile]
                    print(df_sorted)
                    df_sorted = df_sorted.reset_index(drop=True)
                    print(df_sorted['両眼.注視Z座標[mm]'])
                    average = df_sorted['両眼.注視Z座標[mm]'].mean()
                    print("###########################################################")
                    print(average)
                    print(len(df_sorted))
                    num = df_sorted['番号'][0] - start
                    print(num, average)
                    if len(df_sorted) > 1:
                        diop_list.append([num, average])
                        t += 240
            except KeyError:
                break
        df_diop = pd.DataFrame(diop_list, columns=['フレーム数', '両眼.注視Z座標[mm]'])
        df_diop.to_csv(output_path + file.split("\\")[-1])


name_dict = {
    "11": [1.5, 6, 1.5, 12],
    "12": [1.5, 5, 1.5, 8],
    "13": [1.5, 4, 1.5, 4],
    "14": [1.5, 5, 1.5, 1.5],
    "15": [1.5, 5, 1.5, 1.5],
    "16": [1.5, 1.5, 1.5, 1.5],
    "17": [1.5, 6, 1.5, 6],
}

if __name__ == "__main__":
    if not os.path.exists("../data/emr_extracted"):
        os.mkdir("../data/emr_extracted")
    for key in name_dict.keys():
        name = key
        # max_limit_1 = input("最初の10個の最大値を入力してください: ")
        # min_limit_1 = input("最初の10個の最小値を入力してください: ")
        # max_limit_2 = input("最後の10個の最大値を入力してください: ")
        # min_limit_2 = input("最後の10個の最小値を入力してください: ")
        min_limit_1 = name_dict[key][0]
        max_limit_1 = name_dict[key][1]
        min_limit_2 = name_dict[key][2]
        max_limit_2 = name_dict[key][3]
        path = "../data/devided_emr/" + name + "/*.csv"
        output_path = "../data/emr_extracted/" + name + "/"
        if not os.path.exists(output_path):
            os.mkdir(output_path)
        files = glob.glob(path)
        files = natsort.natsorted(files)
        file_names = []
        for file in files:
            file_names.append(int(file.split("\\")[-1].split(".")[0]))
        # filenamesの中の値10のインデックスを取得
        idx = file_names.index(10)
        # idxで二つに分ける
        files1 = files[:idx]
        files2 = files[idx:]
        print(files1, files2)
        emr_extract_max(files1, output_path, float(
            max_limit_1), float(min_limit_1))
        emr_extract_max(files2, output_path, float(
            max_limit_2), float(min_limit_2))
