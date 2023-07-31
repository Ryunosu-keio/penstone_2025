import matplotlib.pyplot as plt
import random
import time
import string
import asyncio
import websockets

def display_random_chars(delay, n_times):
    # ランダムな数字とアルファベットを生成
    all_chars = string.digits + string.ascii_uppercase

    # プロットのためのfigureとaxesを生成
    fig, ax = plt.subplots()

    for _ in range(n_times):
        # ランダムな位置を選択
        x_pos = random.uniform(0, 1)
        y_pos = random.uniform(0, 1)

        # ランダムな文字を選択
        char = random.choice(all_chars)

        # ランダムな位置に文字を表示
        ax.text(x_pos, y_pos, char, transform=ax.transAxes, fontsize=40)

        # 軸の非表示
        plt.axis('off')

        # タイトルを設定
        plt.title("")

        # プロットを一時停止
        plt.pause(delay)

        # クリアー画像
        ax.cla()
        # char_list.append([char, x_pos, y_pos])

    plt.close()

# if __name__ == '__main__':
#     char_list = []
#     # 使用例
# display_random_chars(2.5, 50)
    # print(char_list)

async def client():
    # Connect to the server
    async with websockets.connect("ws://localhost:8765") as websocket:
        # Send "start" message
        await websocket.send("start")

        # Start displaying random chars
        display_random_chars(2.5, 50)

# Start the client
asyncio.get_event_loop().run_until_complete(client())