import create_photos_fromlist as cpf
import back_rate as br
from library.transform_condition import transform_condition
import pandas as pd
import os

if __name__ == "__main__":
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
        if i < 3:
            df_back = pd.read_excel(
                "imageCreationExcel/back/0831_1_" + str(i) + ".xlsx")
            df_front = pd.read_excel(
                "imageCreationExcel/front/0831_1_" + str(i) + "_front.xlsx")
            df_front.to_excel("imageCreationExcel/front/" +
                              name + "_front.xlsx", index=False)
            df_back.to_excel("imageCreationExcel/back/" +
                             name + ".xlsx", index=False)
        else:
            br.back_rate(p=0.33, q=0.5, savefile=name, num=num,
                         use_photos_path=use_photos_path)
            cpf.create_photos_fromlist(usefile=name)
