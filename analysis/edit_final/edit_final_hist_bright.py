import pandas as pd
from PIL import Image
import numpy as np
from tqdm import tqdm

def calculate_average_brightness(image):
    # グレースケールに変換
    grayscale_image = image.convert('L')
    # numpy配列に変換
    img_array = np.array(grayscale_image)
    # 合計輝度値を計算
    total_brightness = img_array.sum()
    # ピクセル数を計算
    num_pixels = img_array.size
    # 平均輝度を計算
    return total_brightness / num_pixels

# データフレームの読み込み
df = pd.read_excel('../data/final_part1/final_bright_add_modified.xlsx')

# 'experiment_images'ディレクトリのパスと組み合わせて、完全な画像パスを生成
# folder_nameとfile_nameの両方を文字列に変換してから結合
df['image_path'] = '../experiment_images/' + df['folder_name'].astype(str) + '_' + df['file_name'].astype(str) + '/' + df['image_name'].astype(str)


# 輝度値を格納するためのリスト
brightness_values = [] 

# 各画像に対して輝度値を計算
for image_path in tqdm(df['image_path']):
    try:
        img = Image.open(image_path)
        brightness = calculate_average_brightness(img)
        brightness_values.append(brightness)
    except FileNotFoundError:
        print(f"Image at {image_path} not found.")
        brightness_values.append(None)  # 画像が見つからない場合はNoneを追加nn

# 新しい列として輝度値をデータフレームに追加
df['hist_bright'] = brightness_values


# データフレームを保存（必要に応じて）
df.to_excel('../data/final_part1/updated_dataframe.xlsx', index=False)
