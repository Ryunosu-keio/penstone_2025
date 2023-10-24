import create_photos_fromlist as cpf
import back_rate as br
from library.transform_condition import transform_condition
import pandas as pd
import os
import random

if __name__ == "__main__":

#############################################################################
# dark experiment
    # グリッドリストを作成する
    # シャッフルするのも必要かも
    
    adjust_params = {
    "brightness": [0, 30],  
    "contrast": [0.8, 1.2],
    "gamma": [0.5, 1.1],
    "sharpness": [0, 1.0],
    "equalization": [4, 32]
    }

    popped_param_list = br.make_all_grid_dicts(adjust_params)
    random.shuffle(popped_param_list)
    popped_param_list_5 = popped_param_list*5
########################################################################################

    filename = input("使用するエクセルファイルの名前を決めてください")
    room_condition = input("部屋の明るさを入力してください（明るい場合1）")
    figure_condition = input("文字の明るさを入力してください（明るい場合1）")
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

        #############################################################################
        # default
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
        
        #############################################################################
        # dark experiment
        br.back_rate(p=0.33, q=0.5, savefile=name, num=num,
                         use_photos_path=use_photos_path)
        
        #paramlistが空ならば
        # if popped_param_list :
        #   popped_param_list = make_all_grid_dict()
        #ポップしたリストを返す      
        # popped_param_list = br.back_rate(p=0.33, q=0.5, savefile=name, num=num,
        #                        use_photos_path=use_photos_path, param_list = popped_param_list)
        cpf.create_photos_fromlist(usefile=name)
        ##############################################################################