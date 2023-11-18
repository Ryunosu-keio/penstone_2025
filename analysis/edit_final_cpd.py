import pandas as pd

df = pd.read_excel("../data/final_part2/dark_add_contrast.xlsx")

df["contrast_value"] = (df["digit_brightness"]-df["non_digit_brightness"])/(df["digit_brightness"]+df["non_digit_brightness"])
df["contrast_sensitivity"]=1/df["contrast_value"]

df.to_excel("../data/final_part2/dark_add_contrast_sensitivity.xlsx")