import pandas as pd
import glob


room = int(input("bright or dark? 1:bright 2:dark"))
if room == 1:
    df_final = pd.read_excel("../data/final_recent_bright/final_recent_bright_add_entropy_skewgray2_michaelson_sf_mse.xlsx")
    dfs_button = glob.glob("../data/integrate_emr_button_std/*.csv")

elif room == 2:
    df_final = pd.read_excel("../data/final_recent_dark/final_recent_dark_add_entropy_fft_color_skewgray2_michaelson_sf_mse.xlsx")
    dfs_button = glob.glob("../data/integrate_emr_button_std2/*.csv")
print("len(df_final)",len(df_final))

#dfs_buttonの中身をconcatする
dfs_button_concat = pd.concat([pd.read_csv(f) for f in dfs_button])


#dfs_button_concatをdf_finalにマージする
dfs_button_concat = dfs_button_concat[["frame","フレーム数","diopter", "day", "time", "button", "timeFromStart", "timeFromDisplay", "num", "timeFromDisplay_std"]]
df_final = pd.merge(df_final, dfs_button_concat, on=["frame","フレーム数","diopter"], how="left")

#df_finalの空欄のある行を削除

df_final = df_final.dropna()

print("len(df_final_dropped)",len(df_final))

# if room == 1:
#     df_final.to_excel("../data/final_recent_bright/final_recent_bright_add_entropy_skewgray2_michaelson_sf_mse_button.xlsx")
# elif room == 2:
#     df_final.to_excel("../data/final_recent_dark/final_recent_dark_add_entropy_skewgray2_michaelson_sf_mse_button.xlsx")