import pandas as pd
import os
from create_edited_photo import create_edited_photo
import cv2
import math


file = "imageCreationExcel/sample2.xlsx"

def rounds(x,k=2):
    return round(x, k - math.floor(math.log10(abs(x)))- 1)

def create_photos_fromlist(file):
    df = pd.read_excel(file)
    for i in range(len(df)):
        df_now = df.iloc[i, :]
        selected_parameters = {
            df_now["param1"] : df_now["param1_value"],
            df_now["param2"] : df_now["param2_value"],
            df_now["param3"] : df_now["param3_value"],
        }
        file = df_now["filename"]
        filename = file.split("\\")[-1]
        # filename = file.split("/")[-1]
        filename = filename.split(".")[0]
        img_array = create_edited_photo(file, selected_parameters)
        if df_now["param3"] == "None":
            cv2.imwrite("experiment_images/" + str(i+1) + filename + "_" + df_now["param1"] + str(rounds(float(df_now["param1_value"]))) + "_" + df_now["param2"] + str(rounds(float(df_now["param2_value"]))) + ".jpg", img_array)
        else:
            cv2.imwrite("experiment_images/" + str(i+1) + filename + "_" + df_now["param1"] + str(rounds(float(df_now["param1_value"]))) + "_" + df_now["param2"] + str(rounds(float(df_now["param2_value"]))) + "_" + df_now["param3"] + str(rounds(float(df_now["param3_value"]))) + ".jpg", img_array)

create_photos_fromlist(file)
