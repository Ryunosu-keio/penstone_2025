import create_photos_fromlist as cpf
import back_rate as br
from library.transform_condition import transform_condition
import pandas as pd
import os
import random

if __name__ == "__main__":
    original_param_dics = br.make_all_grid_dics()
    random.shuffle(original_param_dics)
    poped_param_dicts = original_param_dics.copy()

    # filename = input("使用するエクセルファイルの名前を決めてください")
    room_condition = input("部屋の明るさを入力してください（明るい場合1）")
    figure_condition = input("文字の明るさを入力してください（明るい場合1）")
    for sub in range(101, 120, 1):
        filename = str(sub)
        use_photos_path = transform_condition(room_condition, figure_condition)
        num = 48
        if not os.path.exists("imageCreationExcel/back/" + filename + "/"):
            os.mkdir("imageCreationExcel/back/" + filename + "/")
        if not os.path.exists("imageCreationExcel/front/" + filename + "/"):
            os.mkdir("imageCreationExcel/front/" + filename + "/")
        filename_dir = filename + "/" + filename
        for i in range(20):
            name = filename_dir + "_" + str(i)
            filename_str = filename + "_ " + str(i)
            # if i < 2:
            #     df_back = pd.read_excel
            #         "imageCreationExcel/back/0831_1_" + str(i) + ".xlsx")
            #     df_front = pd.read_excel(
            #         "imageCreationExcel/front/0831_1_" + str(i) + "_front.xlsx")
            #     df_front.to_excel("imageCreationExcel/front/" +
            #                       name + "_front.xlsx", index=False)
            #     df_back.to_excel("imageCreationExcel/back/" +
            #                      name + ".xlsx", index=False)
            # else:
            #     br.back_rate(p=0.33, q=0.5, savefile=name, num=num,
            #                  use_photos_path=use_photos_path)
            #     cpf.create_photos_fromlist(usefile=name)

            # dark experiment
            poped_param_dicts = br.back_rate(p=0.33, q=0.5, savefile=name, num=num,
                                             use_photos_path=use_photos_path, param_dicts=poped_param_dicts, original_param_dicts=original_param_dics)

            # paramlistが空ならば
            # if poped_param_list:
            #   poped_param_list =
            # ポップしたリストを返す
            # poped_param_list = br.back_rate(p=0.33, q=0.5, savefile=name, num=num,
            #                        use_photos_path=use_photos_path, param_list = poped_param_list)
            cpf.create_photos_fromlist(usefile=name)
