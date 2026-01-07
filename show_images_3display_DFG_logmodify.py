# -*- coding: utf-8 -*-
"""
experiment_main_display.py
- Excel を読み、Front(文字) と Back(画像) を 2ウィンドウで提示
- DISPLAY1: Front（最大化）
- DISPLAY3: Back（右下に寄せる）
- DISPLAY2: 使わない

依存:
  pip install keyboard pandas matplotlib pillow openpyxl

追加:
- experiment_images_verify の場所を F/D/G から自動選択
- ★ズレ対策:
  1) Enter基準の「絶対時刻スケジュール」を廃止
  2) 「実際に描画が終わった瞬間」を display_time として採用
  3) キーの受付は display_time ～ display_time+TRIAL_SEC の窓だけ
  4) コールバックでは event.time（押下時刻）を使う（遅延配送でもズレない）
"""

import os
import time
import threading
from datetime import datetime

import matplotlib.pyplot as plt
import pandas as pd
import keyboard
from PIL import Image

# ============================================================
# 実験パラメータ（ここだけ変えればOK）
# ============================================================
TRIAL_SEC = 5.0  # 2.5 or 5.0 など

# 画像を事前に全部読む（最初の1試行だけ重い問題を潰す）
PRELOAD_IMAGES = True

# キー受付の安全マージン（表示直後の超高速押下の取りこぼし対策）
# ※draw直後に window_start を置くので基本不要だが、心配なら 0.01 など
WINDOW_EARLY_MARGIN_SEC = 0.00

# ============================================================
# F/D/G のパス選択ヘルパ
# ============================================================
def pick_existing_dir(*candidates: str) -> str:
    for p in candidates:
        if os.path.exists(p):
            return p
    return ""

# ============================================================
# Windows の DISPLAY1/2/3 の「座標・サイズ」を ctypes で取得
# ============================================================
import ctypes
from ctypes import wintypes

ENUM_CURRENT_SETTINGS = -1
DISPLAY_DEVICE_ATTACHED_TO_DESKTOP = 0x00000001

class POINTL(ctypes.Structure):
    _fields_ = [("x", wintypes.LONG), ("y", wintypes.LONG)]

class DEVMODEW(ctypes.Structure):
    _fields_ = [
        ("dmDeviceName", wintypes.WCHAR * 32),
        ("dmSpecVersion", wintypes.WORD),
        ("dmDriverVersion", wintypes.WORD),
        ("dmSize", wintypes.WORD),
        ("dmDriverExtra", wintypes.WORD),
        ("dmFields", wintypes.DWORD),
        ("dmPosition", POINTL),
        ("dmDisplayOrientation", wintypes.DWORD),
        ("dmDisplayFixedOutput", wintypes.DWORD),
        ("dmColor", wintypes.SHORT),
        ("dmDuplex", wintypes.SHORT),
        ("dmYResolution", wintypes.SHORT),
        ("dmTTOption", wintypes.SHORT),
        ("dmCollate", wintypes.SHORT),
        ("dmFormName", wintypes.WCHAR * 32),
        ("dmLogPixels", wintypes.WORD),
        ("dmBitsPerPel", wintypes.DWORD),
        ("dmPelsWidth", wintypes.DWORD),
        ("dmPelsHeight", wintypes.DWORD),
        ("dmDisplayFlags", wintypes.DWORD),
        ("dmDisplayFrequency", wintypes.DWORD),
        ("dmICMMethod", wintypes.DWORD),
        ("dmICMIntent", wintypes.DWORD),
        ("dmMediaType", wintypes.DWORD),
        ("dmDitherType", wintypes.DWORD),
        ("dmReserved1", wintypes.DWORD),
        ("dmReserved2", wintypes.DWORD),
        ("dmPanningWidth", wintypes.DWORD),
        ("dmPanningHeight", wintypes.DWORD),
    ]

class DISPLAY_DEVICEW(ctypes.Structure):
    _fields_ = [
        ("cb", wintypes.DWORD),
        ("DeviceName", wintypes.WCHAR * 32),
        ("DeviceString", wintypes.WCHAR * 128),
        ("StateFlags", wintypes.DWORD),
        ("DeviceID", wintypes.WCHAR * 128),
        ("DeviceKey", wintypes.WCHAR * 128),
    ]

user32 = ctypes.WinDLL("user32", use_last_error=True)

