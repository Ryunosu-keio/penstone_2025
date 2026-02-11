import matplotlib.pyplot as plt
import pandas as pd
import os
import time
import keyboard
import threading
from PIL import Image
from datetime import datetime

# ==========================================
# グローバル変数・設定
# ==========================================
state_lock = threading.Lock()
experiment_start_time = 0.0
trial_start_time = 0.0

# 1枚目（trial0）の表示時刻（time.time()）を基準にフレーム換算する
first_display_time_unix = None

# 1試行ごとの一時記録用
current_trial_data = {
    "answered": False,
    "key": None,
    "rt": None,
    "timestamp": None
}

# 全試行の結果を貯めるリスト
all_trial_results = []

# ==========================================
# 正解キーの設定
# ==========================================
# Match    -> t (一致)
# Mismatch -> b (不一致)
# Ignore   -> None (押さないのが正解)
TARGET_KEY_MAP = {
    "Match": "t",
    "Mismatch": "b"
}

# ==========================================
# ステータス正規化（Excelが数値/文字どっちでも耐える）
# ==========================================
def normalize_status(x):
    """
    Excelのstatusが
      - "Match"/"Mismatch"/"Ignore"
      - 1/2/4
      - "Filler" 等
    のどれでも、"Match"/"Mismatch"/"Ignore" に寄せる
    """
    if x is None:
        return "Ignore"

    s = str(x).strip()

    # 数値っぽい
    if s.isdigit():
        v = int(s)
        if v == 1:
            return "Match"
        if v == 2:
            return "Mismatch"
        if v == 4:
            return "Ignore"
        return "Ignore"

    # 文字
    s_low = s.lower()
    if s_low == "match":
        return "Match"
    if s_low == "mismatch":
        return "Mismatch"
    if s_low in ["ignore", "filler", "no response", "none"]:
        return "Ignore"

    # その他は安全側（Ignore）へ
    return "Ignore"


# ==========================================
# キー入力ハンドラ (suppress対応)
# ==========================================
def on_key_event(event):
    """キーが押された瞬間に呼ばれる関数"""
    global current_trial_data, trial_start_time

    key_name = event.name  # 't' or 'b'

    with state_lock:
        # すでに回答済みなら無視（1試行1回まで）
        if current_trial_data["answered"]:
            return

        # データを記録
        current_trial_data["answered"] = True
        current_trial_data["key"] = key_name
        current_trial_data["timestamp"] = datetime.now()
        current_trial_data["rt"] = time.time() - trial_start_time


