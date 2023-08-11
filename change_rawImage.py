from PIL import Image
import glob

output_path = "testpic_yobi_transformed/"

files = glob.glob("testpic_yobi/*.JPG")

for file in files:
    filename = file.split("\\")[-1]
    filename = filename.split(".")[0]
    # 画像を読み込む
    image = Image.open(file)

    # 画像を左右反転
    flipped_image = image.transpose(Image.FLIP_LEFT_RIGHT)

    # 画像のサイズを取得
    width, height = flipped_image.size

    # 縦：横 = 14：47 の比率にリサイズするための新しいサイズを計算
    new_width = width
    new_height = int((14/47) * new_width)

    # 画像の中心を基準にクロッピングする座標を計算
    left = 0
    right = new_width
    top = (height - new_height) // 2
    bottom = top + new_height

    # 画像をクロッピング
    cropped_image = flipped_image.crop((left, top, right, bottom))

    # 画像を保存
    cropped_image.save(output_path+filename+".JPG")
