import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
import os
from tqdm import tqdm
import glob


def log_cleaner2(num):
    files = glob.glob("../log/" + str(num) + "/*.txt")
    if not os.path.exists("../log/" + str(num) + "_cleaned"):
        print("make directory")
        os.mkdir("../log/" + str(num) + "_cleaned")
    else:
        print("directory already exists")
    print(files)
    for file in tqdm(files):
        file_name = file.split("\\")[-1].split(".")[0]
        times_list = []
        figure_list = []
        contrast_list = []
        gamma_list = []
        sharpness_list = []
        brightness_list = []
        equalization_list = []
        try:
            df = pd.read_csv(file, header=None, sep=" ", encoding='utf-8')
        except UnicodeDecodeError:
            try:
                df = pd.read_csv(file, header=None, sep=" ",
                                 encoding='ISO-8859-1')
            except:
                print(
                    f"Could not read the file {file} due to encoding issues.")
                continue
        # df = pd.read_csv(file, header=None, sep=" ")
        # df.columns = ['day', 'time', 'button', 'timeFromStart', 'timeFromDisplay', 'image', 'status']
        # df のデータを一つ飛ばしで削除する
        # df = df[df['button'].isin(["t", "f"])]
        # df = df.drop(df.index[::2])
        df = df.reset_index(drop=True)
        df_img = df['image_name']
        for i in range(len(df_img)):
            # delete .jpg from df_img[i]
            img_name = df_img[i].replace('.jpg', '')
            times = img_name.split('_')[0]
            times_list.append(times)
            figure = img_name.split('_')[1]
            figure_list.append(figure)
            # if df_img[i] include gamma, extract word until _ next to gamma
            if 'gamma' in img_name:
                # gammaという文字の隣にある_までの文字列を抽出
                gamma = img_name.split('gamma')[1].split('_')[0]
                gamma_list.append(gamma)
            else:
                gamma_list.append(0)
            if 'contrast' in img_name:
                contrast = img_name.split('contrast')[1].split('_')[0]
                contrast_list.append(contrast)
            else:
                contrast_list.append(0)
            if 'sharpness' in img_name:
                sharpness = img_name.split('sharpness')[1].split('_')[0]
                sharpness_list.append(sharpness)
            else:
                sharpness_list.append(0)
            if 'brightness' in img_name:
                brightness = img_name.split('brightness')[1].split('_')[0]
                brightness_list.append(brightness)
            else:
                brightness_list.append(0)
            if 'equalization' in img_name:
                equalization = img_name.split('equalization')[1].split('_')[0]
                equalization_list.append(equalization)
            else:
                equalization_list.append(0)
        df['times'] = times_list
        df['figure'] = figure_list
        df['contrast'] = contrast_list
        df['gamma'] = gamma_list
        df['sharpness'] = sharpness_list
        df['brightness'] = brightness_list
        df['equalization'] = equalization_list
        df.to_csv("../log/" + str(num) + "_cleaned/" +
                  file_name + "_cleaned.csv", index=False)


if __name__ == "__main__":
    for i in range(1, 18):
        # num = input("実験参加者の番号を入力してください")
        log_cleaner2(i)
