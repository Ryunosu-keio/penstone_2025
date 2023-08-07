import matplotlib.pyplot as plt
import random
import time
import string
import asyncio
import websockets
import pandas as pd

should_proceed = False
status_now = 0
count = 0

def display_random_chars(delay, filename, key):
    global status_list
    global status_now
    global should_proceed
    global count

    df = pd.read_excel("imageCreationExcel/front/" + filename + "_front.xlsx")
    random_data = df["files"].to_list()
    #背景色の指定
    letter_face_color_list ={"1":["black","white"], "2":["white","black"]}
    letter_face_color_list
    plt.rcParams['figure.facecolor'] = letter_face_color_list[key][0]
    # プロットのためのfigureとaxesを生成
    fig, ax = plt.subplots()
    
    plt.get_current_fig_manager().window.state('zoomed')


    start_time = time.time()  # 初期時間を記録

    for char in random_data:
        status_now = status_list[count]

        ax.set_facecolor("yellow")
        # ランダムな位置を選択
        # x_pos = random.uniform(0, 1)
        # y_pos = random.uniform(0, 1)
        x_pos = 0.5
        y_pos = 0.5

        # ランダムな位置に文字を表示、フォントを指定
        ax.text(x_pos, y_pos, char, transform=ax.transAxes, fontsize=40, color=letter_face_color_list[key][1])
        
        # 軸の非表示
        plt.axis('off')

        # タイトルを設定
        plt.title("")

    
        # プロットを表示
        plt.draw()
        plt.pause(0.01)
        while status_now != 4 and not should_proceed:
            time.sleep(0.1)

        # プログラムの実行開始からの経過時間を計算
        elapsed_time = time.time() - start_time

        # 次のイテレーションの開始時刻を計算
        next_time = start_time + ((elapsed_time // delay) + 1) * delay

        # 次のイテレーションの開始時刻まで待つ
        time.sleep(max(0, next_time - time.time()))

        # クリアー画像
        ax.cla()
        count += 1

    plt.close()

    plt.get_current_fig_manager().window.state('zoomed')


filename = input("ファイル名を教えてください")
key = input("黒背景なら１,白背景なら２を入力してください")

df = pd.read_excel("imageCreationExcel/back/" + filename + ".xlsx")
status_list = df["status"].to_list()


# display_random_chars(2.5, 50, filename)

async def server(websocket, path):
    global should_proceed
    async for message in websocket:
        if message == "start":
            # Start displaying images when receiving "start" message
            display_random_chars(2.5,filename,key)
        elif message == "proceed":
            should_proceed = True

start_server = websockets.serve(server, "192.168.6.2", 8765)

# Start the server
asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()