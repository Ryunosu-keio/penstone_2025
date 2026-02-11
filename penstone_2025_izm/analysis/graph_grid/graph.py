import matplotlib.pyplot as plt
import glob
import pandas as pd
import natsort

# ============================================================
# EMR デバイス依存の列名（機種変更時はここだけ変える）
# ============================================================
EMR_COL_FRAME  = "番号"                  # フレーム番号
EMR_COL_BOTH_Z = "両眼.注視Z座標[mm]"     # 両眼注視Z座標

participant = input("被験者番号を入力してください")

path = "../data/devided_emr/" + participant + "/*.csv"
files = glob.glob(path)
print(files)
files = natsort.natsorted(files)

i=0
for file in files:
    data = pd.read_csv(file)
    data[EMR_COL_BOTH_Z] = 1000/data[EMR_COL_BOTH_Z]
    # df = df.drop(columns=["フレームカウンタ", "時刻カウンタ", "リセットスイッチ", "CUEシグナル",
    #                               "TTL入力", "両眼.タイムアウト", "左眼.タイムアウト", "右眼.タイムアウト"])
    plt.figure(figsize=(15, 7))
    data = data[data[EMR_COL_BOTH_Z] < 20]
    plt.plot(data[EMR_COL_FRAME]/2, data[EMR_COL_BOTH_Z], marker='o', linestyle='-')
    plt.title(file)
    plt.xlabel(EMR_COL_FRAME)
    plt.ylabel(EMR_COL_BOTH_Z)
    plt.grid(True)
    plt.tight_layout()
    plt.show()


    
        # df.to_excel(file.split(".")[0] + ".xlsx")