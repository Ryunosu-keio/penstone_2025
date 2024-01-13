
######全パターン一度に##########
import pandas as pd
from PIL import Image, ImageDraw
import matplotlib.pyplot as plt
import numpy as np
import glob
import itertools
from tqdm import tqdm

# df = pd.read_excel("../data/final_part1/final_bright_add_modified.xlsx")
# df_dark = pd.read_excel("../data/final_part2/darkfinal_modified.xlsx")

#赤グリッド内の画像名のdfをつくる
def extract_red_imagename(room) :
    if room == "bright":
        df_path_list = glob.glob("../histogram/redpic/*.csv")
    else:
        df_path_list = glob.glob("../histogram/bad_grids_dark/*.csv")
    df_list = []
    red_grid_list = []

    for df_path in df_path_list:
        df = pd.read_csv(df_path)
        df = df.drop(df.columns[0],axis=1)
        df_list.append(df)
        # red_grid_type = df_path.split("\\")[-1].split('_')[1].rstrip('.csv')
        red_grid_type = df_path.split("\\")[-1].rstrip('.csv')
        red_grid_list_temp = [red_grid_type for _ in range(len(df))]
        red_grid_list += red_grid_list_temp

    df_red = pd.concat(df_list, ignore_index=True)
    print(df_red)
    print("len(red_grid_list)",len(red_grid_list))
    return df_red, red_grid_list

#df_finalから赤グリッドの行だけ抜き出す
def make_df_final_for_hist(df_red, room):
    # df_red = extract_red_imagename(room ="bright")
    if room == "bright":
        df_final = pd.read_excel("../data/final_part1/final_bright_add_modified.xlsx")
    else:
        # df_final = pd.read_excel("../data/final_part2/darkfinal_modified.xlsx")
        df_final = pd.read_excel("../data/final_part2/add_contrast_max.xlsx")
    # df_final_red = df_final[df_final["image_name"].isin(df_red["image_name"])]
    df_final_red = pd.merge(df_red[['image_name']], df_final, on='image_name', how='left')
    #image_nameの列の重複を削除
    df_final_red = df_final_red.drop_duplicates(subset='image_name')
    print(df_final_red)
    # df_final_red.to_csv("../histogram/red_grids_dark/darkfinal_red.csv")
    return df_final_red

#赤グリッドの画像とそのヒストグラムの関連リストを作る
def hist_list_by_df(df):
    image_name = df["image_name"]
    # image_path = f"../experiment_images/*/{image_name}"ばかめ
    image_path = glob.glob("../experiment_images/*/*")

    img_list = []
    hist_list = []
    image_path_list = []
    diopter_list = []
    hist_contrast_list = []
    # n= int(input("diopter上位何個見たいですか: "))
    n =len(df["image_name"])
    print("n=" + str(n))
    for i, image_name in enumerate(df["image_name"].head(n)):
        # print(i)
        # print(image_name)
        try:
            image_path = glob.glob("../experiment_images/*/" + image_name)[0]
            # print(image_path)
            image_path_list.append(image_path.split("\\")[-1])
            img = Image.open(image_path)
            img_list.append(img)
            hist = np.asarray(img.convert("RGB")).reshape(-1, 3)##############RGB
            # hist = np.asarray(img.convert("L"))###################grayscale
            hist_list.append(hist)
            diopter = df["diopter"].iloc[i]
            diopter_list.append(diopter)
            hist_contrast = df["mode_brightness"].iloc[i]
            hist_contrast_list.append(hist_contrast)
            
        except IndexError:
            print("datalost")
            print("this data is lost: ", image_path)
            # データが見つからなかった場合、リストに空の要素またはデフォルト値を追加
            # image_path_list.append(None)  # または適切なデフォルト値
            # image_path_list.append(image_path)
            # img_list.append(None)  # または適切なデフォルト値
            # hist_list.append(None)  # または適切なデフォルト値
            # diopter_list.append(diopter)  # または適切なデフォルト値

             # 代替画像を作成 (白い画像など)
            placeholder_img = Image.new('RGB', (100, 100), (255, 255, 255))
            d = ImageDraw.Draw(placeholder_img)
            d.text((10, 40), "No Image", fill=(0, 0, 0))
            
            image_path_list.append("placeholder.png")
            img_list.append(placeholder_img)
            hist_list.append(np.zeros((1, 3)))  # ゼロのヒストグラムデータ
            diopter_list.append(None)
    return img_list, hist_list, image_path_list, diopter_list, hist_contrast_list

