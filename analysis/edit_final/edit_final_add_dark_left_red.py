import pandas as pd
import glob

# df_dark データフレームの読み込み
df_dark = pd.read_excel("../data/final_recent_dark/final_recent_dark_add_entropy_fft_color_skewgray2_michaelson_sf_mse.xlsx")

left_paths = glob.glob("../histogram/red_grids_dark_left/*.csv")

for left_path in left_paths:
    left_df = pd.read_csv(left_path)
    for _, row in left_df.iterrows():
        image_name = row['image_name']
        df_dark.loc[df_dark['image_name'] == image_name, 'isred'] = "red"

    df_dark.to_excel("../data/final_recent_dark/final_recent_dark_add_entropy_fft_color_skewgray2_michaelson_sf_mse_left.xlsx", index=False)