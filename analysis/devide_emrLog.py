import pandas as pd
import os
import glob

def devide_emrLog(num):
    times = 0
    emrfiles = glob.glob('../data/emr/' + num + '/*.csv')
    for emrfile in emrfiles:
        output_dir = '../data/devided_emr/' + num

        if not os.path.exists(output_dir):
            os.makedirs(output_dir, exist_ok=True)
        else:
            print("already exists")

        emr_df = pd.read_csv(emrfile)
        columns = emr_df.columns

        cue_intervals_emrfile = []
        in_interval = False

        for i in range(len(emr_df) - 1):
            if not pd.isna(emr_df.iloc[i]['CUEスイッチ']) and pd.isna(emr_df.iloc[i+1]['CUEスイッチ']):
                start = i + 1
                in_interval = True
            elif in_interval and not pd.isna(emr_df.iloc[i]['CUEスイッチ']):
                end = i
                cue_intervals_emrfile.append((start, end))
                in_interval = False

        if in_interval:
            cue_intervals_emrfile.append([start, len(emr_df) - 1])

        for i in range(len(cue_intervals_emrfile)-1,-1,-1):
            if cue_intervals_emrfile[i][1] - cue_intervals_emrfile[i][0] < 10000:
                cue_intervals_emrfile.pop(i)
        print(cue_intervals_emrfile)

        for i in range(len(cue_intervals_emrfile)):
            emr_df[cue_intervals_emrfile[i][0]:cue_intervals_emrfile[i][1]].to_csv(output_dir + "/" + str(times) + ".csv", index=False, sep=",", encoding="utf-8-sig", columns=columns)
            times += 1

participant = input("被験者番号を入力してください")
devide_emrLog(participant)
