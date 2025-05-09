import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import glob
import os
import natsort


def log_remove_gap(num):
    # num = input("被験者番号を入力してください")

    log_files = glob.glob("../log/" + num + "/*.txt")
    log_files = natsort.natsorted(log_files)

    if int(num) <= 10:
        use_list_name_list = log_files[0].split(
            "\\")[-1].split(".")[0].split("_")
        use_list_name = use_list_name_list[0] + "_" + \
            use_list_name_list[1] + "_" + use_list_name_list[2]
    elif int(num) == 11:
        use_list_name = "0831_1"
    else:
        use_list_name_list = log_files[0].split(
            "\\")[-1].split(".")[0].split("_")
        use_list_name = use_list_name_list[0]

    xlsx_files = glob.glob(
        "../imageCreationExcel/back/" + use_list_name + "/*.xlsx")
    xlsx_files = natsort.natsorted(xlsx_files)

    output_dir = '../log_removeGap2/' + num + "_removeGap/"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir, exist_ok=True)
    else:
        print("already exists")

    for i in range(len(log_files)):
        times_list = []
        log_file = log_files[i]
        xlsx_file = xlsx_files[i]
        print(log_file)
        print(xlsx_file)
        log_file_name = log_file.split("\\")[-1].split(".")[0]
        df_xlsx = pd.read_excel(xlsx_file)
        df_xlsx = df_xlsx[df_xlsx['status'] != 4]
        print(df_xlsx)
        df_xlsx = df_xlsx.reset_index(drop=True)
        print(df_xlsx)
        for j in range(len(df_xlsx)):
            times = df_xlsx['image_name'][j].split('_')[0]
            times_list.append(times)
        try:
            df_log = pd.read_csv(log_file, header=None,
                                 sep=" ", encoding='utf-8')
        except UnicodeDecodeError:
            try:
                df_log = pd.read_csv(log_file, header=None,
                                     sep=" ", encoding='ISO-8859-1')
            except:
                print(
                    f"Could not read the file {log_file} due to encoding issues.")
                continue
        df_log.columns = ['day', 'time', 'button',
                          'timeFromStart', 'timeFromDisplay', 'image', 'status']
        df_log = df_log[df_log['button'].isin(["t", "f"])]
        df_log = df_log.drop(df_log.index[::2])
        df_log = df_log.reset_index(drop=True)

        v = 0
        for j in range(len(df_log)):
            try:
                # if int(df_log['status'][j]) == 4:
                #     for k in range(len(times_list)):
                #         print(times_list[k])
                #         print(df_log['image'][j].split('_')[0])
                #         if int(df_log['image'][j].split('_')[0]) - int(times_list[k]) < 2:
                #             print(times_list)
                #             print(k)
                #             print(times_list[k])
                #             print(df_log['image'][j])
                #             print(df_xlsx)
                #             print(df_xlsx['image_name'][k])
                #             df_log['status'][j] = df_xlsx['status'][k]
                #             df_log['image'][j] = df_xlsx['image_name'][k]
                #             print(df_log['image'][j])
                #             # times_list.pop(k)
                #             # v += 1

                #             break
                for k in range(len(times_list)):
                    print(times_list[k])
                    print(df_log['image'][j].split('_')[0])
                    if int(df_log['image'][j].split('_')[0])-1 == int(df_xlsx['image_name'][k].split('_')[0]):
                        print(times_list)
                        print(k)
                        print(times_list[k])
                        print(df_log['image'][j])
                        print(df_xlsx)
                        print(df_xlsx['image_name'][k])
                        df_log['status'][j] = df_xlsx['status'][k]
                        df_log['image'][j] = df_xlsx['image_name'][k]
                        print(df_log['image'][j])
                        # times_list.pop(k)
                        # v += 1

                        break
            except ValueError:
                print("ValueError")
                continue
        df_log.to_csv(output_dir + log_file_name, index=False,
                      sep=" ", encoding="utf-8-sig")

    print(log_files)
    print(xlsx_files)


if __name__ == "__main__":
    # num = input("被験者番号を入力してください")
    for num in range(114, 115):
        num = str(num)
        log_remove_gap(num)
