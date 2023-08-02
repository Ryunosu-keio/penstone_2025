import matplotlib.pyplot as plt
import random
import time
import string
import asyncio
import websockets
import pandas as pd

def display_random_chars(delay, n_times, filename):
    df = pd.read_excel("imageCreationExcel/front/" + filename + "_front.xlsx")
    random_data = df["files"].to_list()
    # プロットのためのfigureとaxesを生成
    fig, ax = plt.subplots()
    plt.get_current_fig_manager().window.state('zoomed')


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

    plt.get_current_fig_manager().window.state('zoomed')
# display_random_chars(2.5, 50)

# if __name__ == '__main__':
#     char_list = []
#     # 使用例
# display_random_chars(2.5, 50)
    # print(char_list)

filename = input("ファイル名を教えてください")

async def server(websocket, path):
    async for message in websocket:
        if message == "start":
            # Start displaying images when receiving "start" message
            display_random_chars(2.5, 50, filename)

start_server = websockets.serve(server, "192.168.6.2", 8765)

# Start the server
asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()