"""
add_emr_columns_to_experiment_log_v2_pages.py
---------------------------------------------
実験ログCSV（experiment_main_display.py）に、EMR切り出しCSV（devided_emr 1セグメント）を
「フレーム」で合わせて列追加して保存。さらに、48試行の縦線（刺激開始）を
"trials_per_page本ずつ" 区切って xlim を制限した拡大プロットをページ分割で保存する。

✅ 追加（ログに入る列）:
- emr_frame_rel
- emr_left_pupil_mm_raw / emr_right_pupil_mm_raw / emr_both_pupil_mm_raw
- emr_both_Z_mm_raw
- emr_diopter_raw (= 1000/Z)
- emr_left_pupil_mm / emr_right_pupil_mm / emr_both_pupil_mm (前処理後)
- emr_both_Z_mm (前処理後)
- emr_diopter_clipped0 (範囲外→0 の diopter)
- emr_diopter_peak (★元コード踏襲：刺激フレームから先の局所最大)
- emr_diopter_peak_frame_rel (そのピークが出たEMR相対フレーム)

✅ ページ分割プロット保存:
- save_root_dir/Bright/... または save_root_dir/Dark/... に自動で振り分け
  （ログCSVのパスに "Bright"/"Dark" が含まれていればそれで判定）

※ グラフが「途切れる」のは、前処理で NaN（欠損）を作ると matplotlib の折れ線が分断されるため。
  ただし「可視化だけ繋げたい」場合に備えて、プロット用の補間オプションも付けています。

依存:
  pip install pandas numpy matplotlib
"""

import os
import re
import argparse
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


# ============================================================
# ユーザー設定（ここだけ編集すればOK）
# ============================================================

EXPERIMENT_LOG_CSV = "../../log/Dark/S115/S115_0.csv"
EMR_SEGMENT_CSV    = "../../data/devided_emr/110/0.csv"
OUT_LOG_CSV        = "../../data/log_with_emr/Dark/S115/S115_0_with_emr.csv"

# ログ側のフレーム列（両方あるなら、EMR_FPSに合わせて自動で選ぶ）
FRAME_COL_120 = "Frame_120fps"
FRAME_COL_60  = "Frame_60fps"

# ★今回だけEMRを60Hzで撮ってしまった → 60 にする
EMR_FPS = 120  # 60 or 120

# merge_asof の許容誤差（フレーム単位）
# 60Hzなら ±1~2 くらいが現実的（±2なら約±33ms）
TOLERANCE_FRAMES = 2

# -------- 前処理パラメータ（全部のデータに適用）--------
# pupil(mm)の物理レンジ（まずこれが最優先）
PUPIL_MIN_MM = 1.0
PUPIL_MAX_MM = 7.0 #6.0

# Z(mm)のレンジ（実験系に合わせて調整）
Z_MIN_MM = 100.0 # 100mm リアルに考えたら450だけどまあ300とかかな やま二つになっちゃう
Z_MAX_MM = 6000.0

# diopter の有効レンジ（元コード思想：範囲外は0）
DIOPTER_MIN = 1.5 #1.5 #666mm　奥
DIOPTER_MAX = 10 #10.0 # 100mm 手前

# Hampel（ロバスト外れ値）: windowは奇数推奨
HAMPEL_WIN   = 11
HAMPEL_SIGMA = 3.0

# 小ギャップ補間（フレーム）
# 60Hzなら10→約167ms、120Hzなら10→約83ms
INTERP_MAX_GAP_FRAMES = 10

# 平滑化（rolling）窓（フレーム数）
# 60Hzなら 5~11、120Hzなら 9~21
SMOOTH_MED_WIN  = 5
SMOOTH_MEAN_WIN = 5

# ★「元コード踏襲」：刺激提示フレームから、上昇が止まる地点（局所最大）を取る探索窓
# 元コード t += 240 は（120Hz想定で）2秒ぶん → 秒指定で安全に
PEAK_WINDOW_SEC = 2.0

# -------- ページ分割プロット設定 --------
TRIALS_PER_PAGE   = 16      # 16本ずつ
PAD_LEFT_FRAMES   = 30     # 左余白
PAD_RIGHT_FRAMES  = 180    # 右余白（2~3秒ぶん相当を見たいなら増やす）
SHOW_PLOTS        = True   # 画面にも出す
SAVE_PAGES        = True   # ページPNGを保存する

