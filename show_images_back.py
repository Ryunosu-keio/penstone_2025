import os
import time
from PIL import Image
import matplotlib.pyplot as plt
import asyncio
import websockets
import keyboard
import threading
import pandas as pd

# logたち
log_file = "log.txt"
start_time = 0
figure = ""

# フロントが数字かどうか


def log_keyboard_input():
    global start_time
    global figure
    while True:
        event = keyboard.read_event()

        elapsed_time = event.time - start_time

        with open(log_file, mode='a') as f:
            f.write(f"{event.name} {elapsed_time} {figure}\n")


def display_images(folder_path, delay):
    global figure
    global start_time

    # df = pd.read_excel("imageCreationExcel/" + use_images + ".xlsx")
    # df["image_name"] の順番でimage_filesにソート
    # image_files = df["image_name"].tolist()
    # 数字の順番でソート
    image_files = sorted(os.listdir(folder_path))

    # 画像表示のためのfigureとaxesを生成
    plt.rcParams['figure.facecolor'] ="black"
    fig, ax = plt.subplots()

    # ウィンドウを全画面表示に設定
    plt.get_current_fig_manager().window.state('zoomed')
    
    # サブプロットの余白をすべて0に設定
    plt.subplots_adjust(left=0.5, bottom=-0.8, top=1, right=1)

    start_time = time.time()  # 初期時間を記録
    for image_file in image_files:
        print(image_file)
        # ファイルが画像であることを確認
        if image_file.lower().endswith(('.png', '.jpg', '.jpeg')):
            filename = image_file.split(".")[0]
            figure = filename
            image_path = os.path.join(folder_path, image_file)
            img = Image.open(image_path)           
            # ここを変えると画像のサイズを変更できる
            img = img.resize((int(img.width * 0.1), int(img.height * 0.1)))
            # 画像表示位置を変更
            # ax.set_position([0, 0, 1, 1])
            ax.imshow(img)
            plt.axis('off')  # 軸の非表示

            # 画像のタイトルをファイル名にする
            plt.title("")

            # 画像を表示
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

use_images = input("どの画像セットを使いますか？")

# display_images('experiment_images/' + use_images + "/", 2.5)

df = pd.read_excel("imageCreationExcel/back/" + use_images + ".xlsx")
status_list = df["status"].tolist()


keyboard_thread = threading.Thread(target=log_keyboard_input)

# スレッドを開始
keyboard_thread.start()

async def client():
    # Connect to the server
    global websocket
    async with websockets.connect("ws://192.168.6.2:8765") as websocket:
        # Send "start" message
        await websocket.send("start")

        # Start displaying random chars
        display_images('experiment_images/' + use_images + "/", 2.5)

# Start the client
asyncio.get_event_loop().run_until_complete(client())
