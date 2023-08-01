
import os
import time
from PIL import Image
import matplotlib.pyplot as plt
import asyncio
import websockets


def display_images(folder_path, delay):
    # フォルダ内のファイル名を取得し、アルファベット順にソート
    image_files = sorted(os.listdir(folder_path))

    # 画像表示のためのfigureとaxesを生成
    fig, ax = plt.subplots()

    start_time = time.time()  # 初期時間を記録

    for image_file in image_files:
        # ファイルが画像であることを確認
        if image_file.lower().endswith(('.png', '.jpg', '.jpeg')):
            image_path = os.path.join(folder_path, image_file)
            img = Image.open(image_path)
            
            # ここを変えると画像のサイズを変更できる
            img = img.resize((int(img.width * 0.6), int(img.height * 0.05)))
            # 画像表示位置を変更
            ax.set_position([0.4, -0.2, 1, 1])

            # 画像を表示
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

# 使用例
# display_images('experiment_images/', 2.5)


# 使用例
# display_images('experiment_images/', 2.5)

async def client():
    # Connect to the server
    async with websockets.connect("ws://192.168.6.2:8765") as websocket:
        # Send "start" message
        await websocket.send("start")

        # Start displaying random chars
        display_images('experiment_images/', 2.5)

# Start the client
asyncio.get_event_loop().run_until_complete(client())