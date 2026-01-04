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

first_display_time_unix = None

current_trial_data = {
    "answered": False,
    "key": None,
    "rt": None,
    "timestamp": None
}

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
# ★ 新しいExcel仕様に合わせた status 正規化
#  - match/unmatch/filler (小文字)
#  - Match/Mismatch/Ignore (大文字)
#  - 1/2/4
# ==========================================
def normalize_status(x):
    if x is None:
        return "Ignore"

    s = str(x).strip()
    if s == "" or s.lower() == "nan":
        return "Ignore"

    # 数値っぽい（旧互換）
    if s.isdigit():
        v = int(s)
        if v == 1:
            return "Match"
        if v == 2:
            return "Mismatch"
        if v == 4:
            return "Ignore"
        return "Ignore"

    s_low = s.lower()
    if s_low in ["match", "matched"]:
        return "Match"
    if s_low in ["mismatch", "unmatch", "unmatched"]:
        return "Mismatch"
    if s_low in ["ignore", "filler", "none", "no response"]:
        return "Ignore"

    return "Ignore"


# ==========================================
# キー入力ハンドラ (suppress対応)
# ==========================================
def on_key_event(event):
    global current_trial_data, trial_start_time
    key_name = event.name  # 't' or 'b'

    with state_lock:
        if current_trial_data["answered"]:
            return

        current_trial_data["answered"] = True
        current_trial_data["key"] = key_name
        current_trial_data["timestamp"] = datetime.now()
        current_trial_data["rt"] = time.time() - trial_start_time


