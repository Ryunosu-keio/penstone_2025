import glob
import natsort
import pandas as pd
import os


def integrate_adjust(folders, filenum):
    output_dir = "../data/integrated_adjust_all_"+filenum+"_final/"
    if not os.path.exists(output_dir):
        os.mkdir(output_dir)
    folders = natsort.natsorted(folders)
    print("len(folers)", len(folders))
    dio_ave = []
    ave_participants = {}
    for folder in folders:
        folder_name = folder.split("\\")[-1]
        dio_participants = []
        files = glob.glob(folder + "/*")
        files = natsort.natsorted(files)
        # print(files)
        for file in files:
            file_name = file.split("\\")[-1].split(".")[0]
            if int(file_name) < 10:
                # ほしいデータ
                # df = pd.read_csv("../data/integrated/" +
                # folder_name + "/" + file_name + ".csv")
                df = pd.read_csv(file)
                df["diopter"] = 1/df["diopter"]
                dio_mean = df["diopter"].mean()
                print(
                    f"folder_name:{folder_name},file_name:{file_name},dio_mean:{dio_mean}")
                dio_participants.append(dio_mean)
        if len(dio_participants) != 0:
            sum = 0
            for i in range(len(dio_participants)):
                sum += dio_participants[i]
            temp = sum/len(dio_participants)
            ave_participants[folder_name + "_before_half"] = temp
            if int(folder_name) < 18:
                dio_ave.append(temp)
    print("len(avec_participants)前半まで", len(ave_participants))

    for folder in folders:
        folder_name = folder.split("\\")[-1]
        dio_participants = []
        files = glob.glob(folder + "/*")
        files = natsort.natsorted(files)
        for file in files:
            file_name = file.split("\\")[-1].split(".")[0]
            if int(file_name) > 9:
                # ほしいデータ
                # df = pd.read_csv("../data/integrated/" +
                # folder_name + "/" + file_name + ".csv")
                df = pd.read_csv(file)
                df["diopter"] = 1/df["diopter"]
                dio_mean = df["diopter"].mean()
                print(
                    f"folder_name:{folder_name},file_name:{file_name},dio_mean:{dio_mean}")
                dio_participants.append(dio_mean)
        if len(dio_participants) != 0:
            sum = 0
            for i in range(len(dio_participants)):
                sum += dio_participants[i]
            temp = sum/len(dio_participants)
            ave_participants[folder_name + "_after_half"] = temp
            # print("after folder:",folder_name,ave_participants[folder_name + "_after_half"])
            if int(folder_name) < 18:
                dio_ave.append(temp)
    print("len(avec_participants)後半まで", len(ave_participants))
    print(dio_ave)

    sum = 0
    print("len(dio_ave))", len(dio_ave))
    for i in range(len(dio_ave)):
        sum += dio_ave[i]
        print(i, dio_ave[i], sum)
    all_ave = sum/len(dio_ave)
    print(all_ave)
    for key in ave_participants:
        ave_participants[key] = all_ave - ave_participants[key]
        # print(ave_participants[key])###########################
    for folder in folders:
        folder_name = folder.split("\\")[-1]
        files = glob.glob(folder + "/*")
        dio_participants = []
        if not os.path.exists(output_dir + "/" + folder_name + "/"):
            os.mkdir(output_dir + "/" + folder_name + "/")
        for file in files:
            file_name = file.split("\\")[-1].split(".")[0]
            if int(file_name) < 10:
                # df = pd.read_csv("../data/integrated/" +
                #                 folder_name + "/" + file_name + ".csv")
                df = pd.read_csv(file)
                df["diopter"] = 1/df["diopter"]
                df["diopter"] += ave_participants[folder_name + "_before_half"]
                df["diopter"] = 1/df["diopter"]
                df.to_csv(output_dir + folder_name + "/" + file_name + ".csv")
                # print(file + "is done")
        for file in files:
            file_name = file.split("\\")[-1].split(".")[0]
            if int(file_name) > 9:
                # df = pd.read_csv("../data/integrated/" +
                #                 folder_name + "/" + file_name + ".csv")
                df = pd.read_csv(file)
                df["diopter"] = 1/df["diopter"]
                df["diopter"] += ave_participants[folder_name + "_after_half"]
                df["diopter"] = 1/df["diopter"]
                df.to_csv(output_dir + folder_name + "/" + file_name + ".csv")
                # print(file + " is done")


if __name__ == "__main__":
    filenum = "dark"
    folders = glob.glob("../data/integrated"+filenum+"/*")
    folders = natsort.natsorted(folders)
    # print(folders)
    # remove_list = []
    # for folder in folders:
    #     print(folder)
    #     folder_name = folder.split("\\")[-1]
    #     # print(int(folder_name))
    #     if int(folder_name) <11:
    #         remove_list.append(folder)
    #         # print(folder)
    # for remove_folder in remove_list:
    #     folders.remove(remove_folder)
    integrate_adjust(folders,filenum="dark")


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
