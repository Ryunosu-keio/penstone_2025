# -*- coding: utf-8 -*-
"""
emr_task_windows_addpupil_and_plots-240.py
-------------------------------------
実験ログ(1行=1タスク想定)と EMR セグメントCSV をフレームで突合し、
「ディオプター上昇 & frontが数字」のタスクだけを対象に、

- task window（stim_frame から task_sec 秒）
- baseline window（onset直前）
- miosis window（peak後 lag してから）
を決めて、
diopter値・baseline・縮瞳率などをログに追加する。

さらに可視化：
(1) 連結ビュー：対象タスク区間だけを横軸でつなげて、4段（左/右/平均/diopter）に並べる
    baseline区間とmiosis区間を"違う色"でハイライト
    ★追加：diopter立ち上がり(onset)の 240フレーム前まで遡って描画（緑の縦線=onset）
(2) グリッドビュー：4×16固定で各タスクを並べる
    ★必ずfrontが数字のフレーム（16個）を使用
    ★ディオプターが取れなかったフレームは空白
    ★ログが不足している場合は白紙で「log_insufficient」というファイル名

依存:
  pip install pandas numpy matplotlib
"""

import os
import re
import glob
import argparse
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from tqdm import tqdm

# ============================================================
# EMR デバイス依存の列名（機種変更時はここだけ変える）
# ============================================================
EMR_COL_FRAME      = "番号"                  # フレーム番号
EMR_COL_LEFT_PUPIL = "左眼.瞳孔径[mm]"       # 左眼瞳孔径
EMR_COL_RIGHT_PUPIL= "右眼.瞳孔径[mm]"       # 右眼瞳孔径
EMR_COL_BOTH_Z     = "両眼.注視Z座標[mm]"     # 両眼注視Z座標
EMR_REQUIRED_COLS  = [EMR_COL_FRAME, EMR_COL_LEFT_PUPIL, EMR_COL_RIGHT_PUPIL, EMR_COL_BOTH_Z]


# ============================================================
# ユーティリティ
# ============================================================
def _must_have(df:  pd.DataFrame, cols, name="df"):
    missing = [c for c in cols if c not in df.columns]
    if missing:
        raise RuntimeError(f"{name} に必須列がありません: {missing}\n現在の列: {df.columns. tolist()}")

def _ensure_dir(path:  str):
    os.makedirs(path, exist_ok=True)

def _ensure_dir_for_file(path: str):
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)

def infer_condition_from_path(path: str) -> str:
    p = os.path.normpath(str(path)).lower()
    if "bright" in p:
        return "Bright"
    if "dark" in p:
        return "Dark"
    return "Unknown"

def infer_subject_from_path(path: str) -> str:
    s = str(path)
    m = re.search(r"(S\d+)", s, flags=re.IGNORECASE)
    return m.group(1).upper() if m else "UnknownSubject"

def pick_frame_col(df_log: pd.DataFrame, emr_fps: int) -> str:
    FRAME_COL_120 = "Frame_120fps"
    FRAME_COL_60  = "Frame_60fps"
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

def infer_digit_mask(df_log: pd.DataFrame, digit_col: str | None = None, front_col:  str | None = None) -> pd.Series:
    """
    frontが数字かどうかの判定（柔軟に）
    優先:  digit_col が存在すればそれを使う
    次点: front_col を文字列として isdigit
    それでも無理なら「常にTrue」にしないで False 返す（安全側）
    """
    if digit_col and digit_col in df_log.columns:
        s = df_log[digit_col]
        if s.dtype == bool:
            return s. fillna(False)
        v = pd.to_numeric(s, errors="coerce")
        if v.notna().any():
            return (v. fillna(0).astype(float) != 0)
        return s.astype(str).str.lower().isin(["true", "1", "yes", "y"])

    for cand in ["front_is_digit", "FrontIsDigit", "is_digit", "IsDigit", "front_digit"]:
        if cand in df_log.columns:
            return infer_digit_mask(df_log, digit_col=cand, front_col=front_col)

    if front_col and front_col in df_log.columns:
        return df_log[front_col].astype(str).str.strip().str.fullmatch(r"\d+").fillna(False)

    for cand in ["front", "Front", "figure", "Figure", "stim", "Stim", "text", "Text"]:
        if cand in df_log.columns:
            return df_log[cand].astype(str).str.strip().str.fullmatch(r"\d+").fillna(False)

    return pd.Series([False] * len(df_log), index=df_log.index)


