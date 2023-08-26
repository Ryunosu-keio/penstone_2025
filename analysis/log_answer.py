import pandas as pd 
import numpy as np
import matplotlib.pyplot as plt
import glob
import os
import natsort


use_folders = ["0824_rb_fd/", "0825_rb_fd/"]
output_dir = '../log/answers/'
if not os.path.exists(output_dir):
    os.makedirs(output_dir, exist_ok=True)

for use_folder in use_folders:
    xlsx_files = glob.glob("../imageCreationExcel/back/" + use_folder + "*.xlsx")
    xlsx_files = natsort.natsorted(xlsx_files)
    if not os.path.exists(output_dir + use_folder):
        os.makedirs(output_dir + use_folder, exist_ok=True)
    for file in xlsx_files:
        filename = file.split("\\")[-1]
        df = pd.read_excel(file)
        df = df[df['status'] != 4]
        df = df.reset_index(drop=True)
        frames = []
        for i in range(len(df)):
            image_num = int(df['image_name'][i].split("_")[0])
            frames.append(image_num * 300)
        df['frame'] = frames
        df.to_excel(output_dir + use_folder + filename, index=False)

