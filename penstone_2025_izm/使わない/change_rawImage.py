from PIL import Image
import glob
import os
from tqdm import tqdm
from library.transform_condition import transform_condition


# output_path = "testpic_yobi_transformed/"
room = input("変換する画像の部屋の条件を入力してください（明るい場合1）")
figure = input("変換する画像の文字の条件を入力してください（明るい場合1）")
path = transform_condition(room, figure)
output_path = "pictures/transformed/" + path + "/"
if not os.path.exists(output_path):
    os.makedirs(output_path)

files = glob.glob("pictures/original_data/" + path + "/*.JPG")

for file in tqdm(files):
    filename = file.split("\\")[-1]
    filename = filename.split(".")[0]
    # 画像を読み込む
    image = Image.open(file)

    # 画像を左右反転
    if path == "roomDark_figureBright":
        image = image.transpose(Image.FLIP_LEFT_RIGHT)

    # 画像のサイズを取得
    width, height = image.size

    # 縦：横 = 14：47 の比率にリサイズするための新しいサイズを計算
    new_width = width
    new_height = int((14/47) * new_width)

    # 画像の中心を基準にクロッピングする座標を計算
    left = 0
    right = new_width
    top = (height - new_height) // 2
    bottom = top + new_height

    # 画像をクロッピング
    cropped_image = image.crop((left, top, right, bottom))

    # 画像を保存
    cropped_image.save(output_path+filename+".JPG")
