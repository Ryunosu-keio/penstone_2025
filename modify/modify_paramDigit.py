import pandas as pd
import matplotlib.pyplot as plt

params = ["gamma", "contrast", "sharpness",  "brightness",  "equalization"]

filename = input("Enter filename: ")

filename = "../data/final_part2/" + filename

df = pd.read_excel(filename + ".xlsx")

for param in params:
    for i in range(len(df)):
        if df.loc[i, param] != 0:
            if df.loc[i, "param1"] == param:
                df.loc[i, param] = df.loc[i, "param1_value"]
            elif df.loc[i, "param2"] == param:
                df.loc[i, param] = df.loc[i, "param2_value"]
            elif df.loc[i, "param3"] == param:
                df.loc[i, param] = df.loc[i, "param3_value"]
        if param == "equalization":
            if df.loc[i, param] != 0:
                # intに直す
                df.loc[i, param] = int(float(df.loc[i, param]))

df.to_excel(filename + "_modified.xlsx", index=False)
