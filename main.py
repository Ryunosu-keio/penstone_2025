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
        br.back_rate(p=0.33, q=0.5, savefile=name, num=num,
                         use_photos_path=use_photos_path)
        
        #paramlistが空ならば
        # if poped_param_list:
        #   poped_param_list = 
        #ポップしたリストを返す      
        # poped_param_list = br.back_rate(p=0.33, q=0.5, savefile=name, num=num,
        #                        use_photos_path=use_photos_path, param_list = poped_param_list)
        cpf.create_photos_fromlist(usefile=name)


def make_all_grid_dics(adjust_params):
        
    # 3つのキーの組み合わせを取得
    three_key_combinations = list(combinations(adjust_params.keys(), 3))

    # 各キーに対する値のリストを3分割する関数
    def split_into_three(r):
        return [(round(r[0] + (r[1] - r[0]) * i/3, 2), round(r[0] + (r[1] - r[0]) * (i+1)/3, 2)) for i in range(3)]

    all_combinations = []

    # 3つのキーのそれぞれの組み合わせに対して処理
    for comb in three_key_combinations:
        ranges = [split_into_three(adjust_params[key]) for key in comb]
        
        # 3つのキーのそれぞれの3分割したリストのすべての組み合わせを作成
        for values in product(*ranges):
            dic = {comb[i]: values[i] for i in range(3)}
            all_combinations.append(dic)

    # 結果を表示
    for comb in all_combinations:
        print(comb)

    return all_combinations