EnumDisplayDevicesW = user32.EnumDisplayDevicesW
EnumDisplayDevicesW.argtypes = [wintypes.LPCWSTR, wintypes.DWORD, ctypes.POINTER(DISPLAY_DEVICEW), wintypes.DWORD]
EnumDisplayDevicesW.restype = wintypes.BOOL

EnumDisplaySettingsW = user32.EnumDisplaySettingsW
EnumDisplaySettingsW.argtypes = [wintypes.LPCWSTR, wintypes.DWORD, ctypes.POINTER(DEVMODEW)]
EnumDisplaySettingsW.restype = wintypes.BOOL

def get_display_rect(display_number: int):
    target = fr"\\.\DISPLAY{display_number}"
    dd = DISPLAY_DEVICEW()
    dd.cb = ctypes.sizeof(DISPLAY_DEVICEW)

    i = 0
    found = None
    while EnumDisplayDevicesW(None, i, ctypes.byref(dd), 0):
        name = dd.DeviceName
        flags = dd.StateFlags
        if (flags & DISPLAY_DEVICE_ATTACHED_TO_DESKTOP) and name == target:
            found = name
            break
        i += 1

    if found is None:
        raise RuntimeError(f"{target} が 'ATTACHED' として見つかりません。Windowsの表示設定を確認してください。")

    dm = DEVMODEW()
    dm.dmSize = ctypes.sizeof(DEVMODEW)
    ok = EnumDisplaySettingsW(found, ENUM_CURRENT_SETTINGS, ctypes.byref(dm))
    if not ok:
        raise RuntimeError(f"{target} の現在設定(ENUM_CURRENT_SETTINGS)が取得できません。")

    x, y = int(dm.dmPosition.x), int(dm.dmPosition.y)
    w, h = int(dm.dmPelsWidth), int(dm.dmPelsHeight)
    return x, y, w, h

def debug_print_displays():
    dd = DISPLAY_DEVICEW()
    dd.cb = ctypes.sizeof(DISPLAY_DEVICEW)
    i = 0
    print("=== Attached Displays ===")
    while EnumDisplayDevicesW(None, i, ctypes.byref(dd), 0):
        if dd.StateFlags & DISPLAY_DEVICE_ATTACHED_TO_DESKTOP:
            name = dd.DeviceName
            dm = DEVMODEW()
            dm.dmSize = ctypes.sizeof(DEVMODEW)
            if EnumDisplaySettingsW(name, ENUM_CURRENT_SETTINGS, ctypes.byref(dm)):
                print(f"{name}  pos=({dm.dmPosition.x},{dm.dmPosition.y}) size=({dm.dmPelsWidth}x{dm.dmPelsHeight})")
            else:
                print(f"{name}  (mode取得失敗)")
        i += 1

def place_figure_on_rect(fig, rect, mode="fullscreen", w_ratio=0.9, h_ratio=0.9, padx=20, pady=80, borderless=True):
    mx, my, mw, mh = rect
    mgr = fig.canvas.manager
    win = getattr(mgr, "window", None)

    # TkAgg
    if win is not None and hasattr(win, "wm_geometry"):
        win.update_idletasks()
        win.state("normal")

        if mode == "fullscreen":
            if borderless and hasattr(win, "overrideredirect"):
                try:
                    win.overrideredirect(True)
                except Exception:
                    pass
            win.geometry(f"{mw}x{mh}+{mx}+{my}")
            return

        if mode == "bottomright":
            ww = int(mw * w_ratio)
            hh = int(mh * h_ratio)
            x = mx + mw - ww - padx
            y = my + mh - hh - pady
            win.geometry(f"{ww}x{hh}+{x}+{y}")
            return

    # Qt系
    if win is not None and hasattr(win, "move"):
        if mode == "fullscreen":
            if hasattr(win, "showNormal"):
                win.showNormal()
            if hasattr(win, "setGeometry"):
                win.setGeometry(mx, my, mw, mh)
            else:
                if hasattr(win, "resize"):
                    win.resize(mw, mh)
                win.move(mx, my)
            return

        if mode == "bottomright":
            ww = int(mw * w_ratio)
            hh = int(mh * h_ratio)
            x = mx + mw - ww - padx
            y = my + mh - hh - pady
            if hasattr(win, "resize"):
                win.resize(ww, hh)
            win.move(x, y)
            return

    print("[WARN] backendの都合で自動移動できません（TkAgg推奨）。")

