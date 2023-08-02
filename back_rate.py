import glob
import random
import pandas as pd
from front_rate import generate_random_data

# front_list = generate_random_data(50)
# print(front_list)

# 確率たち
p = 0.5 #数字が一致する確率
q = 0.8 #数字が一致しないときに似てる記号が現れる確率

a = "0"

print(a.isdigit())


savefile = input("保存するファイル名を入力してください")
num = int(input("表示回数を入力してください"))

front_list = generate_random_data(num, savefile)

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
figures = [] #イメージのファイルの一文字目を入れるリスト
images = [] #確定したイメージを入れるリスト
status = [] #数字が一致するかどうかを入れるリスト


for image_path in original_images:
    if "/" in image_path:
        first_char = image_path.split("/")[-1][0]
    else:
        first_char = image_path.split("\\")[-1][0]
    figures.append(first_char)
print(figures)

for i in range(num):
    chosen_images = []
    if front_list[i].isdigit():#数字だったら
        print("############数字だったよ#############")
        if front_list[i] in similar_char_list.keys():#数字の画像があるか
            print("############似てる数字だったよ#############")
            if random.random() < p:#確率pで
                # print("p")
                for j in range(len(figures)):
                    print(figures[j])
                    if figures[j] == front_list[i]:#1文字目がその数字と一致したら
                        image = original_images[j]
                        print("############一致したよ#############")
                        status.append("一致")
                        break
            else:#確率1-p
                # print("1-p")
                similar_char = similar_char_list[front_list[i]]#似てる数字を探す
                if random.random() < q:
                    for j in range(len(figures)):
                        if figures[j] == similar_char:
                            image = original_images[j]
                            print("############一致しなかった、ペアのアルファベットにするよ#############")
                            status.append("ペアのアルファベット")
                            break
                else:
                    different_images = []
                    for j in range(len(figures)):
                        if figures[j] != front_list[i]:
                            different_images.append(original_images[j])
                    image = random.choice(different_images)
                    status.append("ペアのアルファベットではない")
                    print("############一致しなかった、ペアのアルファベットではないよ#############")
        else:
            status.append("画像がない数字")
            print("############ここにない数字だよ#############")
            image = random.choice(original_images)
    else:
        status.append("アルファベット")
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
    if "/" in images[i] :
        filename = images[i].split("/")[-1]
        filename = "testpic/" + filename
    else:
        filename = images[i].split("\\")[-1]
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
        condition_list.append([filename, selected_parameters_keys[0], selected_parameters[selected_parameters_keys[0]], selected_parameters_keys[1], selected_parameters[selected_parameters_keys[1]], "None", "None", status[i]])
    else:
        condition_list.append([filename, selected_parameters_keys[0], selected_parameters[selected_parameters_keys[0]], selected_parameters_keys[1], selected_parameters[selected_parameters_keys[1]], selected_parameters_keys[2], selected_parameters[selected_parameters_keys[2]], status[i]])
df = pd.DataFrame(condition_list, columns=["filename", "param1", "param1_value", "param2", "param2_value", "param3", "param3_value", "status"])
print(df)
df.to_excel("imageCreationExcel/back/" + savefile  + ".xlsx", index=False)