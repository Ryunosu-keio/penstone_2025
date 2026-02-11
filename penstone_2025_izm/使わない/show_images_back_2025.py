# show_images_back_2025_fixed.py
# 目的：
# - t / b 以外は一切ログしない（押してないキーが残らない）
# - 1枚の画像につき t/b は「最初の1回だけ」記録（連打・長押しリピートで大量に出ない）
# - suppress=True でターミナルに文字が残らない（環境によっては管理者権限が必要）

import os
import time
import threading
from datetime import datetime

import pandas as pd
from PIL import Image
import matplotlib.pyplot as plt
from natsort import natsorted

import asyncio
import websockets
import keyboard

# =========================
# 設定
# =========================
DELAY_SEC = 2.5
WEBSOCKET_URL = "ws://192.168.12.18:8765"

# 画像リストの決め方：
# 1) Excel に image_name 列があれば、それを優先して表示順にする
# 2) なければフォルダの中身を natsort で並べる
USE_EXCEL_IMAGE_ORDER_IF_EXISTS = True

# =========================
# グローバル状態（キー入力スレッドと表示ループで共有）
# =========================
state_lock = threading.Lock()

start_time = 0.0                 # プログラム開始（ログ用）
display_start_time = 0.0         # 現在の画像を出し始めた時刻（ログ用）
current_figure = ""              # 現在表示中の画像ファイル名
current_status = ""              # Excelの status
answered_for_current_image = False

log_path = ""                    # 出力ログファイルパス


# =========================
# ログ書き込み
# =========================
def write_log(key_name: str, event_time: float):
    """
    t / b のみがここに来る想定。
    1枚の画像につき最初の1回だけログする。
    """
    global answered_for_current_image

    with state_lock:
        # 画像がまだ出てない / 既に回答済みなら無視
        if not current_figure:
            return
        if answered_for_current_image:
            return

        elapsed_time = event_time - start_time
        tap_time = event_time - display_start_time

        line = f"{datetime.now()} {key_name} {elapsed_time} {tap_time} {current_figure} {current_status}\n"

        # これで「1枚につき1回」になる
        answered_for_current_image = True

    # 書き込みはロック外（遅延を最小化）
    with open(log_path, mode="a", encoding="utf-8") as f:
        f.write(line)


# =========================
# 画像表示
# =========================
def display_images(image_files, df, delay, ax, folder_path):
    global start_time, display_start_time, current_figure, current_status, answered_for_current_image

    start_time = time.time()

    # df と画像の対応：行数ズレを避けたいので、status があればそれを参照する
    # image_files の順が df の順（image_name）なら i 対応でOK
    has_status = ("status" in df.columns)

    for i, image_file in enumerate(image_files):
        if not image_file.lower().endswith((".png", ".jpg", ".jpeg")):
            continue

        # 画像切り替え時に「未回答」に戻す
        with state_lock:
            current_figure = image_file
            current_status = str(df["status"].iloc[i]) if has_status and i < len(df) else ""
            answered_for_current_image = False
            display_start_time = time.time()

        image_path = os.path.join(folder_path, image_file)
        img = Image.open(image_path)

        # 表示サイズ（必要なら倍率調整）
        img = img.resize((int(img.width * 0.1), int(img.height * 0.1)))

        ax.imshow(img)
        plt.axis("off")
        plt.title("")
        plt.draw()
        plt.pause(0.01)

        # 正確に delay 間隔で進める（ドリフト防止）
        elapsed = time.time() - start_time
        next_time = start_time + ((elapsed // delay) + 1) * delay
        time.sleep(max(0, next_time - time.time()))

        ax.cla()

    plt.close()


# =========================
# Excel / 画像順序の決定
# =========================
def build_image_list(df, folder_path):
    files_in_dir = natsorted(os.listdir(folder_path))

    if USE_EXCEL_IMAGE_ORDER_IF_EXISTS and ("image_name" in df.columns):
        excel_order = [str(x) for x in df["image_name"].tolist()]
        # フォルダに存在するものだけにする
        set_dir = set(files_in_dir)
        ordered = [fn for fn in excel_order if fn in set_dir]
        # 念のため、Excelに無いがフォルダにある画像を末尾に追加したいなら以下を有効化
        # rest = [fn for fn in files_in_dir if fn not in set(ordered)]
        # ordered.extend(rest)
        return ordered

    return files_in_dir


# =========================
# メイン（WebSocket + 表示 + キーフック）
# =========================
def main():
    global log_path

    participant_number = input("参加者番号を入力してください: ").strip()
    use_images = input("どの画像セットを使いますか？: ").strip()
    key_bg = input("黒背景なら１,白背景なら２を入力してください: ").strip()

    # ログディレクトリとファイルの準備
    os.makedirs(f"log/{participant_number}", exist_ok=True)
    log_path = f"log/{participant_number}/{use_images}.txt"
    if not os.path.exists(log_path):
        with open(log_path, mode="w", encoding="utf-8") as f:
            f.write("")  # 空で作る

    # 背景色
    letter_face_color_list = {"1": "black", "2": "white"}
    plt.rcParams["figure.facecolor"] = letter_face_color_list.get(key_bg, "black")

    # キーフック：t/b だけ拾う（それ以外は拾わない＝押してないログが出ない）
    # suppress=True でターミナルへの入力を抑止（環境により管理者権限が必要な場合あり）
    hook_t = keyboard.on_press_key(
        "t",
        lambda e: write_log("t", getattr(e, "time", time.time())),
        suppress=True,
    )
    hook_b = keyboard.on_press_key(
        "b",
        lambda e: write_log("b", getattr(e, "time", time.time())),
        suppress=True,
    )

    # 任意：緊急終了（esc）
    hook_esc = keyboard.on_press_key(
        "esc",
        lambda e: (_ for _ in ()).throw(KeyboardInterrupt()),
        suppress=True,
    )

    async def client():
        # Excel / 画像フォルダ
        filedir = use_images.split("_")[0]
        excel_path = f"imageCreationExcel/back/{filedir}/{use_images}.xlsx"
        folder_path = f"D:/experiment_images/{use_images}/"

        df = pd.read_excel(excel_path)
        image_files = build_image_list(df, folder_path)

        fig, ax = plt.subplots()

        # 全画面（Windows + TkAgg想定。環境で効かない場合あり）
        try:
            plt.get_current_fig_manager().window.state("zoomed")
        except Exception:
            pass

        # 余白（あなたの元コードを踏襲）
        plt.subplots_adjust(left=0.507, bottom=-0.7, top=1, right=1)

        async with websockets.connect(WEBSOCKET_URL) as websocket:
            await websocket.send("start")
            display_images(image_files, df, DELAY_SEC, ax, folder_path)

    try:
        asyncio.get_event_loop().run_until_complete(client())
    except KeyboardInterrupt:
        print("\n[ESC] で終了しました。")
    finally:
        # フック解除
        try:
            keyboard.unhook(hook_t)
            keyboard.unhook(hook_b)
            keyboard.unhook(hook_esc)
        except Exception:
            pass


if __name__ == "__main__":
    main()
