import pandas as pd
import glob
import os

path = "../data/integrated_adjust_all/*"

folders = glob.glob(path)

# new_df = pd.DataFrame()
for folder in folders:
    files = glob.glob(folder + "/*")
    for file in files:
        print(file)
        df = pd.read_csv(file)
        # if "frame" not in new_df.columns :
        if not "new_df" in locals():
            new_df = df.copy()
        else:
            print(df)
            print(new_df)
            new_df = pd.concat([df, new_df], axis=0)
        print(new_df)
print(new_df)
new_df = new_df.reset_index(drop=True)
print(new_df)
if not os.path.exists("../data/final_part1/"):
    os.mkdir("../data/final_part1/")
new_df.to_excel("../data/final_part1/final_all.xlsx", index=False)