# ============================================================
# 実験ロジック
# ============================================================
state_lock = threading.Lock()

# ★この“窓”に入ったキーだけが、その試行の反応として採用される
trial_window_start_epoch = 0.0
trial_window_end_epoch = 0.0

first_display_epoch = None

current_trial_data = {
    "answered": False,
    "key": None,
    "rt": None,                 # 秒（display基準）
    "key_epoch": None,          # time.time() 系
    "key_dt": None,             # datetime
}
all_trial_results = []

TARGET_KEY_MAP = {"Match": "t", "Mismatch": "b"}

def normalize_status(x):
    if x is None:
        return "Ignore"
    s = str(x).strip()
    if s == "" or s.lower() == "nan":
        return "Ignore"
    if s.isdigit():
        v = int(s)
        return "Match" if v == 1 else "Mismatch" if v == 2 else "Ignore"
    s_low = s.lower()
    if s_low in ["match", "matched"]:
        return "Match"
    if s_low in ["mismatch", "unmatch", "unmatched"]:
        return "Mismatch"
    if s_low in ["ignore", "filler", "none", "no response"]:
        return "Ignore"
    return "Ignore"

def is_front_numeric(s: str) -> bool:
    """
    front が数字課題かどうか（Excelが 6.0 になる等も吸収）
    """
    if s is None:
        return False
    t = str(s).strip()
    if t == "":
        return False
    if t.isdigit():
        return True
    # "6.0" みたいなのも数字扱い
    try:
        f = float(t)
        return abs(f - round(f)) < 1e-9
    except Exception:
        return False

def on_key_event(event):
    """
    ★ズレ対策の核:
    - keyboard はコールバックが“遅れて”呼ばれることがある
      → なので now=time.time() ではなく event.time（押下時刻）を使う
    - event.time が、その試行の受付窓に入っている場合だけ採用
    - 1試行1入力
    """
    global current_trial_data, trial_window_start_epoch, trial_window_end_epoch

    # keyboard の event.time を優先（押下時刻）
    t = getattr(event, "time", None)
    if t is None:
        t = time.time()

    with state_lock:
        if current_trial_data["answered"]:
            return

        # 受付窓の外なら、その試行の反応としては無視（次試行にも持ち越さない）
        if t < trial_window_start_epoch or t > trial_window_end_epoch:
            return

        current_trial_data["answered"] = True
        current_trial_data["key"] = event.name
        current_trial_data["key_epoch"] = float(t)
        current_trial_data["key_dt"] = datetime.fromtimestamp(float(t))
        current_trial_data["rt"] = float(t) - float(trial_window_start_epoch)

def _draw_and_flush(fig):
    """
    draw が終わった後の時刻を display_time にしたいので、同期描画する
    """
    try:
        fig.canvas.draw()
        fig.canvas.flush_events()
    except Exception:
        pass

def preload_images(img_folder_path: str, image_names: list[str]) -> dict[str, Image.Image]:
    cache = {}
    for name in image_names:
        p = os.path.join(img_folder_path, str(name))
        try:
            cache[name] = Image.open(p).copy()
        except Exception:
            cache[name] = None
    return cache

