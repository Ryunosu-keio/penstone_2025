import glob
import random
import pandas as pd
from itertools import combinations, product
from front_rate import generate_random_data


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



def back_rate(p=0.33, q=0.5, savefile="", num=48, use_photos_path="roomDark_figureBright"):
    # 確率たち
    # p = 0.5 #数字が一致する確率
    # q = 0.8 #数字が一致しないときに似てる記号が現れる確率

    # ステータス
    # 0:数字が出現し、一致する
    # 1:数字が出現するが、似た記号が現れる
    # 2:数字が出現するが、似た記号が現れない
    # 3:数字が出現するが、数字の画像がない
    # 4:数字が出現しない

    # savefile = input("保存するファイル名を入力してください")
    # num = int(input("表示回数を入力してください"))
    use_photos_path = "pictures\\transformed\\" + use_photos_path

    front_list = generate_random_data(num, savefile)

    original_images = glob.glob(use_photos_path + "/*.jpg")
    print(original_images)

    ####################################################################################
    # default
    # adjust_params = {
    #     "brightness": [0, 30],  # パラメーターの値を入れる
    #     "contrast": [0.8, 1.2],
    #     "gamma": [0.5, 1.1],
    #     "sharpness": [0, 1.0],
    #     "equalization": [4, 32]
    # }


    ####################################################################################
    #add experiment
    # gcs_red_1 = {"gamma": [0.7,0.9], "contrast": [0.8,0.93], "sharpness":[0.66, 1.0]}

    # gcs_1 = {"gamma": [0.7,0.9], "contrast": [0.8,0.93], "sharpness":[1.0, 1.33]}

    # gcs_2 = {"gamma": [0.7,0.9], "contrast": [0.66,0.8], "sharpness":[1.0, 1.33]}

    # gcs_3 = {"gamma": [0.7,0.9], "contrast": [0.66,0.8], "sharpness":[0.66, 1.0]}


    # gcs_red_2 = {"gamma": [0.9,1.1], "contrast": [1.066,1.2], "sharpness":[0.33, 0.66]}

    # gcs_4 = {"gamma": [0.9,1.1], "contrast": [1.2,1.333], "sharpness":[0.33, 0.66]}

    # gcs_5 = {"gamma": [1.1,1.3], "contrast": [1.066,1.2], "sharpness":[0.33, 0.66]}

    # gcs_6 = {"gamma": [1.1,1.3], "contrast": [1.2,1.333], "sharpness":[0.33, 0.66]}

    # gcs_void = {"gamma": [0.5,0.7], "contrast": [0.8,0.93], "sharpness":[0.66, 1.0]}


    # gcb_void = {"gamma": [0.7,1.1], "contrast": [1.066,1.2], "brightness":[20,30]}


    # gse = {"gamma":[0.3,0.7],"sharpness":[0.33,0.66],"equalization":[13,23]}

    # cse_1 = {"contrast":[0.933,1.066],"sharpness":[0.666,1.333],"equalization":[13,23]}

    # cse_2 = {"contrast":[0.933,1.066],"sharpness":[0.333,0.666],"equalization":[1,13]}

    # cse_3 = {"contrast":[1.066,1.333],"sharpness":[0.333,0.666],"equalization":[13,23]}

    # param_dics = [gcs_red_1,gcs_1,gcs_2,gcs_3,gcs_red_2,gcs_4,gcs_5,gcs_6,gcs_void,gcb_void,gse,cse_1,cse_2,cse_3]
   
    ###############################################################################################
    # dark experiment

    adjust_params = {
    "brightness": [0, 30],  
    "contrast": [0.8, 1.2],
    "gamma": [0.5, 1.1],
    "sharpness": [0, 1.0],
    "equalization": [4, 32]
    }
    
    param_dics_original = make_all_grid_dics(adjust_params)
    print("param_dics_original",param_dics_original)
    param_dics = param_dics_original.copy()
    random.shuffle(param_dics)
    print("param_dics",param_dics)
    ##############################################################################################

    
    condition_list = []
    chosen_images = []
    similar_char_list = {"0": "C", "1": "I", "2": "S",
                         "3": "E", "7": "T", "8": "B", "9": "P"}
    figures = []  # イメージのファイルの一文字目を入れるリスト
    images = []  # 確定したイメージを入れるリスト
    status = []  # 数字が一致するかどうかを入れるリスト

    for image_path in original_images:
        if "/" in image_path:
            first_char = image_path.split("/")[-1][0]
        else:
            first_char = image_path.split("\\")[-1][0]
        figures.append(first_char)
    print(figures)



    for i in range(num):
        chosen_images = []
        if front_list[i].isdigit():  # 数字だったら
            #################################pop""""""""""""""""""""""###################"
            print("############数字だったよ#############")
            if front_list[i] in similar_char_list.keys():  # 数字の画像があるか
                print("############似てる数字だったよ#############")
                if random.random() < p:  # 確率pで
                    # print("p")
                    for j in range(len(figures)):
                        print(figures[j])
                        if figures[j] == front_list[i]:  # 1文字目がその数字と一致したら
                            image = original_images[j]
                            print("############一致したよ#############")
                            status.append(0)  # 数字が一致する
                            break
                else:  # 確率1-p
                    # print("1-p")
                    similar_char = similar_char_list[front_list[i]]  # 似てる数字を探す
                    if random.random() < q:
                        for j in range(len(figures)):
                            if figures[j] == similar_char:
                                image = original_images[j]
                                print(
                                    "############一致しなかった、ペアのアルファベットにするよ#############")
                                status.append(1)  # 数字が一致しないが、似てる記号が現れる
                                break
                    else:
                        different_images = []
                        for j in range(len(figures)):
                            if figures[j] != front_list[i]:
                                different_images.append(original_images[j])
                        image = random.choice(different_images)
                        status.append(2)  # 数字が一致せず、似てる記号も現れない
                        print("############一致しなかった、ペアのアルファベットではないよ#############")
            else:
                status.append(3)  # 数字が出現するが、数字の画像がない
                print("############ここにない数字だよ#############")
                image = random.choice(original_images)
            ######owattara popo###################
        else:
            status.append(4)  # 数字が出現しない
            print("############アルファベットだよ#############")
            image = random.choice(original_images)
        images.append(image)
        print(front_list[i])
        print(len(images))
        print(images[i])
        print(len(status))
        print(status[i])

    print(chosen_images)
    print(images)
    for i in range(len(images)):
        if "/" in images[i]:
            filename = images[i].split("/")[-1]
            filename = use_photos_path + "/" + filename
        else:
            filename = images[i].split("\\")[-1]
            filename = use_photos_path + "\\" + filename
        # filename = filename.split(".")[0]
        selected_parameters = {}

        # random choice from adjust_params by 2~3
