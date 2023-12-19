import pandas as pd
import statsmodels.api as sm
import glob

file_path = glob.glob("../histogram/red_grids_dark/*.csv")

for file in file_path:
    df_mini = pd.read_csv(file)

    df = pd.read_excel("../data/final_part2/add_contrast_max.xlsx")

    # df_miniに含まれるimage_nameの行だけをdfから抜き出す
    df = df[df["image_name"].isin(df_mini["image_name"])]
    df.duplicated(subset='image_name')
    print(df)

    # 説明変数（独立変数）と目的変数（従属変数）を設定
    X = df[["mode_brightness"]]  # 説明変数の列名を指定
    y = df['diopter']  # 目的変数の列名を指定

    # 定数項を追加
    X = sm.add_constant(X)

    # 重回帰モデルを作成し、結果を表示
    model = sm.OLS(y, X).fit()
    print(model.summary())

# %% 
    




    