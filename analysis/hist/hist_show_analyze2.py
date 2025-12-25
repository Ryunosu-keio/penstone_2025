
# ######全パターン一度に##########
# import pandas as pd
# from PIL import Image
# import matplotlib.pyplot as plt
# import numpy as np
# import glob
# import itertools
# from tqdm import tqdm
# # % matplotlib notebook



# dios = [1,2]
# rooms = [1,2]
# # 全ての組み合わせを生成
# all_combs = list(itertools.combinations(['gamma', 'contrast', 'brightness', 'sharpness', 'equalization'], 3))

# # 'brightness'と'equalization'が同時に含まれない組み合わせのみを選択
# param_combs = []
# for comb in all_combs:
#     if not ('brightness' in comb and 'equalization' in comb):
#         param_combs.append(comb)

# print(param_combs)
    
# for dio in dios[0:1]:
#     # bool = int(input("diopterよいなら1,悪いなら2:"))
#     if dio == 1:
#         bool = True
#         title_dio = "best"
#         print("diopterいい画像")
#     else :
#         bool = False
#         title_dio = "worst"
#         print("diopter悪い画像")

#     for room in rooms:
#         # directory = int(input("明所なら1,暗所なら2:"))
#         if room == 1 :
#             df = pd.read_excel("../data/final_part1/final_bright_add_modified.xlsx")
#             title_room = "bright"
#             print("bright")
#         if room == 2 :
#             df = pd.read_excel("../data/final_part2/darkfinal_modified.xlsx")
#             title_room = "dark"
#             print("dark")
            
#         df = df.sort_values(by="diopter",ascending = bool)


#             # # 要素のリスト
#             # elements = ['gamma', 'contrast', 'brightness', 'sharpness', 'equalization']
#             # # 3つの要素を取るすべての組み合わせを生成
#             # combinations = list(itertools.combinations(elements, 3))
#             # for i,comb in enumerate(combinations):
#             #     if i not in [7,9]:
#             #         print(i,combinations[i]

#             # 0('gamma', 'contrast', 'brightness')
#             # 1('gamma', 'contrast', 'sharpness')
#             # 2('gamma', 'contrast', 'equalization')
#             # 3('gamma', 'brightness', 'sharpness')
#             # 4('gamma', 'brightness', 'equalization')
#             # 5('gamma', 'sharpness', 'equalization')
#             # 6('contrast', 'brightness', 'sharpness')
#             # 8('contrast', 'sharpness', 'equalization')

#             # i = int(input("組み合わせを選んで"))
#         for param_comb in tqdm(param_combs):
#             comb = param_comb
#             print(comb)
#             df = df[(df[['param1', 'param2', 'param3']].isin(comb)).all(axis=1)]
#             print(df)


#             image_name = df["image_name"]
#             # image_path = f"../experiment_images/*/{image_name}"ばかめ
#             image_path = glob.glob("../experiment_images/*/*")

#             img_list = []
#             hist_list = []
#             image_path_list = []
#             diopter_list = []
#             # n= int(input("diopter上位何個見たいですか: "))
#             n = min(20, len(df["image_name"]))
#             print("n=" + str(n))
#             for i, image_name in enumerate(df["image_name"].head(n)):
#                 # print(i)
#                 # print(image_name)
#                 try:
#                     image_path = glob.glob("../experiment_images/*/" + image_name)[0]
#                     # print(image_path)
#                     image_path_list.append(image_path.split("\\")[-1])
#                     img = Image.open(image_path)
#                     img_list.append(img)
#                     hist = np.asarray(img.convert("RGB")).reshape(-1, 3)
#                     hist_list.append(hist)
#                     diopter = df["diopter"].iloc[i]
#                     diopter_list.append(diopter)

#                 except IndexError:
#                     print("data lost")
#                     # データが見つからなかった場合、リストに空の要素またはデフォルト値を追加
#                     image_path_list.append(None)  # または適切なデフォルト値
#                     img_list.append(None)  # または適切なデフォルト値
#                     hist_list.append(None)  # または適切なデフォルト値
#                     diopter_list.append(None)  # または適切なデフォルト値