# ==========================================
# メイン処理
# ==========================================
def main():
    global experiment_start_time, trial_start_time, current_trial_data, all_trial_results, first_display_time_unix

    # --------------------------
    # 1) 入力
    # --------------------------
    participant_id_raw = input("参加者番号を入力してください (例: S01 または 1): ").strip()
    set_num = input("セット番号を入力してください (例: 0): ").strip()

    # 被験者フォルダ名を生成コードに合わせる（S01 形式推奨）
    # もし数字だけなら Sxx に変換
    if participant_id_raw.isdigit():
        participant_id = f"S{int(participant_id_raw):02d}"
    else:
        participant_id = participant_id_raw

    print("\n条件を選択してください:")
    print("1: Bright")
    print("2: Dark")
    cond_input = input("選択肢を入力 (1 or 2): ").strip()

    if cond_input == "1":
        cond_label = "Bright"
        bg_mode = "2"  # 白背景
        print(f">> Bright モードでセット {set_num} を開始します")
    elif cond_input == "2":
        cond_label = "Dark"
        bg_mode = "1"  # 黒背景
        print(f">> Dark モードでセット {set_num} を開始します")
    else:
        print("エラー: 1 か 2 を入力してください。")
        return

    # --------------------------
    # 2) パス構築（★生成コードに合わせる）
    # --------------------------
    # Excel:
    #   C:\...\imageCreationExcel\Bright|Dark\S01\0.xlsx
    # EXCEL_ROOT = r"C:\Users\naklab\Documents\kiyota\penstone_2025\imageCreationExcel"
    EXCEL_ROOT = "./imageCreationExcel"
    excel_path = os.path.join(EXCEL_ROOT, cond_label, participant_id, f"{set_num}.xlsx")

    # Images:
    #   F:\experiment_images_verify\Bright|Dark\S01\0\<image_name>
    IMAGE_ROOT = r"F:\experiment_images_verify"
    img_folder_path = os.path.join(IMAGE_ROOT, cond_label, participant_id, str(set_num))

    if not os.path.exists(excel_path):
        print(f"\nエラー: Excelファイルが見つかりません。\nパス: {excel_path}")
        return

    if not os.path.exists(img_folder_path):
        print(f"\nエラー: 画像フォルダが見つかりません。\nパス: {img_folder_path}")
        return

    # --------------------------
    # 3) データ読み込み（Excel 1枚）
    # --------------------------
    try:
        df = pd.read_excel(excel_path)
    except Exception as e:
        print(f"Excel読み込みエラー: {e}")
        return

    # 必須列チェック（生成コードの仕様）
    required_cols = ["front", "status", "image_name"]
    missing = [c for c in required_cols if c not in df.columns]
    if missing:
        print(f"\nエラー: Excelに必須列がありません: {missing}\n列一覧: {df.columns.tolist()}")
        return

    # --------------------------
    # 4) ログ保存先準備
    # --------------------------
    log_dir = os.path.join("log", cond_label, participant_id)
    os.makedirs(log_dir, exist_ok=True)
    log_filename = f"{participant_id}_{set_num}.csv"
    log_path = os.path.join(log_dir, log_filename)

    # --------------------------
    # 5) キーボードフック設定
    # --------------------------
    keyboard.on_press_key("t", on_key_event, suppress=True)
    keyboard.on_press_key("b", on_key_event, suppress=True)
    keyboard.add_hotkey('esc', lambda: (_ for _ in ()).throw(KeyboardInterrupt), suppress=True)

    # --------------------------
    # 6) 画面設定
    # --------------------------
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
    # 2画面運用なら右に寄せる（必要なら調整）
    mngr_back.window.wm_geometry("+1920+0")
    mngr_back.window.state('zoomed')

    plt.pause(0.5)
    print("\n準備完了。Enterで開始します...")
    input()

    # --------------------------
    # 7) 実験ループ
    # --------------------------
    experiment_start_time = time.time()
    first_display_time_unix = None
    all_trial_results = []

    try:
        for i in range(len(df)):
            # --- 試行初期化 ---
            with state_lock:
                current_trial_data = {"answered": False, "key": None, "rt": None, "timestamp": None}
                trial_start_time = time.time()

            # --- 表示データ準備 ---
            char_to_show = str(df.loc[i, "front"]).strip()
            img_name = str(df.loc[i, "image_name"]).strip()

            # status 正規化
            # frontがアルファベットなら強制 Ignore（安全）
            if (char_to_show != "") and (not char_to_show.isdigit()):
                status = "Ignore"
            else:
                status = normalize_status(df.loc[i, "status"])

            # back（ログ用）
            back_char_val = "-"
            if "back" in df.columns:
                back_char_val = str(df.loc[i, "back"])
            else:
                # 旧互換
                back_char_val = "?"

            # --- 描画: Front ---
            plt.figure(fig_front.number)
            ax_front.cla()
            ax_front.axis('off')
            ax_front.set_facecolor(bg_color)
            ax_front.text(
                0.5, 0.5, char_to_show,
                transform=ax_front.transAxes,
                fontsize=100, color=txt_color, ha='center', va='center'
            )

            # --- 描画: Back ---
            plt.figure(fig_back.number)
            ax_back.cla()
            ax_back.axis('off')
            ax_back.set_facecolor(bg_color)

            try:
                img_path = os.path.join(img_folder_path, img_name)
                img = Image.open(img_path)
                ax_back.imshow(img)
            except Exception:
                # 画像が無い/読めないなら背景のみ（落とさない）
                pass

            plt.pause(0.001)

            # --- 表示オンセット記録 ---
            display_dt = datetime.now()
            display_unix = time.time()

            if first_display_time_unix is None:
                first_display_time_unix = display_unix

            elapsed_from_first = display_unix - first_display_time_unix
            frame_60 = int(round(elapsed_from_first * 60.0))
            frame_120 = int(round(elapsed_from_first * 120.0))

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

            if status == "Ignore":
                if user_key is None:
                    accuracy = 1
                    result_type = "Correct Rejection"
                    jp_label = "正解(スルー成功)"
                else:
                    accuracy = 0
                    result_type = "False Alarm"
                    jp_label = "お手つき(スルー失敗)"
            else:
                correct_key = TARGET_KEY_MAP.get(status, "b")

                if user_key is None:
                    accuracy = 0
                    result_type = "Omission"
                    jp_label = "無反応(不正解)"
                elif user_key == correct_key:
                    accuracy = 1
                    if status == "Match":
                        result_type = "Hit"
                        jp_label = "正解(一致)"
                    else:
                        result_type = "Correct Rejection"
                        jp_label = "正解(不一致)"
                else:
                    accuracy = 0
                    if status == "Match":
                        result_type = "Miss"
                        jp_label = "ミス(見逃し)"
                    else:
                        result_type = "False Alarm"
                        jp_label = "お手つき(誤反応)"

            row_data = df.iloc[i].to_dict()

            row_data["final_status"] = status
            row_data["Front_Char"] = char_to_show
            row_data["Back_Char"] = back_char_val

            row_data["Display_Timestamp"] = display_dt.isoformat(timespec="milliseconds")
            row_data["Elapsed_From_First_Display_s"] = float(elapsed_from_first)
            row_data["Frame_60fps"] = int(frame_60)
            row_data["Frame_120fps"] = int(frame_120)

            row_data["Key_Timestamp"] = current_trial_data["timestamp"] if current_trial_data["timestamp"] else ""
            row_data["Reaction_Time"] = current_trial_data["rt"] if current_trial_data["rt"] else ""
            row_data["User_Key"] = user_key if user_key else "None"

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

            base_cols = df.columns.tolist()
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
