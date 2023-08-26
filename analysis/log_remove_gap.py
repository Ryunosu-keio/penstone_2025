import pandas as pd 
import numpy as np
import matplotlib.pyplot as plt
import glob
import os

num = input("被験者番号を入力してください")

log_files = glob.glob("../log/" + num + "/*.txt")

use_list_name_list = log_files[0].split("\\")[-1].split(".")[0].split("_")

use_list_name = use_list_name_list[0] + "_" + use_list_name_list[1] + "_" + use_list_name_list[2]

xlsx_files = glob.glob("../imageCreationExcel/back/" + use_list_name + "/*.xlsx")

output_dir = '../log/' + num + "_removeGap/"
if not os.path.exists(output_dir):
    os.makedirs(output_dir, exist_ok=True)
else:
    print("already exists")

for i in range(len(log_files)):
    times_list = []
    log_file = log_files[i]
    xlsx_file = xlsx_files[i]
    log_file_name = log_file.split("\\")[-1].split(".")[0]
    df_xlsx = pd.read_excel(xlsx_file)
    df_xlsx = df_xlsx[df_xlsx['status'] != 4]
    df_xlsx = df_xlsx.reset_index(drop=True)
    for j in range(len(df_xlsx)):
        times = df_xlsx['image_name'][j].split('_')[0]
        times_list.append(times)
    try:
        df_log = pd.read_csv(log_file, header=None, sep=" ", encoding='utf-8')
    except UnicodeDecodeError:
        try:
            df_log = pd.read_csv(log_file, header=None, sep=" ", encoding='ISO-8859-1')
        except:
            print(f"Could not read the file {log_file} due to encoding issues.")
            continue
    df_log.columns = ['day', 'time', 'button', 'timeFromStart', 'timeFromDisplay', 'image', 'status']
    for j in range(len(df_log)):
        try :
            if int(df_log['status'][j]) == 4:
                for k in range(len(times_list)):
                    if abs(int(times_list[k]) - int(df_log['image'][j].split('_')[0])) < 3:
                        df_log['status'][i] = df_xlsx['status'][k]
                        df_log['image'][i] = df_xlsx['image_name'][k]
                        times_list.pop(k)
                        break
        except ValueError:
            print("ValueError")
            continue
    df_log.to_csv(output_dir + log_file_name , index=False, sep=" ", encoding="utf-8-sig")