# ============================================================
# EMR 読み込み（範囲外 diopter は 0）
# ============================================================
def load_emr_with_diopter(
    emr_csv: str,
    diopter_min: float,
    diopter_max:  float,
    pupil_min_mm: float,
    pupil_max_mm: float,
) -> pd.DataFrame:
    df = pd.read_csv(emr_csv)

    # ★列名の前後のスペースを除去
    df.columns = df.columns.str.strip()

    _must_have(df, EMR_REQUIRED_COLS, name="EMR")

    for c in EMR_REQUIRED_COLS:
        df[c] = pd.to_numeric(df[c], errors="coerce")

    start_num = df[EMR_COL_FRAME].iloc[0]
    df["emr_frame_rel"] = (df[EMR_COL_FRAME] - start_num).astype("int64")

    df["emr_left_pupil_mm_raw"]  = df[EMR_COL_LEFT_PUPIL]
    df["emr_right_pupil_mm_raw"] = df[EMR_COL_RIGHT_PUPIL]
    df["emr_both_pupil_mm_raw"]  = (df["emr_left_pupil_mm_raw"] + df["emr_right_pupil_mm_raw"]) / 2.0

    # ★ 前処理パラメータ（emr_extract_max2_by_logframe.py と同じ）
    HAMPEL_WIN = 11
    HAMPEL_SIGMA = 3.0
    INTERP_MAX_GAP_FRAMES = 10
    SMOOTH_MED_WIN = 5
    SMOOTH_MEAN_WIN = 5
    Z_MIN_MM = 100.0
    Z_MAX_MM = 6000.0

    def _clip_nan(s, lo, hi):
        x = pd.to_numeric(s, errors="coerce").astype(float)
        return x.where((x >= float(lo)) & (x <= float(hi)), np.nan)

    def hampel_filter(s: pd.Series, window: int = 11, n_sigma: float = 3.0) -> pd.Series:
        x = pd.to_numeric(s, errors="coerce").astype(float)
        if window < 3:
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
        x = pd.to_numeric(s, errors="coerce").astype(float)
        if max_gap <= 0:
            return x
        is_na = x.isna()
        if not is_na.any():
            return x
        grp = (is_na != is_na.shift(1)).cumsum()
        gap_len = is_na.groupby(grp).transform("sum")
        x2 = x.copy()
        x2[is_na & (gap_len > max_gap)] = np.nan
        x2 = x2.interpolate(method="linear", limit=max_gap, limit_direction="both")
        return x2

    def smooth_series(s: pd.Series, med_win: int, mean_win: int) -> pd.Series:
        x = pd.to_numeric(s, errors="coerce").astype(float)
        if med_win >= 3:
            x = x.rolling(window=med_win, center=True, min_periods=max(2, med_win // 2)).median()
        if mean_win >= 3:
            x = x.rolling(window=mean_win, center=True, min_periods=max(2, mean_win // 2)).mean()
        return x

    def preprocess(x: pd.Series, lo: float, hi: float) -> pd.Series:
        y = _clip_nan(x, lo, hi)
        y = hampel_filter(y, window=HAMPEL_WIN, n_sigma=HAMPEL_SIGMA)
        y = interpolate_small_gaps(y, max_gap=INTERP_MAX_GAP_FRAMES)
        y = smooth_series(y, med_win=SMOOTH_MED_WIN, mean_win=SMOOTH_MEAN_WIN)
        return y

    # ★ 瞳孔径の前処理
    left_s  = preprocess(df["emr_left_pupil_mm_raw"],  pupil_min_mm, pupil_max_mm)
    right_s = preprocess(df["emr_right_pupil_mm_raw"], pupil_min_mm, pupil_max_mm)
    df["emr_left_pupil_mm"]  = left_s
    df["emr_right_pupil_mm"] = right_s
    df["emr_both_pupil_mm"]  = (df["emr_left_pupil_mm"] + df["emr_right_pupil_mm"]) / 2.0

    # ★ Z座標の前処理
    z_s = preprocess(df[EMR_COL_BOTH_Z], Z_MIN_MM, Z_MAX_MM)

    # ★ ディオプターの計算（前処理後のZから）
    z2 = pd.to_numeric(z_s, errors="coerce").astype(float)
    diop = np.where((z2 > 0) & np.isfinite(z2), 1000.0 / z2, np.nan)
    diop = pd.Series(diop, index=df.index)

    # ★ ディオプターの範囲クリップ（範囲外は0）
    diop0 = diop.where((diop >= float(diopter_min)) & (diop <= float(diopter_max)), 0.0)

    # ★ 0があるので平滑化（0を一旦NaN扱い→平滑→戻す）
    diop0_s = smooth_series(diop0.replace(0.0, np.nan), med_win=SMOOTH_MED_WIN, mean_win=SMOOTH_MEAN_WIN).fillna(0.0)

    df["emr_diopter_raw"] = diop
    df["emr_diopter_clipped0"] = diop0_s

    out_cols = [
        "emr_frame_rel",
        "emr_left_pupil_mm", "emr_right_pupil_mm", "emr_both_pupil_mm",
        "emr_diopter_raw", "emr_diopter_clipped0",
    ]
    return df[out_cols]. sort_values("emr_frame_rel").reset_index(drop=True)


# ============================================================
# タスク1件：window決定 + 指標計算（自動）
# ============================================================
def compute_task_windows_and_metrics_auto(
    emr_df: pd.DataFrame,
    stim_frame: int,
    emr_fps:  int,
    task_sec:  float,

    onset_search_sec: float,
    onset_delta_d: float,

    peak_search_sec: float,

    baseline_frames: int,
    miosis_lag_sec:  float,
    miosis_frames: int,

    diopter_increase_min_d: float,
    baseline_mode: str = "onset",  # "onset" or "stim"
):
    x = emr_df["emr_frame_rel"]. to_numpy(dtype=int)
    diop0 = emr_df["emr_diopter_clipped0"].to_numpy(dtype=float)

    if len(x) == 0:
        return {"Skip_Task": True, "Skip_Reason": "empty_emr"}

    if stim_frame < int(x[0]) or stim_frame > int(x[-1]):
        return {"Skip_Task": True, "Skip_Reason": "stim_out_of_emr_range"}

    task_frames = max(1, int(round(float(task_sec) * emr_fps)))
    task_start = int(stim_frame)
    task_end   = int(stim_frame + task_frames - 1)
    if task_end > int(x[-1]):
        task_end = int(x[-1])

    m_task = (x >= task_start) & (x <= task_end)
    if not np.any(m_task):
        return {"Skip_Task": True, "Skip_Reason": "no_task_frames_in_emr"}

    onset_search_frames = max(1, int(round(onset_search_sec * emr_fps)))
    onset_end_frame = min(task_end, task_start + onset_search_frames)

    m_onset = (x >= task_start) & (x <= onset_end_frame)
    seg_onset_x = x[m_onset]
    seg_onset_d = diop0[m_onset]

    base_d_candidates = seg_onset_d[:  min(10, len(seg_onset_d))]
    base_d_candidates = base_d_candidates[base_d_candidates > 0]
    baseline_diopter = float(np.median(base_d_candidates)) if len(base_d_candidates) else 0.0

    onset_frame = None
    for xf, dv in zip(seg_onset_x, seg_onset_d):
        if dv > 0 and (dv - baseline_diopter) >= float(onset_delta_d):
            onset_frame = int(xf)
            break

    if onset_frame is None:
        return {
            "Skip_Task": True, "Skip_Reason": "no_diopter_onset",
            "task_start_frame_emr": task_start,
            "task_end_frame_emr": task_end,
            "diopter_baseline": baseline_diopter,
        }

    peak_search_frames = max(1, int(round(peak_search_sec * emr_fps)))
    peak_end_frame = min(task_end, task_start + peak_search_frames)

    m_peak = (x >= task_start) & (x <= peak_end_frame)
    seg_peak_x = x[m_peak]
    seg_peak_d = diop0[m_peak]
    if len(seg_peak_d) == 0:
        return {"Skip_Task": True, "Skip_Reason": "peak_search_empty"}

    peak_idx_rel = int(np.argmax(seg_peak_d))
    peak_frame = int(seg_peak_x[peak_idx_rel])
    peak_value = float(seg_peak_d[peak_idx_rel])

    diopter_delta = peak_value - baseline_diopter
    if (not np.isfinite(diopter_delta)) or diopter_delta < float(diopter_increase_min_d):
        return {
            "Skip_Task": True, "Skip_Reason": "diopter_increase_too_small",
            "task_start_frame_emr":  task_start,
            "task_end_frame_emr":  task_end,
            "diopter_baseline": baseline_diopter,
            "diopter_onset_frame": onset_frame,
            "diopter_peak_frame": peak_frame,
            "diopter_peak_value":  peak_value,
            "diopter_delta":  diopter_delta,
        }

    # ★Diopter下降検出（固定：onsetから150フレーム後）
    descent_frame = onset_frame + 150
    if descent_frame > task_end:
        descent_frame = task_end




    # ★ベースラインウィンドウの計算（モード選択）
    if baseline_mode == "stim":
        # 刺激開始から120フレーム前の区間
        b2 = task_start - 1
        b1 = task_start - 120
        if b1 < int(x[0]):
            return {
                "Skip_Task": True, "Skip_Reason": "baseline_window_before_emr_start",
                "task_start_frame_emr": task_start,
                "task_end_frame_emr": task_end,
                "diopter_baseline": baseline_diopter,
                "diopter_onset_frame": onset_frame,
                "diopter_peak_frame": peak_frame,
                "diopter_peak_value": peak_value,
                "diopter_delta": diopter_delta,
            }
    else:  # "onset" (デフォルト)
        # onset直前の指定フレーム数
        b2 = onset_frame - 1
        b1 = max(task_start, onset_frame - int(baseline_frames))

    if b2 < b1:
        return {
            "Skip_Task": True, "Skip_Reason": "baseline_window_missing",
            "task_start_frame_emr": task_start,
            "task_end_frame_emr": task_end,
            "diopter_baseline": baseline_diopter,
            "diopter_onset_frame": onset_frame,
            "diopter_peak_frame": peak_frame,
            "diopter_peak_value": peak_value,
            "diopter_delta": diopter_delta,
        }

    # ★Miosis区間の再定義（onset → descent）
    m1 = onset_frame  # 上昇開始
    m2 = descent_frame  # 下降開始

    # 区間が有効かチェック
    if m1 >= m2 or m2 > task_end:
        return {
            "Skip_Task":  True, "Skip_Reason":  "invalid_miosis_window",
            "task_start_frame_emr": task_start,
            "task_end_frame_emr": task_end,
            "diopter_baseline": baseline_diopter,
            "diopter_onset_frame": onset_frame,
            "diopter_peak_frame": peak_frame,
            "diopter_peak_value":  peak_value,
            "diopter_delta": diopter_delta,
            "diopter_descent_frame": descent_frame,
            "baseline_frame_start": b1,
            "baseline_frame_end": b2,
        }


    left  = emr_df["emr_left_pupil_mm"].to_numpy(dtype=float)
    right = emr_df["emr_right_pupil_mm"].to_numpy(dtype=float)
    both  = emr_df["emr_both_pupil_mm"].to_numpy(dtype=float)

    def _win_vals(series, f1, f2):
        m = (x >= int(f1)) & (x <= int(f2))
        v = series[m]
        v = v[np.isfinite(v)]
        return v

    def _win_vals_with_min_frame(series, f1, f2):
        """値と最小値のフレームを返す"""
        m = (x >= int(f1)) & (x <= int(f2))
        frames_in_win = x[m]
        vals_in_win = series[m]
        finite_mask = np.isfinite(vals_in_win)
        if not np.any(finite_mask):
            return np.array([]), np.nan
        vals_finite = vals_in_win[finite_mask]
        frames_finite = frames_in_win[finite_mask]
        min_idx = np.argmin(vals_finite)
        min_frame = int(frames_finite[min_idx])
        return vals_finite, min_frame

    Lb = _win_vals(left,  b1, b2)
    Rb = _win_vals(right, b1, b2)
    Bb = _win_vals(both,  b1, b2)

    # miosis区間の値と最小値フレームを取得
    Lm, Lm_min_frame = _win_vals_with_min_frame(left, m1, m2)
    Rm, Rm_min_frame = _win_vals_with_min_frame(right, m1, m2)
    Bm, Bm_min_frame = _win_vals_with_min_frame(both, m1, m2)

    def _mean_or_nan(v): return float(np.mean(v)) if len(v) else np.nan
    def _min_or_nan(v):  return float(np.min(v))  if len(v) else np.nan

    Lb_mean, Rb_mean, Bb_mean = _mean_or_nan(Lb), _mean_or_nan(Rb), _mean_or_nan(Bb)
    Lm_mean, Rm_mean, Bm_mean = _mean_or_nan(Lm), _mean_or_nan(Rm), _mean_or_nan(Bm)
    Lm_min,  Rm_min,  Bm_min  = _min_or_nan(Lm),  _min_or_nan(Rm),  _min_or_nan(Bm)

    def _chg(b, m):
        if (not np.isfinite(b)) or b <= 0 or (not np.isfinite(m)):
            return np.nan
        return float((b - m) / b)

    return {
        "Skip_Task":  False,
        "Skip_Reason": "",

        "task_start_frame_emr": task_start,
        "task_end_frame_emr": task_end,

        "diopter_baseline":  baseline_diopter,
        "diopter_onset_frame": onset_frame,
        "diopter_peak_frame":  peak_frame,
        "diopter_peak_value": peak_value,
        "diopter_delta": diopter_delta,
        "diopter_descent_frame": descent_frame,

        "baseline_frame_start": b1,
        "baseline_frame_end": b2,
        "miosis_frame_start": m1,
        "miosis_frame_end": m2,

        "pupil_left_baseline":   Lb_mean,
        "pupil_right_baseline":  Rb_mean,
        "pupil_both_baseline":  Bb_mean,

        "pupil_left_miosis_mean":   Lm_mean,
        "pupil_right_miosis_mean": Rm_mean,
        "pupil_both_miosis_mean":  Bm_mean,

        "pupil_left_miosis_min":  Lm_min,
        "pupil_right_miosis_min": Rm_min,
        "pupil_both_miosis_min":   Bm_min,

        "pupil_left_miosis_min_frame": Lm_min_frame,
        "pupil_right_miosis_min_frame": Rm_min_frame,
        "pupil_both_miosis_min_frame": Bm_min_frame,

        "pupil_left_change_rate_mean":  _chg(Lb_mean, Lm_mean),
        "pupil_right_change_rate_mean": _chg(Rb_mean, Rm_mean),
        "pupil_both_change_rate_mean":   _chg(Bb_mean, Bm_mean),

        "pupil_left_change_rate_min":  _chg(Lb_mean, Lm_min),
        "pupil_right_change_rate_min": _chg(Rb_mean, Rm_min),
        "pupil_both_change_rate_min":   _chg(Bb_mean, Bm_min),
    }


# ============================================================
# 可視化（連結：4段縦）
# ============================================================
def plot_tasks_concat_4stack(
    df_log: pd.DataFrame,
    emr_df: pd.DataFrame,
    out_png: str,
    gap_frames: int = 10,
    show:  bool = False,
    only_valid: bool = True,
    pre_onset_frames: int = 240,
):
    """
    横軸：対象タスク区間だけを順番に連結した擬似index
    縦：左/右/平均/diopter を 4段
    baseline と miosis を違う色で塗る
    ★追加：onset(緑の縦線) の pre_onset_frames 前まで遡って描画
    """
    df = df_log.copy()
    if only_valid and "Skip_Task" in df.columns:
        df = df[df["Skip_Task"] == False]. copy()
    df = df.reset_index(drop=True)
    if len(df) == 0:
        raise RuntimeError("描画対象タスクがありません（Skip_Taskを確認）")

    x_all = emr_df["emr_frame_rel"].to_numpy(dtype=int)
    L_all = emr_df["emr_left_pupil_mm"].to_numpy(dtype=float)
    R_all = emr_df["emr_right_pupil_mm"].to_numpy(dtype=float)
    B_all = emr_df["emr_both_pupil_mm"].to_numpy(dtype=float)
    D_all = emr_df["emr_diopter_clipped0"].to_numpy(dtype=float)

    fig, axes = plt.subplots(4, 1, figsize=(16, 10), sharex=True)
    axL, axR, axB, axD = axes

    Xs, Ls, Rs, Bs, Ds = [], [], [], [], []
    spans_task, spans_base, spans_mio = [], [], []
    vlines_onset = []
    x_offset = 0

    emr_min_f = int(x_all[0])
    emr_max_f = int(x_all[-1])

    for i in range(len(df)):
        ts = df.loc[i, "task_start_frame_emr"]
        te = df.loc[i, "task_end_frame_emr"]
        b1 = df.loc[i, "baseline_frame_start"]
        b2 = df.loc[i, "baseline_frame_end"]
        m1 = df.loc[i, "miosis_frame_start"]
        m2 = df.loc[i, "miosis_frame_end"]
        onset = df.loc[i, "diopter_onset_frame"]

        if not (np.isfinite(ts) and np.isfinite(te) and np.isfinite(b1) and np.isfinite(b2)
                and np.isfinite(m1) and np.isfinite(m2) and np.isfinite(onset)):
            continue
        ts, te, b1, b2, m1, m2, onset = int(ts), int(te), int(b1), int(b2), int(m1), int(m2), int(onset)

        plot_start = max(emr_min_f, onset - int(pre_onset_frames))
        plot_end = min(te, emr_max_f)
        if plot_end < plot_start:
            continue

        mask = (x_all >= plot_start) & (x_all <= plot_end)
        if not np.any(mask):
            continue

        xt = x_all[mask]
        Lt = L_all[mask]
        Rt = R_all[mask]
        Bt = B_all[mask]
        Dt = D_all[mask]

        local_n = len(xt)
        x_local = np.arange(local_n, dtype=int) + x_offset

        Xs.append(x_local); Ls.append(Lt); Rs.append(Rt); Bs.append(Bt); Ds.append(Dt)

        def _frame_to_local(f):
            j = int(np.searchsorted(xt, f))
            j = int(np.clip(j, 0, local_n - 1))
            if j > 0 and abs(xt[j] - f) > abs(xt[j-1] - f):
                j -= 1
            return int(j)

        jts = _frame_to_local(ts)
        jte = _frame_to_local(te)
        spans_task.append((x_local[jts], x_local[jte]))

        jb1, jb2 = _frame_to_local(b1), _frame_to_local(b2)
        jm1, jm2 = _frame_to_local(m1), _frame_to_local(m2)
        spans_base.append((x_local[jb1], x_local[jb2]))
        spans_mio.append((x_local[jm1], x_local[jm2]))

        jon = _frame_to_local(onset)
        vlines_onset.append(x_local[jon])

        x_offset = int(x_local[-1]) + 1 + int(gap_frames)

    if len(Xs) == 0:
        raise RuntimeError("描画できるタスクがありません（windowがNaN等）")

    X = np.concatenate(Xs)
    L = np.concatenate(Ls)
    R = np.concatenate(Rs)
    B = np.concatenate(Bs)
    D = np.concatenate(Ds)

    axL.plot(X, L, linewidth=1.0)
    axR.plot(X, R, linewidth=1.0)
    axB.plot(X, B, linewidth=1.6)
    axD.plot(X, D, linewidth=1.2)

    axL.set_ylabel("Left pupil [mm]")
    axR.set_ylabel("Right pupil [mm]")
    axB.set_ylabel("Both pupil [mm]")
    axD.set_ylabel("Diopter [D]")
    axD.set_xlabel("Concatenated frames (pseudo index)")

    for (s, e) in spans_task:
        for ax in axes:
            ax.axvspan(s, e, color="#888888", alpha=0.08, linewidth=0)
    # for (s, e) in spans_base:
    #     for ax in axes:
    #         ax.axvspan(s, e, color="#2ca02c", alpha=0.22, linewidth=0)
    for (s, e) in spans_base:
        for ax in axes:
            ax.axvline(s, color="#1f77b4", alpha=0.6, linewidth=1.0, linestyle='--')
    for (s, e) in spans_mio:
        for ax in axes:
            ax.axvspan(s, e, color="#d62728", alpha=0.18, linewidth=0)

    for xv in vlines_onset:
        for ax in axes:
            ax. axvline(xv, color="#2ca02c", alpha=0.85, linewidth=1.2)

    fig.suptitle(f"Concatenated (4-stack): onset=green line / baseline start=blue line / miosis=red span (pre_onset={pre_onset_frames}f)")
    fig.tight_layout()
    _ensure_dir_for_file(out_png)
    fig.savefig(out_png, dpi=200)

    if show:
        pass
    else:
        plt. close(fig)

    valid_df = df_log. copy()
    if "Skip_Task" in valid_df.columns:
        valid_df = valid_df[valid_df["Skip_Task"] == False]. copy()
    return len(valid_df)


# ============================================================
# 可視化（4×16 グリッド）★必ずfrontが数字の16個を使用
# ============================================================
def plot_tasks_grid_4x16_digit_only(
    df_log: pd.DataFrame,
    emr_df: pd.DataFrame,
    out_png: str,
    show: bool = False,
    pre_onset_frames: int = 240,
):
    """
    ★必ずfrontが数字のタスク16個を選択して4×16グリッド描画
    ★ディオプターが取れなかったタスクは空白
    ★ログが16個未満の場合は白紙で「log_insufficient」ファイル名
    """
    # ★frontが数字のタスクのみ抽出
    df_digit = df_log[df_log["FrontIsDigit_inferred"] == True].copy()
    df_digit = df_digit.reset_index(drop=True)

    n_digit = len(df_digit)

    # ★ログが16個未満の場合：白紙PNG生成
    if n_digit < 16:
        fig, ax = plt.subplots(figsize=(16, 10))
        ax.text(0.5, 0.5, f"Insufficient digit tasks:  {n_digit}/16",
                ha='center', va='center', fontsize=20, color='red')
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)
        ax.axis('off')

        # ファイル名を変更
        out_dir = os.path.dirname(out_png)
        base = os.path.splitext(os.path.basename(out_png))[0]
        out_png_insufficient = os.path.join(out_dir, f"{base}_log_insufficient_{n_digit}of16.png")

        _ensure_dir_for_file(out_png_insufficient)
        fig.savefig(out_png_insufficient, dpi=200)
        plt.close(fig)

        print(f"[WARNING] Insufficient digit tasks ({n_digit}/16), saved blank:  {out_png_insufficient}")
        return 0

    # ★先頭16個のfrontが数字のタスクを使用
    df = df_digit.iloc[:16].copy()

    # ★タイトル用の情報を取得
    base_name = os.path.splitext(os.path.basename(out_png))[0]
    # ファイル名から被験者番号とタスク番号を抽出（例：S08_3_grid_4x16）
    import re
    match = re.search(r'(S\d+)_(\d+)', base_name)
    if match:
        subject_id = match.group(1)
        task_num = match.group(2)
        title_str = f"{subject_id}_Set{task_num}_grid_4×16"
    else:
        title_str = f"{base_name}_grid_4×16"

    x_all = emr_df["emr_frame_rel"].to_numpy(dtype=int)
    emr_min_f = int(x_all[0])
    emr_max_f = int(x_all[-1])

    fig, axes = plt.subplots(4, 16, figsize=(40, 10), sharey="row")

    valid_count = 0  # ★実際に描画されたタスク数

    for i in range(16):
        # ★Skip_Task == True または必要な列がNaNなら空白
        skip = df.loc[i, "Skip_Task"] if "Skip_Task" in df.columns else True
        skip_reason = df.loc[i, "Skip_Reason"] if "Skip_Reason" in df.columns else "unknown"

        ts = df.loc[i, "task_start_frame_emr"]
        te = df.loc[i, "task_end_frame_emr"]
        b1 = df.loc[i, "baseline_frame_start"]
        b2 = df. loc[i, "baseline_frame_end"]
        m1 = df.loc[i, "miosis_frame_start"]
        m2 = df.loc[i, "miosis_frame_end"]
        onset = df.loc[i, "diopter_onset_frame"]

        # ★スキップ判定とダミープロット用のフラグ
        has_onset = np.isfinite(onset)
        has_windows = np.isfinite(b1) and np.isfinite(b2) and np.isfinite(m1) and np.isfinite(m2)
        can_plot = np.isfinite(ts) and np.isfinite(te)

        # ★完全にデータがない場合のみテキスト表示
        if skip or not can_plot:
            reason_lines = skip_reason.replace('_', '\n')
            for r in range(4):
                axes[r, i].text(0.5, 0.5, reason_lines, ha='center', va='center',
                               fontsize=6, color='red', multialignment='center', transform=axes[r, i].transAxes)
                # ★x軸目盛りのみ非表示、y軸はsharey="row"で自動管理
                axes[r, i].set_xticks([])
                # ★左端列以外はy軸目盛りを非表示
                if i > 0:
                    axes[r, i].tick_params(labelleft=False)
            continue

        ts, te = int(ts), int(te)

        # ★onsetがある場合はその前から、ない場合はタスク開始から描画
        if has_onset:
            onset = int(onset)
            plot_start = max(emr_min_f, onset - int(pre_onset_frames))
        else:
            plot_start = max(emr_min_f, ts - int(pre_onset_frames))

        plot_end = min(te, emr_max_f)

        if plot_end < plot_start:
            for r in range(4):
                axes[r, i].set_axis_off()
            continue

        mask = (x_all >= plot_start) & (x_all <= plot_end)
        if not np.any(mask):
            for r in range(4):
                axes[r, i]. set_axis_off()
            continue

        seg = emr_df.loc[mask]. copy()
        x = seg["emr_frame_rel"]. to_numpy(dtype=int)
        xr = x - x[0]
        x0 = int(x[0])

        L = seg["emr_left_pupil_mm"].to_numpy(dtype=float)
        R = seg["emr_right_pupil_mm"].to_numpy(dtype=float)
        B = seg["emr_both_pupil_mm"].to_numpy(dtype=float)
        D = seg["emr_diopter_clipped0"].to_numpy(dtype=float)

        # ★診断情報：データ点数とフレーム範囲
        n_frames = len(xr)
        frame_range = int(plot_end - plot_start) if plot_end > plot_start else 0

        # ★相対座標計算（onsetがない場合はNaNのまま）
        rts, rte = ts - x0, te - x0
        if has_windows:
            b1, b2, m1, m2 = int(b1), int(b2), int(m1), int(m2)
            rb1, rb2 = b1 - x0, b2 - x0
            rm1, rm2 = m1 - x0, m2 - x0
        if has_onset:
            ron = onset - x0

        # descent_frame取得
        descent_frame = df.loc[i, "diopter_descent_frame"] if "diopter_descent_frame" in df.columns else np.nan
        has_descent = np.isfinite(descent_frame)
        if has_descent:
            rdescent = int(descent_frame) - x0

        axes[0, i].plot(xr, L, linewidth=1.0)
        axes[1, i].plot(xr, R, linewidth=1.0)
        axes[2, i].plot(xr, B, linewidth=1.6)
        axes[3, i].plot(xr, D, linewidth=1.2)

        # ★★★ 計算したフレームと値をマーカーでプロット ★★★
        # diopter peak (オレンジ星マーク) - diopterグラフ
        diopter_peak_frame = df.loc[i, "diopter_peak_frame"] if "diopter_peak_frame" in df.columns else np.nan
        diopter_peak_value = df.loc[i, "diopter_peak_value"] if "diopter_peak_value" in df.columns else np.nan
        if np.isfinite(diopter_peak_frame) and np.isfinite(diopter_peak_value):
            rpeak = int(diopter_peak_frame) - x0
            if 0 <= rpeak < len(xr):
                axes[3, i].scatter([rpeak], [diopter_peak_value], marker='*', s=120,
                                   color='orange', edgecolors='darkorange', linewidths=1.5,
                                   zorder=10, label='Diopter Peak')

        # pupil baseline (青い四角) - 瞳孔グラフ
        pupil_left_baseline = df.loc[i, "pupil_left_baseline"] if "pupil_left_baseline" in df.columns else np.nan
        pupil_right_baseline = df.loc[i, "pupil_right_baseline"] if "pupil_right_baseline" in df.columns else np.nan
        pupil_both_baseline = df.loc[i, "pupil_both_baseline"] if "pupil_both_baseline" in df.columns else np.nan
        if has_windows:
            # baselineの中央フレームに表示
            baseline_mid = (rb1 + rb2) // 2
            if np.isfinite(pupil_left_baseline):
                axes[0, i].scatter([baseline_mid], [pupil_left_baseline], marker='s', s=60,
                                   color='blue', edgecolors='darkblue', linewidths=1.0,
                                   zorder=10, label='Baseline')
            if np.isfinite(pupil_right_baseline):
                axes[1, i].scatter([baseline_mid], [pupil_right_baseline], marker='s', s=60,
                                   color='blue', edgecolors='darkblue', linewidths=1.0,
                                   zorder=10)
            if np.isfinite(pupil_both_baseline):
                axes[2, i].scatter([baseline_mid], [pupil_both_baseline], marker='s', s=60,
                                   color='blue', edgecolors='darkblue', linewidths=1.0,
                                   zorder=10)

        # pupil minimum (赤い三角) - 瞳孔グラフ（保存された最小値フレームを使用）
        pupil_left_min = df.loc[i, "pupil_left_miosis_min"] if "pupil_left_miosis_min" in df.columns else np.nan
        pupil_right_min = df.loc[i, "pupil_right_miosis_min"] if "pupil_right_miosis_min" in df.columns else np.nan
        pupil_both_min = df.loc[i, "pupil_both_miosis_min"] if "pupil_both_miosis_min" in df.columns else np.nan

        # 保存された最小値フレームを取得
        left_min_frame = df.loc[i, "pupil_left_miosis_min_frame"] if "pupil_left_miosis_min_frame" in df.columns else np.nan
        right_min_frame = df.loc[i, "pupil_right_miosis_min_frame"] if "pupil_right_miosis_min_frame" in df.columns else np.nan
        both_min_frame = df.loc[i, "pupil_both_miosis_min_frame"] if "pupil_both_miosis_min_frame" in df.columns else np.nan

        # Left pupil
        if np.isfinite(pupil_left_min) and np.isfinite(left_min_frame):
            r_min_frame = int(left_min_frame) - x0  # 相対フレームに変換
            if r_min_frame >= 0 and r_min_frame <= max(xr):
                axes[0, i].scatter([r_min_frame], [pupil_left_min], marker='v', s=20,
                                   color='red', edgecolors='darkred', linewidths=1.0,
                                   zorder=10, label='Min')

        # Right pupil
        if np.isfinite(pupil_right_min) and np.isfinite(right_min_frame):
            r_min_frame = int(right_min_frame) - x0
            if r_min_frame >= 0 and r_min_frame <= max(xr):
                axes[1, i].scatter([r_min_frame], [pupil_right_min], marker='v', s=20,
                                   color='red', edgecolors='darkred', linewidths=1.0,
                                   zorder=10)

        # Both pupil
        if np.isfinite(pupil_both_min) and np.isfinite(both_min_frame):
            r_min_frame = int(both_min_frame) - x0
            if r_min_frame >= 0 and r_min_frame <= max(xr):
                axes[2, i].scatter([r_min_frame], [pupil_both_min], marker='v', s=20,
                                   color='red', edgecolors='darkred', linewidths=1.0,
                                   zorder=10)

        for r in range(4):
            axes[r, i].axvspan(rts, rte, color="#888888", alpha=0.08, linewidth=0)
            if has_windows:
                # baseline開始線（青破線）
                axes[r, i].axvline(rb1, color="#1f77b4", alpha=0.6, linewidth=1.0, linestyle='--')
            # ★タスク開始位置を青い縦線で表示
            axes[r, i].axvline(rts, color="#1f77b4", alpha=0.5, linewidth=1.0, linestyle='--', label='Task Start')
            # ★onset位置を緑の縦線で表示（onsetがある場合のみ）
            if has_onset:
                axes[r, i].axvline(ron, color="#2ca02c", alpha=0.85, linewidth=1.2, label='Onset')
            # ★descent位置をピンクの縦線で表示（descentがある場合のみ）
            if has_descent:
                axes[r, i].axvline(rdescent, color="#d62728", alpha=0.85, linewidth=1.2, label='Descent')
            # ★左端列以外はy軸ラベルを非表示
            if i > 0:
                axes[r, i].tick_params(labelleft=False)

        # ★メトリクス情報をタイトルに追加
        d_delta = df.loc[i, "diopter_delta"] if "diopter_delta" in df.columns else np.nan
        d_baseline = df.loc[i, "diopter_baseline"] if "diopter_baseline" in df.columns else np.nan
        d_peak = df.loc[i, "diopter_peak_value"] if "diopter_peak_value" in df.columns else np.nan
        pupil_chg = df.loc[i, "pupil_both_change_rate_mean"] if "pupil_both_change_rate_mean" in df.columns else np.nan

        # ★診断：onsetとタスク開始の距離（onsetがある場合のみ）
        onset_delay = ron - rts if has_onset else np.nan

        # ★診断：実際のディオプター値の範囲を確認
        D_valid = D[np.isfinite(D) & (D > 0)]
        d_min = float(np.min(D_valid)) if len(D_valid) > 0 else 0.0
        d_max = float(np.max(D_valid)) if len(D_valid) > 0 else 0.0
        d_range = d_max - d_min
        d_zero_count = int(np.sum(D == 0))
        d_zero_pct = (d_zero_count / len(D) * 100) if len(D) > 0 else 0.0

        # ★診断：瞳孔径の範囲
        B_valid = B[np.isfinite(B)]
        b_min = float(np.min(B_valid)) if len(B_valid) > 0 else 0.0
        b_max = float(np.max(B_valid)) if len(B_valid) > 0 else 0.0
        b_range = b_max - b_min
        b_nan_pct = (np.sum(~np.isfinite(B)) / len(B) * 100) if len(B) > 0 else 0.0

        # ★診断：相対座標のwindow位置
        if has_onset:
            onset_rel = ron
        else:
            onset_rel = "NA"
        if has_windows:
            baseline_rel = f"{rb1}-{rb2}"
            miosis_rel = f"{rm1}-{rm2}"
        else:
            baseline_rel = "NA"
            miosis_rel = "NA"

        title_text = f"T{i+1}"
        title_color = 'black'

        # タイトルを設定（1行のみ）
        axes[0, i].set_title(title_text, fontsize=15, color=title_color, ha='center')

    # ★縦軸ラベル設定（一番左の列のみ）
    axes[0, 0].set_ylabel("Left pupil [mm]", fontsize=8)
    axes[1, 0].set_ylabel("Right pupil [mm]", fontsize=8)
    axes[2, 0].set_ylabel("Both pupil [mm]", fontsize=8)
    axes[3, 0].set_ylabel("Diopter [D]", fontsize=8)

    fig.suptitle(title_str, fontsize=12, y=0.995)
    fig.tight_layout(rect=[0, 0, 1, 0.99])
    fig.savefig(out_png, dpi=200)

    if show:
        pass
    else:
        plt.close(fig)

    return valid_count


# ============================================================
# メイン
# ============================================================
# ============================================================
# メイン（全ファイル自動生成版 + 一桁は0埋め）
# ============================================================
def main():
    ap = argparse.ArgumentParser()

    DEFAULT_SAVE_DIR = "../../data/task_windows"
    DEFAULT_OUT_ROOT = "../../data/log_with_emr_metrics"

    ap.add_argument("--save_dir", default=DEFAULT_SAVE_DIR)
    ap.add_argument("--out_root", default=DEFAULT_OUT_ROOT)
    ap.add_argument("--emr_fps", type=int, default=120, choices=[60, 120])
    ap.add_argument("--digit_col", default=None)
    ap.add_argument("--front_col", default=None)
    ap.add_argument("--diopter_min", type=float, default=1.5)
    ap.add_argument("--diopter_max", type=float, default=10.0)
    ap.add_argument("--pupil_min", type=float, default=1.0)
    ap.add_argument("--pupil_max", type=float, default=10.0)
    ap.add_argument("--task_sec", type=float, default=2.5)
    ap.add_argument("--onset_search_sec", type=float, default=1.0)
    ap.add_argument("--onset_delta_d", type=float, default=0.2)
    ap.add_argument("--peak_search_sec", type=float, default=2.0)
    ap.add_argument("--baseline_frames", type=int, default=120)  # 120f = 1.0秒 (120fpsの場合)
    ap.add_argument("--baseline_mode", type=str, default="stim", choices=["onset", "stim"],
                    help="Baseline window: 'onset'=onset直前, 'stim'=刺激開始120f前")
    ap.add_argument("--miosis_lag_sec", type=float, default=0.0)
    ap.add_argument("--miosis_frames", type=int, default=100)
    ap.add_argument("--diopter_increase_min_d", type=float, default=0.3)
    ap.add_argument("--make_concat", action="store_true")
    ap.add_argument("--make_grid", action="store_true", default=True)
    ap.add_argument("--no_make_grid", action="store_true")
    ap.add_argument("--show_plots", action="store_true")
    ap.add_argument("--pre_onset_frames", type=int, default=240)#240

    args = ap.parse_args()

    # ★パラメータに基づいて出力フォルダとファイル名サフィックスを生成
    # Miosisパラメータ
    lag_str = f"lag{args.miosis_lag_sec:.1f}".replace(".", "p")
    mio_frames_str = f"mioF{args.miosis_frames}"

    # Baselineパラメータ
    baseline_str = f"BL{args.baseline_mode}{args.baseline_frames}"

    # その他の重要パラメータ
    onset_delta_str = f"onD{args.onset_delta_d:.1f}".replace(".", "p")
    diopter_min_str = f"dMin{args.diopter_increase_min_d:.1f}".replace(".", "p")

    # 日付を取得（YYYYMMDD形式）
    from datetime import datetime
    date_str = datetime.now().strftime("%Y%m%d")

    # フォルダ用サフィックス（主要パラメータのみ）+ マーカー付き表記 + 日付
    folder_suffix = f"{lag_str}_{mio_frames_str}_{baseline_str}_markers_{date_str}"

    # ファイル名用サフィックス（全パラメータ）
    file_suffix = f"{lag_str}_{mio_frames_str}_{baseline_str}_{onset_delta_str}_{diopter_min_str}"

    args.out_root = os.path.join(args.out_root, folder_suffix)
    args.save_dir = os.path.join(args.save_dir, folder_suffix)
    args.params_suffix = file_suffix  # ファイル名用に保存

    print(f"[INFO] === パラメータ設定 ===")
    print(f"[INFO] 出力フォルダ: {args.out_root}")
    print(f"[INFO] グラフフォルダ: {args.save_dir}")
    print(f"[INFO] ファイルサフィックス: {file_suffix}")
    print(f"[INFO] miosis: lag={args.miosis_lag_sec}s, frames={args.miosis_frames}")
    print(f"[INFO] baseline: mode={args.baseline_mode}, frames={args.baseline_frames}")
    print(f"[INFO] thresholds: onset_delta={args.onset_delta_d}, diopter_min={args.diopter_increase_min_d}")
    print(f"[INFO] ========================")

    # ★全ファイル自動処理
    configs = []

    # Bright:  S01～S15, セグメント0～9 (★被験者ごとにtask_sec変更)
    for s in range(1, 20):
        for seg in range(0, 10):
            configs.append(("Bright", s, seg))

    # Dark: S101～S119, セグメント0～9
    for s in range(101, 120):
        for seg in range(0, 10):
            configs.append(("Dark", s, seg))

    for env, subject_num, task_num in tqdm(configs, desc="Processing files"):
        # ★一桁の場合は0埋め（S01, S02, ... ）
        subject_id = f"S{subject_num:02d}" if subject_num < 100 else f"S{subject_num}"

        log_csv = f"../../log/{env}/{subject_id}/{subject_id}_{task_num}.csv"
        emr_csv = f"../../data/devided_emr/{subject_num}/{task_num}.csv"

        # ファイルが存在しない場合はスキップ
        if not os.path.exists(log_csv) or not os.path.exists(emr_csv):
            print(f"[SKIP] {env} {subject_id} seg={task_num}: ファイルが見つかりません")
            continue

        # ★Bright条件で被験者ごとにtask_secを設定
        if env == "Bright":
            if subject_num == 1:
                args.task_sec = 5.0
            elif 2 <= subject_num <= 4:
                args.task_sec = 3.75
            else:
                args.task_sec = 2.5  # デフォルト
        else:
            args.task_sec = 2.5  # Dark条件はデフォルト

        # print(f"\n[PROCESSING] {env} {subject_id} seg={task_num} (task_sec={args.task_sec}s)")

        try:
            process_single_file(
                log_csv=log_csv,
                emr_csv=emr_csv,
                args=args,
            )
        except Exception as e:
            print(f"[ERROR] {env} {subject_id} seg={task_num}: {e}")
            continue

    print("\n[COMPLETE] 全ファイル処理完了")

    # ★メトリクスの統合処理 (旧 4_integrate_metrics.py)
    merge_outputs(args.out_root)


def process_single_file(log_csv, emr_csv, args):
    """1ファイル分の処理"""
    cond = infer_condition_from_path(log_csv)
    subj = infer_subject_from_path(log_csv)
    base = os.path.splitext(os.path. basename(log_csv))[0]
    # パラメータ情報をファイル名に含める
    out_csv = os.path.join(args.out_root, cond, subj, f"{base}_metrics_{args.params_suffix}.csv")

    df_log = pd.read_csv(log_csv, encoding="utf-8-sig")

    frame_col = pick_frame_col(df_log, args. emr_fps)
    df_log[frame_col] = pd.to_numeric(df_log[frame_col], errors="coerce")
    df_log = df_log.dropna(subset=[frame_col]).copy()
    df_log[frame_col] = df_log[frame_col].astype("int64")

    digit_mask = infer_digit_mask(df_log, digit_col=args. digit_col, front_col=args.front_col)
    df_log["FrontIsDigit_inferred"] = digit_mask. astype(bool)

    emr_df = load_emr_with_diopter(
        emr_csv,
        diopter_min=args. diopter_min,
        diopter_max=args. diopter_max,
        pupil_min_mm=args.pupil_min,
        pupil_max_mm=args.pupil_max,
    )
    emr_df["emr_frame_rel"] = pd.to_numeric(emr_df["emr_frame_rel"], errors="coerce").astype("int64")
    emr_df = emr_df.dropna(subset=["emr_frame_rel"]).sort_values("emr_frame_rel").reset_index(drop=True)

    new_cols = [
        "Skip_Task", "Skip_Reason",
        "task_start_frame_emr", "task_end_frame_emr",
        "diopter_baseline", "diopter_onset_frame", "diopter_peak_frame", "diopter_peak_value", "diopter_delta", "diopter_descent_frame",
        "baseline_frame_start", "baseline_frame_end",
        "miosis_frame_start", "miosis_frame_end",
        "pupil_left_baseline", "pupil_right_baseline", "pupil_both_baseline",
        "pupil_left_miosis_mean", "pupil_right_miosis_mean", "pupil_both_miosis_mean",
        "pupil_left_miosis_min", "pupil_right_miosis_min", "pupil_both_miosis_min",
        "pupil_left_miosis_min_frame", "pupil_right_miosis_min_frame", "pupil_both_miosis_min_frame",
        "pupil_left_change_rate_mean", "pupil_right_change_rate_mean", "pupil_both_change_rate_mean",
        "pupil_left_change_rate_min", "pupil_right_change_rate_min", "pupil_both_change_rate_min",
    ]
    for c in new_cols:
        if c not in df_log.columns:
            df_log[c] = np. nan
    df_log["Skip_Task"] = True
    df_log["Skip_Reason"] = ""

    for idx in range(len(df_log)):
        stim_frame = int(df_log.loc[idx, frame_col])

        if not bool(df_log.loc[idx, "FrontIsDigit_inferred"]):
            df_log.loc[idx, "Skip_Task"] = True
            df_log.loc[idx, "Skip_Reason"] = "front_not_digit"
            continue

        res = compute_task_windows_and_metrics_auto(
            emr_df=emr_df,
            stim_frame=stim_frame,
            emr_fps=args.emr_fps,
            task_sec=args.task_sec,
            onset_search_sec=args.onset_search_sec,
            onset_delta_d=args.onset_delta_d,
            peak_search_sec=args.peak_search_sec,
            baseline_frames=args.baseline_frames,
            miosis_lag_sec=args. miosis_lag_sec,
            miosis_frames=args. miosis_frames,
            diopter_increase_min_d=args.diopter_increase_min_d,
            baseline_mode=args.baseline_mode,
        )

        for k, v in res.items():
            df_log.loc[idx, k] = v

    _ensure_dir_for_file(out_csv)
    df_log.to_csv(out_csv, index=False, encoding="utf-8-sig")
    # print(f"  [OK] saved: {out_csv}")

    out_dir = os.path.join(args.save_dir, cond, subj)
    _ensure_dir(out_dir)

    if args.make_concat:
        concat_png = os.path.join(out_dir, f"{base}_concat_4stack. png")
        plot_tasks_concat_4stack(
            df_log=df_log,
            emr_df=emr_df,
            out_png=concat_png,
            gap_frames=10,
            show=args.show_plots,
            only_valid=True,
            pre_onset_frames=args.pre_onset_frames,
        )
        print(f"  [OK] saved plot: {concat_png}")

    if args.make_grid:
        grid_png = os.path.join(out_dir, f"{base}_grid_4x16.png")
        n_actual = plot_tasks_grid_4x16_digit_only(
            df_log=df_log,
            emr_df=emr_df,
            out_png=grid_png,
            show=args.show_plots,
            pre_onset_frames=args.pre_onset_frames,
        )
        if n_actual > 0:
            grid_png_renamed = os.path. join(out_dir, f"{base}_grid_4x16_valid{n_actual}.png")
            if grid_png != grid_png_renamed and os.path.exists(grid_png):
                os.rename(grid_png, grid_png_renamed)
                print(f"  [OK] saved plot:  {grid_png_renamed}")


def merge_outputs(out_root):
    """
    out_root 下の Bright/*/*.csv と Dark/*/*.csv を収集して、
    out_root/merged/ に統合 Excel を作成する。
    """
    print(f"\n[INFO] メトリクスの統合を開始します... (Source: {out_root})")

    merged_dir = os.path.join(out_root, "merged")
    os.makedirs(merged_dir, exist_ok=True)

    def subject_folder_name(path: str) -> str:
        return os.path.basename(os.path.dirname(path))

    def integrate_and_save(env):
        files = glob.glob(os.path.join(out_root, env, "*", "*.csv"))
        if not files:
            print(f"  [WARN] {env} の CSV が見つかりません。スキップします。")
            return

        dfs = []
        subjects = set()
        for f in files:
            dfs.append(pd.read_csv(f, encoding="utf-8-sig"))
            subjects.add(subject_folder_name(f))

        df_all = pd.concat(dfs, ignore_index=True)
        n_subs = len(subjects)
        out_path = os.path.join(merged_dir, f"integrated_{env.lower()}_metrics_n{n_subs}.xlsx")

        try:
            with pd.ExcelWriter(out_path, engine="openpyxl") as writer:
                df_all.to_excel(writer, index=False, sheet_name=env)
            print(f"  [OK] {env}: {len(files)} files, {n_subs} subjects -> {out_path}")
        except Exception as e:
            print(f"  [ERROR] {env} の統合保存に失敗しました: {e}")

    integrate_and_save("Bright")
    integrate_and_save("Dark")


if __name__ == "__main__":
    main()
