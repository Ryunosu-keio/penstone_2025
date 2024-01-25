import pandas as pd
import glob

df_final = pd.read_excel("../data/final_recent_dark/final_recent_dark_add_entropy_fft.xlsx")

dfs_button = glob.glob("../data/integrate_emr_button_std2/*.csv")

#dfs_buttonの中身をconcatする
dfs_button_concat = pd.concat([pd.read_csv(f) for f in dfs_button])


#dfs_button_concatをdf_finalにマージする
dfs_button_concat = dfs_button_concat[["image_name", "day", "time", "button", "timeFromStart", "timeFromDisplay", "num", "timeFromDisplay_std"]]
df_final = pd.merge(df_final, dfs_button_concat, on="image_name", how="left")

#df_finalの空欄のある行を削除
df_final = df_final.dropna()

df_final.to_excel("../data/final_recent_dark/final_recent_dark_add_entropy_fft_button_dropna.xlsx")