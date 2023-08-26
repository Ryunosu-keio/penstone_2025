import matplotlib.pyplot as plt
import glob
import pandas as pd


path = "../data/devided_emr/yoshiki/*.csv"
output_path = "../data/emr_extracted/"

files = glob.glob(path)

t = 0

for file in files:
    df = pd.read_csv(file)
    df['両眼.注視Z座標[mm]'] = 1000/df['両眼.注視Z座標[mm]']
    # df['両眼.注視Z座標[mm]'] = 1000/df['両眼.注視Z座標[mm]']
    # 両岸.注視Z座標[mm]が10以上の値を0にする
    for i in range(len(df)):
        if df['両眼.注視Z座標[mm]'][i] > 10:
            df['両眼.注視Z座標[mm]'][i] = 0
    diop_list = []
    for i in range(len(df)):
        key = i + t
        try:
            if df['両眼.注視Z座標[mm]'][key] > 1.5:
                print(i)
                max = 0
                j = 0
                while max < df['両眼.注視Z座標[mm]'][t+i+j] or df['両眼.注視Z座標[mm]'][t+i+j] == 0:
                    max = df['両眼.注視Z座標[mm]'][t+i+j]
                    j += 1
                diop_list.append([i,max])
                t += 240
        except KeyError:
            break
    df_diop = pd.DataFrame(diop_list, columns=['フレーム数', '両眼.注視Z座標[mm]'])
    df_diop.to_csv(output_path + file.split("\\")[-1])

        