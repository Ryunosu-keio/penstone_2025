# -*- coding: utf-8 -*-
"""
add_emr_to_experiment_log_5s_with_pupil_metrics.py
--------------------------------------------------
5秒間隔の実験ログCSV（experiment_main_display.pyの出力）に、
EMRセグメントCSV（devided_emrの1セグメント）をフレームで突合して列追加し、
さらに「diopter立ち上がりがあった試行だけ」瞳孔ベースライン/縮瞳値/変化率を計算する。

要件（あなたの指定）:
- ディオプターが増えなかったタスクは飛ばす（Skip）
- グラフには「対象ディオプターフレーム内の瞳孔」を色付け
- 計算: 左右/平均の瞳孔径
    - baseline（diopter立ち上がり前の数フレーム）
    - miosis（diopter最大値の後の数フレーム：遅れて縮瞳する想定）
    - 変化率（baseline→miosis）

依存:
  pip install pandas numpy matplotlib

使い方例:
  python add_emr_to_experiment_log_5s_with_pupil_metrics.py ^
    --log_csv "../../log/Bright/S06/S06_1.csv" ^
    --emr_csv "../../data/devided_emr/6/1.csv" ^
    --out_csv "../../data/integrated_2025/Bright/S06/S06_1_with_emr_metrics.csv" ^
    --save_dir "../../data/graphs/pupil_miosis_marked" ^
    --emr_fps 120

注意:
- 実験ログ側には Frame_60fps / Frame_120fps のどちらかが必要
- EMR側は「番号」「左眼.瞳孔径[mm]」「右眼.瞳孔径[mm]」「両眼.注視Z座標[mm]」が必要
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


# ============================================================
# EMR 読み込み（あなたのコード思想に寄せる：範囲外は0）
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

    # 相対フレーム
    start_num = df["番号"].iloc[0]
    df["emr_frame_rel"] = df["番号"] - start_num

    # pupil
    df["emr_left_pupil_mm_raw"]  = df["左眼.瞳孔径[mm]"]
    df["emr_right_pupil_mm_raw"] = df["右眼.瞳孔径[mm]"]
    df["emr_both_pupil_mm_raw"]  = (df["emr_left_pupil_mm_raw"] + df["emr_right_pupil_mm_raw"]) / 2.0

    # 物理レンジ外は NaN（瞳孔は0化しないほうが後処理が安定）
    def _clip_nan(s, lo, hi):
        x = pd.to_numeric(s, errors="coerce").astype(float)
        return x.where((x >= float(lo)) & (x <= float(hi)), np.nan)

    df["emr_left_pupil_mm"]  = _clip_nan(df["emr_left_pupil_mm_raw"],  pupil_min_mm, pupil_max_mm)
    df["emr_right_pupil_mm"] = _clip_nan(df["emr_right_pupil_mm_raw"], pupil_min_mm, pupil_max_mm)
    df["emr_both_pupil_mm"]  = (df["emr_left_pupil_mm"] + df["emr_right_pupil_mm"]) / 2.0

    # diopter = 1000/Z
    z = pd.to_numeric(df["両眼.注視Z座標[mm]"], errors="coerce").astype(float)
    diop = np.where((z > 0) & np.isfinite(z), 1000.0 / z, np.nan)
    diop = pd.Series(diop, index=df.index).astype(float)

    # あなたの元コード思想：範囲外は 0
    diop0 = diop.where((diop >= float(diopter_min)) & (diop <= float(diopter_max)), 0.0)

    df["emr_diopter_raw"] = diop
    df["emr_diopter_clipped0"] = diop0

    out_cols = [
        "emr_frame_rel",
        "emr_left_pupil_mm_raw", "emr_right_pupil_mm_raw", "emr_both_pupil_mm_raw",
        "emr_left_pupil_mm", "emr_right_pupil_mm", "emr_both_pupil_mm",
        "emr_diopter_raw", "emr_diopter_clipped0",
    ]
    return df[out_cols].sort_values("emr_frame_rel").reset_index(drop=True)


# ============================================================
# 1試行ごとの diopter 立ち上がり/ピーク + 瞳孔ベースライン/縮瞳計算
# ============================================================
def compute_trial_metrics(
    emr_df: pd.DataFrame,
    stim_frame: int,
    emr_fps: int,
    # onset検出
    onset_search_sec: float,
    onset_delta_d: float,
    # diopterピーク探索
    peak_search_sec: float,
    # baseline window（onset直前）
    baseline_frames: int,
    # miosis window（peak後の遅れを考慮）
    miosis_lag_sec: float,
    miosis_frames: int,
    # diopterが「増えた」判定
    diopter_increase_min_d: float,
):
    """
    returns:
      dict (metrics), and a dict for plotting windows
    """

    # EMR配列
    x = emr_df["emr_frame_rel"].values.astype(int)
    diop0 = emr_df["emr_diopter_clipped0"].values.astype(float)

    # stim_frame が EMR の範囲内か
    if stim_frame < int(x[0]) or stim_frame > int(x[-1]):
        return None, None

    # search window indices
    onset_search_frames = max(1, int(round(onset_search_sec * emr_fps)))
    peak_search_frames  = max(1, int(round(peak_search_sec  * emr_fps)))

    # stim_frame に最も近い index
    i0 = int(np.searchsorted(x, stim_frame))
    if i0 > 0 and abs(x[i0] - stim_frame) > abs(x[i0 - 1] - stim_frame):
        i0 -= 1
    i0 = int(np.clip(i0, 0, len(x) - 1))

    # 解析対象の diopter 列（stim 以降）
    i_onset_end = min(len(x), i0 + onset_search_frames)
    seg_onset_x = x[i0:i_onset_end]
    seg_onset_d = diop0[i0:i_onset_end]

    # onset: 「最初の非ゼロ」 + 「その直前の基準より onset_delta 以上」
    # baseline_diopter は onset探索区間の最初の数フレームで推定（0を除外）
    base_d_candidates = seg_onset_d[: min(10, len(seg_onset_d))]
    base_d_candidates = base_d_candidates[base_d_candidates > 0]
    baseline_diopter = float(np.median(base_d_candidates)) if len(base_d_candidates) else 0.0

    onset_frame = None
    for xf, dv in zip(seg_onset_x, seg_onset_d):
        if dv > 0 and (dv - baseline_diopter) >= float(onset_delta_d):
            onset_frame = int(xf)
            break

    if onset_frame is None:
        # diopter立ち上がりなし
        return None, None

    # peak (stimからpeak_search_sec)
    i_peak_end = min(len(x), i0 + peak_search_frames)
    seg_peak_x = x[i0:i_peak_end]
    seg_peak_d = diop0[i0:i_peak_end]

    if len(seg_peak_d) == 0:
        return None, None

    peak_idx_rel = int(np.argmax(seg_peak_d))
    peak_frame = int(seg_peak_x[peak_idx_rel])
    peak_value = float(seg_peak_d[peak_idx_rel])

    # diopter increase 判定（baseline_diopterから）
    diopter_delta = peak_value - baseline_diopter
    if not np.isfinite(diopter_delta) or diopter_delta < float(diopter_increase_min_d):
        # 「増えなかった」扱いでスキップ
        return {
            "diopter_baseline": baseline_diopter,
            "diopter_onset_frame": onset_frame,
            "diopter_peak_frame": peak_frame,
            "diopter_peak_value": peak_value,
            "diopter_delta": diopter_delta,
            "skip_reason": "diopter_increase_too_small",
        }, {
            "stim_frame": stim_frame,
            "onset_frame": onset_frame,
            "peak_frame": peak_frame,
            "baseline_win": None,
            "miosis_win": None,
        }

    # --- pupil windows ---
    # baseline: onset直前 baseline_frames
    b1 = max(int(x[0]), onset_frame - int(baseline_frames))
    b2 = onset_frame - 1
    if b2 < b1:
        # baseline window取れない
        return {
            "diopter_baseline": baseline_diopter,
            "diopter_onset_frame": onset_frame,
            "diopter_peak_frame": peak_frame,
            "diopter_peak_value": peak_value,
            "diopter_delta": diopter_delta,
            "skip_reason": "baseline_window_missing",
        }, {
            "stim_frame": stim_frame,
            "onset_frame": onset_frame,
            "peak_frame": peak_frame,
            "baseline_win": None,
            "miosis_win": None,
        }

    # miosis: peak後 miosis_lag_sec 遅らせてから miosis_frames
    lag_frames = int(round(float(miosis_lag_sec) * emr_fps))
    m1 = peak_frame + lag_frames
    m2 = m1 + int(miosis_frames) - 1
    if m2 > int(x[-1]):
        # miosis windowがEMR範囲外
        return {
            "diopter_baseline": baseline_diopter,
            "diopter_onset_frame": onset_frame,
            "diopter_peak_frame": peak_frame,
            "diopter_peak_value": peak_value,
            "diopter_delta": diopter_delta,
            "skip_reason": "miosis_window_out_of_range",
        }, {
            "stim_frame": stim_frame,
            "onset_frame": onset_frame,
            "peak_frame": peak_frame,
            "baseline_win": (b1, b2),
            "miosis_win": None,
        }

    # pupil series
    left  = emr_df["emr_left_pupil_mm"].values.astype(float)
    right = emr_df["emr_right_pupil_mm"].values.astype(float)
    both  = emr_df["emr_both_pupil_mm"].values.astype(float)

    # frame -> index slice helper（xは連番想定だが、念のためマスク）
    def _win_vals(series, f1, f2):
        m = (x >= int(f1)) & (x <= int(f2))
        v = series[m]
        v = v[np.isfinite(v)]
        return v

    # baseline pupil
    Lb = _win_vals(left,  b1, b2)
    Rb = _win_vals(right, b1, b2)
    Bb = _win_vals(both,  b1, b2)

    # miosis pupil（平均＋最小も取る）
    Lm = _win_vals(left,  m1, m2)
    Rm = _win_vals(right, m1, m2)
    Bm = _win_vals(both,  m1, m2)

    def _mean_or_nan(v): return float(np.mean(v)) if len(v) else np.nan
    def _min_or_nan(v):  return float(np.min(v))  if len(v) else np.nan

    Lb_mean, Rb_mean, Bb_mean = _mean_or_nan(Lb), _mean_or_nan(Rb), _mean_or_nan(Bb)
    Lm_mean, Rm_mean, Bm_mean = _mean_or_nan(Lm), _mean_or_nan(Rm), _mean_or_nan(Bm)

    Lm_min, Rm_min, Bm_min = _min_or_nan(Lm), _min_or_nan(Rm), _min_or_nan(Bm)

    # change rate（baselineがNaN/0ならNaN）
    def _chg(b, m):
        if (not np.isfinite(b)) or b <= 0 or (not np.isfinite(m)):
            return np.nan
        return float((b - m) / b)

    out = {
        "diopter_baseline": baseline_diopter,
        "diopter_onset_frame": onset_frame,
        "diopter_peak_frame": peak_frame,
        "diopter_peak_value": peak_value,
        "diopter_delta": diopter_delta,

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

        "skip_reason": "",
    }

    plot_meta = {
        "stim_frame": stim_frame,
        "onset_frame": onset_frame,
        "peak_frame": peak_frame,
        "baseline_win": (b1, b2),
        "miosis_win": (m1, m2),
    }
    return out, plot_meta


# ============================================================
# 可視化（対象試行だけ、diopter窓内の瞳孔を色付け）
# ============================================================
def plot_trial(
    emr_df: pd.DataFrame,
    plot_meta: dict,
    out_png: str,
    pad_left_sec: float,
    pad_right_sec: float,
    emr_fps: int,
    show: bool,
):
    x = emr_df["emr_frame_rel"].values.astype(int)
    diop = emr_df["emr_diopter_clipped0"].values.astype(float)
    L = emr_df["emr_left_pupil_mm"].values.astype(float)
    R = emr_df["emr_right_pupil_mm"].values.astype(float)
    B = emr_df["emr_both_pupil_mm"].values.astype(float)

    stim = int(plot_meta["stim_frame"])
    onset = int(plot_meta["onset_frame"])
    peak = int(plot_meta["peak_frame"])

    # 表示範囲（onset～miosisをちゃんと含む）
    bwin = plot_meta.get("baseline_win", None)
    mwin = plot_meta.get("miosis_win", None)

    if mwin is not None:
        right_anchor = mwin[1]
    else:
        right_anchor = peak

    x0 = max(int(x[0]), int(onset - round(pad_left_sec * emr_fps)))
    x1 = min(int(x[-1]), int(right_anchor + round(pad_right_sec * emr_fps)))

    m = (x >= x0) & (x <= x1)

    fig, ax1 = plt.subplots(figsize=(14, 6))
    ax2 = ax1.twinx()

    # pupil (left/right/both)
    ax1.plot(x[m], L[m], linewidth=1.0, label="Left pupil [mm]")
    ax1.plot(x[m], R[m], linewidth=1.0, label="Right pupil [mm]")
    ax1.plot(x[m], B[m], linewidth=2.0, label="Both pupil [mm]")

    # diopter
    ax2.plot(x[m], diop[m], linewidth=1.5, label="Diopter [D]")

    # 縦線：stim / onset / peak
    ax1.axvline(stim, linewidth=1.0, alpha=0.6)
    ax1.axvline(onset, linewidth=1.2, alpha=0.8)
    ax1.axvline(peak, linewidth=1.2, alpha=0.8)

    # 色付け（baseline window / miosis window）
    # ※ axvspan で範囲を薄く塗る（色指定は必要なら変えてOK）
    if bwin is not None:
        ax1.axvspan(bwin[0], bwin[1], alpha=0.18)
    if mwin is not None:
        ax1.axvspan(mwin[0], mwin[1], alpha=0.18)

    ax1.set_xlim(x0, x1)
    ax1.set_xlabel("EMR frame (rel)")
    ax1.set_ylabel("Pupil diameter [mm]")
    ax2.set_ylabel("Diopter [D]")

    ax1.set_title(f"Trial window: stim={stim}, onset={onset}, peak={peak}  xlim={x0}-{x1}")

    # 凡例（左右2軸）
    h1, l1 = ax1.get_legend_handles_labels()
    h2, l2 = ax2.get_legend_handles_labels()
    ax1.legend(h1 + h2, l1 + l2, loc="upper right")

    plt.tight_layout()
    _ensure_dir_for_file(out_png)
    plt.savefig(out_png, dpi=200)

    if show:
        plt.show()
    else:
        plt.close(fig)


# ============================================================
# メイン：ログにEMR列＋メトリクス列追加して保存
# ============================================================
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--log_csv",  help="experiment_main_display.py のログCSV",default="../../log/Bright/S07/S07_0.csv")
    ap.add_argument("--emr_csv",  help="devided_emr の1セグメントCSV",default="../../data/devided_emr/S07/1.csv")
    ap.add_argument("--out_csv",  help="出力CSV（列追加後）",default="../../data/integrated_2025/Bright/S07/S07_0_with_emr_metrics.csv")
    ap.add_argument("--save_dir", default="./plots_pupil_miosis", help="プロット保存ルート")
    ap.add_argument("--emr_fps", type=int, default=120, choices=[60, 120])

    # diopter範囲（あなたの辞書ベースでここは人ごとに変えたい場合がある）
    ap.add_argument("--diopter_min", type=float, default=1.5)
    ap.add_argument("--diopter_max", type=float, default=10.0)

    # pupilレンジ
    ap.add_argument("--pupil_min", type=float, default=1.0)
    ap.add_argument("--pupil_max", type=float, default=10.0)

    # onset/peak detection
    ap.add_argument("--onset_search_sec", type=float, default=1.0, help="stim後どれだけ探すか（立ち上がり検出）")
    ap.add_argument("--onset_delta_d", type=float, default=0.2, help="baseline diopterから何D上がったらonset扱いか")
    ap.add_argument("--peak_search_sec", type=float, default=2.0, help="stim後どれだけ探すか（peak検出）")

    # baseline/miosis window
    ap.add_argument("--baseline_frames", type=int, default=10, help="onset直前のベースライン窓（フレーム）")
    ap.add_argument("--miosis_lag_sec", type=float, default=0.5, help="peakの後、縮瞳が遅れる分の遅延秒")
    ap.add_argument("--miosis_frames", type=int, default=10, help="縮瞳値を取る窓（フレーム）")

    # skip判定
    ap.add_argument("--diopter_increase_min_d", type=float, default=0.3, help="diopter増加がこれ未満ならskip")

    # plotting
    ap.add_argument("--plot_pad_left_sec", type=float, default=1.0)
    ap.add_argument("--plot_pad_right_sec", type=float, default=2.0)
    ap.add_argument("--show_plots", action="store_true", help="画面にも出す")

    args = ap.parse_args()

    # 読み込み
    df_log = pd.read_csv(args.log_csv, encoding="utf-8-sig")
    frame_col = pick_frame_col(df_log, args.emr_fps)

    # フレーム列整形
    df_log[frame_col] = pd.to_numeric(df_log[frame_col], errors="coerce")
    df_log = df_log.dropna(subset=[frame_col]).copy()
    df_log[frame_col] = df_log[frame_col].astype(int)

    # EMRロード
    emr_df = load_emr_with_diopter(
        args.emr_csv,
        diopter_min=args.diopter_min,
        diopter_max=args.diopter_max,
        pupil_min_mm=args.pupil_min,
        pupil_max_mm=args.pupil_max,
    )
    # --- merge_asof 前にキーdtypeを揃える（超重要）---
    df_log[frame_col] = pd.to_numeric(df_log[frame_col], errors="coerce").astype("int64")

    emr_df["emr_frame_rel"] = pd.to_numeric(emr_df["emr_frame_rel"], errors="coerce").astype("int64")

    # 念のため sort（merge_asof 必須）
    df_log = df_log.dropna(subset=[frame_col]).sort_values(frame_col).reset_index(drop=True)
    emr_df = emr_df.dropna(subset=["emr_frame_rel"]).sort_values("emr_frame_rel").reset_index(drop=True)

    # merge_asof（最寄りフレームを付ける：参照用）
    # ここで emr_frame_rel / pupil / diopter の「そのフレーム値」をログに付与
    merged = pd.merge_asof(
        df_log.sort_values(frame_col).reset_index(drop=True),
        emr_df.sort_values("emr_frame_rel"),
        left_on=frame_col,
        right_on="emr_frame_rel",
        direction="nearest",
        tolerance=2,  # だいたい±2フレームまで
    )

    # 追加列（メトリクス）
    metric_cols = [
        "Skip_Diopter",
        "Skip_Reason",
        "diopter_baseline", "diopter_onset_frame", "diopter_peak_frame", "diopter_peak_value", "diopter_delta",
        "pupil_left_baseline", "pupil_right_baseline", "pupil_both_baseline",
        "pupil_left_miosis_mean", "pupil_right_miosis_mean", "pupil_both_miosis_mean",
        "pupil_left_miosis_min", "pupil_right_miosis_min", "pupil_both_miosis_min",
        "pupil_left_change_rate_mean", "pupil_right_change_rate_mean", "pupil_both_change_rate_mean",
        "pupil_left_change_rate_min", "pupil_right_change_rate_min", "pupil_both_change_rate_min",
    ]
    for c in metric_cols:
        merged[c] = np.nan
    merged["Skip_Diopter"] = False
    merged["Skip_Reason"] = ""

    # 保存先ディレクトリ（ログ名から振り分け）
    cond = infer_condition_from_path(args.log_csv)
    subj = infer_subject_from_path(args.log_csv)
    base = os.path.splitext(os.path.basename(args.log_csv))[0]
    plot_dir = os.path.join(args.save_dir, cond, subj, base)
    _ensure_dir(plot_dir)

    print("=======================================")
    print("[INFO] log_csv :", args.log_csv)
    print("[INFO] emr_csv :", args.emr_csv)
    print("[INFO] out_csv :", args.out_csv)
    print("[INFO] frame_col used :", frame_col)
    print("[INFO] plots saved to :", plot_dir)
    print("=======================================")

    # 各試行で計算
    for idx in range(len(merged)):
        stim_frame = int(merged.loc[idx, frame_col])

        metrics, plot_meta = compute_trial_metrics(
            emr_df=emr_df,
            stim_frame=stim_frame,
            emr_fps=args.emr_fps,
            onset_search_sec=args.onset_search_sec,
            onset_delta_d=args.onset_delta_d,
            peak_search_sec=args.peak_search_sec,
            baseline_frames=args.baseline_frames,
            miosis_lag_sec=args.miosis_lag_sec,
            miosis_frames=args.miosis_frames,
            diopter_increase_min_d=args.diopter_increase_min_d,
        )

        if metrics is None and plot_meta is None:
            merged.loc[idx, "Skip_Diopter"] = True
            merged.loc[idx, "Skip_Reason"] = "no_diopter_onset"
            continue

        # metrics はあるが skip_reason が入ってる場合（増えてない、窓がない等）
        skip_reason = metrics.get("skip_reason", "")
        if skip_reason:
            merged.loc[idx, "Skip_Diopter"] = True
            merged.loc[idx, "Skip_Reason"] = skip_reason
            # 参考として diopter系だけ入れる（あとはNaNのまま）
            for k in ["diopter_baseline", "diopter_onset_frame", "diopter_peak_frame", "diopter_peak_value", "diopter_delta"]:
                if k in metrics:
                    merged.loc[idx, k] = metrics[k]
            continue

        # 通常ケース：全て入れる
        merged.loc[idx, "Skip_Diopter"] = False
        merged.loc[idx, "Skip_Reason"] = ""
        for k, v in metrics.items():
            if k == "skip_reason":
                continue
            merged.loc[idx, k] = v

        # 対象試行だけプロット保存
        out_png = os.path.join(plot_dir, f"trial_{idx:03d}_stim{stim_frame}.png")
        plot_trial(
            emr_df=emr_df,
            plot_meta=plot_meta,
            out_png=out_png,
            pad_left_sec=args.plot_pad_left_sec,
            pad_right_sec=args.plot_pad_right_sec,
            emr_fps=args.emr_fps,
            show=args.show_plots,
        )

    # 保存
    _ensure_dir_for_file(args.out_csv)
    merged.to_csv(args.out_csv, index=False, encoding="utf-8-sig")
    print(f"[OK] saved out_csv: {args.out_csv}")

    # どのくらい skip されたか
    n_total = len(merged)
    n_skip = int(np.sum(merged["Skip_Diopter"].astype(bool)))
    print(f"[INFO] Skip trials: {n_skip}/{n_total}")
    print("[INFO] Done.")


if __name__ == "__main__":
    main()
