import matplotlib.pyplot as plt
import glob
import pandas as pd
import natsort

# participant = input("被験者番号を入力してください")

# path = "../data/devided_emr/" + participant + "/*.csv"
# files = glob.glob(path)
# print(files)
# files = natsort.natsorted(files)

# i=0
# for file in files:
#     data = pd.read_csv(file)
#     data['両眼.注視Z座標[mm]'] = 1000/data['両眼.注視Z座標[mm]']
#     # df = df.drop(columns=["フレームカウンタ", "時刻カウンタ", "リセットスイッチ", "CUEシグナル", 
#     #                               "TTL入力", "両眼.タイムアウト", "左眼.タイムアウト", "右眼.タイムアウト"])
#     # x軸を時系列、y軸を"両眼.注視Z座標[mm]"とした折れ線グラフをプロット
#     plt.figure(figsize=(15, 7))
#     # x軸をインデックスにして、y軸を"両眼.注視Z座標[mm]"とした折れ線グラフをプロット
#     # plt.plot(data.index, data['両眼.注視Z座標[mm]'], marker='o', linestyle='-', label='両眼.注視Z座標[mm]')
#     plt.plot(data["番号"]/2, data['両眼.注視Z座標[mm]'], marker='o', linestyle='-')
#     plt.title(file)
#     plt.xlabel('番号')
#     plt.ylabel('両眼.注視Z座標[mm]')
#     plt.grid(True)
#     plt.tight_layout()
#     plt.show()


folders = glob.glob("../data/devided_emr/*")

for folder in folders:
    files = glob.glob(folder + "/*.csv")
    files = natsort.natsorted(files)
    num = 0
    for i in range(2):
        df_concat = pd.DataFrame()
        for j in range(10):
            df = pd.read_csv(files[num])
            df_concat = pd.concat([df_concat, df], axis=0)
            num += 1
            print(df)
            # print(df_concat)
        df_concat = df_concat.reset_index(drop=True)
        df_concat['両眼.注視Z座標[mm]'] = 1000/df_concat['両眼.注視Z座標[mm]']
        df_concat = df_concat[df_concat['両眼.注視Z座標[mm]'] < 15 ]
        plt.scatter(df_concat["番号"]/2, df_concat['両眼.注視Z座標[mm]'], marker='o', s = 1)
        plt.title("被験者" + folder.split("\\")[-1] + "の" + str(i+1) + "回目の実験")
        plt.xlabel('番号')
        plt.ylabel('両眼.注視Z座標[mm]')
        plt.grid(True)
        plt.tight_layout()
        plt.show()

