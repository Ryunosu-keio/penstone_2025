# -*- coding: utf-8 -*-
import time
import ctypes
from ctypes import wintypes

import matplotlib
matplotlib.use("TkAgg")  # Tk の window.wm_geometry を使うため明示

import matplotlib.pyplot as plt

# =========================
# Windows API: display enumerate
# =========================
user32 = ctypes.windll.user32

ENUM_CURRENT_SETTINGS = -1
DISPLAY_DEVICE_ATTACHED_TO_DESKTOP = 0x00000001
DISPLAY_DEVICE_PRIMARY_DEVICE      = 0x00000004

class DISPLAY_DEVICEW(ctypes.Structure):
    _fields_ = [
        ("cb", wintypes.DWORD),
        ("DeviceName", wintypes.WCHAR * 32),   # \\.\DISPLAY1 など
        ("DeviceString", wintypes.WCHAR * 128),
        ("StateFlags", wintypes.DWORD),
        ("DeviceID", wintypes.WCHAR * 128),
        ("DeviceKey", wintypes.WCHAR * 128),
    ]

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

def enum_displays():
    """ \\.\DISPLAY1/2/3... の pos/size/flags を取る（チェック用コードと同系統） """
    out = {}
    i = 0
    while True:
        dd = DISPLAY_DEVICEW()
        dd.cb = ctypes.sizeof(DISPLAY_DEVICEW)
        ok = user32.EnumDisplayDevicesW(None, i, ctypes.byref(dd), 0)
        if not ok:
            break

        name = dd.DeviceName
        flags = dd.StateFlags

        # デスクトップにアタッチされてるものだけ
        if flags & DISPLAY_DEVICE_ATTACHED_TO_DESKTOP:
            dm = DEVMODEW()
            dm.dmSize = ctypes.sizeof(DEVMODEW)
            ok2 = user32.EnumDisplaySettingsW(name, ENUM_CURRENT_SETTINGS, ctypes.byref(dm))
            if ok2:
                out[name] = {
                    "x": int(dm.dmPosition.x),
                    "y": int(dm.dmPosition.y),
                    "w": int(dm.dmPelsWidth),
                    "h": int(dm.dmPelsHeight),
                    "primary": bool(flags & DISPLAY_DEVICE_PRIMARY_DEVICE),
                    "device_string": dd.DeviceString
                }

        i += 1
    return out

def place_tk_window(fig, x, y, w, h):
    """ TkAggウィンドウを指定座標/サイズへ。zoomedは使わず geometry で埋める """
    mgr = fig.canvas.manager
    win = getattr(mgr, "window", None)
    if win is None or not hasattr(win, "wm_geometry"):
        return

    win.update_idletasks()
    win.state("normal")
    win.wm_geometry(f"{w}x{h}+{x}+{y}")
    win.update_idletasks()

def main():
    displays = enum_displays()

    print("=== Windows Displays (ATTACHED) ===")
    for k, v in displays.items():
        prim = " PRIMARY" if v["primary"] else ""
        print(f"{k} pos=({v['x']},{v['y']}) size=({v['w']}x{v['h']}){prim}")

    # ---- ここを固定：あなたの要望 ----
    FRONT = r"\\.\DISPLAY1"  # 文字（真ん中の 2560x1440 想定）
    BACK  = r"\\.\DISPLAY3"  # 画像（左の 1920x1080 想定）
    # --------------------------------

    if FRONT not in displays or BACK not in displays:
        print("[ERROR] FRONT/BACK の display が見つからない。上の一覧と一致させて。")
        return

    # Front window (文字)
    fig_f, ax_f = plt.subplots()
    fig_f.canvas.manager.set_window_title("Front")
    ax_f.axis("off")
    ax_f.text(0.5, 0.5, "FRONT", transform=ax_f.transAxes, fontsize=120,
              ha="center", va="center")

    # Back window (画像枠)
    fig_b, ax_b = plt.subplots()
    fig_b.canvas.manager.set_window_title("Back")
    ax_b.axis("off")
    ax_b.text(0.5, 0.5, "BACK", transform=ax_b.transAxes, fontsize=80,
              ha="center", va="center")

    # 一度描画して window を確実に作る
    plt.show(block=False)
    plt.pause(0.2)

    # ---- Front: DISPLAY1 全面（geometryで埋める）----
    f = displays[FRONT]
    place_tk_window(fig_f, f["x"], f["y"], f["w"], f["h"])

    # ---- Back: DISPLAY3 右下（少し小さめ）----
    b = displays[BACK]
    bw = int(b["w"] * 0.90)
    bh = int(b["h"] * 0.90)
    bx = b["x"] + (b["w"] - bw) - 20
    by = b["y"] + (b["h"] - bh) - 80
    place_tk_window(fig_b, bx, by, bw, bh)

    print("\n=> 文字がDISPLAY1、BACKがDISPLAY3に出ていればOK。")
    print("閉じるまで待機中...")
    plt.show()

if __name__ == "__main__":
    main()
