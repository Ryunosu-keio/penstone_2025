import pandas as pd

emrfile = 'D:\data\emr\emr.csv'

# df = pd.read_csv(emrfile, header=None, sep=" ")

# df["CUEスイッチ"]

# Cueが出現した後の空白が続く部分を取得
cue_intervals_emrfile = []
in_interval = False

# Iterate through the data to find intervals
for i in range(len(emrfile) - 1):
    # If the current row has a cue and the next row has a blank, this is the start of an interval
    if not pd.isna(emrfile.iloc[i]['CUEスイッチ']) and pd.isna(emrfile.iloc[i+1]['CUEスイッチ']):
        start = i + 1
        in_interval = True
    # If we are inside an interval and encounter a non-blank cue, this is the end of the interval
    elif in_interval and not pd.isna(emrfile.iloc[i]['CUEスイッチ']):
        end = i
        cue_intervals_emrfile.append((start, end))
        in_interval = False

# If the last interval goes until the end of the data, add it to the list
if in_interval:
    cue_intervals_emrfile.append([start, len(emrfile) - 1])

# [[start, goal],]
cue_intervals_emrfile

# goal - startが5000以下のもの（90秒くらい以下のもの）を除く
for i in range(len(cue_intervals_emrfile)):
    if cue_intervals_emrfile[i][1] - cue_intervals_emrfile[i][0] < 5000:
        cue_intervals_emrfile.pop(i)

