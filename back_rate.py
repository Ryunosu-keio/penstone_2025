import glob
import random
import pandas as pd
from front_rate import generate_random_data

front_list = generate_random_data(50)
print(front_list)
# display_random_chars(2.5, 50, front_list)


savefile = input("保存するファイル名を入力してください")

original_images = glob.glob("testpic/*.jpg")

adjust_params = {
    "brightness": [0, 60], # パラメーターの値を入れる
    "contrast": [0.8,1.2],
    "gamma": [0.5,1.1],
    "sharpness":[0, 1.0],
    "equalization":[4,32]
}

condition_list = []
chosen_images = []
similar_char_list= {"0":"C","1":"I","2":"S","3":"E","7":"T","8":"B","9":"P"}

p = 0.3 #数字が一致する確率
q = 0.3 #数字が一致しないときに似てる記号が現れる確率
for i in range(50):
    if front_list[i].isdigit():#数字だったら
        if random.random() < p:#確率pで
            #一致するchosen_listを作る
            for image_path in original_images:#original_imagesから
                first_char = image_path.split("/")[-1][0]#一文字目を調べて
                if first_char == front_list[i]:#1文字目がその数字と一致したら
                    chosen_images.append(image_path)#候補に採用して
                    print(chosen_images)
            image = random.choice(chosen_images)#その中からランダムで選ぶ
        else:#確率1-p
            #一致しないchosen_listを作る
            for image_path in original_images:
                first_char = image_path.split("/")[-1][0]
                if first_char != front_list[i]:
                    chosen_images.append(image_path)
                    if random.random() < q:
                        key = front_list[i]#ペアのアルファベットを探す
                        similar_images = []
                        for image_path in chosen_images:
                            first_char = image_path.split("/")[-1][0]#一文字目を調べて
                            if first_char == similar_char_list[key]:#1文字目が数字と似たアルファベットだったら
                                 similar_images.append(image_path)#候補に採用して
                                 image = random.choice(similar_images)#ランダムに選ぶ
                    else:
                        key = front_list[i]#ペアのアルファベットを探す
                        different_images = []
                        for image_path in chosen_images:
                            first_char = image_path.split("/")[-1][0]#一文字目を調べて
                            if first_char != similar_char_list[key]:#1文字目が数字と似たアルファベットではなかったら
                                different_images.append(image_path)#候補に採用して
                                image = random.choice(different_images)#ランダムに選ぶ
    else:
        image = random.choice(original_images)
            
   
if "/" in image :
    filename = image.split("/")[-1]
    filename = "testpic/" + filename
else:
    filename = image.split("\\")[-1]
    filename = "testpic\\" + filename
# filename = filename.split(".")[0]
selected_parameters = {}
# random choice from adjust_params by 2~3
selected_parameters_keys = random.sample(list(adjust_params.keys()), random.randint(2,3))

# Check if 'equalization' is selected and move it to the end
if "equalization" in selected_parameters_keys:
    selected_parameters_keys.remove("equalization")
    selected_parameters_keys.append("equalization")
# create dataframe [filename, param1, param1_value, param2, param2_value, param3, param3_value]
for key in selected_parameters_keys:
    selected_parameters[key] = random.uniform(adjust_params[key][0], adjust_params[key][1])
if len(selected_parameters_keys) == 2:
    condition_list.append([filename, selected_parameters_keys[0], selected_parameters[selected_parameters_keys[0]], selected_parameters_keys[1], selected_parameters[selected_parameters_keys[1]], "None", "None"])
else:
    condition_list.append([filename, selected_parameters_keys[0], selected_parameters[selected_parameters_keys[0]], selected_parameters_keys[1], selected_parameters[selected_parameters_keys[1]], selected_parameters_keys[2], selected_parameters[selected_parameters_keys[2]]])
df = pd.DataFrame(condition_list, columns=["filename", "param1", "param1_value", "param2", "param2_value", "param3", "param3_value"])
print(df)
df.to_excel("imageCreationExcel/" + savefile  + ".xlsx", index=False)