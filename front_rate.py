import matplotlib.pyplot as plt
import random
import time
import string

def display_random_chars(delay, n_times, random_data):
    # プロットのためのfigureとaxesを生成
    fig, ax = plt.subplots()

    start_time = time.time()  # 初期時間を記録

    for char in random_data:
        # ランダムな位置を選択
        x_pos = random.uniform(0, 1)
        y_pos = random.uniform(0, 1)

        # ランダムな位置に文字を表示
        ax.text(x_pos, y_pos, char, transform=ax.transAxes, fontsize=40)

        # 軸の非表示
        plt.axis('off')

        # タイトルを設定
        plt.title("")

        # プロットを表示
        plt.draw()
        plt.pause(0.01)

        # プログラムの実行開始からの経過時間を計算
        elapsed_time = time.time() - start_time

        # 次のイテレーションの開始時刻を計算
        next_time = start_time + ((elapsed_time // delay) + 1) * delay

        # 次のイテレーションの開始時刻まで待つ
        time.sleep(max(0, next_time - time.time()))

        # クリアー画像
        ax.cla()

    plt.close()

# random_dataを生成
def generate_random_data(length=50):
    letters = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    digits = "0123456789"
    
    # アルファベットと数字を結合
    all_chars = list(letters + digits)
    
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
        
    return data

data_length = 50  # 表示するデータの長さ
random_data = generate_random_data(data_length)
# 表示の遅延時間と表示回数を指定して表示
# delay = 2.5
# n_times = 50
# display_random_chars(delay, n_times, random_data)

