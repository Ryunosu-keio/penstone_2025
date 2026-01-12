# -*- coding: utf-8 -*-
"""
emr_task_windows_addpupil_and_plots.py
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
    baseline区間とmiosis区間を“違う色”でハイライト
    ★追加：diopter立ち上がり(onset)の 240フレーム前まで遡って描画（緑の縦線=onset）
(2) グリッドビュー：4×N（N=対象タスク数）で各タスクを並べる（必要なら）
    ★同様に onset-240 まで遡って描画

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
# ユーティリティ
# ============================================================
def _must_have(df: pd.DataFrame, cols, name="df"):
    missing = [c for c in cols if c not in df.columns]
    if missing:
        raise RuntimeError(f"{name} に必須列がありません: {missing}\n現在の列: {df.columns.tolist()}")

def _ensure_dir(path: str):
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

def infer_digit_mask(df_log: pd.DataFrame, digit_col: str | None = None, front_col: str | None = None) -> pd.Series:
    """
    frontが数字かどうかの判定（柔軟に）
    優先: digit_col が存在すればそれを使う
    次点: front_col を文字列として isdigit
    それでも無理なら「常にTrue」にしないで False 返す（安全側）
    """
    if digit_col and digit_col in df_log.columns:
        s = df_log[digit_col]
        if s.dtype == bool:
            return s.fillna(False)
        v = pd.to_numeric(s, errors="coerce")
        if v.notna().any():
            return (v.fillna(0).astype(float) != 0)
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
    diopter_max: float,
    pupil_min_mm: float,
    pupil_max_mm: float,
) -> pd.DataFrame:
    df = pd.read_csv(emr_csv)
    _must_have(df, ["番号", "左眼.瞳孔径[mm]", "右眼.瞳孔径[mm]", "両眼.注視Z座標[mm]"], name="EMR")

    for c in ["番号", "左眼.瞳孔径[mm]", "右眼.瞳孔径[mm]", "両眼.注視Z座標[mm]"]:
        df[c] = pd.to_numeric(df[c], errors="coerce")

    start_num = df["番号"].iloc[0]
    df["emr_frame_rel"] = (df["番号"] - start_num).astype("int64")

    df["emr_left_pupil_mm_raw"]  = df["左眼.瞳孔径[mm]"]
    df["emr_right_pupil_mm_raw"] = df["右眼.瞳孔径[mm]"]
    df["emr_both_pupil_mm_raw"]  = (df["emr_left_pupil_mm_raw"] + df["emr_right_pupil_mm_raw"]) / 2.0

    def _clip_nan(s, lo, hi):
        x = pd.to_numeric(s, errors="coerce").astype(float)
        return x.where((x >= float(lo)) & (x <= float(hi)), np.nan)

    df["emr_left_pupil_mm"]  = _clip_nan(df["emr_left_pupil_mm_raw"],  pupil_min_mm, pupil_max_mm)
    df["emr_right_pupil_mm"] = _clip_nan(df["emr_right_pupil_mm_raw"], pupil_min_mm, pupil_max_mm)
    df["emr_both_pupil_mm"]  = (df["emr_left_pupil_mm"] + df["emr_right_pupil_mm"]) / 2.0

    z = pd.to_numeric(df["両眼.注視Z座標[mm]"], errors="coerce").astype(float)
    diop = np.where((z > 0) & np.isfinite(z), 1000.0 / z, np.nan)
    diop = pd.Series(diop, index=df.index).astype(float)

    diop0 = diop.where((diop >= float(diopter_min)) & (diop <= float(diopter_max)), 0.0)

    df["emr_diopter_raw"] = diop
    df["emr_diopter_clipped0"] = diop0

    out_cols = [
        "emr_frame_rel",
        "emr_left_pupil_mm", "emr_right_pupil_mm", "emr_both_pupil_mm",
        "emr_diopter_raw", "emr_diopter_clipped0",
    ]
    return df[out_cols].sort_values("emr_frame_rel").reset_index(drop=True)


# ============================================================
# タスク1件：window決定 + 指標計算（自動）
# ============================================================
def compute_task_windows_and_metrics_auto(
    emr_df: pd.DataFrame,
    stim_frame: int,
    emr_fps: int,
    task_sec: float,

    onset_search_sec: float,
    onset_delta_d: float,

    peak_search_sec: float,

    baseline_frames: int,
    miosis_lag_sec: float,
    miosis_frames: int,

    diopter_increase_min_d: float,
):
    x = emr_df["emr_frame_rel"].to_numpy(dtype=int)
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

    base_d_candidates = seg_onset_d[: min(10, len(seg_onset_d))]
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
            "task_start_frame_emr": task_start,
            "task_end_frame_emr": task_end,
            "diopter_baseline": baseline_diopter,
            "diopter_onset_frame": onset_frame,
            "diopter_peak_frame": peak_frame,
            "diopter_peak_value": peak_value,
            "diopter_delta": diopter_delta,
        }

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

    lag_frames = int(round(float(miosis_lag_sec) * emr_fps))
    m1 = peak_frame + lag_frames
    m2 = m1 + int(miosis_frames) - 1
    if m2 > task_end:
        return {
            "Skip_Task": True, "Skip_Reason": "miosis_window_out_of_task",
            "task_start_frame_emr": task_start,
            "task_end_frame_emr": task_end,
            "diopter_baseline": baseline_diopter,
            "diopter_onset_frame": onset_frame,
            "diopter_peak_frame": peak_frame,
            "diopter_peak_value": peak_value,
            "diopter_delta": diopter_delta,
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

    Lb = _win_vals(left,  b1, b2)
    Rb = _win_vals(right, b1, b2)
    Bb = _win_vals(both,  b1, b2)

    Lm = _win_vals(left,  m1, m2)
    Rm = _win_vals(right, m1, m2)
    Bm = _win_vals(both,  m1, m2)

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
        "Skip_Task": False,
        "Skip_Reason": "",

        "task_start_frame_emr": task_start,
        "task_end_frame_emr": task_end,

        "diopter_baseline": baseline_diopter,
        "diopter_onset_frame": onset_frame,
        "diopter_peak_frame": peak_frame,
        "diopter_peak_value": peak_value,
        "diopter_delta": diopter_delta,

        "baseline_frame_start": b1,
        "baseline_frame_end": b2,
        "miosis_frame_start": m1,
        "miosis_frame_end": m2,

        "pupil_left_baseline":  Lb_mean,
        "pupil_right_baseline": Rb_mean,
        "pupil_both_baseline":  Bb_mean,

        "pupil_left_miosis_mean":  Lm_mean,
        "pupil_right_miosis_mean": Rm_mean,
        "pupil_both_miosis_mean":  Bm_mean,

        "pupil_left_miosis_min":  Lm_min,
        "pupil_right_miosis_min": Rm_min,
        "pupil_both_miosis_min":  Bm_min,

        "pupil_left_change_rate_mean":  _chg(Lb_mean, Lm_mean),
        "pupil_right_change_rate_mean": _chg(Rb_mean, Rm_mean),
        "pupil_both_change_rate_mean":  _chg(Bb_mean, Bm_mean),

        "pupil_left_change_rate_min":  _chg(Lb_mean, Lm_min),
        "pupil_right_change_rate_min": _chg(Rb_mean, Rm_min),
        "pupil_both_change_rate_min":  _chg(Bb_mean, Bm_min),
    }


# ============================================================
# 可視化（連結：4段縦）
# ============================================================
def plot_tasks_concat_4stack(
    df_log: pd.DataFrame,
    emr_df: pd.DataFrame,
    out_png: str,
    gap_frames: int = 10,
    show: bool = False,
    only_valid: bool = True,
    pre_onset_frames: int = 240,   # ★追加
):
    """
    横軸：対象タスク区間だけを順番に連結した擬似index
    縦：左/右/平均/diopter を 4段
    baseline と miosis を違う色で塗る
    ★追加：onset(緑の縦線) の pre_onset_frames 前まで遡って描画
    """
    df = df_log.copy()
    if only_valid and "Skip_Task" in df.columns:
        df = df[df["Skip_Task"] == False].copy()
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
    vlines_onset = []  # ★追加：onset縦線位置（連結軸上）
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
        onset = df.loc[i, "diopter_onset_frame"]  # ★追加

        if not (np.isfinite(ts) and np.isfinite(te) and np.isfinite(b1) and np.isfinite(b2)
                and np.isfinite(m1) and np.isfinite(m2) and np.isfinite(onset)):
            continue
        ts, te, b1, b2, m1, m2, onset = int(ts), int(te), int(b1), int(b2), int(m1), int(m2), int(onset)

        # ★描画開始：onset - 240（EMR範囲にクランプ）
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

        # ★task span（灰）は「本来のタスク開始ts〜te」だけ塗る（pre区間は塗らない）
        jts = _frame_to_local(ts)
        jte = _frame_to_local(te)
        spans_task.append((x_local[jts], x_local[jte]))

        jb1, jb2 = _frame_to_local(b1), _frame_to_local(b2)
        jm1, jm2 = _frame_to_local(m1), _frame_to_local(m2)
        spans_base.append((x_local[jb1], x_local[jb2]))
        spans_mio.append((x_local[jm1], x_local[jm2]))

        # ★onset縦線
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

    # task（薄い灰）、baseline（緑）、miosis（赤）
    for (s, e) in spans_task:
        for ax in axes:
            ax.axvspan(s, e, color="#888888", alpha=0.08, linewidth=0)
    for (s, e) in spans_base:
        for ax in axes:
            ax.axvspan(s, e, color="#2ca02c", alpha=0.22, linewidth=0)
    for (s, e) in spans_mio:
        for ax in axes:
            ax.axvspan(s, e, color="#d62728", alpha=0.18, linewidth=0)

    # ★onset（緑の縦線）
    for xv in vlines_onset:
        for ax in axes:
            ax.axvline(xv, color="#2ca02c", alpha=0.85, linewidth=1.2)

    fig.suptitle(f"Concatenated (4-stack): onset=green line / baseline=green span / miosis=red span (pre_onset={pre_onset_frames}f)")
    fig.tight_layout()
    _ensure_dir_for_file(out_png)
    fig.savefig(out_png, dpi=200)

    if show:
        # display commented out
        pass
    else:
        plt.close(fig)

    # ★実際に描画されたタスク数を返す（4×N ではなく 4×16 なため）
    # df.を使ってValid タスク数を返す
    valid_df = df_log.copy()
    if "Skip_Task" in valid_df.columns:
        valid_df = valid_df[valid_df["Skip_Task"] == False].copy()
    return len(valid_df)


# ============================================================
# 可視化（4×N グリッド）
# ============================================================
def plot_tasks_grid_4xN(
    df_log: pd.DataFrame,
    emr_df: pd.DataFrame,
    out_png: str,
    show: bool = False,
    only_valid: bool = True,
    max_tasks: int | None = None,
    pre_onset_frames: int = 240,   # ★追加
):
    """
    4×16 グリッドを常に作成。実際に描画されたタスク数を返す。
    """
    df = df_log.copy()
    if only_valid and "Skip_Task" in df.columns:
        df = df[df["Skip_Task"] == False].copy()
    df = df.reset_index(drop=True)

    # ★常に 4×16 に固定
    N = 16
    # 実際のタスク数は len(df) だが、16個まで描画（足りなければ空白）
    actual_count = len(df)

    x_all = emr_df["emr_frame_rel"].to_numpy(dtype=int)
    emr_min_f = int(x_all[0])
    emr_max_f = int(x_all[-1])

    fig, axes = plt.subplots(4, N, figsize=(max(16, 2.4*N), 10), sharey="row")
    if N == 1:
        axes = np.array(axes).reshape(4, 1)

    for i in range(N):
        # ★タスクがない場合（i >= len(df)）は空白
        if i >= len(df):
            for r in range(4):
                axes[r, i].set_axis_off()
            continue

        ts = df.loc[i, "task_start_frame_emr"]
        te = df.loc[i, "task_end_frame_emr"]
        b1 = df.loc[i, "baseline_frame_start"]
        b2 = df.loc[i, "baseline_frame_end"]
        m1 = df.loc[i, "miosis_frame_start"]
        m2 = df.loc[i, "miosis_frame_end"]
        onset = df.loc[i, "diopter_onset_frame"]  # ★追加

        if not (np.isfinite(ts) and np.isfinite(te) and np.isfinite(b1) and np.isfinite(b2)
                and np.isfinite(m1) and np.isfinite(m2) and np.isfinite(onset)):
            for r in range(4):
                axes[r, i].set_axis_off()
            continue

        ts, te, b1, b2, m1, m2, onset = int(ts), int(te), int(b1), int(b2), int(m1), int(m2), int(onset)

        # ★描画開始：onset - 240（EMR範囲にクランプ）
        plot_start = max(emr_min_f, onset - int(pre_onset_frames))
        plot_end = min(te, emr_max_f)
        if plot_end < plot_start:
            for r in range(4):
                axes[r, i].set_axis_off()
            continue

        mask = (x_all >= plot_start) & (x_all <= plot_end)
        if not np.any(mask):
            for r in range(4):
                axes[r, i].set_axis_off()
            continue

        seg = emr_df.loc[mask].copy()
        x = seg["emr_frame_rel"].to_numpy(dtype=int)
        xr = x - x[0]  # 描画区間内相対
        x0 = int(x[0])  # = plot_start 近辺

        L = seg["emr_left_pupil_mm"].to_numpy(dtype=float)
        R = seg["emr_right_pupil_mm"].to_numpy(dtype=float)
        B = seg["emr_both_pupil_mm"].to_numpy(dtype=float)
        D = seg["emr_diopter_clipped0"].to_numpy(dtype=float)

        rb1, rb2 = b1 - x0, b2 - x0
        rm1, rm2 = m1 - x0, m2 - x0
        rts, rte = ts - x0, te - x0
        ron = onset - x0

        axes[0, i].plot(xr, L, linewidth=1.0)
        axes[1, i].plot(xr, R, linewidth=1.0)
        axes[2, i].plot(xr, B, linewidth=1.6)
        axes[3, i].plot(xr, D, linewidth=1.2)

        # ★task灰（本来のts〜te）
        for r in range(4):
            axes[r, i].axvspan(rts, rte, color="#888888", alpha=0.08, linewidth=0)

        # baseline / miosis
        for r in range(4):
            axes[r, i].axvspan(rb1, rb2, color="#2ca02c", alpha=0.22, linewidth=0)
            axes[r, i].axvspan(rm1, rm2, color="#d62728", alpha=0.18, linewidth=0)

        # ★onset（緑の縦線）
        for r in range(4):
            axes[r, i].axvline(ron, color="#2ca02c", alpha=0.85, linewidth=1.2)

        axes[0, i].set_title(f"Task {i}")
        axes[3, i].set_xlabel("frames (rel)")

    axes[0, 0].set_ylabel("Left [mm]")
    axes[1, 0].set_ylabel("Right [mm]")
    axes[2, 0].set_ylabel("Both [mm]")
    axes[3, 0].set_ylabel("Diopter [D]")

    fig.suptitle(f"Per-task grid (4×16, {actual_count} tasks): onset=green line / baseline=green span / miosis=red span (pre_onset={pre_onset_frames}f)")
    fig.tight_layout()
    _ensure_dir_for_file(out_png)
    fig.savefig(out_png, dpi=200)

    if show:
        # display commented out
        pass
    else:
        plt.close(fig)

    # ★実際に描画されたタスク数を返す
    return actual_count


# ============================================================
# メイン
# ============================================================
def main():
    ap = argparse.ArgumentParser()

    # ★ デフォルト（自分の環境に合わせてここだけ直せば、引数なしで動く）r
    env = input("環境を選択してください (Bright:1 Dark:2): ")
    if env == "1":
        env = "Bright"
    elif env == "2":
        env = "Dark"
    else:
        raise RuntimeError("環境は 1 (Bright) または 2 (Dark) を入力してください。")
    subject_num = int(input("被験者ID数字部分を入力（例: 107）: "))
    subject_id = f"S{subject_num}"

    task_num = int(input("タスク番号を入力（例: 0）: "))
    DEFAULT_LOG_CSV = f"../../log/{env}/{subject_id}/{subject_id}_{task_num}.csv"
    DEFAULT_EMR_CSV = f"../../data/devided_emr/{subject_num}/{task_num}.csv"
    DEFAULT_SAVE_DIR = "../../data/graphs/task_windows"
    DEFAULT_OUT_ROOT = "../../data/integrated_2025"   # 好きな場所にしてOK

    ap.add_argument("--log_csv", default=DEFAULT_LOG_CSV,
                    help="experiment_main_display.py のログCSV（1行=1タスク想定）")
    ap.add_argument("--emr_csv", default=DEFAULT_EMR_CSV,
                    help="devided_emr の1セグメントCSV")


    ap.add_argument("--out_root", default=DEFAULT_OUT_ROOT,
                    help="out_csv を省略したときの出力ルート（log配下に出さない）")
    ap.add_argument("--out_csv", default=None,
                    help="出力CSV（未指定なら out_root/条件/被験者/ に自動生成）")

    ap.add_argument("--save_dir", default=DEFAULT_SAVE_DIR, help="プロット保存ルート")
    ap.add_argument("--emr_fps", type=int, default=120, choices=[60, 120])

    ap.add_argument("--digit_col", default=None, help="frontが数字かどうかの列名（True/False or 0/1）。無ければ推定。")
    ap.add_argument("--front_col", default=None, help="front文字（数字判定に使う）。無ければ推定。")

    ap.add_argument("--diopter_min", type=float, default=1.5)
    ap.add_argument("--diopter_max", type=float, default=10.0)

    ap.add_argument("--pupil_min", type=float, default=1.0)
    ap.add_argument("--pupil_max", type=float, default=10.0)

    ap.add_argument("--task_sec", type=float, default=2.5, help="1タスクの秒数（stimから何秒分を対象にするか）")

    ap.add_argument("--onset_search_sec", type=float, default=1.0)
    ap.add_argument("--onset_delta_d", type=float, default=0.2)
    ap.add_argument("--peak_search_sec", type=float, default=2.0)

    ap.add_argument("--baseline_frames", type=int, default=10)
    ap.add_argument("--miosis_lag_sec", type=float, default=0.5)
    ap.add_argument("--miosis_frames", type=int, default=10)

    ap.add_argument("--diopter_increase_min_d", type=float, default=0.3)

    ap.add_argument("--make_concat", action="store_true", help="連結ビューを作る")
    ap.add_argument("--make_grid", action="store_true",default=True,help="4×Nビューを作る")
    ap.add_argument("--show_plots", action="store_true", help="画面にも表示（保存もする）")

    ap.add_argument("--pre_onset_frames", type=int, default=240, help="onset(緑線)の何フレーム前まで遡って描画するか")

    args = ap.parse_args()

    # ★ out_csv 未指定なら、log_csv と同じ場所に自動生成
    # ★ out_csv 未指定なら out_root 側に保存（log配下に出さない）
    if args.out_csv is None or str(args.out_csv).strip() == "":
        cond = infer_condition_from_path(args.log_csv)      # Bright/Dark/Unknown
        subj = infer_subject_from_path(args.log_csv)        # S107 等 / UnknownSubject
        base = os.path.splitext(os.path.basename(args.log_csv))[0]
        args.out_csv = os.path.join(args.out_root, cond, subj, f"{base}_with_emr_metrics.csv")



    df_log = pd.read_csv(args.log_csv, encoding="utf-8-sig")

    frame_col = pick_frame_col(df_log, args.emr_fps)
    df_log[frame_col] = pd.to_numeric(df_log[frame_col], errors="coerce")
    df_log = df_log.dropna(subset=[frame_col]).copy()
    df_log[frame_col] = df_log[frame_col].astype("int64")

    digit_mask = infer_digit_mask(df_log, digit_col=args.digit_col, front_col=args.front_col)
    df_log["FrontIsDigit_inferred"] = digit_mask.astype(bool)

    emr_df = load_emr_with_diopter(
        args.emr_csv,
        diopter_min=args.diopter_min,
        diopter_max=args.diopter_max,
        pupil_min_mm=args.pupil_min,
        pupil_max_mm=args.pupil_max,
    )
    emr_df["emr_frame_rel"] = pd.to_numeric(emr_df["emr_frame_rel"], errors="coerce").astype("int64")
    emr_df = emr_df.dropna(subset=["emr_frame_rel"]).sort_values("emr_frame_rel").reset_index(drop=True)

    new_cols = [
        "Skip_Task", "Skip_Reason",
        "task_start_frame_emr", "task_end_frame_emr",
        "diopter_baseline", "diopter_onset_frame", "diopter_peak_frame", "diopter_peak_value", "diopter_delta",
        "baseline_frame_start", "baseline_frame_end",
        "miosis_frame_start", "miosis_frame_end",
        "pupil_left_baseline", "pupil_right_baseline", "pupil_both_baseline",
        "pupil_left_miosis_mean", "pupil_right_miosis_mean", "pupil_both_miosis_mean",
        "pupil_left_miosis_min", "pupil_right_miosis_min", "pupil_both_miosis_min",
        "pupil_left_change_rate_mean", "pupil_right_change_rate_mean", "pupil_both_change_rate_mean",
        "pupil_left_change_rate_min", "pupil_right_change_rate_min", "pupil_both_change_rate_min",
    ]
    for c in new_cols:
        if c not in df_log.columns:
            df_log[c] = np.nan
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
            miosis_lag_sec=args.miosis_lag_sec,
            miosis_frames=args.miosis_frames,
            diopter_increase_min_d=args.diopter_increase_min_d,
        )

        for k, v in res.items():
            df_log.loc[idx, k] = v

    _ensure_dir_for_file(args.out_csv)
    df_log.to_csv(args.out_csv, index=False, encoding="utf-8-sig")
    print("[OK] saved:", args.out_csv)

    cond = infer_condition_from_path(args.log_csv)
    subj = infer_subject_from_path(args.log_csv)
    base = os.path.splitext(os.path.basename(args.log_csv))[0]
    out_dir = os.path.join(args.save_dir, cond, subj, base)
    _ensure_dir(out_dir)

    if args.make_concat:
        concat_png = os.path.join(out_dir, f"{base}_concat_4stack.png")
        plot_tasks_concat_4stack(
            df_log=df_log,
            emr_df=emr_df,
            out_png=concat_png,
            gap_frames=10,
            show=args.show_plots,
            only_valid=True,
            pre_onset_frames=args.pre_onset_frames,   # ★追加
        )
        print("[OK] saved plot:", concat_png)

    if args.make_grid:
        grid_png = os.path.join(out_dir, f"{base}_grid_4xN.png")
        n_actual = plot_tasks_grid_4xN(
            df_log=df_log,
            emr_df=emr_df,
            out_png=grid_png,
            show=args.show_plots,
            only_valid=True,
            pre_onset_frames=args.pre_onset_frames,   # ★追加
        )
        # ★ファイル名にN数を反映
        grid_png_renamed = os.path.join(out_dir, f"{base}_grid_4x{n_actual}.png")
        if grid_png != grid_png_renamed:
            os.rename(grid_png, grid_png_renamed)
            print(f"[OK] saved plot (renamed): {grid_png_renamed}")
        else:
            print("[OK] saved plot:", grid_png)

    n_total = len(df_log)
    n_valid = int(np.sum((df_log["Skip_Task"] == False).astype(int)))
    print(f"[INFO] valid tasks (digit & diopter-rise): {n_valid}/{n_total}")


if __name__ == "__main__":
    main()