# 保存ルート（この下に Bright/Dark が自動で掘られる）
SAVE_ROOT_DIR = "../../data/graphs/pages"

# プロット用：線が途切れるのが嫌なら True（可視化用に小ギャップだけ補間）
PLOT_CONNECT_GAPS = True
PLOT_MAX_GAP_FRAMES = 30  # 可視化で繋ぐ最大ギャップ（長すぎるのは繋がない）

# -------- EMR デバイス依存の列名（機種変更時はここだけ変える）--------
EMR_COL_FRAME      = "番号"                  # フレーム番号
EMR_COL_LEFT_PUPIL = "左眼.瞳孔径[mm]"       # 左眼瞳孔径
EMR_COL_RIGHT_PUPIL= "右眼.瞳孔径[mm]"       # 右眼瞳孔径
EMR_COL_BOTH_Z     = "両眼.注視Z座標[mm]"     # 両眼注視Z座標
EMR_REQUIRED_COLS  = [EMR_COL_FRAME, EMR_COL_LEFT_PUPIL, EMR_COL_RIGHT_PUPIL, EMR_COL_BOTH_Z]

# ============================================================


# -----------------------------
# ユーティリティ
# -----------------------------
def _must_have(df: pd.DataFrame, cols, name="df"):
    missing = [c for c in cols if c not in df.columns]
    if missing:
        raise RuntimeError(f"{name} に必須列がありません: {missing}\n現在の列: {df.columns.tolist()}")

def _ensure_dir_for_file(path: str):
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)

def _ensure_dir(path: str):
    os.makedirs(path, exist_ok=True)

def infer_condition_from_path(path: str) -> str:
    p = os.path.normpath(str(path)).lower()
    if "bright" in p:
        return "Bright"
    if "dark" in p:
        return "Dark"
    return "Unknown"

def infer_subject_from_path(path: str) -> str:
    # 例: .../S01/... から S01 を拾う（なければ UnknownSubject）
    s = str(path)
    m = re.search(r"(S\d+)", s, flags=re.IGNORECASE)
    return m.group(1).upper() if m else "UnknownSubject"

def pick_frame_col(df_log: pd.DataFrame, emr_fps: int) -> str:
    # EMRが60Hzなら Frame_60fps を優先、120Hzなら Frame_120fps を優先
    if emr_fps == 60 and FRAME_COL_60 in df_log.columns:
        return FRAME_COL_60
    if emr_fps == 120 and FRAME_COL_120 in df_log.columns:
        return FRAME_COL_120
    # fallback
    if FRAME_COL_60 in df_log.columns:
        return FRAME_COL_60
    if FRAME_COL_120 in df_log.columns:
        return FRAME_COL_120
    raise RuntimeError(f"実験ログに {FRAME_COL_60} または {FRAME_COL_120} がありません。")

def _clip_to_nan(s: pd.Series, lo: float, hi: float) -> pd.Series:
    s = pd.to_numeric(s, errors="coerce").astype(float)
    return s.where((s >= float(lo)) & (s <= float(hi)), np.nan)

# Hampel filter（ロバスト外れ値除去）
def hampel_filter(s: pd.Series, window: int = 11, n_sigma: float = 3.0) -> pd.Series:
    x = pd.to_numeric(s, errors="coerce").astype(float)
    if window is None or window < 3:
        return x
    if window % 2 == 0:
        window += 1
    k = window // 2

    med = x.rolling(window=window, center=True, min_periods=max(3, k)).median()
    mad = (x - med).abs().rolling(window=window, center=True, min_periods=max(3, k)).median()
    sigma = 1.4826 * mad

    outlier = (x - med).abs() > (n_sigma * sigma)
    y = x.copy()
    y[outlier] = np.nan
    return y

def interpolate_small_gaps(s: pd.Series, max_gap: int) -> pd.Series:
    """
    NaNギャップが max_gap 以内なら線形補間で埋める（長い欠損は埋めない）
    """
    x = pd.to_numeric(s, errors="coerce").astype(float)
    if max_gap is None or max_gap <= 0:
        return x

    is_na = x.isna()
    if not is_na.any():
        return x

    grp = (is_na != is_na.shift(1)).cumsum()
    gap_len = is_na.groupby(grp).transform("sum")

    # 長すぎる欠損は補間しない（そのままNaN）
    x2 = x.copy()
    x2[is_na & (gap_len > max_gap)] = np.nan
    x2 = x2.interpolate(method="linear", limit=max_gap, limit_direction="both")
    return x2