##############################################################################################################################
        #default
        # selected_parameters_keys = random.sample(
        #     list(adjust_params.keys()), random.randint(2, 3))
        
##############################################################################################################################
        # add experiment
        # selected_param_dic = random.choice(param_dics)
        # selected_parameters_keys = list(selected_param_dic.keys())
############################################################################################################################        
        # dark experiment
        # shuffled_dics = param_dics.copy()
        # random.shuffle(shuffled_dics)
        # If all dictionaries have been chosen, reshuffle
        # if not param_dics:
        #     shuffled_dics = param_dics.copy()
        #     random.shuffle(shuffled_dics)
        #     print("shuffled_dics is reshuffled at",i)
        # print("_",i)
        # selected_param_dic = shuffled_dics.pop(0)

        selected_param_dic = param_dics[i]
        selected_parameters_keys = list(selected_param_dic.keys())
        print("selected_param_dic",selected_param_dic)
        print("selected_parameters_keys",selected_parameters_keys)
    
##############################################################################################################################

        # brightnesとequalization同時に試すために一旦コメントアウト。
        # # Check if 'equalization' and 'brightness' are both selected and if so, remove one of them randomly
        # if 'equalization' in selected_parameters_keys and 'brightness' in selected_parameters_keys:
        #     remove_key = random.choice(['equalization', 'brightness'])
        #     selected_parameters_keys.remove(remove_key)
        #     # append one more other parameter to selected_parameters_keys randomly withpout 'equalization' or 'brightness
        #     # Add another key from the ones not yet chosen
        #     ############################################################################
        #     # default
        #     # not_selected_keys = [key for key in adjust_params.keys(
        #     # ) if key not in selected_parameters_keys]
        #     #############################################################################
        #     # add experiment
        #     # not_selected_keys = [key for key in selected_param_dic.keys(
        #     # ) if key not in selected_parameters_keys]
        #     ###################################################################################
        #     # dark experiment
        #     not_selected_keys = [key for key in selected_param_dic.keys(
        #     ) if key not in selected_parameters_keys]
        #     ###################################################################################
        #     # Ensure that 'equalization' and 'brightness' are not both added again
        #     if 'equalization' in selected_parameters_keys:
        #         not_selected_keys.remove('brightness')
        #     if 'brightness' in selected_parameters_keys:
        #         not_selected_keys.remove('equalization')

        #     selected_parameters_keys.append(random.choice(not_selected_keys))

        # Check if 'equalization' is selected and move it to the end
        if "equalization" in selected_parameters_keys:
            selected_parameters_keys.remove("equalization")
            selected_parameters_keys.append("equalization")
        # create dataframe [filename, param1, param1_value, param2, param2_value, param3, param3_value]
        for key in selected_parameters_keys:
            #####################################################################################################
            # default
            # selected_parameters[key] = random.uniform(
            #     adjust_params[key][0], adjust_params[key][1])
            #############################################################################################################
            # add experiment
            selected_parameters[key] = random.uniform(selected_param_dic[key][0], selected_param_dic[key][1])
            ############################################################################################################################
        if len(selected_parameters_keys) == 2:
            condition_list.append([filename, selected_parameters_keys[0], selected_parameters[selected_parameters_keys[0]],
                                selected_parameters_keys[1], selected_parameters[selected_parameters_keys[1]], "None", "None", status[i]])
        else:
            condition_list.append([filename, selected_parameters_keys[0], selected_parameters[selected_parameters_keys[0]], selected_parameters_keys[1],
                                selected_parameters[selected_parameters_keys[1]], selected_parameters_keys[2], selected_parameters[selected_parameters_keys[2]], status[i]])
    df = pd.DataFrame(condition_list, columns=[
                      "filename", "param1", "param1_value", "param2", "param2_value", "param3", "param3_value", "status"])
    print(df)
    df.to_excel("imageCreationExcel/back/" + savefile + ".xlsx", index=False)
    # pop
    return pop