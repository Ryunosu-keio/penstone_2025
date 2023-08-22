import pandas as pd 
import glob


num = input("実験参加者の番号を入力してください")

add_list_for_emr = ["timeFromStart", "timeFromDisplay", "image", "times", "figure", "contrast", "gamma", "sharpness", "brightness", "equalization", "status"]

# 両眼.注視X座標[mm]	両眼.注視Y座標[mm]	両眼.注視Z座標[mm] 左眼.注視X座標[mm]	左眼.注視Y座標[mm]	左眼.注視Z座標[mm] 右眼.注視X座標[mm]	右眼.注視Y座標[mm]	右眼.注視Z座標[mm]
add_list_for_log =["両眼.注視X座標[mm]", "両眼.注視Y座標[mm]", "両眼.注視Z座標[mm]", "左眼.注視x座標", "左眼.注視y座標", "左眼.注視z座標", "右眼.注視x座標", "右眼.注視y座標", "右眼.注視z座標"]
log_file = "log.xlsx"
emr_file = "emr.xlsx"

def get_file_list(path):
    files = glob.glob(path)
    return files

def get_file_name(path):
    file_name = path.split("\\")[-1].split(".")[0]
    return file_name



log_files = get_file_list("log/" + num + "_cleaned/*.csv")
emr_files = get_file_list("data/devided_emr/" + num + "/*.csv")

for i in range(len(log_files)):
    log_df = pd.read_excel(log_files[i])
    emr_df = pd.read_excel(emr_files[i])

    # logの時間を秒からミリ秒に変換
    for j in range(len(log_df)):
        log_df["timeFromStart"][i] = int(log_df["timeFromStart"][i] * 120)
    
    # emr番号を0から始まるようにする
    for j in range(len(emr_df)):
        emr_df["番号"][j] = emr_df["番号"][j] - emr_df["番号"][0]

    # drop column "cueスイッチ" from emr_df
    emr_df = emr_df.drop(columns=["フレームカウンタ", "時刻カウンタ", "リセットスイッチ", "CUEシグナル", 
                                  "TTL入力", "両眼.タイムアウト", "左眼.タイムアウト", "右眼.タイムアウト"])
    # add columns to emr_df
    for column in add_list_for_emr:
        emr_df[column] = [0 for _ in range(len(emr_df))]

    # add log data to emr data       
    for j in range(len(log_df)):
        for column in range(len(add_list_for_emr)):
            emr_df[column][emr_df["番号"] == log_df["timeFromStart"][j]]= log_df[column][j]
    
    # add emr data to log data
    for j in range(len(log_df)):
        for column in range(len(add_list_for_log)):
            log_df[column][j] = emr_df[column][int(log_df["timeFromStart"][j])]

    # save log data
    log_df.to_excel("log/" + get_file_name(log_files[i]) + "_integrated.xlsx")
    emr_df.to_excel("emr/" + get_file_name(emr_files[i]) + "_integrated.xlsx")