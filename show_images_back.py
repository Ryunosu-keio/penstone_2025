
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
            plt.pause(delay)  # ここで一時停止すると、図が表示されます

            # クリアー画像
            ax.cla()

    plt.close()

# 使用例
# display_images('experiment_images/', 2.5)
async def server(websocket, path):
    async for message in websocket:
        if message == "start":
            # Start displaying images when receiving "start" message
            display_images('experiment_images/', 2.5)

start_server = websockets.serve(server, "localhost", 8765)

# Start the server
asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()