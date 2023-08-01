import matplotlib.pyplot as plt
import random
import time
import string
import pandas as pd

# random_dataを生成
def generate_random_data(length=50, filename="random_data"):
    letters = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    digits = "0123789"
    # digits = "0123456789"
    
    # アルファベットと数字を結合
    # all_chars = list(letters + digits)
    
    # ランダムな順番でアルファベットと数字を選択
    data = []
    for i in range(length):
        # 1から9までのランダムな整数を生成
        random_number = random.randint(1, 9)
        
        # ランダムな乱数が8以下の場合はアルファベットを、9の場合は数字を選択
        if random_number <= 8:
            data.append(random.choice(letters))
        else:
            data.append(random.choice(digits))
    # save data to excel
    df = pd.DataFrame(data, columns=["files"])
    df.to_excel("imageCreationExcel/front/" + filename + "_front.xlsx", index=False)
        
    return data

data_length = 50  # 表示するデータの長さ
random_data = generate_random_data(data_length)
# 表示の遅延時間と表示回数を指定して表示
# delay = 2.5
# n_times = 50
# display_random_chars(delay, n_times, random_data)