#matplotlibで10n枚ずつ表示する
def show_hists(red_grid_list,hist_contrast_list,room):
    # ここでは例として、画像の数を20と仮定
    image_count = len(img_list)

    # 行数は5行で固定
    nrows = 5

    # 列数を計算（画像ごとに2列必要なため、画像の数に応じて調整）
    ncols = (image_count // nrows) * 2
    if image_count % nrows > 0:
        ncols += 2  # 余分な画像がある場合、余分な列を追加


    # サブプロットを作成
    fig, axes = plt.subplots(nrows=nrows, ncols=ncols, figsize=(ncols*5, nrows*5))
    # data = f"{str(title_room)} {str(comb)} {str(title_dio)} {str(n)}"
    # fig.suptitle( f"Pictures and Histograms of {data}", fontsize=100)


    image_title_list = []
    for i, (img, dio) in enumerate(zip(image_path_list,diopter_list)):
        if dio is not None:
            image_title_list.append(f"{img}\ndiopter:{format(dio, '.2f')}")
            # image_title_list.append(f"{img}\ndiopter:{format(dio, '.2f')}")
            # image_title_list.append(f"No.{i+1}\n{img}\ndiopter:{dio, '.2f'}")
            # image_title_list.append(f"No.{i+1}\ndiopter:{format(dio,'.2f')}")
            # image_title_list.append(f"diopter:{format(dio,'.2f')}")
            # image_title_list.append(f"diopter:{format(dio, '.2f')}")
        else:
            image_title_list.append("diopter: N/A")


    # 画像とヒストグラムを配置
    for i in range(image_count):
        col_index_img = (i // nrows) * 2
        col_index_hist = col_index_img + 1

        # 画像を表示
        ax_img = axes[i % nrows, col_index_img]
        if img_list[i] is not None:
            ax_img.imshow(img_list[i])
            # ax_img.set_title(image_title_list[i] + "\n" + red_grid_list[i], fontsize=10)
            ax_img.set_title(red_grid_list[i]+"\n"+ image_title_list[i]+"\n"+ str(hist_contrast_list[i]), fontsize=20)
        ax_img.axis('off')  # 画像がNoneでも軸は非表示に

        # ヒストグラムを表示
        ax_hist = axes[i % nrows, col_index_hist]
        if hist_list[i] is not None:
            ax_hist.hist(hist_list[i], color=["red", "green", "blue"], bins=128)#############################RGB
            # ax_hist.hist(hist_list[i].ravel(), bins=128, color='gray')###########################gray

        ax_hist.axis('on')  # ヒストグラムがNoneでも軸は表示

    plt.tight_layout()
    # plt.savefig(f"../histogram/result/{data}.pdf")
    # plt.savefig(f"../histogram/result/{data}.png")
    # print("datasaved")
    if room == "bright":
        plt.savefig("../histogram/redpic/hist_red.pdf")
    else:
        plt.savefig("../histogram/bad_grids_dark/hist_bad_dark_max.pdf")
    plt.show()



room = str(input("room = bright or dark:"))
df_red, red_grid_list = extract_red_imagename(room)
df_final_red = make_df_final_for_hist(df_red, room)
img_list = hist_list_by_df(df_final_red)[0]
hist_list = hist_list_by_df(df_final_red)[1]
image_path_list = hist_list_by_df(df_final_red)[2]
diopter_list = hist_list_by_df(df_final_red)[3]
hist_contrast_list = hist_list_by_df(df_final_red)[4]

show_hists(red_grid_list,hist_contrast_list,room)
