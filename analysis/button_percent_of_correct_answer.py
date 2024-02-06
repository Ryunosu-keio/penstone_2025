import pandas as pd
import glob


#########bright
df_all = pd.DataFrame()
paths = glob.glob("../data/integrate_emr_button_std/*.csv")
for path in paths:
    df =pd.read_csv(path)
    df_all = pd.concat([df_all, df])

df = df_all





####dark
# df = pd.read_excel("../data/final_recent_dark/final_recent_dark_add_entropy_skewgray2_michaelson_sf_mse_button700.xlsx")

#dfのカラムリストを表示
print(df.columns.values)

# df_correct_0 = df[df["button"] == "t" & df["status"] == 0]
# df_correct_1 = df[df["button"] == "f" & df["status"] == 1]
# df_correct_2 = df[df["button"] == "f" & df["status"] == 2]

# df_incorrect = 

df["iscorrect"] = pd.NA

for i, row in df.iterrows():
    if row["button"] == "t" and row["status"] == 0:
        df.loc[i, "iscorrect"] = "correct"
    elif row["button"] == "f" and row["status"] == 1:
        df.loc[i, "iscorrect"] = "correct"
    elif row["button"] == "f" and row["status"] == 2:
        df.loc[i, "iscorrect"] = "correct"
    else:
        df.loc[i, "iscorrect"] = "incorrect"

    count_correct = len(df[df["iscorrect"] == "correct"])
    count_incorrect = len(df[df["iscorrect"] == "incorrect"])

    percentage_correct = count_correct / (count_correct + count_incorrect)

print("count_correct:", count_correct)
print("count_incorrect:", count_incorrect)
print("percentage_correct:", percentage_correct)

# df = df[df["iscorrect"] =="correct"]

# # "status"と"button"の列だけ表示
# print(df[["status", "button"]])
# print(df)

#################################################################################################################






# path_list = glob.glob("../data/integrate_emr_button_std/*.csv")
# # path_list = glob.glob("../data/integrate_emr_button_std2/*.csv")
# print(path_list)
# #dataのなかのbutton.csvで終わるファイルのパスを取得

# df_all = pd.DataFrame()
# for path in path_list:
#     df = pd.read_csv(path)
#     # plt.figure()
#     # plt.hist(df["timeFromDisplay"])
#     # plt.show()
#     df_all = pd.concat([df_all, df])
# print(df_all["timeFromDisplay"].mean(),df_all["timeFromDisplay"].std())

# plt.figure()
# plt.hist(df_all["timeFromDisplay"])
# plt.title("Histogram of button press time of all participants (bright)")
# plt.xlabel("Time from display [s]")
# plt.ylabel("Frequency")
# # 平均と分散をラベル表示
# #x軸最大値を取得
# xmax = plt.xlim()[1]
# ymax = plt.ylim()[1]
# mean = df_all["timeFromDisplay"].mean()
# std = df_all["timeFromDisplay"].std()
# plt.text(xmax*0.8,ymax*0.8,"mean: " + str(round(mean,3)) + "\n" + "std: " + str(round(std, 3)))
# plt.show()
#########################################################################333333333333333333

# df_final = pd.read_excel("../data/final_recent_dark/final_recent_dark_add_entropy_skewgray2_michaelson_sf_mse_button700.xlsx")
# df_final = df_final[df_final["timeFromDisplay"] < mean]
