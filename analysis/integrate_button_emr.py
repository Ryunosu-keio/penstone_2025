import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import glob
import os
import natsort

# ボタンログとEMRログを統合する
# 1. ボタンログのstatusが4の行を削除する
# 2. EMRログのstatusが4の行を削除する

# 奇麗にしたボタンログを読み込む
path_button = "../log_removeGap2/"
# 奇麗にしたEMRログを読み込む
path_emr = "../data/integrateddark/"
# path_emr = "../data/integrated_adjust_all/"
path_list_emr = glob.glob(path_emr + "*")
path_list_button = glob.glob(path_button + "*")
emrNum_list = []
for path in path_list_emr:
    emrNum_list.append(path.split("\\")[-1])
df_concated_all = pd.DataFrame()
for num in emrNum_list:
    path_button_num = path_button + num + "_removeGap/"
    path_emr_num = path_emr + num + "/"
    path_list_emr_num = glob.glob(path_emr_num + "*")
    path_list_button_num = glob.glob(path_button_num + "*")
    emr_num_num_list = []
    for path in path_list_emr_num:
        emr_num_num_list.append(path.split("\\")[-1].split(".")[0])

    df_concated = pd.DataFrame()
    for num_num in emr_num_num_list:
        for i in range(len(path_list_button_num)):
            if int(num_num) == int(path_list_button_num[i].split("_")[-1]):
                path_button_num_num = path_list_button_num[i]
        path_emr_num_num = path_emr_num + num_num + ".csv"

        df_emr = pd.read_csv(path_emr_num_num)
        df_button = pd.read_csv(path_button_num_num, sep=" ")
        # ['day', 'time', 'button', 'timeFromStart', 'timeFromDisplay', 'image', 'status']をnanとしてdf_emrに追加
        df_emr['day'] = np.nan
        df_emr['time'] = np.nan
        df_emr['button'] = np.nan
        df_emr['timeFromStart'] = np.nan
        df_emr['timeFromDisplay'] = np.nan
        df_emr["num"] = num
        # df_emr['status'] = np.nan

        for i in range(len(df_emr)):
            # df_emr['time'][i] = df_emr['time'][i].split(".")[0]
            for j in range(len(df_button)):
                if df_button["status"][j] != 4.0:
                    if df_emr["image_name"][i] == df_button["image"][j]:
                        df_emr['timeFromStart'][i] = df_button['timeFromStart'][j]
                        df_emr['timeFromDisplay'][i] = df_button['timeFromDisplay'][j]
                        df_emr['button'][i] = df_button['button'][j]
                        df_emr['day'][i] = df_button['day'][j]
                        df_emr['time'][i] = df_button['time'][j]
                        # df_emr['status'][i] = df_button['status'][j]
        print(df_emr)
        df_emr = df_emr.dropna()
        df_emr = df_emr.reset_index(drop=True)
        print(df_emr)
        df_concated = pd.concat([df_concated, df_emr])
    df_concated = df_concated.reset_index(drop=True)

    # standardize timeFromDisplay
    df_concated["timeFromDisplay_std"] = (
        df_concated["timeFromDisplay"] - df_concated["timeFromDisplay"].mean()) / df_concated["timeFromDisplay"].std()

    df_concated.to_csv("../data/integrate_emr_button_std2/" +
                       num + "_integrated_emr_button.csv")
    df_concated_all = pd.concat([df_concated_all, df_concated])
df_concated_all = df_concated_all.reset_index(drop=True)
df_concated_all.to_csv("../data/all_integrated_emr_button2.csv")