def main():
    global trial_window_start_epoch, trial_window_end_epoch, current_trial_data, all_trial_results, first_display_epoch

    debug_print_displays()

    participant_id_raw = input("参加者番号 (例: 昼なら1　夜なら101): ").strip()
    set_num = input("セット番号 (例: 0): ").strip()

    participant_id = f"S{int(participant_id_raw):02d}" if participant_id_raw.isdigit() else participant_id_raw

    print("\n条件を選択:")
    print("1: Bright")
    print("2: Dark")
    cond_input = input("1 or 2: ").strip()

    if cond_input == "1":
        # cond_label, bg_mode = "Bright", "2"
        cond_label, bg_mode = "Bright", "1"
    elif cond_input == "2":
        cond_label, bg_mode = "Dark", "1"
    else:
        print("エラー: 1 か 2")
        return

    # Excel
    EXCEL_ROOT = "./imageCreationExcel"
    excel_path = os.path.join(EXCEL_ROOT, cond_label, participant_id, f"{set_num}.xlsx")

    # Images
    IMAGE_ROOT = pick_existing_dir(
        r"F:\experiment_images_verify",
        r"D:\experiment_images_verify",
        r"G:\experiment_images_verify",
    )
    if IMAGE_ROOT == "":
        print(r"\nエラー: experiment_images_verify が F:\ / D:\ / G:\ にありません")
        return

    img_folder_path = os.path.join(IMAGE_ROOT, cond_label, participant_id, str(set_num))

    if not os.path.exists(excel_path):
        print(f"\nエラー: Excelが無い: {excel_path}")
        return
    if not os.path.exists(img_folder_path):
        print(f"\nエラー: 画像フォルダが無い: {img_folder_path}")
        return

    try:
        df = pd.read_excel(excel_path)
    except Exception as e:
        print(f"Excel読み込みエラー: {e}")
        return

    required_cols = ["front", "status", "image_name"]
    missing = [c for c in required_cols if c not in df.columns]
    if missing:
        print(f"\nエラー: 必須列なし {missing}\n列: {df.columns.tolist()}")
        return

    # ログ
    log_dir = os.path.join("log", cond_label, participant_id)
    os.makedirs(log_dir, exist_ok=True)
    log_path = os.path.join(log_dir, f"{participant_id}_{set_num}.csv")

    # キーボード
    keyboard.on_press_key("t", on_key_event, suppress=True)
    keyboard.on_press_key("b", on_key_event, suppress=True)
    keyboard.add_hotkey("esc", lambda: (_ for _ in ()).throw(KeyboardInterrupt), suppress=True)

    # 画面色
    colors = {"1": ["black", "white"], "2": ["white", "black"]}
    bg_color, txt_color = colors[bg_mode][0], colors[bg_mode][1]
    plt.rcParams["toolbar"] = "None"

    # Front / Back ウィンドウ作成
    fig_front, ax_front = plt.subplots()
    fig_front.canvas.manager.set_window_title("Front")
    fig_front.patch.set_facecolor(bg_color)
    ax_front.axis("off")

    fig_back, ax_back = plt.subplots()
    fig_back.canvas.manager.set_window_title("Back")
    fig_back.patch.set_facecolor(bg_color)
    ax_back.axis("off")

    rect1 = get_display_rect(1)
    rect3 = get_display_rect(3)
    place_figure_on_rect(fig_front, rect1, mode="fullscreen")
    place_figure_on_rect(fig_back, rect3, mode="fullscreen", w_ratio=0.9, h_ratio=0.9, padx=20, pady=80)

    plt.figure(fig_back.number)
    plt.subplots_adjust(left=0.507, bottom=-0.7, top=1, right=1)

    # ウォームアップ描画（最初だけ重い問題を軽減）
    ax_front.cla(); ax_front.axis("off"); ax_front.set_facecolor(bg_color)
    ax_front.text(0.5, 0.5, "", transform=ax_front.transAxes, fontsize=100, color=txt_color, ha="center", va="center")
    ax_back.cla(); ax_back.axis("off"); ax_back.set_facecolor(bg_color)
    _draw_and_flush(fig_front)
    _draw_and_flush(fig_back)

    # 画像プリロード（任意）
    image_cache = None
    if PRELOAD_IMAGES:
        print("[INFO] preloading images ...")
        image_names = [str(x).strip() for x in df["image_name"].tolist()]
        image_cache = preload_images(img_folder_path, image_names)
        print("[INFO] preload done.")

    plt.pause(0.2)
    print("\n準備完了。Enterで開始...")
    input()

    first_display_epoch = None
    all_trial_results = []

    try:
        for i in range(len(df)):
            # 試行データ初期化
            with state_lock:
                current_trial_data = {"answered": False, "key": None, "rt": None, "key_epoch": None, "key_dt": None}
                # ★窓は“いったん閉じておく”（試行切替の持ち越し防止）
                trial_window_start_epoch = 10**18
                trial_window_end_epoch = -10**18

            char_to_show = str(df.loc[i, "front"]).strip()
            img_name = str(df.loc[i, "image_name"]).strip()

            # front が数字のときだけ status 判定
            if (char_to_show != "") and (not is_front_numeric(char_to_show)):
                status = "Ignore"
            else:
                status = normalize_status(df.loc[i, "status"])

            back_char_val = str(df.loc[i, "back"]) if "back" in df.columns else "?"

            # ===== 描画 =====
            plt.figure(fig_front.number)
            ax_front.cla()
            ax_front.axis("off")
            ax_front.set_facecolor(bg_color)
            ax_front.text(
                0.5, 0.5, char_to_show, transform=ax_front.transAxes,
                fontsize=100, color=txt_color, ha="center", va="center"
            )

            plt.figure(fig_back.number)
            ax_back.cla()
            ax_back.axis("off")
            ax_back.set_facecolor(bg_color)
            try:
                if image_cache is not None:
                    img = image_cache.get(img_name, None)
                else:
                    img_path = os.path.join(img_folder_path, img_name)
                    img = Image.open(img_path)
                if img is not None:
                    ax_back.imshow(img)
            except Exception:
                pass

            # ★ここがズレ対策の核：draw/flush “後” を表示時刻にする
            _draw_and_flush(fig_front)
            _draw_and_flush(fig_back)

            display_epoch = time.time()
            display_dt = datetime.fromtimestamp(display_epoch)

            if first_display_epoch is None:
                first_display_epoch = display_epoch

            elapsed_from_first = display_epoch - first_display_epoch
            frame_60 = int(round(elapsed_from_first * 60.0))
            frame_120 = int(round(elapsed_from_first * 120.0))

            # ★この試行の受付窓（event.time で判定する）
            with state_lock:
                trial_window_start_epoch = display_epoch - WINDOW_EARLY_MARGIN_SEC
                trial_window_end_epoch = display_epoch + TRIAL_SEC

            # 締め切りまで待つ（絶対スケジュール廃止）
            while True:
                rem = trial_window_end_epoch - time.time()
                if rem <= 0:
                    break
                time.sleep(min(0.005, rem))

            with state_lock:
                user_key = current_trial_data["key"]
                rt = current_trial_data["rt"]
                key_dt = current_trial_data["key_dt"]

            # 採点
            if status == "Ignore":
                if user_key is None:
                    accuracy, result_type, jp_label = 1, "Correct Rejection", "正解(スルー成功)"
                else:
                    accuracy, result_type, jp_label = 0, "False Alarm", "お手つき(スルー失敗)"
            else:
                correct_key = TARGET_KEY_MAP.get(status, "b")
                if user_key is None:
                    accuracy, result_type, jp_label = 0, "Omission", "無反応(不正解)"
                elif user_key == correct_key:
                    accuracy = 1
                    if status == "Match":
                        result_type, jp_label = "Hit", "正解(一致)"
                    else:
                        result_type, jp_label = "Correct Rejection", "正解(不一致)"
                else:
                    accuracy = 0
                    if status == "Match":
                        result_type, jp_label = "Miss", "ミス(見逃し)"
                    else:
                        result_type, jp_label = "False Alarm", "お手つき(誤反応)"

            # ログ行
            row_data = df.iloc[i].to_dict()
            row_data.update({
                "final_status": status,
                "Front_Char": char_to_show,
                "Back_Char": back_char_val,

                "Display_Timestamp": display_dt.isoformat(timespec="milliseconds"),
                "Display_Epoch": float(display_epoch),

                "Elapsed_From_First_Display_s": float(elapsed_from_first),
                "Frame_60fps": int(frame_60),
                "Frame_120fps": int(frame_120),

                "Key_Timestamp": key_dt.isoformat(timespec="milliseconds") if key_dt else "",
                "Reaction_Time": float(rt) if rt is not None else "",
                "User_Key": user_key if user_key else "None",

                "Accuracy": accuracy,
                "Result_Type": result_type,
                "Judgment": jp_label,
            })
            all_trial_results.append(row_data)

    except KeyboardInterrupt:
        print("\n実験を中断しました。")
    finally:
        keyboard.unhook_all()
        plt.close("all")

        if all_trial_results:
            print("\nログ保存中...")
            df_result = pd.DataFrame(all_trial_results)

            base_cols = df.columns.tolist()
            new_cols = [
                "final_status",
                "Display_Timestamp", "Display_Epoch",
                "Elapsed_From_First_Display_s", "Frame_60fps", "Frame_120fps",
                "Key_Timestamp", "Reaction_Time",
                "Front_Char", "Back_Char", "User_Key",
                "Accuracy", "Result_Type", "Judgment",
            ]
            final_cols = [c for c in base_cols if c not in new_cols] + new_cols
            df_result = df_result.reindex(columns=final_cols)

            df_result.to_csv(log_path, index=False, encoding="utf-8-sig")
            print(f"保存完了: {log_path}")

        print("実験終了")

if __name__ == "__main__":
    main()