#             image_title_list = []
#             for i, (img, dio) in enumerate(zip(image_path_list,diopter_list)):
#                 image_title_list.append(f"No.{i+1}\n{img}\ndiopter:{dio}")



#             # 10n枚ずつ
#             # 実際の環境では以下の行をアンコメントして、実行時に入力を受け取る
#             # image_count = int(input("画像の数を入力してください: "))

#             # ここでは例として、画像の数を20と仮定
#             image_count = n

#             # 行数は5行で固定
#             nrows = 5

#             # 列数を計算（画像ごとに2列必要なため、画像の数に応じて調整）
#             # ncols = (image_count // nrows) * 2
#             ncols = 8

#             # サブプロットを作成
#             fig, axes = plt.subplots(nrows=nrows, ncols=ncols, figsize=(ncols*10, nrows*10))
#             data = f"{str(title_room)} {str(comb)} {str(title_dio)} {str(n)}"
#             fig.suptitle( f"Pictures and Histograms of {data}", fontsize=100)

#             # 画像とヒストグラムを配置
#             for i in range(image_count):
#                 col_index_img = (i // nrows) * 2
#                 col_index_hist = col_index_img + 1

#                 # 画像を表示
#                 ax_img = axes[i % nrows, col_index_img]
#                 if img_list[i] is not None:
#                     ax_img.imshow(img_list[i])
#                     ax_img.set_title(image_title_list[i], fontsize=30)
#                 ax_img.axis('off')  # 画像がNoneでも軸は非表示に

#                 # ヒストグラムを表示
#                 ax_hist = axes[i % nrows, col_index_hist]
#                 if hist_list[i] is not None:
#                     ax_hist.hist(hist_list[i], color=["red", "green", "blue"], bins=128)
#                 ax_hist.axis('on')  # ヒストグラムがNoneでも軸は表示

#             plt.tight_layout()
#             # plt.savefig(f"../histogram/result/{data}.pdf")
#             # plt.savefig(f"../histogram/result/{data}.png")
#             print("datasaved")
#             # plt.show()


# # dfのimage_pathから画像を読み込み、ヒストグラムを表示する関数
            
# # def show_histograms(df):
# #     # 画像のパスを取得
# #     image_path = df['image_path'].tolist()

# #     # 画像を読み込み、ヒストグラムを表示
# #     for path in image_path:
# #         if os.path.exists(path):
# #             img = Image.open(path)
# #             plt.imshow(img)
# #             plt.show()
# #             hist = np.asarray(img.convert("RGB")).reshape(-1, 3)
# #             plt.hist(hist, color=["red", "green", "blue"], bins=128)
# #             plt.show()
# #         else:
# #             print("画像が見つかりません。")



import pandas as pd
from PIL import Image
import matplotlib.pyplot as plt
import numpy as np
import glob
import itertools
from tqdm import tqdm
import os

def load_images_and_hist(df, n):
    img_list, hist_list, image_path_list, diopter_list = [], [], [], []
    skewness_list = []#! Lab


    for i, image_name in enumerate(df["image_name"].head(n)):
        try:
            image_path = glob.glob("../experiment_images/*/" + image_name)[0]
            image_path_list.append(image_path.split("\\")[-1])
            img = Image.open(image_path)
            img_list.append(img)
            # hist = np.asarray(img.convert("RGB")).reshape(-1, 3)
            #lab空間に変換#! Lab
            hist = np.asarray(img.convert("LAB")).reshape(-1, 3)#! Lab
            #l成分のヒストグラム#! Lab
            hist = hist[:,0]#! Lab
            hist_list.append(hist)
            diopter = df["diopter"].iloc[i]
            diopter_list.append(diopter)
            skewness = df["skewness_luminance"].iloc[i]
            skewness_list.append(skewness)
        except IndexError:
            # print("Data lost for image:", image_name)
            image_path_list.append(None)
            img_list.append(None)
            hist_list.append(None)
            diopter_list.append(None)
            skewness_list.append(None)

    return img_list, hist_list, image_path_list, diopter_list, skewness_list

