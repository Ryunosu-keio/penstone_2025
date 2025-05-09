import matplotlib.pyplot as plt
import glob
import pandas as pd
import os



def emr_extract_max(files, output_path, max_limit=10, min_limit=1.5):
    for file in files:
        t = 0
        df = pd.read_csv(file)
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
                    max = 0
                    j = 0
                    while max < df['両眼.注視Z座標[mm]'][t+i+j] or df['両眼.注視Z座標[mm]'][t+i+j] == 0:
                        max = df['両眼.注視Z座標[mm]'][t+i+j]
                        j += 1
                    diop_list.append([t+i+j,max])
                    t += 240
            except KeyError:
                break
        df_diop = pd.DataFrame(diop_list, columns=['フレーム数', '両眼.注視Z座標[mm]'])
        df_diop.to_csv(output_path + file.split("\\")[-1])

        
if __name__ == "__main__":
    if not os.path.exists("../data/emr_extracted"):
        os.mkdir("../data/emr_extracted")
    name = input("被験者番号を入力してください: ")
    path = "../data/devided_emr/"+ name +"/*.csv"
    output_path = "../data/emr_extracted/" + name + "/"
    if not os.path.exists(output_path):
        os.mkdir(output_path)
    files = glob.glob(path)
    emr_extract_max(files, output_path)