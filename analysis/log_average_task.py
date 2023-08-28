import glob
import natsort
import pandas as pd
import os

files = glob.glob("../data/integrated/*/*")
folders = glob.glob("../data/integrated/*")
output_dir = "../data/integrated_adjust/"
if not os.path.exists(output_dir):
    os.mkdir(output_dir)
files = natsort.natsorted(files)
folders = natsort.natsorted(folders)
# print(files)



dio_ave = []
ave_participants = {}
for folder in folders:   
    folder_name = folder.split("\\")[-1]
    dio_participants = []
    for i in range(10):
        file = files[i]
        file_name = file.split("\\")[-1].split(".")[0]  
        # ほしいデータ
        df = pd.read_csv("../data/integrated/" + folder_name + "/" + file_name +".csv")
        df["diopter"] = 1/df["diopter"]
        dio_mean = df["diopter"].mean()
        dio_participants.append(dio_mean)
    sum = 0
    for i in range(len(dio_participants)):
        sum += dio_participants[i]
    temp = sum/len(dio_participants)
    ave_participants[folder_name] = temp
    dio_ave.append(temp)
sum = 0
for i in range(len(dio_ave)):
    sum += dio_ave[i]
all_ave = sum/len(dio_ave)
for key in ave_participants:
    ave_participants[key] = all_ave - ave_participants[key]

for folder in folders:   
    folder_name = folder.split("\\")[-1]
    dio_participants = []
    if not os.path.exists(output_dir + "/" + folder_name + "/"):
        os.mkdir(output_dir + "/" + folder_name + "/")
    for i in range(10):
        file = files[i]
        file_name = file.split("\\")[-1].split(".")[0]  
        df = pd.read_csv("../data/integrated/" + folder_name + "/" + file_name +".csv")
        print(df["diopter"])
        df["diopter"] += ave_participants[folder_name]
        print(ave_participants[folder_name])
        print(df["diopter"])
        df["diopter"] = 1/df["diopter"]
        df.to_csv(output_dir + folder_name + "/" + file_name +".csv")
    







# df = pd.DataFrame(columns=["i", "emr", "answer","差分"])

# files = glob.glob("../data/integrated/*/*")
# folders = glob.glob("../data/integrated/*")
# files = natsort.natsorted(files)
# folders = natsort.natsorted(folders)

# print(folders, files)
# # i行目を指定する (例: 2行目の場合、i = 1を指定する)
# i = 0
# for i in range(20):
#     sum_values = 0
#     for file in files:
#         file_name = file.split("\\")[-1].split(".")[0]
#         for folder in folders:
#             folder_name = folder.split("\\")[-1].split(".")[0]
#             # ファイルのパスを作成
#             path = f"../data/integrated/{folder_name}/{file_name}.csv"
            
#             # CSVファイルを読み込む
#             df = pd.read_csv(path)
#             print(folder_name,file_name,df)
#             # i行目のdiopterの値を取得して合計する
#             sum_values += df['diopter'].iloc[i]

#     print(f"Total sum of 'diopter' values at row {i+1} across all files: {sum_values}")