def smooth_series(s: pd.Series, med_win: int, mean_win: int) -> pd.Series:
    x = pd.to_numeric(s, errors="coerce").astype(float)
    if med_win and med_win >= 3:
        x = x.rolling(window=med_win, center=True, min_periods=max(2, med_win // 2)).median()
    if mean_win and mean_win >= 3:
        x = x.rolling(window=mean_win, center=True, min_periods=max(2, mean_win // 2)).mean()
    return x

def series_for_plot(s: pd.Series, max_gap: int) -> pd.Series:
    """
    可視化だけ、途切れを減らすために小ギャップを補間する（保存データは変えない）
    """
    x = pd.to_numeric(s, errors="coerce").astype(float)
    if not PLOT_CONNECT_GAPS:
        return x
    return interpolate_small_gaps(x, max_gap=max_gap)


# -----------------------------
# EMR 読み込み + 前処理
# -----------------------------
def load_and_prepare_emr(emr_csv: str) -> pd.DataFrame:
    df = pd.read_csv(emr_csv)
    _must_have(df, EMR_REQUIRED_COLS, name="EMR")

    for c in EMR_REQUIRED_COLS:
        df[c] = pd.to_numeric(df[c], errors="coerce")

    # 相対フレーム
    start_num = df[EMR_COL_FRAME].iloc[0]
    df["emr_frame_rel"] = df[EMR_COL_FRAME] - start_num

    # raw
    df["emr_left_pupil_mm_raw"]  = df[EMR_COL_LEFT_PUPIL]
    df["emr_right_pupil_mm_raw"] = df[EMR_COL_RIGHT_PUPIL]
    df["emr_both_pupil_mm_raw"]  = (df["emr_left_pupil_mm_raw"] + df["emr_right_pupil_mm_raw"]) / 2.0

    df["emr_both_Z_mm_raw"] = df[EMR_COL_BOTH_Z]
    z_raw = pd.to_numeric(df["emr_both_Z_mm_raw"], errors="coerce")
    df["emr_diopter_raw"] = np.where((z_raw > 0) & (~np.isnan(z_raw)), 1000.0 / z_raw, np.nan)

    # ---- 前処理（共通パイプライン）----
    def _preproc(x: pd.Series, lo: float, hi: float) -> pd.Series:
        y = _clip_to_nan(x, lo, hi)                              # 1) 物理レンジ
        y = hampel_filter(y, window=HAMPEL_WIN, n_sigma=HAMPEL_SIGMA)  # 2) Hampel外れ値
        y = interpolate_small_gaps(y, max_gap=INTERP_MAX_GAP_FRAMES)   # 3) 小ギャップ補間
        y = smooth_series(y, med_win=SMOOTH_MED_WIN, mean_win=SMOOTH_MEAN_WIN)  # 4) 平滑化
        return y

    left_s  = _preproc(df["emr_left_pupil_mm_raw"],  PUPIL_MIN_MM, PUPIL_MAX_MM)
    right_s = _preproc(df["emr_right_pupil_mm_raw"], PUPIL_MIN_MM, PUPIL_MAX_MM)
    z_s     = _preproc(df["emr_both_Z_mm_raw"],       Z_MIN_MM, Z_MAX_MM)

    df["emr_left_pupil_mm"]  = left_s
    df["emr_right_pupil_mm"] = right_s
    df["emr_both_pupil_mm"]  = (df["emr_left_pupil_mm"] + df["emr_right_pupil_mm"]) / 2.0
    df["emr_both_Z_mm"]      = z_s

    # diopter（前処理後Zから）
    z2 = pd.to_numeric(df["emr_both_Z_mm"], errors="coerce").astype(float)
    diop = np.where((z2 > 0) & (~np.isnan(z2)), 1000.0 / z2, np.nan)
    diop = pd.Series(diop, index=df.index)

    # ---- 元コード思想：範囲外は 0 ----
    diop0 = diop.where((diop >= DIOPTER_MIN) & (diop <= DIOPTER_MAX), 0.0)

    # 0があるので、平滑化は「0を一旦NaN扱い→平滑→戻す」
    diop0_s = smooth_series(diop0.replace(0.0, np.nan), med_win=SMOOTH_MED_WIN, mean_win=SMOOTH_MEAN_WIN).fillna(0.0)
    df["emr_diopter_clipped0"] = diop0_s.values

    out_cols = [
        "emr_frame_rel",
        "emr_left_pupil_mm_raw", "emr_right_pupil_mm_raw", "emr_both_pupil_mm_raw",
        "emr_both_Z_mm_raw", "emr_diopter_raw",
        "emr_left_pupil_mm", "emr_right_pupil_mm", "emr_both_pupil_mm",
        "emr_both_Z_mm",
        "emr_diopter_clipped0",
    ]
    out = df[out_cols].sort_values("emr_frame_rel").reset_index(drop=True)
    return out


# -----------------------------
# ★ diopter の取り方（元コード踏襲）
#   刺激フレーム start から先を見て
#   while (max < val) or (val == 0) を繰り返し、上昇が止まる地点の max を取る
# -----------------------------
def diopter_peak_from_start(diop0: np.ndarray, start_idx: int, max_search: int) -> tuple[float, int]:
    """
    returns: (peak_value, peak_idx)
    見つからなければ (np.nan, -1)
    """
    n = len(diop0)
    if start_idx < 0 or start_idx >= n:
        return (np.nan, -1)

    mx = 0.0
    j = 0
    last_idx = start_idx

    while j < max_search and (start_idx + j) < n:
        v = float(diop0[start_idx + j])
        last_idx = start_idx + j

        # break 条件：v が 0 ではなく、かつ mx >= v（上昇終了）
        if (v != 0.0) and (mx >= v):
            break

        mx = v
        j += 1

    if mx == 0.0:
        return (np.nan, -1)
    return (mx, last_idx)

def add_diopter_peak_columns(merged: pd.DataFrame, emr_df: pd.DataFrame, frame_col: str) -> pd.DataFrame:
    stim_frames = pd.to_numeric(merged[frame_col], errors="coerce").values.astype(float)

    emr_frames = emr_df["emr_frame_rel"].values.astype(float)
    diop0 = emr_df["emr_diopter_clipped0"].values.astype(float)

    max_search = int(round(PEAK_WINDOW_SEC * EMR_FPS))
    max_search = max(1, max_search)

    peaks = []
    peak_frames = []

    for sf in stim_frames:
        if np.isnan(sf):
            peaks.append(np.nan)
            peak_frames.append(np.nan)
            continue

        idx = int(np.clip(np.searchsorted(emr_frames, sf), 0, len(emr_frames) - 1))
        if idx > 0 and abs(emr_frames[idx] - sf) > abs(emr_frames[idx - 1] - sf):
            idx -= 1

        pv, pi = diopter_peak_from_start(diop0, idx, max_search=max_search)
        peaks.append(pv)
        peak_frames.append(emr_frames[pi] if pi >= 0 else np.nan)

    merged["emr_diopter_peak"] = peaks
    merged["emr_diopter_peak_frame_rel"] = peak_frames
    return merged


# -----------------------------
# merge_asof でフレーム合わせ + 保存
# -----------------------------
def add_emr_columns_to_log(experiment_log_csv: str, emr_csv: str, out_csv: str) -> tuple[pd.DataFrame, str, pd.DataFrame]:
    df_log = pd.read_csv(experiment_log_csv, encoding="utf-8-sig")
    frame_col = pick_frame_col(df_log, EMR_FPS)

    # すでに emr_* 列があるログを読んでも重複しないように削る
    emr_like_cols = [c for c in df_log.columns if c.startswith("emr_")]
    if emr_like_cols:
        df_log = df_log.drop(columns=emr_like_cols)

    df_log[frame_col] = pd.to_numeric(df_log[frame_col], errors="coerce")
    df_log = df_log.dropna(subset=[frame_col]).sort_values(frame_col).reset_index(drop=True)

    emr_df = load_and_prepare_emr(emr_csv)

    merged = pd.merge_asof(
        df_log,
        emr_df,
        left_on=frame_col,
        right_on="emr_frame_rel",
        direction="nearest",
        tolerance=TOLERANCE_FRAMES,
    )

    merged = add_diopter_peak_columns(merged, emr_df, frame_col)

    _ensure_dir_for_file(out_csv)
    merged.to_csv(out_csv, index=False, encoding="utf-8-sig")

    print(f"[OK] saved: {out_csv}")
    print(f"[INFO] used frame col: {frame_col} / EMR_FPS={EMR_FPS} / tolerance: ±{TOLERANCE_FRAMES} frames")
    n_total = len(merged)
    n_hit = merged["emr_frame_rel"].notna().sum()
    print(f"[INFO] matched rows: {n_hit}/{n_total} (unmatched become NaN)")
    return merged, frame_col, emr_df


# -----------------------------
# ページ分割・拡大プロット（Bright/Darkで保存フォルダ分け）
# -----------------------------
def plot_alignment_zoom_pages(
    log_with_emr_csv: str,
    emr_csv: str,
    trials_per_page: int = 5,
    pad_left_frames: int = 30,
    pad_right_frames: int = 60,
    save_root_dir: str | None = None,
    show:  bool = True,
    save: bool = True,
):
    """
    48試行の縦線（刺激開始）を、trials_per_page本ずつ区切って
    xlim を制限して拡大表示する。保存時は save_root_dir/Bright or Dark に自動振り分け。

    ★追加：frontが数字のフレームを赤い縦線 or 別マーカーで表示
    """
    df = pd.read_csv(log_with_emr_csv, encoding="utf-8-sig")

    frame_col = pick_frame_col(df, EMR_FPS)
    df[frame_col] = pd.to_numeric(df[frame_col], errors="coerce")
    df = df.dropna(subset=[frame_col]).copy()

    emr_df = load_and_prepare_emr(emr_csv)
    x_emr = emr_df["emr_frame_rel"].values. astype(float)

    # ★ frontが数字かどうかを判定（文字列→数値変換できるか）
    def is_numeric_front(val):
        if pd.isna(val):
            return False
        try:
            float(str(val))
            return True
        except:
            return False

    # ★ 刺激提示フレーム（frontが数字）と通常フレームを分離
    df["is_stimulus"] = df. get("front", pd.Series([None]*len(df))).apply(is_numeric_front)

    stimulus_frames = df[df["is_stimulus"]][frame_col].values. astype(float)
    stimulus_frames = np.unique(stimulus_frames[~np.isnan(stimulus_frames)])
    stimulus_frames. sort()

    # 全フレーム（従来通り）
    vlines_all = np.asarray(df[frame_col].astype(float).values)
    vlines_all = np.unique(vlines_all[~np. isnan(vlines_all)])
    vlines_all.sort()

    # 散布（x,yのNaN/infを除外してサイズ不一致を防ぐ）
    def _scatter(ax, x, y, s=14, **kwargs):
        x = np.asarray(x, dtype=float)
        y = np.asarray(y, dtype=float)
        m = np.isfinite(x) & np.isfinite(y)
        ax.scatter(x[m], y[m], s=s, **kwargs)

    # 保存フォルダ（Bright/Dark/Unknown） + 被験者 + ベース名
    cond = infer_condition_from_path(log_with_emr_csv)
    subj = infer_subject_from_path(log_with_emr_csv)
    base = os.path.splitext(os.path.basename(log_with_emr_csv))[0]

    save_dir = None
    if save_root_dir and save:
        save_dir = os.path.join(save_root_dir, cond, subj, base)
        _ensure_dir(save_dir)

    n_trials = len(vlines_all)
    n_pages = int(np.ceil(n_trials / trials_per_page))

    # プロット用：途切れを減らす（可視化だけ）
    left_plot  = series_for_plot(emr_df["emr_left_pupil_mm"],  max_gap=PLOT_MAX_GAP_FRAMES).values
    right_plot = series_for_plot(emr_df["emr_right_pupil_mm"], max_gap=PLOT_MAX_GAP_FRAMES).values
    both_plot  = series_for_plot(emr_df["emr_both_pupil_mm"],  max_gap=PLOT_MAX_GAP_FRAMES).values
    diop_plot  = series_for_plot(emr_df["emr_diopter_clipped0"], max_gap=PLOT_MAX_GAP_FRAMES).values

    for page in range(n_pages):
        sidx = page * trials_per_page
        eidx = min((page + 1) * trials_per_page, n_trials)

        vlines = vlines_all[sidx: eidx]
        if len(vlines) == 0:
            continue

        # ★ このページに含まれる刺激フレームを抽出
        stim_in_page = stimulus_frames[(stimulus_frames >= vlines[0] - pad_left_frames) &
                                       (stimulus_frames <= vlines[-1] + pad_right_frames)]

        x0 = float(vlines[0]) - pad_left_frames
        x1 = float(vlines[-1]) + pad_right_frames

        fig, axes = plt.subplots(4, 1, figsize=(24, 10), sharex=True)

        # 1) left pupil
        axes[0].plot(x_emr, left_plot, linewidth=1.0)
        _scatter(axes[0], df[frame_col]. values, df. get("emr_left_pupil_mm", np.nan), s=12)
        axes[0].set_ylabel("Left pupil [mm]")
        axes[0].set_title(f"EMR alignment ({cond}/{subj}/{base})  page {page+1}/{n_pages}  xlim={x0:.0f}-{x1:.0f}")

        # 2) right pupil
        axes[1].plot(x_emr, right_plot, linewidth=1.0)
        _scatter(axes[1], df[frame_col].values, df.get("emr_right_pupil_mm", np.nan), s=12)
        axes[1].set_ylabel("Right pupil [mm]")

        # 3) both pupil
        axes[2].plot(x_emr, both_plot, linewidth=1.0)
        _scatter(axes[2], df[frame_col].values, df.get("emr_both_pupil_mm", np.nan), s=12)
        axes[2].set_ylabel("Both pupil [mm]")

        # 4) diopter + peak
        axes[3].plot(x_emr, diop_plot, linewidth=1.0, label="EMR continuous")

        # ★ 通常のログ点（オレンジ）
        _scatter(axes[3], df[frame_col].values, df. get("emr_diopter_clipped0", np.nan),
                s=12, label="Log frames")

        # ★ 刺激フレームのdiopter値を緑の点で強調
        stim_df = df[df["is_stimulus"]].copy()
        _scatter(axes[3], stim_df[frame_col].values, stim_df.get("emr_diopter_clipped0", np.nan),
                s=40, color="lime", marker="^", edgecolors="green", linewidths=1.5,
                label="Stimulus frames", zorder=5)

        # ★ ピーク値（元のまま）
        if "emr_diopter_peak" in df. columns:
            _scatter(axes[3], df[frame_col].values, df["emr_diopter_peak"].values, s=20)

        axes[3]. set_ylabel("Diopter [D]")
        axes[3].set_xlabel(f"Frame (log col: {frame_col})")
        axes[3].legend(loc="upper right", fontsize=8)

        # ★ 縦線：刺激フレームは赤、それ以外はグレー + タスク番号表示
        stim_set = set(stim_in_page)

        # 各vlinesに対応する全体でのタスク番号を取得（1始まり）
        for i, xv in enumerate(vlines):
            task_num = sidx + i + 1  # 全体のタスク番号（1-48）
            is_stim = xv in stim_set

            for ax_idx, ax in enumerate(axes):
                # 縦線
                if is_stim:
                    ax.axvline(x=float(xv), color="red", linewidth=1.2, alpha=0.7)
                else:
                    ax.axvline(x=float(xv), color="gray", linewidth=0.7, alpha=0.4)

                # 一番上の軸にだけタスク番号を表示
                if ax_idx == 0:
                    y_lim = ax.get_ylim()
                    y_range = y_lim[1] - y_lim[0]
                    y_pos = y_lim[1] + y_range * 0.02  # 上端から少し上に配置
                    ax.text(float(xv), y_pos, str(task_num),
                           ha='center', va='bottom', fontsize=8,
                           color='red' if is_stim else 'gray',
                           fontweight='bold' if is_stim else 'normal',
                           clip_on=False)  # クリップしないでテキストを表示

        # y軸の上限を少し広げてテキスト表示領域を確保
        for ax_idx, ax in enumerate(axes):
            ax.set_xlim(x0, x1)
            if ax_idx == 0:
                y_lim = ax.get_ylim()
                y_range = y_lim[1] - y_lim[0]
                ax.set_ylim(y_lim[0], y_lim[1] + y_range * 0.08)

        plt.tight_layout()

        if save_dir:
            out_path = os.path.join(save_dir, f"{base}_page_{page+1:02d}.png")
            plt.savefig(out_path, dpi=200)
            print(f"[OK] saved: {out_path}")

        plt.close(fig)


# ============================================================
# コマンドライン引数パーサ
# ============================================================
def parse_args():
    """コマンドライン引数を解析"""
    p = argparse.ArgumentParser(
        description="EMRセグメントをログに追加し、試行ごとのページ分割グラフを保存"
    )
    p.add_argument("--trials-per-page", type=int, default=TRIALS_PER_PAGE,
                   help=f"1ページに表示する試行数 (デフォルト: {TRIALS_PER_PAGE})")
    p.add_argument("--pad-left-frames", type=int, default=PAD_LEFT_FRAMES,
                   help=f"ページ左余白のフレーム数 (デフォルト: {PAD_LEFT_FRAMES})")
    p.add_argument("--pad-right-frames", type=int, default=PAD_RIGHT_FRAMES,
                   help=f"ページ右余白のフレーム数 (デフォルト: {PAD_RIGHT_FRAMES})")
    p.add_argument("--show-plots", action="store_true",
                   help="画面にプロットを表示する")
    p.add_argument("--no-save", action="store_true",
                   help="PNGファイルを保存しない")
    p.add_argument("--save-root", type=str, default=SAVE_ROOT_DIR,
                   help=f"保存先ルートディレクトリ (デフォルト: {SAVE_ROOT_DIR})")
    return p.parse_args()


# ============================================================
# 実行
# ============================================================
if __name__ == "__main__":
    args = parse_args()

    # Bright: S1..S19, segments 0..9
    for s in range(1, 20):
        subj = f"S{s:02d}"
        for seg in range(0, 10):
            EXPERIMENT_LOG_CSV = os.path.join("..", "..", "log", "Bright", subj, f"{subj}_{seg}.csv")
            EMR_SEGMENT_CSV    = os.path.join("..", "..", "data", "devided_emr", str(s), f"{seg}.csv")
            OUT_LOG_CSV        = os.path.join("..", "..", "data", "log_with_emr", "Bright", subj, f"{subj}_{seg}_with_emr.csv")
            try:
                print(f"[RUN] Bright {subj} seg={seg}")
                merged_df, used_frame_col, emr_df = add_emr_columns_to_log(EXPERIMENT_LOG_CSV, EMR_SEGMENT_CSV, OUT_LOG_CSV)
                plot_alignment_zoom_pages(
                    OUT_LOG_CSV,
                    EMR_SEGMENT_CSV,
                    trials_per_page=args.trials_per_page,
                    pad_left_frames=args.pad_left_frames,
                    pad_right_frames=args.pad_right_frames,
                    save_root_dir=args.save_root,
                    show=args.show_plots,
                    save=(not args.no_save),
                )
            except Exception as e:
                print(f"[ERROR] Bright {subj} seg={seg} -> {e}")
                continue

    # Dark: S101..S109, segments 0..9
    for s in range(101,120):
        subj = f"S{s:03d}"
        for seg in range(5, 10):
            EXPERIMENT_LOG_CSV = os.path.join("..", "..", "log", "Dark", subj, f"{subj}_{seg}.csv")
            EMR_SEGMENT_CSV    = os.path.join("..", "..", "data", "devided_emr", str(s), f"{seg}.csv")
            OUT_LOG_CSV        = os.path.join("..", "..", "data", "log_with_emr", "Dark", subj, f"{subj}_{seg}_with_emr.csv")
            try:
                print(f"[RUN] Dark {subj} seg={seg}")
                merged_df, used_frame_col, emr_df = add_emr_columns_to_log(EXPERIMENT_LOG_CSV, EMR_SEGMENT_CSV, OUT_LOG_CSV)
                plot_alignment_zoom_pages(
                    OUT_LOG_CSV,
                    EMR_SEGMENT_CSV,
                    trials_per_page=args.trials_per_page,
                    pad_left_frames=args.pad_left_frames,
                    pad_right_frames=args.pad_right_frames,
                    save_root_dir=args.save_root,
                    show=args.show_plots,
                    save=(not args.no_save),
                )
            except Exception as e:
                print(f"[ERROR] Dark {subj} seg={seg} -> {e}")
                continue
