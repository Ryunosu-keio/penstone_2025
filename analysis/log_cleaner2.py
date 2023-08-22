import pandas as pd 
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
import os
from tqdm import tqdm
import glob

num = input("実験参加者の番号を入力してください")

def log_cleaner2(num):
    files = glob.glob("log/" + num + "/*.txt")

    # path = Path(__file__).parent
    # path /= '../../実験データ/0816/ボタン押下ログ/'
    # file = str(path.resolve()) + '\\0816log.xlsx'
    # sheets = pd.ExcelFile(file).sheet_names

    # output_file = str(path.resolve()) + '\\0816log_cleaned.xlsx'
    for file in tqdm(files):
        file_name = file.split("\\")[-1].split(".")[0]
        times_list = []
        figure_list = []
        contrast_list = []
        gamma_list = []
        sharpness_list = []
        brightness_list = []
        equalization_list = []
        df = pd.read_csv(file, header=None, sep=" ")
        #df のデータを一つ飛ばしで削除する
        df = df.drop(df['figure'] != ("t" or "f"))
        df = df.drop(df.index[::2])
        df.columns = ['day', 'time', 'button', 'timeFromStart', 'timeFromDisplay', 'image', 'status']
        df = df.reset_index(drop=True)
        df_img = df['image']
        for i in range(len(df_img)):
            # delete .jpg from df_img[i]
            img_name = df_img[i].replace('.jpg', '')
            times= img_name.split('_')[0]
            times_list.append(times)
            figure = img_name.split('_')[1]
            figure_list.append(figure)
            # if df_img[i] include gamma, extract word until _ next to gamma
            if 'gamma' in img_name:
                # gammaという文字の隣にある_までの文字列を抽出
                gamma = img_name.split('gamma')[1].split('_')[0]
                gamma_list.append(gamma)
            else :
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
        if not os.path.exists("log/" + num + "_cleaned"):
            print("make directory")
            os.mkdir("log/" + num + "_cleaned")
        else: 
            print("directory already exists")
        df.to_csv("log/" + num + "_cleaned/" + file_name + "_cleaned.csv", index=False)

# ()には被験者番号を入れる
log_cleaner2(num)

    # output_file = "log/" + num + "/log_cleaned.xlsx"

    # with pd.ExcelWriter(output_file) as writer:
    #     for file in tqdm(files):
    #         file_name = file.split("\\")[-1].split(".")[0]
    #         times_list = []
    #         figure_list = []
    #         contrast_list = []
    #         gamma_list = []
    #         sharpness_list = []
    #         brightness_list = []
    #         equalization_list = []
    #         df = pd.read_csv(file, header=None, sep=" ")
    #         #df のデータを一つ飛ばしで削除する
    #         df = df.drop(df['figure'] != ("c" or "d"))
    #         df = df.drop(df.index[::2])
    #         df.columns = ['day', 'time', 'button', 'timeFromStart', 'timeFromDisplay', 'image']
    #         df = df.reset_index(drop=True)
    #         df_img = df['image']
    #         for i in range(len(df_img)):
    #             # delete .jpg from df_img[i]
    #             img_name = df_img[i].replace('.jpg', '')
    #             times= img_name.split('_')[0]
    #             times_list.append(times)
    #             figure = img_name.split('_')[1]
    #             figure_list.append(figure)
    #             # if df_img[i] include gamma, extract word until _ next to gamma
    #             if 'gamma' in img_name:
    #                 # gammaという文字の隣にある_までの文字列を抽出
    #                 gamma = img_name.split('gamma')[1].split('_')[0]
    #                 gamma_list.append(gamma)
    #             else :
    #                 gamma_list.append(0)
    #             if 'contrast' in img_name:
    #                 contrast = img_name.split('contrast')[1].split('_')[0]
    #                 contrast_list.append(contrast)
    #             else:
    #                 contrast_list.append(0)
    #             if 'sharpness' in img_name:
    #                 sharpness = img_name.split('sharpness')[1].split('_')[0]
    #                 sharpness_list.append(sharpness)
    #             else:
    #                 sharpness_list.append(0)
    #             if 'brightness' in img_name:
    #                 brightness = img_name.split('brightness')[1].split('_')[0]
    #                 brightness_list.append(brightness)
    #             else:
    #                 brightness_list.append(0)
    #             if 'equalization' in img_name:
    #                 equalization = img_name.split('equalization')[1].split('_')[0]
    #                 equalization_list.append(equalization)
    #             else:
    #                 equalization_list.append(0)
    #         df['times'] = times_list
    #         df['figure'] = figure_list
    #         df['contrast'] = contrast_list
    #         df['gamma'] = gamma_list
    #         df['sharpness'] = sharpness_list
    #         df['brightness'] = brightness_list
    #         df['equalization'] = equalization_list
    #         df.to_excel(writer, sheet_name=file_name, index=False)
        
        


    