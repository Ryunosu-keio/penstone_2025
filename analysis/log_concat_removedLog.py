import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import glob
import os
import natsort

path = "../log_removeGap/"
path_list = glob.glob(path + "*/*")
# for path in path_list:

print(path_list)
df_concat = pd.DataFrame()
for path in path_list:
    df = pd.read_csv(path, sep=" ")
    print(df)
    df_concat = pd.concat([df_concat, df])
    print(df_concat)
df_concat = df_concat.reset_index(drop=True)

# df_concat = df_concat[df_concat['button'].isin(["t", "f"])]
df_concat = df_concat[df_concat["status"] != 4.0]
df_concat.to_csv("../log_concat_removedLog.csv", index=False)
