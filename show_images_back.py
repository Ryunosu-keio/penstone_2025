import os
import time
from PIL import Image
import matplotlib.pyplot as plt
import asyncio
import websockets
import keyboard
import threading

log_file = "log.txt"

start_time = 0

def log_keyboard_input():
    global start_time
    while True:

        event = keyboard.read_event()

        elapsed_time = event.time - start_time

        with open(log_file, mode='a') as f:
            f.write(f"{event.name} {elapsed_time}\n")


def display_images(folder_path, delay):
    global start_time
    # フォルダ内のファイル名を取得し、アルファベット順にソート
    image_files = sorted(os.listdir(folder_path))

    # 画像表示のためのfigureとaxesを生成
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

keyboard_thread = threading.Thread(target=log_keyboard_input)

# スレッドを開始
keyboard_thread.start()

# 使用例
display_images('experiment_images/sample5/', 2.5)

# async def client():
#     # Connect to the server
#     async with websockets.connect("ws://192.168.6.2:8765") as websocket:
#         # Send "start" message
#         await websocket.send("start")

#         # Start displaying random chars
#         display_images('experiment_images/', 2.5)

# # Start the client
# asyncio.get_event_loop().run_until_complete(client())


# # 'b'キーが押されたときにclient関数を実行する
# keyboard.add_hotkey('b', lambda: asyncio.get_event_loop().run_until_complete(client()))

# # 何かキーが押されるまで待つ
# keyboard.wait()