# ==========================================
# メイン処理
# ==========================================
def main():
    global experiment_start_time, trial_start_time, current_trial_data, all_trial_results, first_display_time_unix

    # 1. 入力
    participant_id = input("参加者番号を入力してください (例: 101): ").strip()
    set_num = input("セット番号を入力してください (例: 0): ").strip()

    print("\n条件を選択してください:")
    print("1: Bright (昼・背景白)")
    print("2: Dark   (夜・背景黒)")
    cond_input = input("選択肢を入力 (1 or 2): ").strip()

    cond_label = ""
    bg_mode = ""

    if cond_input == "1":
        cond_label = "Bright"
        bg_mode = "2"  # 白
        print(f">> Bright (昼) モードでセット {set_num} を開始します")
    elif cond_input == "2":
        cond_label = "Dark"
        bg_mode = "1"  # 黒
        print(f">> Dark (夜) モードでセット {set_num} を開始します")
    else:
        print("エラー: 1 か 2 を入力してください。")
        return

    # 2. パス構築
    # Excelファイル名: 101_0.xlsx (Conditionは含まない)
    excel_filename = f"{participant_id}_{set_num}"
    # 画像フォルダ名: 101_0_Bright (Conditionを含む)
    unique_identifier_for_folder = f"{participant_id}_{set_num}_{cond_label}"

    # Back Excel Path (imageCreationExcel/back/Bright/101/...)
    base_back_dir = f"imageCreationExcel/back/{cond_label}/{participant_id}"
    excel_path = os.path.join(base_back_dir, f"{excel_filename}.xlsx")

    # Front Excel Path
    base_front_dir = f"imageCreationExcel/front/{cond_label}/{participant_id}"
    front_path = os.path.join(base_front_dir, f"{excel_filename}_front.xlsx")

    # 画像フォルダ
    img_folder_path = f"F:/experiment_images_verify/{unique_identifier_for_folder}/"

    # ファイル存在確認
    if not os.path.exists(excel_path):
        print(f"\nエラー: Excelファイルが見つかりません。\nパス: {excel_path}")
        return
    if not os.path.exists(front_path):
        print(f"\nエラー: Front Excelが見つかりません。\nパス: {front_path}")
        return
    if not os.path.exists(img_folder_path):
        print(f"\nエラー: 画像フォルダが見つかりません。\nパス: {img_folder_path}")
        return

    # 3. データ読み込み
    try:
        df_front = pd.read_excel(front_path)
        front_chars = df_front["files"].to_list()
        df_back = pd.read_excel(excel_path)
    except Exception as e:
        print(f"ファイル読み込みエラー: {e}")
        return

    # 4. ログ保存先準備
    log_dir = f"log/{cond_label}/{participant_id}"
    os.makedirs(log_dir, exist_ok=True)
    log_filename = f"{participant_id}_{set_num}.csv"
    log_path = os.path.join(log_dir, log_filename)

    # 5. キーボードフック設定 (suppress=True で入力を隠す)
    keyboard.on_press_key("t", on_key_event, suppress=True)
    keyboard.on_press_key("b", on_key_event, suppress=True)
    keyboard.add_hotkey('esc', lambda: (_ for _ in ()).throw(KeyboardInterrupt), suppress=True)

    # 6. 画面設定
    colors = {"1": ["black", "white"], "2": ["white", "black"]}
    bg_color = colors[bg_mode][0]
    txt_color = colors[bg_mode][1]

    plt.rcParams['toolbar'] = 'None'

    # Front Window
    fig_front, ax_front = plt.subplots()
    fig_front.canvas.manager.set_window_title("Front")
    fig_front.patch.set_facecolor(bg_color)
    ax_front.axis('off')
    plt.figure(fig_front.number)
    plt.get_current_fig_manager().window.state('zoomed')

    # Back Window
    fig_back, ax_back = plt.subplots()
    fig_back.canvas.manager.set_window_title("Back")
    fig_back.patch.set_facecolor(bg_color)
    ax_back.axis('off')
    plt.figure(fig_back.number)
    plt.subplots_adjust(left=0.507, bottom=-0.7, top=1, right=1)
    mngr_back = plt.get_current_fig_manager()
    mngr_back.window.wm_geometry("+1920+0")
    mngr_back.window.state('zoomed')

    plt.pause(0.5)
    print("\n準備完了。Enterで開始します...")
    input()  # ここだけは標準入力を使うので入力が見えます

    # 7. 実験ループ
    experiment_start_time = time.time()
    first_display_time_unix = None  # 念のため初期化

    try:
        for i in range(len(df_back)):
            # --- 試行初期化 ---
            with state_lock:
                current_trial_data = {
                    "answered": False,
                    "key": None,
                    "rt": None,
                    "timestamp": None
                }
                # 仮の開始時刻（のちほど“表示直後の時刻”で上書きする）
                trial_start_time = time.time()

            # --- 表示データ準備 ---
            char_to_show = str(front_chars[i]).strip()
            img_name = str(df_back["image_name"][i]).strip() if "image_name" in df_back.columns else ""

            # ステータス判定
            # Frontが数字以外なら "Ignore" (Excelの値に関わらず)
            if (char_to_show != "") and (not char_to_show.isdigit()):
                status = "Ignore"
            else:
                # Excelのstatusを正規化（数値でも文字でもOK）
                raw_status = df_back["status"][i] if "status" in df_back.columns else None
                status = normalize_status(raw_status)

            # Back文字 (ログ用)
            raw_filename = str(df_back["filename"][i]) if "filename" in df_back.columns else ""
            back_char_val = "-"

            # Backの意味（数字）は、Back Excelの back_char 列があればそれを優先して使う
            if "back_char" in df_back.columns:
                try:
                    back_char_val = str(df_back.iloc[i]["back_char"])
                except Exception:
                    back_char_val = "?"
            else:
                # フォールバック: filename列の先頭1文字から推定（無ければ ?）
                if "dummy" in raw_filename.lower() or raw_filename == "" or raw_filename == "nan":
                    back_char_val = "-"
                else:
                    try:
                        back_char_val = os.path.basename(raw_filename)[0]
                    except Exception:
                        back_char_val = "?"

            # --- 描画 ---
            # Front (文字)
            plt.figure(fig_front.number)
            ax_front.cla()
            ax_front.axis('off')
            ax_front.set_facecolor(bg_color)
            ax_front.text(
                0.5, 0.5, char_to_show, transform=ax_front.transAxes,
                fontsize=100, color=txt_color, ha='center', va='center'
            )

            # Back (画像) : Ignoreでも画像は表示する
            plt.figure(fig_back.number)
            ax_back.cla()
            ax_back.axis('off')
            ax_back.set_facecolor(bg_color)

            try:
                img_path = os.path.join(img_folder_path, img_name)
                img = Image.open(img_path)
                ax_back.imshow(img)
            except Exception:
                # 画像がない場合は背景色のみ
                pass

            plt.pause(0.001)

            # --- ★表示（刺激オンセット）時刻を記録 ---
            display_dt = datetime.now()   # リアル日時
            display_unix = time.time()    # フレーム換算用

            # 1枚目を0フレームの基準にする
            if first_display_time_unix is None:
                first_display_time_unix = display_unix

            elapsed_from_first = display_unix - first_display_time_unix
            frame_60 = int(round(elapsed_from_first * 60.0))
            frame_120 = int(round(elapsed_from_first * 120.0))

            # RT基準も「表示直後の時刻」に合わせる（より正確）
            with state_lock:
                trial_start_time = display_unix

            # --- 待機 (2.5秒固定) ---
            elapsed_so_far = time.time() - experiment_start_time
            target_time = (i + 1) * 2.5
            wait_duration = target_time - elapsed_so_far
            if wait_duration > 0:
                time.sleep(wait_duration)

            # --- 判定と記録 ---
            user_key = current_trial_data["key"]
            result_type = ""
            jp_label = ""
            accuracy = 0

            # ★ 判定ロジック
            if status == "Ignore":
                # === Ignore (アルファベット) ===
                # 押さないのが正解
                if user_key is None:
                    accuracy = 1
                    result_type = "Correct Rejection"
                    jp_label = "正解(スルー成功)"
                else:
                    accuracy = 0
                    result_type = "False Alarm"
                    jp_label = "お手つき(スルー失敗)"

            else:
                # === Match / Mismatch (数字) ===
                correct_key = TARGET_KEY_MAP.get(status, None)
                if correct_key is None:
                    # 保険：数字なのにstatusが不明な場合は不一致側(b)に倒す
                    correct_key = "b"

                if user_key is None:
                    # 無反応
                    result_type = "Omission"
                    accuracy = 0
                    jp_label = "無反応(不正解)"

                elif user_key == correct_key:
                    # 正解
                    accuracy = 1
                    if status == "Match":
                        result_type = "Hit"
                        jp_label = "正解(一致)"
                    else:
                        result_type = "Correct Rejection"
                        jp_label = "正解(不一致)"

                else:
                    # 不正解
                    accuracy = 0
                    if status == "Match":
                        result_type = "Miss"
                        jp_label = "ミス(見逃し)"
                    else:
                        result_type = "False Alarm"
                        jp_label = "お手つき(誤反応)"

            # 行データ作成
            row_data = df_back.iloc[i].to_dict()

            # 判定に使ったもの＆基本情報
            row_data["final_status"] = status
            row_data["Front_Char"] = char_to_show
            row_data["Back_Char"] = back_char_val

            # ★追加：表示リアル日時、フレーム番号（60/120fps）
            row_data["Display_Timestamp"] = display_dt.isoformat(timespec="milliseconds")
            row_data["Elapsed_From_First_Display_s"] = float(elapsed_from_first)
            row_data["Frame_60fps"] = int(frame_60)
            row_data["Frame_120fps"] = int(frame_120)

            # 反応情報
            row_data["Key_Timestamp"] = current_trial_data["timestamp"] if current_trial_data["timestamp"] else ""
            row_data["Reaction_Time"] = current_trial_data["rt"] if current_trial_data["rt"] else ""
            row_data["User_Key"] = user_key if user_key else "None"

            # 正誤
            row_data["Accuracy"] = accuracy
            row_data["Result_Type"] = result_type
            row_data["Judgment"] = jp_label

            all_trial_results.append(row_data)

    except KeyboardInterrupt:
        print("\n実験を中断しました。")
    finally:
        keyboard.unhook_all()
        plt.close('all')

        if all_trial_results:
            print("\nログを保存しています...")
            df_result = pd.DataFrame(all_trial_results)

            # 列の並び順を整理
            base_cols = df_back.columns.tolist()
            new_cols = [
                "final_status",
                "Display_Timestamp",
                "Elapsed_From_First_Display_s",
                "Frame_60fps",
                "Frame_120fps",
                "Key_Timestamp",
                "Reaction_Time",
                "Front_Char",
                "Back_Char",
                "User_Key",
                "Accuracy",
                "Result_Type",
                "Judgment",
            ]

            final_cols = [c for c in base_cols if c not in new_cols] + new_cols
            df_result = df_result.reindex(columns=final_cols)

            df_result.to_csv(log_path, index=False, encoding="utf-8-sig")
            print(f"保存完了: {log_path}")

        print("実験終了")


if __name__ == "__main__":
    main()