def plot_images_and_hists(img_list, hist_list, image_title_list,skewness_list, title_data, nrows=5):
    ncols = 8
    fig, axes = plt.subplots(nrows=nrows, ncols=ncols, figsize=(ncols*10, nrows*10))
    fig.suptitle(f"Pictures and Histograms of {title_data}", fontsize=10)

    for i in range(len(img_list)):
        col_index_img = (i // nrows) * 2
        col_index_hist = col_index_img + 1
        ax_img = axes[i % nrows, col_index_img]
        if img_list[i] is not None:
            ax_img.imshow(img_list[i])
            # ax_img.set_title(image_title_list[i], fontsize=5)
            ax_img.set_title(f"Skewness: {round(skewness_list[i],2)}", fontsize=30)#! Lab
        ax_img.axis('off')

        ax_hist = axes[i % nrows, col_index_hist]
        if hist_list[i] is not None:
            # ax_hist.hist(hist_list[i], color=["red", "green", "blue"], bins=128)
            ax_hist.hist(hist_list[i], bins=128) #! Lab
            #lab空間に変換

        ax_hist.axis('on')
        #縦軸の数値を非表示
        ax_hist.set_yticklabels([])

    plt.tight_layout()
    os.makedirs(f"../histogram/result/skewness", exist_ok=True)
    plt.savefig(f"../histogram/result/skewness/{title_data}.pdf")
    # print("Data saved")
    # plt.show()

def main():
    dios = [1, 2]
    rooms = [1, 2]
    all_combs = list(itertools.combinations(['gamma', 'contrast', 'brightness', 'sharpness', 'equalization'], 3))
    param_combs = [comb for comb in all_combs if not ('brightness' in comb and 'equalization' in comb)]

    for dio in dios:
        title_dio = "best" if dio == 1 else "worst"
        # print(f"Diopter: {title_dio}")

        for room in rooms:
            # file_path = "../data/final_part1/final_bright_add_modified.xlsx" if room == 1 else "../data/final_part2/darkfinal_modified.xlsx"
            
            if room == 1:
                file_path = "../data/final_recent_bright/final_recent_bright_add_entropy_skewgray2_michaelson_sf_mse_sf2_luminance_sobel_std_par_figure.xlsx"
                title_room = "bright"
                # print(f"Room condition: {title_room}")
                df = pd.read_excel(file_path)
                # df = df.sort_values(by="diopter", ascending=(dio == 1))
                #df = df[-1.2 < df["skewness_luminance"] < -0.8]
                #! Lab
                df = df[(df["skewness_luminance"] > -1.2) & (df["skewness_luminance"] < -0.8)]

            else:
                file_path = "../data/final_recent_dark/final_recent_dark_add_entropy_fft_color_skewgray2_michaelson_sf_mse_luminance_sobel_std_par_figure.xlsx"
                title_room = "dark"
                # print(f"Room condition: {title_room}")
                df = pd.read_excel(file_path)
                # df = df.sort_values(by="diopter", ascending=(dio == 1))
                # df = df[2 < df["skewness_luminance"] < 6]
                #! Lab
                df = df[(df["skewness_luminance"] > -1) & (df["skewness_luminance"] < 6)]



            
            

            for param_comb in tqdm(param_combs):
                filtered_df = df[(df[['param1', 'param2', 'param3']].isin(param_comb)).all(axis=1)]
                # print("Combination:", param_comb)
                # print(filtered_df)

                n = min(20, len(filtered_df["image_name"]))
                img_list, hist_list, image_path_list, diopter_list,skewness_list= load_images_and_hist(filtered_df, n)

                # image_title_list = [f"No.{i+1}\n{img}\ndiopter:{dio}" for i, (img, dio) in enumerate(zip(image_path_list, diopter_list))]
                image_title_list =[]
                title_data = f"{title_room} {param_comb} {title_dio} {n}"
                plot_images_and_hists(img_list, hist_list, image_title_list, skewness_list, title_data, nrows=5)

if __name__ == "__main__":
    main()


            