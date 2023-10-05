import pandas as pd
import glob
import os
import natsort

def integrate_participants(filename):
    path = "../data/integrated_adjust_all_test/*"

    folders = glob.glob(path)
    folders =natsort.natsorted(folders)
    
    # new_df = pd.DataFrame()
    for folder in folders:
        folder_name = folder.split("\\")[-1]
        files = glob.glob(folder + "/*")
        files = natsort.natsorted(files)
        for file in files:
            file_name = file.split("\\")[-1].split(".")[0]
            print(file)
            df = pd.read_csv(file)
            df["folder_name"] = folder_name
            df["file_name"] = file_name
            # if "frame" not in new_df.columns :
            if not "new_df" in locals():
                new_df = df.copy()
            else:
                # print(df)
                # print(new_df)
                new_df = pd.concat([df, new_df], axis=0)
            # print(new_df)
    # print(new_df)
    new_df = new_df.reset_index(drop=True)
    # print(new_df)
    if not os.path.exists("../data/final_part1/"):
        os.mkdir("../data/final_part1/")
    new_df.to_excel("../data/final_part1/" + filename + ".xlsx", index=False)


if __name__ == "__main__":
    filename = input("ファイル名を入力してください")
    integrate_participants(filename)
