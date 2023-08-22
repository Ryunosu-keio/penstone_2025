import pandas as pd
import os
import glob



def devide_emrLog(num):
    times = 0
    emrfiles = glob.glob('../data/emr/' + num + '/*.csv')
    for emrfile in emrfiles:
        # emrfile = '../data/emr/' + num + '.csv'

        output_dir = '../data/devided_emr/' + num

        if not os.path.exists(output_dir):
            os.makedirs(output_dir, exist_ok=True)
        else:
            print("already exists")

        emr_df = pd.read_csv(emrfile)
        print(emr_df)

        # df["CUEスイッチ"]

        # Cueが出現した後の空白が続く部分を取得
        cue_intervals_emrfile = []
        in_interval = False

        # Iterate through the data to find intervals
        for i in range(len(emr_df) - 1):
            # If the current row has a cue and the next row has a blank, this is the start of an interval
            if not pd.isna(emr_df.iloc[i]['CUEスイッチ']) and pd.isna(emr_df.iloc[i+1]['CUEスイッチ']):
                start = i + 1
                in_interval = True
            # If we are inside an interval and encounter a non-blank cue, this is the end of the interval
            elif in_interval and not pd.isna(emr_df.iloc[i]['CUEスイッチ']):
                end = i
                cue_intervals_emrfile.append((start, end))
                in_interval = False

        # If the last interval goes until the end of the data, add it to the list
        if in_interval:
            cue_intervals_emrfile.append([start, len(emr_df) - 1])

        # [[start, goal],]
        # cue_intervals_emrfile

        # goal - startが5000以下のもの（90秒くらい以下のもの）を除く
        for i in range(len(cue_intervals_emrfile)-1,-1,-1):
            if cue_intervals_emrfile[i][1] - cue_intervals_emrfile[i][0] < 5000:
                cue_intervals_emrfile.pop(i)

        # emr_dfをcue_intervals_emrfileに従って分割する
        for i in range(len(cue_intervals_emrfile)):
            emr_df[cue_intervals_emrfile[i][0]:cue_intervals_emrfile[i][1]].to_csv(output_dir + "/" + str(times) + ".csv", index=False, header=None, sep=" ")
            times += 1

# ()には被験者番号を入れる
devide_emrLog("komoto")
