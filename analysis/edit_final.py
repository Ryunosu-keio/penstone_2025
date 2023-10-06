import pandas as pd
import glob

path = "../data/final_part1/final_add.xlsx"
df = pd.read_excel(path)
print(type(df["folder_name"]))
conditions = ((df["brightness"] == 0) & (df["equalization"] == 0)  
            & (df["gamma"] >= 0.7) & (df["gamma"] <= 0.9)
            & (df["contrast"] >= 0.8) & (df["contrast"] <= 0.93)
            & (df["sharpness"] >= 0.66) & (df["sharpness"] <= 1.0)
            & (df["folder_name"] >= 18) & (df["folder_name"] <= 23)
            )
df_red_excluded = df.drop(df[conditions].index)
print(df)

df_red_excluded.to_excel("../data/final_part1/final_add_editted.xlsx")