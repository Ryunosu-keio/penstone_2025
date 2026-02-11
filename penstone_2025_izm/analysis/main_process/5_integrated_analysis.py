# -*- coding: utf-8 -*-
"""
integrated_analysis.py
------------------------------------
縮瞳・輻輳・反応速度の統合分析

【指標】
- 縮瞳率 (miosis_rate)
- 輻輳距離 (distance_mm)
- 反応速度 (RT)
- 縮瞳反応時間 (miosis_RT) : miosis_frame_start - task_start_frame_emr (sec)

【検定】
- ABC (original, brightonly, model) のみ
- One-way ANOVA & RM-ANOVA
- 有意差線あり（全体/画像キー別）

【出力】
- imagekey別 & 全体統合
- 被験者別推移（全員重ね）
- ★被験者ごとフォルダに「被験者別サマリー」も保存
   - 1被験者につき、各指標ごとに 5パネル（imagekey4 + ALL）の図を保存
   - 検定は描かず（被験者内の傾向確認用）
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy import stats
from statsmodels.stats.anova import AnovaRM
from statsmodels.stats.multicomp import pairwise_tukeyhsd
from itertools import combinations
from collections import defaultdict
import os
import warnings
warnings.filterwarnings('ignore')

plt.rcParams['font.family'] = 'MS Gothic'
plt.rcParams['axes.unicode_minus'] = False

# =====================
# フォントサイズ定数
# =====================
FONT_SIZE_SUPTITLE = 0       # 全体タイトル
FONT_SIZE_TITLE = 48          # サブプロットタイトル（image_key + ANOVA結果）
FONT_SIZE_XLABEL = 48         # 横軸ラベル（original, brightonly, model）
FONT_SIZE_YLABEL = 48         # 縦軸ラベル
FONT_SIZE_TICK = 36           # 目盛りラベル（縦軸の数値）
FONT_SIZE_SIG = 36           # 有意差バーのテキスト

# =====================
# グラフサイズ定数
# =====================
FIG_SIZE_4PANELS = (48, 12)   # 4枚パネルの画像サイズ（より横長に）
FIG_SIZE_7PANELS = (48, 48)   # 7枚パネルの画像サイズ（3行構成に合わせて調整）

# =====================
# 線太さ定数
# =====================
LINE_WIDTH_SPINE = 3.0        # 外枠の太さ
LINE_WIDTH_ZERO = 2.5         # 0基準線の太さ
LINE_WIDTH_GRID = 1.5         # グリッド線の太さ

# =====================
# 設定
# =====================
base_dir = "../../data/log_with_emr_metrics"
available_params = []
if os.path.exists(base_dir):
    for item in os.listdir(base_dir):
        if os.path.isdir(os.path.join(base_dir, item)) and item.startswith("lag"):
            if os.path.exists(os.path.join(base_dir, item, "merged")):
                available_params.append(item)

if not available_params:
    raise FileNotFoundError("利用可能なパラメータフォルダが見つかりません")

print("\n=== 利用可能な計算パラメータ ===")
for i, param in enumerate(available_params, 1):
    print(f"{i}. {param}")

param_idx = int(input(f"\n使用するパラメータを選択 (1-{len(available_params)}): ")) - 1
params = available_params[param_idx]
n = int(input("\n被験者何人入りのデータ使う？: "))

bright_file = f"../../data/log_with_emr_metrics/{params}/merged/integrated_bright_metrics_n{n}.xlsx"
dark_file   = f"../../data/log_with_emr_metrics/{params}/merged/integrated_dark_metrics_n{n}.xlsx"

# Bright被験者リスト確認と除外指定
print("\n=== Bright条件 ===")
_temp_bright = pd.read_excel(bright_file, engine='openpyxl')
bright_subjects = sorted(_temp_bright['folder_name'].unique())
print(f"利用可能な被験者 ({len(bright_subjects)}人):")
for i, s in enumerate(bright_subjects, 1):
    print(f"  {i}. {s}")

exclude_bright_input = input("Bright: 除外する被験者番号をカンマ区切りで入力（例: 1,5,7）、除外なしはEnter: ").strip()
if exclude_bright_input:
    exclude_indices = [int(x.strip()) - 1 for x in exclude_bright_input.split(",")]
    EXCLUDE_SUBJECTS_BRIGHT = [bright_subjects[i] for i in exclude_indices if 0 <= i < len(bright_subjects)]
    print(f"  Bright除外対象: {EXCLUDE_SUBJECTS_BRIGHT}")
else:
    EXCLUDE_SUBJECTS_BRIGHT = []
    print("  Bright: 除外なし")

# Dark被験者リスト確認と除外指定
print("\n=== Dark条件 ===")
_temp_dark = pd.read_excel(dark_file, engine='openpyxl')
dark_subjects = sorted(_temp_dark['folder_name'].unique())
print(f"利用可能な被験者 ({len(dark_subjects)}人):")
for i, s in enumerate(dark_subjects, 1):
    print(f"  {i}. {s}")

exclude_dark_input = input("Dark: 除外する被験者番号をカンマ区切りで入力（例: 1,5,7）、除外なしはEnter: ").strip()
if exclude_dark_input:
    exclude_indices = [int(x.strip()) - 1 for x in exclude_dark_input.split(",")]
    EXCLUDE_SUBJECTS_DARK = [dark_subjects[i] for i in exclude_indices if 0 <= i < len(dark_subjects)]
    print(f"  Dark除外対象: {EXCLUDE_SUBJECTS_DARK}")
else:
    EXCLUDE_SUBJECTS_DARK = []
    print("  Dark: 除外なし")

# 条件ごとの除外リストを辞書で管理
EXCLUDE_SUBJECTS_MAP = {
    "Bright": EXCLUDE_SUBJECTS_BRIGHT,
    "Dark": EXCLUDE_SUBJECTS_DARK
}

# ディオプター範囲の入力
print("\n=== ディオプター範囲設定 ===")
diopter_min_input = input("ディオプター下限値を入力（デフォルト: 制限なし、Enter でスキップ）: ").strip()
diopter_max_input = input("ディオプター上限値を入力（デフォルト: 制限なし、Enter でスキップ）: ").strip()

DIOPTER_MIN = float(diopter_min_input) if diopter_min_input else None
DIOPTER_MAX = float(diopter_max_input) if diopter_max_input else None

if DIOPTER_MIN is not None or DIOPTER_MAX is not None:
    range_str = f"D{DIOPTER_MIN if DIOPTER_MIN is not None else 'inf'}-{DIOPTER_MAX if DIOPTER_MAX is not None else 'inf'}"
    print(f"  ディオプター範囲: {range_str}")
else:
    range_str = None
    print("  ディオプター範囲: 制限なし")

# 標準化方法の選択
print("\n=== 標準化方法設定 ===")
print("1. 被験者全体で標準化（デフォルト）")
print("2. キャリブレーションブロックごとに標準化（block 0-4 と 5-9 で別々）")
standardization_choice = input("選択 (1 or 2, デフォルト: 1): ").strip()

if standardization_choice == "2":
    STANDARDIZE_BY_CALIBRATION = True
    calib_suffix = "calib"
    print("  標準化: キャリブレーションブロックごと")
else:
    STANDARDIZE_BY_CALIBRATION = False
    calib_suffix = None
    print("  標準化: 被験者全体")

# 方向性フィルタの選択
print("\n=== 方向性フィルタ設定 ===")
print("期待される傾向と逆向きの被験者データを除外")
print("  miosis_rate, distance_mm: model > brightonly")
print("  RT, diopter: model < brightonly")
directional_filter_input = input("方向性フィルタを適用する？ (y/n, デフォルト: n): ").strip().lower()

if directional_filter_input == "y":
    USE_DIRECTIONAL_FILTER = True
    dir_suffix = "dirfilt"
    print("  方向性フィルタ: ON")
else:
    USE_DIRECTIONAL_FILTER = False
    dir_suffix = None
    print("  方向性フィルタ: OFF")

DATA = {"Bright": bright_file, "Dark": dark_file}
IMAGE_KEYS = ["sun_empty", "sun_busy", "rain_empty", "rain_busy"]
PROCS = ["original", "brightonly", "model"]

# 出力先
total_excluded = len(EXCLUDE_SUBJECTS_BRIGHT) + len(EXCLUDE_SUBJECTS_DARK)
suffix_parts = []
if total_excluded > 0:
    suffix_parts.append(f"excludeB{len(EXCLUDE_SUBJECTS_BRIGHT)}D{len(EXCLUDE_SUBJECTS_DARK)}")
if range_str:
    suffix_parts.append(range_str)
if calib_suffix:
    suffix_parts.append(calib_suffix)
if dir_suffix:
    suffix_parts.append(dir_suffix)

# 日付を取得（YYYYMMDD形式）
from datetime import datetime
date_str = datetime.now().strftime("%Y%m%d")

if suffix_parts:
    suffix = "_" + "_".join(suffix_parts)
    OUT_DIR = os.path.join("../../data/statistics", f"{params}_{date_str}", f"n{n}{suffix}", "integrated")
else:
    OUT_DIR = os.path.join("../../data/statistics", f"{params}_{date_str}", f"n{n}", "integrated")
os.makedirs(OUT_DIR, exist_ok=True)



# =====================
# ハズレ値検出（IQR × 1.5）
# =====================
def detect_outliers_iqr(df, metric, subject_col='subject'):
    """
    被験者ごとのIQR × 1.5に基づくハズレ値検出（標準化前のデータに対して）

    Parameters:
    -----------
    df : DataFrame
        データフレーム
    metric : str
        指標名（例: 'RT', 'miosis_rate'）
    subject_col : str
        被験者カラム名

    Returns:
    --------
    Series
        ハズレ値フラグ（True=ハズレ値）
    """
    outlier_flags = pd.Series(False, index=df.index)

    for subject in df[subject_col].unique():
        subject_mask = df[subject_col] == subject
        values = df.loc[subject_mask, metric]

        # Q1, Q3, IQRを計算
        q1 = values.quantile(0.25)
        q3 = values.quantile(0.75)
        iqr = q3 - q1

        # ハズレ値の範囲を計算
        lower_bound = q1 - 1.5 * iqr
        upper_bound = q3 + 1.5 * iqr

        # ハズレ値フラグを設定
        is_outlier = (values < lower_bound) | (values > upper_bound)
        outlier_flags.loc[subject_mask] = is_outlier.values

    return outlier_flags


# =====================
# 前処理
# =====================
def preprocess(df, condition):
    df = df.copy()

    # 条件に応じた除外被験者を除去
    exclude_list = EXCLUDE_SUBJECTS_MAP.get(condition, [])
    if exclude_list and 'folder_name' in df.columns:
        df = df[~df['folder_name'].isin(exclude_list)].copy()

    # frontが数字（あなたのデータでは True が「数字」っぽいけど、ここはあなたの運用に合わせて維持）
    if 'FrontIsDigit_inferred' in df.columns:
        df = df[df['FrontIsDigit_inferred'] == True].copy()

    # image_key抽出
    def extract_image_key(row):
        for col in ['filename', 'Back_Image_Name_Used']:
            if col in df.columns and pd.notna(row.get(col)):
                for key in IMAGE_KEYS:
                    if key in str(row[col]):
                        return key
        return None

    df['image_key'] = df.apply(extract_image_key, axis=1)

    # リネーム
    rename_map = {
        'folder_name': 'subject',
        'process': 'proc',
        'pupil_both_change_rate_mean': 'miosis_rate',
        'BL_stim120_change_rate_mean': 'miosis_rate_stim120',
        'BL_onset120_change_rate_mean': 'miosis_rate_onset120',
        'BL_stim_to_onset_change_rate_mean': 'miosis_rate_sto',
        'diopter_delta': 'diopter',
        'Reaction_Time': 'RT'
    }
    df = df.rename(columns=rename_map)

    # 縮瞳反応時間（刺激開始から縮瞳開始までの秒）
    if 'miosis_frame_start' in df.columns and 'task_start_frame_emr' in df.columns:
        df['miosis_RT'] = (df['miosis_frame_start'] - df['task_start_frame_emr']) / 60.0
        df.loc[(df['miosis_RT'] <= 0) | (df['miosis_RT'] > 10), 'miosis_RT'] = np.nan
    else:
        df['miosis_RT'] = np.nan

    # 輻輳を距離（mm）に変換（diopterも保持）
    if 'diopter' in df.columns:
        df = df[df['diopter'].abs() > 0.01].copy()

        # ディオプター範囲外フラグ（削除はせず、フラグのみ）
        df['diopter_out_of_range'] = False
        if DIOPTER_MIN is not None:
            df.loc[df['diopter'] < DIOPTER_MIN, 'diopter_out_of_range'] = True
        if DIOPTER_MAX is not None:
            df.loc[df['diopter'] > DIOPTER_MAX, 'diopter_out_of_range'] = True

        df['distance_mm'] = 1000.0 / df['diopter']
    else:
        df['distance_mm'] = np.nan
        df['diopter_out_of_range'] = False

    # 必要なカラム（★3種類のベースライン追加）
    required = ['subject', 'image_key', 'proc', 'miosis_rate', 'miosis_rate_stim120', 'miosis_rate_onset120', 'miosis_rate_sto',
                'diopter', 'distance_mm', 'RT', 'miosis_RT', 'trial_id', 'diopter_out_of_range']
    df = df[[col for col in required if col in df.columns]].copy()
    df = df.dropna(subset=['image_key', 'proc'])

    # ========== ハズレ値検出（標準化前、IQR × 1.5） ==========
    for metric in ['miosis_rate', 'miosis_rate_stim120', 'miosis_rate_onset120', 'miosis_rate_sto',
                   'diopter', 'distance_mm', 'RT', 'miosis_RT']:
        if metric in df.columns:
            df[f'is_outlier_{metric}'] = detect_outliers_iqr(df, metric, 'subject')

    # ========== z-score標準化 ==========
    # キャリブレーションブロックごとの標準化が有効な場合、trial_idからblockを抽出
    if STANDARDIZE_BY_CALIBRATION and 'trial_id' in df.columns:
        # trial_idからblock番号を抽出
        parts = df["trial_id"].astype(str).str.extract(r"^S(\d+)_([0-9]+)_([0-9]+)$")
        valid_mask = ~parts.isna().any(axis=1)

        if valid_mask.any():
            df.loc[valid_mask, 'block'] = parts.loc[valid_mask, 1].astype(int)
            # キャリブレーショングループ: 0-4 = 0, 5-9 = 1
            df.loc[valid_mask, 'calib_group'] = (df.loc[valid_mask, 'block'] >= 5).astype(int)
        else:
            # trial_idのパースに失敗した場合は全体で標準化
            df['calib_group'] = 0
    else:
        # 全体で標準化する場合はグループ分けしない
        df['calib_group'] = 0

    # 各指標をz-score標準化（★3種類のベースライン追加）
    for metric in ['miosis_rate', 'miosis_rate_stim120', 'miosis_rate_onset120', 'miosis_rate_sto',
                   'diopter', 'distance_mm', 'RT', 'miosis_RT']:
        if metric in df.columns:
            # ディオプター関連指標の場合、範囲外を除外して標準化パラメータを計算
            if metric in ['diopter', 'distance_mm'] and 'diopter_out_of_range' in df.columns:
                # 範囲内のデータのみで平均・標準偏差を計算
                if STANDARDIZE_BY_CALIBRATION:
                    # 被験者 × キャリブレーショングループ × 範囲内のみで統計量計算
                    group_stats = df[df['diopter_out_of_range'] == False].groupby(['subject', 'calib_group'])[metric].agg(['mean', 'std'])
                    df = df.merge(group_stats, on=['subject', 'calib_group'], how='left', suffixes=('', '_stat'))
                    df[f'z_{metric}'] = (df[metric] - df['mean']) / df['std'].replace(0, np.nan)
                    df[f'z_{metric}'] = df[f'z_{metric}'].fillna(0)
                    df = df.drop(columns=['mean', 'std'])
                else:
                    # 被験者 × 範囲内のみで統計量計算
                    group_stats = df[df['diopter_out_of_range'] == False].groupby('subject')[metric].agg(['mean', 'std'])
                    df = df.merge(group_stats, on='subject', how='left', suffixes=('', '_stat'))
                    df[f'z_{metric}'] = (df[metric] - df['mean']) / df['std'].replace(0, np.nan)
                    df[f'z_{metric}'] = df[f'z_{metric}'].fillna(0)
                    df = df.drop(columns=['mean', 'std'])
            else:
                # その他の指標は通常通り
                if STANDARDIZE_BY_CALIBRATION:
                    df[f'z_{metric}'] = df.groupby(['subject', 'calib_group'])[metric].transform(
                        lambda x: (x - x.mean()) / x.std(ddof=1) if x.std(ddof=1) > 0 else 0
                    )
                else:
                    df[f'z_{metric}'] = df.groupby('subject')[metric].transform(
                        lambda x: (x - x.mean()) / x.std(ddof=1) if x.std(ddof=1) > 0 else 0
                    )

            # 3σ外れ値除去（指標ごとにNaN化、行削除ではなく）
            mask_outlier = df[f'z_{metric}'].abs() >= 3
            if mask_outlier.any():
                df.loc[mask_outlier, f'z_{metric}'] = np.nan
                df.loc[mask_outlier, metric] = np.nan

    # ========== 方向性フィルタ（被験者単位で期待と逆傾向を除外） ==========
    if USE_DIRECTIONAL_FILTER:
        # 期待される傾向の定義
        # model > brightonly なら positive direction (miosis_rate, distance_mm)
        # model < brightonly なら negative direction (RT, diopter)
        expected_direction = {
            'miosis_rate': 'positive',           # model > brightonly
            'miosis_rate_stim120': 'positive',   # model > brightonly
            'miosis_rate_onset120': 'positive',  # model > brightonly
            'miosis_rate_sto': 'positive',       # model > brightonly
            'distance_mm': 'positive',           # model > brightonly
            'RT': 'negative',                    # model < brightonly
            'diopter': 'negative',               # model < brightonly
            'miosis_RT': 'negative'              # model < brightonly (反応速度なので小さい方が良い)
        }

        subjects_to_remove = set()

        for metric, direction in expected_direction.items():
            if metric not in df.columns or f'z_{metric}' not in df.columns:
                continue

            for subj in df['subject'].unique():
                subj_data = df[df['subject'] == subj]

                # brightonly と model の平均を計算
                b_only_mean = subj_data[subj_data['proc'] == 'brightonly'][f'z_{metric}'].mean()
                model_mean = subj_data[subj_data['proc'] == 'model'][f'z_{metric}'].mean()

                if pd.isna(b_only_mean) or pd.isna(model_mean):
                    continue

                # 期待と逆の場合、その被験者のその指標のデータを除外対象に
                if direction == 'positive' and model_mean < b_only_mean:
                    # 期待: model > brightonly だが、実際は model < brightonly
                    subjects_to_remove.add((subj, metric))
                elif direction == 'negative' and model_mean > b_only_mean:
                    # 期待: model < brightonly だが、実際は model > brightonly
                    subjects_to_remove.add((subj, metric))

        # 実際にデータを除外（NaNを代入して、後の処理で除外されるようにする）
        excluded_summary = defaultdict(list)
        for subj, metric in subjects_to_remove:
            mask = (df['subject'] == subj)
            if metric in df.columns:
                df.loc[mask, metric] = np.nan
            if f'z_{metric}' in df.columns:
                df.loc[mask, f'z_{metric}'] = np.nan
            excluded_summary[subj].append(metric)

        n_excluded = len(subjects_to_remove)
        if n_excluded > 0:
            print(f"    方向性フィルタ: {n_excluded} 件の除外")
            for subj in sorted(excluded_summary.keys()):
                metrics_str = ", ".join(excluded_summary[subj])
                print(f"      - {subj}: {metrics_str}")

    return df


# =====================
# 統計検定
# =====================
def cohen_d(g1, g2):
    diff = g1 - g2
    sd = np.std(diff, ddof=1)
    return np.mean(diff) / sd if sd > 0 else 0

def run_anova(df_sub, metric):
    # NaNを除外
    df_clean = df_sub.dropna(subset=[f"z_{metric}"])
    groups = [df_clean[df_clean["proc"] == p][f"z_{metric}"] for p in PROCS]
    if any(len(g) == 0 for g in groups):
        return None, None, None, None

    F, p = stats.f_oneway(*groups)
    tukey = pairwise_tukeyhsd(df_sub[f"z_{metric}"], df_sub["proc"], alpha=0.05)

    # η² (eta-squared)
    all_data = df_sub[f"z_{metric}"]
    grand_mean = all_data.mean()
    ss_total = ((all_data - grand_mean) ** 2).sum()
    ss_between = sum(len(g) * (g.mean() - grand_mean) ** 2 for g in groups)
    eta_sq = ss_between / ss_total if ss_total > 0 else 0

    return F, p, tukey, eta_sq

def run_rm_anova(df_sub, metric):
    subject_proc_counts = df_sub.groupby('subject')['proc'].nunique()
    complete_subjects = subject_proc_counts[subject_proc_counts == len(PROCS)].index
    df_complete = df_sub[df_sub['subject'].isin(complete_subjects)].copy()

    if len(df_complete) == 0 or len(complete_subjects) < 2:
        return None

    try:
        df_agg = df_complete.groupby(['subject', 'proc'])[f'z_{metric}'].mean().reset_index()
        aovrm = AnovaRM(df_agg, depvar=f'z_{metric}', subject='subject', within=['proc'])
        res = aovrm.fit()

        anova_table = res.anova_table
        f_stat = anova_table.loc['proc', 'F Value']
        p_val = anova_table.loc['proc', 'Pr > F']
        df_effect = anova_table.loc['proc', 'Num DF']
        df_error = anova_table.loc['proc', 'Den DF']
        eta_sq = (f_stat * df_effect) / (f_stat * df_effect + df_error)

        return {
            'F': f_stat, 'p': p_val, 'eta_sq': eta_sq,
            'n_subjects': len(complete_subjects), 'table': anova_table,
            'df_effect': df_effect, 'df_error': df_error
        }
    except:
        return None


# =====================
# 有意差線描画
# =====================
def add_sig_lines(ax, pairs, y_max):
    step = 0.35
    highest_y = y_max
    for i, (x1, x2, p, d) in enumerate(pairs):
        y = y_max + step * (i + 0.5)
        ax.plot([x1, x1, x2, x2], [y, y+0.05, y+0.05, y], lw=1.2, c="black")

        sig = "***" if p < 0.001 else "**" if p < 0.01 else "*" if p < 0.05 else "n.s."
        ax.text((x1+x2)/2, y+0.06, f"{sig}\np={p:.3f}, d={d:.2f}",
                ha="center", va="bottom", fontsize=FONT_SIZE_SIG, fontweight='bold')
        highest_y = y + 0.5

    # タイトルと重ならないようにY軸の上限のみを調整（下限は保持）
    cur_ylim = ax.get_ylim()
    new_upper = max(cur_ylim[1], highest_y)
    # 上限を広げた分、下限も同程度広げてバランスを取る
    margin = (new_upper - cur_ylim[1]) * 0.3  # 上限拡大分の30%を下にも反映
    ax.set_ylim(cur_ylim[0] - margin, new_upper)


# =====================
# 被験者「単独」サマリー（検定なし）
# =====================
def _plot_single_subject_no_test(ax, sub, title, metric):
    """
    被験者1人の傾向確認用：ABC(proc) の平均±SEM だけ描く（検定・有意差線は出さない）
    """
    if len(sub) == 0 or f"z_{metric}" not in sub.columns:
        ax.text(0.5, 0.5, "No Data", ha='center', va='center', transform=ax.transAxes)
        ax.set_xticks([])
        ax.set_yticks([])
        ax.set_title(title, fontsize=16, fontweight='bold')
        return

    means = sub.groupby("proc")[f"z_{metric}"].mean().reindex(PROCS)
    sems  = sub.groupby("proc")[f"z_{metric}"].sem().reindex(PROCS)

    x_pos = np.arange(len(PROCS))

    # 色指定はしない（matplotlibのデフォルトサイクルを使うため、procごとに別barを描く）
    for i, p in enumerate(PROCS):
        if pd.isna(means.loc[p]):
            continue
        ax.bar(i, means.loc[p], yerr=sems.loc[p], capsize=4, alpha=0.85)

    ax.set_xticks(x_pos)
    ax.set_xticklabels(PROCS, rotation=15, ha='right', fontsize=14)
    ax.axhline(0, color="gray", ls="--", lw=0.8, alpha=0.6)
    ax.grid(axis='y', alpha=0.25)
    ax.set_title(title, fontsize=16, fontweight='bold')


def plot_per_subject_metric_panels(df, condition, metric, out_dir):
    """
    ★被験者ごとフォルダを作る版
    被験者ごとに、指定metricについて「imagekey4 + ALL」の5パネル図を保存する。
      out_dir/
        S01/
          Bright_miosis_rate_panels.png
          Bright_RT_panels.png
          ...
        S02/
          ...
    """
    if f"z_{metric}" not in df.columns:
        print(f"    [per-subject] {metric}: z列なし -> skip")
        return

    metric_info = {
        'miosis_rate': ('縮瞳率', 'z-scored Miosis Rate'),
        'diopter': ('輻輳 (D)', 'z-scored Diopter (D)'),
        'distance_mm': ('輻輳距離 (mm)', 'z-scored Distance (mm)'),
        'RT': ('ボタン反応時間 (ms)', 'z-scored RT (ms)'),
        'miosis_RT': ('縮瞳反応時間 (s)', 'z-scored Miosis RT (s)')
    }
    title_jp, ylabel = metric_info.get(metric, (metric, f"z_{metric}"))

    subjects = sorted(df['subject'].unique())

    for subj in subjects:
        df_s = df[df['subject'] == subj].copy()
        if len(df_s) == 0:
            continue

        # 被験者フォルダ
        safe_subj = str(subj).replace("/", "_").replace("\\", "_")
        subj_dir = os.path.join(out_dir, safe_subj)
        os.makedirs(subj_dir, exist_ok=True)

        fig, axes = plt.subplots(1, 5, figsize=(22, 4.5), sharey=True)
        fig.suptitle(f"{condition} / {safe_subj} - {title_jp}（ABC差：被験者内傾向）", fontsize=20, fontweight='bold')

        # imagekey別4枚
        for ax, img_key in zip(axes[:4], IMAGE_KEYS):
            sub = df_s[(df_s["image_key"] == img_key) & (df_s["proc"].isin(PROCS))].copy()
            _plot_single_subject_no_test(ax, sub, img_key, metric)

        # ALL
        sub_all = df_s[df_s["proc"].isin(PROCS)].copy()
        _plot_single_subject_no_test(axes[4], sub_all, "ALL", metric)

        axes[0].set_ylabel(ylabel, fontsize=16)
        plt.tight_layout()

        out_name = f"{condition}_{metric}_panels.png"
        plt.savefig(os.path.join(subj_dir, out_name), dpi=300, bbox_inches='tight')
        plt.close(fig)


# =====================
# グラフ作成（全体/画像別 + 検定あり）
# =====================
def plot_analysis(df, condition, metric, test_type, split_by_imagekey, out_dir):
    """
    2種類のレイアウトを生成:
    - 4panels: image_key別（4パネル横並び）
    - 7panels: 3x3レイアウト（image_key4 + ALL系3）
    """
    metric_info = {
        'miosis_rate': ('縮瞳率', 'z-scored Miosis Rate'),
        'diopter': ('輻輳 (D)', 'z-scored Diopter (D)'),
        'distance_mm': ('輻輳距離 (mm)', 'z-scored Distance (mm)'),
        'RT': ('ボタン反応時間 (ms)', 'z-scored RT (ms)'),
        'miosis_RT': ('縮瞳反応時間 (s)', 'z-scored Miosis RT (s)')
    }

    if metric not in metric_info:
        return

    title_jp, ylabel = metric_info[metric]
    test_name = "One-way ANOVA" if test_type == 'oneway' else "RM-ANOVA"

    # === 4panels: image_key別（1行4列）===
    fig, axes = plt.subplots(1, 4, figsize=FIG_SIZE_4PANELS, sharey=False)
    fig.suptitle(f"{condition} - {title_jp} / {test_name}", fontsize=FONT_SIZE_SUPTITLE, fontweight='bold')

    for ax, img_key in zip(axes, IMAGE_KEYS):
        sub = df[(df["image_key"] == img_key) & (df["proc"].isin(PROCS))].copy()
        _plot_single(ax, sub, f"{condition}_{img_key}", metric, test_type)

    axes[0].set_ylabel(ylabel, fontsize=FONT_SIZE_YLABEL)
    plt.tight_layout()
    out_name_4 = f"{condition}_{metric}_{test_type}_4panels.png"
    plt.savefig(os.path.join(out_dir, out_name_4), dpi=300, bbox_inches='tight')
    print(f"    保存: {out_name_4}")
    plt.close()

    # === 7panels: 3x3レイアウト ===
    fig, axes = plt.subplots(3, 3, figsize=FIG_SIZE_7PANELS)
    fig.suptitle(f"{condition} - {title_jp} / {test_name}",
                 fontsize=FONT_SIZE_SUPTITLE, fontweight='bold')

    # 1行目: sun条件
    sub = df[(df["image_key"] == "sun_empty") & (df["proc"].isin(PROCS))].copy()
    _plot_single(axes[0, 0], sub, f"{condition}_sun_empty", metric, test_type)

    sub = df[(df["image_key"] == "sun_busy") & (df["proc"].isin(PROCS))].copy()
    _plot_single(axes[0, 1], sub, f"{condition}_sun_busy", metric, test_type)

    sub_sun = df[(df["image_key"].isin(["sun_empty", "sun_busy"])) & (df["proc"].isin(PROCS))].copy()
    _plot_single(axes[0, 2], sub_sun, f"{condition}_ALL_sun", metric, test_type)

    # 2行目: rain条件
    sub = df[(df["image_key"] == "rain_empty") & (df["proc"].isin(PROCS))].copy()
    _plot_single(axes[1, 0], sub, f"{condition}_rain_empty", metric, test_type)

    sub = df[(df["image_key"] == "rain_busy") & (df["proc"].isin(PROCS))].copy()
    _plot_single(axes[1, 1], sub, f"{condition}_rain_busy", metric, test_type)

    sub_rain = df[(df["image_key"].isin(["rain_empty", "rain_busy"])) & (df["proc"].isin(PROCS))].copy()
    _plot_single(axes[1, 2], sub_rain, f"{condition}_ALL_rain", metric, test_type)

    # 3行目: ALL_empty, ALL_busy, ALL
    sub_empty = df[(df["image_key"].isin(["sun_empty", "rain_empty"])) & (df["proc"].isin(PROCS))].copy()
    _plot_single(axes[2, 0], sub_empty, f"{condition}_ALL_empty", metric, test_type)

    sub_busy = df[(df["image_key"].isin(["sun_busy", "rain_busy"])) & (df["proc"].isin(PROCS))].copy()
    _plot_single(axes[2, 1], sub_busy, f"{condition}_ALL_busy", metric, test_type)

    sub_all = df[df["proc"].isin(PROCS)].copy()
    _plot_single(axes[2, 2], sub_all, f"{condition}_ALL", metric, test_type)

    # Y軸ラベル
    axes[0, 0].set_ylabel(ylabel, fontsize=FONT_SIZE_YLABEL)
    axes[1, 0].set_ylabel(ylabel, fontsize=FONT_SIZE_YLABEL)
    axes[2, 0].set_ylabel(ylabel, fontsize=FONT_SIZE_YLABEL)

    plt.tight_layout()
    out_name_9 = f"{condition}_{metric}_{test_type}_9panels.png"
    plt.savefig(os.path.join(out_dir, out_name_9), dpi=300, bbox_inches='tight')
    print(f"    保存: {out_name_9}")
    plt.close()


def plot_distribution_analysis(df, condition, metric, out_dir):
    """
    有意差を確認するための分布プロット
    - 箱ひげ図（Box plot）
    - バイオリン図（Violin plot）
    - 散布図（個別データポイント）
    - 被験者ごとの変化（ペアプロット）
    """
    metric_info = {
        'miosis_rate': ('縮瞳率', 'z-scored Miosis Rate'),
        'diopter': ('輻輳 (D)', 'z-scored Diopter (D)'),
        'distance_mm': ('輻輳距離 (mm)', 'z-scored Distance (mm)'),
        'RT': ('ボタン反応時間 (ms)', 'z-scored RT (ms)'),
        'miosis_RT': ('縮瞳反応時間 (s)', 'z-scored Miosis RT (s)')
    }

    if metric not in metric_info:
        return

    title_jp, ylabel = metric_info[metric]

    # 出力ディレクトリ
    dist_dir = os.path.join(out_dir, "distribution")
    os.makedirs(dist_dir, exist_ok=True)

    df_use = df[df["proc"].isin(PROCS)].copy()
    if f'z_{metric}' not in df_use.columns or len(df_use) == 0:
        return

    # ディオプター関連の場合、範囲外を除外
    if metric in ['diopter', 'distance_mm'] and 'diopter_out_of_range' in df_use.columns:
        df_use = df_use[df_use['diopter_out_of_range'] == False].copy()

    subjects = sorted(df_use['subject'].unique())
    colors = {'original': 'steelblue', 'brightonly': 'orange', 'model': 'green'}

    # === 図1: 箱ひげ図 + 散布図（3x3 imagekey別） ===
    fig, axes = plt.subplots(3, 3, figsize=(15, 12))
    fig.suptitle(f"{condition} - {title_jp} / データ分布（箱ひげ図 + 散布）", fontsize=20, fontweight='bold')

    layout = [
        ("sun_empty", 0, 0), ("sun_busy", 0, 1), ("ALL_sun", 0, 2),
        ("rain_empty", 1, 0), ("rain_busy", 1, 1), ("ALL_rain", 1, 2),
        (None, 2, 0), (None, 2, 1), ("ALL", 2, 2)
    ]

    for item in layout:
        img_key, row, col = item
        ax = axes[row, col]

        if img_key is None:
            ax.axis('off')
            continue

        if img_key == "ALL":
            sub = df_use.copy()
        elif img_key == "ALL_sun":
            sub = df_use[df_use["image_key"].isin(["sun_empty", "sun_busy"])].copy()
        elif img_key == "ALL_rain":
            sub = df_use[df_use["image_key"].isin(["rain_empty", "rain_busy"])].copy()
        else:
            sub = df_use[df_use["image_key"] == img_key].copy()

        if len(sub) == 0:
            ax.text(0.5, 0.5, "No Data", ha='center', va='center', transform=ax.transAxes)
            ax.set_title(img_key, fontsize=16)
            continue

        # 箱ひげ図
        box_data = [sub[sub['proc'] == p][f'z_{metric}'].dropna().values for p in PROCS]
        bp = ax.boxplot(box_data, positions=range(len(PROCS)), widths=0.6, patch_artist=True)

        for patch, proc in zip(bp['boxes'], PROCS):
            patch.set_facecolor(colors[proc])
            patch.set_alpha(0.5)

        # 散布図（ジッター付き）
        for i, proc in enumerate(PROCS):
            vals = sub[sub['proc'] == proc][f'z_{metric}'].dropna()
            jitter = np.random.normal(0, 0.1, len(vals))
            ax.scatter(i + jitter, vals, c=colors[proc], s=20, alpha=0.6, edgecolors='none')

        ax.set_xticks(range(len(PROCS)))
        ax.set_xticklabels(PROCS, rotation=15, ha='right', fontsize=14)
        ax.axhline(0, color="gray", ls="--", lw=0.8, alpha=0.6)
        ax.grid(axis='y', alpha=0.3)
        ax.set_title(f"{img_key}", fontsize=16, fontweight='bold')

        if col == 0:
            ax.set_ylabel(ylabel, fontsize=14)

    plt.tight_layout()
    out_name = f"{condition}_{metric}_distribution_box.png"
    plt.savefig(os.path.join(dist_dir, out_name), dpi=150, bbox_inches='tight')
    plt.close()

    # === 図2: 被験者ごとのペア変化（brightonly vs model） ===
    fig, axes = plt.subplots(3, 3, figsize=(15, 12))
    fig.suptitle(f"{condition} - {title_jp} / 被験者別変化（brightonly → model）", fontsize=20, fontweight='bold')

    for item in layout:
        img_key, row, col = item
        ax = axes[row, col]

        if img_key is None:
            ax.axis('off')
            continue

        if img_key == "ALL":
            sub = df_use.copy()
        elif img_key == "ALL_sun":
            sub = df_use[df_use["image_key"].isin(["sun_empty", "sun_busy"])].copy()
        elif img_key == "ALL_rain":
            sub = df_use[df_use["image_key"].isin(["rain_empty", "rain_busy"])].copy()
        else:
            sub = df_use[df_use["image_key"] == img_key].copy()

        if len(sub) == 0:
            ax.text(0.5, 0.5, "No Data", ha='center', va='center', transform=ax.transAxes)
            ax.set_title(img_key, fontsize=16)
            continue

        # 被験者ごとにbrightonly→modelの変化をプロット
        for i, subj in enumerate(subjects):
            subj_data = sub[sub['subject'] == subj]
            b_only = subj_data[subj_data['proc'] == 'brightonly'][f'z_{metric}'].mean()
            model = subj_data[subj_data['proc'] == 'model'][f'z_{metric}'].mean()

            if pd.notna(b_only) and pd.notna(model):
                color = 'green' if model > b_only else 'red'  # 期待方向で色分け
                ax.plot([0, 1], [b_only, model], 'o-', color=color, alpha=0.5, lw=1.5, markersize=6)

        ax.set_xticks([0, 1])
        ax.set_xticklabels(['brightonly', 'model'], fontsize=14)
        ax.axhline(0, color="gray", ls="--", lw=0.8, alpha=0.6)
        ax.grid(axis='y', alpha=0.3)
        ax.set_title(f"{img_key}", fontsize=16, fontweight='bold')

        if col == 0:
            ax.set_ylabel(ylabel, fontsize=14)

    plt.tight_layout()
    out_name = f"{condition}_{metric}_distribution_paired.png"
    plt.savefig(os.path.join(dist_dir, out_name), dpi=150, bbox_inches='tight')
    plt.close()

    # === 図3: ヒストグラム（各proc別） ===
    fig, axes = plt.subplots(1, 3, figsize=(15, 5))
    fig.suptitle(f"{condition} - {title_jp} / 度数分布（ALL）", fontsize=20, fontweight='bold')

    for ax, proc in zip(axes, PROCS):
        vals = df_use[df_use['proc'] == proc][f'z_{metric}'].dropna()
        if len(vals) > 0:
            ax.hist(vals, bins=20, color=colors[proc], alpha=0.7, edgecolor='white')
            ax.axvline(vals.mean(), color='red', ls='--', lw=2, label=f'Mean: {vals.mean():.2f}')
            ax.axvline(0, color='gray', ls='--', lw=1, alpha=0.6)
            ax.legend(fontsize=12)
        ax.set_xlabel(ylabel, fontsize=14)
        ax.set_ylabel("度数", fontsize=14)
        ax.set_title(proc, fontsize=16, fontweight='bold')
        ax.grid(axis='y', alpha=0.3)

    plt.tight_layout()
    out_name = f"{condition}_{metric}_distribution_hist.png"
    plt.savefig(os.path.join(dist_dir, out_name), dpi=150, bbox_inches='tight')
    plt.close()

    print(f"    保存: distribution/ ({metric})")



def plot_subject_lines(df, condition, metric, out_dir):
    """被験者ごとの折れ線グラフ（全員重ね）: imagekey別 + all"""
    metric_info = {
        'miosis_rate': ('縮瞳率', 'z-scored Miosis Rate'),
        'diopter': ('輻輳 (D)', 'z-scored Diopter (D)'),
        'distance_mm': ('輻輳距離 (mm)', 'z-scored Diopter (D)'),
        'RT': ('ボタン反応時間 (ms)', 'z-scored RT (ms)'),
        'miosis_RT': ('縮瞳反応時間 (s)', 'z-scored Miosis RT (s)')
    }

    if metric not in metric_info:
        return

    title_jp, ylabel = metric_info[metric]
    df_use = df.copy()

    fig, axes = plt.subplots(1, 5, figsize=(22, 4.5), sharey=True)
    fig.suptitle(f"{condition} - {title_jp} / 被験者別推移（全員重ね）", fontsize=20, fontweight='bold')

    subjects = sorted(df_use['subject'].unique())
    colors = plt.cm.tab20(np.linspace(0, 1, len(subjects)))

    for ax, img_key in zip(axes[:4], IMAGE_KEYS):
        sub = df_use[(df_use["image_key"] == img_key) & (df_use["proc"].isin(PROCS))].copy()
        _plot_subject_lines_single(ax, sub, img_key, metric, subjects, colors)

    sub_all = df_use[df_use["proc"].isin(PROCS)].copy()
    _plot_subject_lines_single(axes[4], sub_all, "ALL", metric, subjects, colors)

    axes[0].set_ylabel(ylabel, fontsize=16)

    handles = [plt.Line2D([0], [0], color=colors[i], lw=1.5, label=s)
               for i, s in enumerate(subjects)]
    axes[4].legend(handles=handles, loc='center left', bbox_to_anchor=(1.02, 0.5),
                   fontsize=10, title='Subject')

    plt.tight_layout()
    out_name = f"{condition}_{metric}_subject_lines.png"
    plt.savefig(os.path.join(out_dir, out_name), dpi=300, bbox_inches='tight')
    print(f"    保存: {out_name}")
    plt.close()


def plot_rt_correlation(df, condition, out_dir):
    """ボタン反応時間と縮瞳反応時間の相関分析"""
    if 'RT' not in df.columns or 'miosis_RT' not in df.columns:
        print("    RT or miosis_RT not available")
        return

    df_valid = df.dropna(subset=['RT', 'miosis_RT']).copy()
    if len(df_valid) < 5:
        print("    データ不足 (n<5)")
        return

    fig, axes = plt.subplots(1, 5, figsize=(22, 4.5))
    fig.suptitle(f"{condition} - ボタン反応時間 vs 縮瞳反応時間", fontsize=20, fontweight='bold')

    subjects = sorted(df_valid['subject'].unique())
    colors = plt.cm.tab20(np.linspace(0, 1, len(subjects)))
    subject_colors = {s: colors[i] for i, s in enumerate(subjects)}

    def plot_scatter(ax, data, title):
        if len(data) < 3:
            ax.text(0.5, 0.5, "No Data", ha='center', va='center', transform=ax.transAxes)
            ax.set_title(title)
            return

        for subj in subjects:
            subj_data = data[data['subject'] == subj]
            if len(subj_data) > 0:
                ax.scatter(subj_data['RT'], subj_data['miosis_RT'],
                           c=[subject_colors[subj]], s=30, alpha=0.6, label=subj)

        r, p = stats.pearsonr(data['RT'], data['miosis_RT'])
        rho, p_spearman = stats.spearmanr(data['RT'], data['miosis_RT'])

        slope, intercept = np.polyfit(data['RT'], data['miosis_RT'], 1)
        x_line = np.linspace(data['RT'].min(), data['RT'].max(), 100)
        ax.plot(x_line, slope * x_line + intercept, 'r-', lw=2, alpha=0.7)

        sig = "***" if p < 0.001 else "**" if p < 0.01 else "*" if p < 0.05 else ""
        ax.set_title(f"{title}\nr={r:.3f}{sig}, ρ={rho:.3f}, n={len(data)}", fontsize=14)
        ax.set_xlabel("ボタン反応時間 (ms)")
        ax.grid(alpha=0.3)

    for ax, img_key in zip(axes[:4], IMAGE_KEYS):
        sub = df_valid[(df_valid["image_key"] == img_key) & (df_valid["proc"].isin(PROCS))].copy()
        plot_scatter(ax, sub, img_key)

    sub_all = df_valid[df_valid["proc"].isin(PROCS)].copy()
    plot_scatter(axes[4], sub_all, "ALL")

    axes[0].set_ylabel("縮瞳反応時間 (s)")

    handles = [plt.Line2D([0], [0], marker='o', color='w', markerfacecolor=subject_colors[s],
                          markersize=6, label=s) for s in subjects]
    axes[4].legend(handles=handles, loc='center left', bbox_to_anchor=(1.02, 0.5),
                   fontsize=10, title='Subject')

    plt.tight_layout()
    out_name = f"{condition}_RT_vs_miosisRT_correlation.png"
    plt.savefig(os.path.join(out_dir, out_name), dpi=300, bbox_inches='tight')
    print(f"    保存: {out_name}")
    plt.close()

    # proc別
    fig, axes = plt.subplots(1, 3, figsize=(15, 5))
    fig.suptitle(f"{condition} - ボタン反応時間 vs 縮瞳反応時間 (処理別)", fontsize=20, fontweight='bold')

    for ax, proc in zip(axes, PROCS):
        sub = df_valid[df_valid["proc"] == proc].copy()
        if len(sub) >= 3:
            for subj in subjects:
                subj_data = sub[sub['subject'] == subj]
                if len(subj_data) > 0:
                    ax.scatter(subj_data['RT'], subj_data['miosis_RT'],
                               c=[subject_colors[subj]], s=30, alpha=0.6)

            r, p = stats.pearsonr(sub['RT'], sub['miosis_RT'])
            slope, intercept = np.polyfit(sub['RT'], sub['miosis_RT'], 1)
            x_line = np.linspace(sub['RT'].min(), sub['RT'].max(), 100)
            ax.plot(x_line, slope * x_line + intercept, 'r-', lw=2, alpha=0.7)

            sig = "***" if p < 0.001 else "**" if p < 0.01 else "*" if p < 0.05 else ""
            ax.set_title(f"{proc}\nr={r:.3f}{sig}, n={len(sub)}", fontsize=14)
        else:
            ax.set_title(f"{proc}\nNo Data", fontsize=14)

        ax.set_xlabel("ボタン反応時間 (ms)")
        ax.grid(alpha=0.3)

    axes[0].set_ylabel("縮瞳反応時間 (s)")
    plt.tight_layout()
    out_name = f"{condition}_RT_vs_miosisRT_by_proc.png"
    plt.savefig(os.path.join(out_dir, out_name), dpi=300, bbox_inches='tight')
    print(f"    保存: {out_name}")
    plt.close()


def plot_trial_progression_per_subject(df, condition, out_dir):
    """
    被験者ごとの trial_id 順プロット（RT / 縮瞳 / 輻輳）
    - trial_idをパースして正しい時系列順に並べる
    - processごとに色分け
    - ハズレ値を❌でマーク
    """
    print(f"\n  [Trial Progression] 被験者ごとのトライアル推移プロット作成中...")

    df_use = df.copy()

    # trial_id が存在しない場合はスキップ
    if 'trial_id' not in df_use.columns:
        print(f"    警告: trial_id 列が存在しないためスキップ")
        return

    # trial_id をパース
    parts = df_use["trial_id"].astype(str).str.extract(r"^S(\d+)_([0-9]+)_([0-9]+)$")

    # パース失敗したデータを除外
    valid_mask = ~parts.isna().any(axis=1)
    if not valid_mask.all():
        n_invalid = (~valid_mask).sum()
        print(f"    警告: {n_invalid} 行のtrial_idがパース不可のため除外")
        df_use = df_use[valid_mask].copy()
        parts = parts[valid_mask]

    if len(df_use) == 0:
        print(f"    エラー: 有効なデータがありません")
        return

    # trial_seq を計算
    df_use["sid"] = parts[0].astype(int)
    df_use["block"] = parts[1].astype(int)
    df_use["t_in_block"] = parts[2].astype(int)
    df_use["trial_seq"] = df_use["block"] * 48 + (df_use["t_in_block"] - 1)

    # ソート
    df_use = df_use.sort_values(["subject", "sid", "block", "t_in_block"]).reset_index(drop=True)

    # 出力ディレクトリ
    prog_dir = os.path.join(out_dir, "trial_progression")
    os.makedirs(prog_dir, exist_ok=True)

    subjects = sorted(df_use["subject"].unique())

    metrics = [
        ("RT", "反応時間 (ms)"),
        ("miosis_rate", "縮瞳率"),
        ("diopter", "輻輳 (diopter)"),
    ]

    saved = 0
    for subj in subjects:
        d = df_use[df_use["subject"] == subj].copy()

        # データがあるかチェック
        has_data = False
        for col, _ in metrics:
            if col in d.columns and d[col].notna().sum() > 0:
                has_data = True
                break

        if not has_data:
            print(f"    [SKIP] {subj}: データなし")
            continue

        fig, axes = plt.subplots(3, 1, figsize=(12, 9), sharex=True)

        # trial_seq -> trial_id マッピング（x軸ラベル用）
        id_map = (
            d[["trial_seq", "trial_id"]]
            .drop_duplicates("trial_seq")
            .set_index("trial_seq")["trial_id"]
            .to_dict()
        )

        # processの並び（凡例用）
        proc_order = sorted(d["proc"].dropna().unique())

        # 各指標をプロット
        for ax, (col, ylabel) in zip(axes, metrics):
            ax.set_ylabel(ylabel, fontsize=14)
            ax.grid(alpha=0.3)

            if col not in d.columns:
                ax.text(0.5, 0.5, "No Data", ha='center', va='center', transform=ax.transAxes)
                continue

            # processごとにプロット
            for p in proc_order:
                dp = d[d["proc"] == p].dropna(subset=[col]).copy()
                if len(dp) == 0:
                    continue

                # ラインと散布図
                ax.scatter(dp["trial_seq"], dp[col], s=16, alpha=0.7, label=p)
                ax.plot(dp["trial_seq"], dp[col], linewidth=1.0, alpha=0.5)

            # ハズレ値を❌でマーク
            outlier_col = f'is_outlier_{col}'
            if outlier_col in d.columns:
                outliers = d[d[outlier_col] == True].dropna(subset=[col])
                if len(outliers) > 0:
                    ax.scatter(outliers["trial_seq"], outliers[col],
                             marker='x', s=100, color='red', linewidths=2,
                             alpha=0.9, zorder=10, label='Outlier (IQR)')

            # ディオプター範囲外を青❌でマーク
            if col == 'diopter' and 'diopter_out_of_range' in d.columns:
                out_of_range = d[d['diopter_out_of_range'] == True].dropna(subset=[col])
                if len(out_of_range) > 0:
                    ax.scatter(out_of_range["trial_seq"], out_of_range[col],
                             marker='x', s=100, color='blue', linewidths=2,
                             alpha=0.9, zorder=11, label='Out of Range')

            # 上段のみ凡例表示
            if ax is axes[0]:
                ax.legend(loc="best", fontsize=12, frameon=True)

        axes[0].set_title(f"{condition} / {subj} - Trial進行（trial_id順）", fontsize=16, fontweight='bold')
        axes[-1].set_xlabel("Trial Sequence", fontsize=14)

        # x軸の設定
        xticks = np.array(sorted(d["trial_seq"].unique()))
        step = max(1, len(xticks) // 12)
        xt_show = xticks[::step]
        axes[-1].set_xticks(xt_show)
        axes[-1].set_xticklabels([id_map.get(int(t), str(t)) for t in xt_show],
                                 rotation=45, ha="right", fontsize=12)

        plt.tight_layout()

        safe_subj = str(subj).replace("/", "_").replace("\\", "_")
        out_path = os.path.join(prog_dir, f"{safe_subj}_trial_progression.png")
        fig.savefig(out_path, dpi=150, bbox_inches="tight")
        plt.close(fig)

        saved += 1

    print(f"    保存完了: {saved} subjects → {os.path.abspath(prog_dir)}")


def plot_subjects_by_imagekey_lines(df, condition, metric, out_dir):
    """
    imagekey別に全被験者の折れ線グラフを比較表示
    各imagekeyにつき1ファイル、被験者ごとに1サブプロット
    """
    metric_info = {
        'miosis_rate': ('縮瞳率', 'z-scored Miosis Rate'),
        'diopter': ('輻輳 (D)', 'z-scored Diopter (D)'),
        'distance_mm': ('輻輳距離 (mm)', 'z-scored Diopter (D)'),
        'RT': ('ボタン反応時間 (ms)', 'z-scored RT (ms)'),
        'miosis_RT': ('縮瞳反応時間 (s)', 'z-scored Miosis RT (s)')
    }

    if metric not in metric_info:
        return

    title_jp, ylabel = metric_info[metric]

    # 出力ディレクトリ
    compare_dir = os.path.join(out_dir, "subjects_by_imagekey", "lines")
    os.makedirs(compare_dir, exist_ok=True)

    subjects = sorted(df['subject'].unique())
    n_subjects = len(subjects)

    # 行列レイアウトを計算
    n_cols = min(5, n_subjects)
    n_rows = (n_subjects + n_cols - 1) // n_cols

    # 各imagekeyについてファイルを作成
    all_keys = IMAGE_KEYS + ["ALL", "ALL_sun", "ALL_rain"]

    for img_key in all_keys:
        # データフィルタリング
        if img_key == "ALL":
            df_key = df[df["proc"].isin(PROCS)].copy()
        elif img_key == "ALL_sun":
            df_key = df[(df["image_key"].isin(["sun_empty", "sun_busy"])) & (df["proc"].isin(PROCS))].copy()
        elif img_key == "ALL_rain":
            df_key = df[(df["image_key"].isin(["rain_empty", "rain_busy"])) & (df["proc"].isin(PROCS))].copy()
        else:
            df_key = df[(df["image_key"] == img_key) & (df["proc"].isin(PROCS))].copy()

        if len(df_key) == 0:
            continue

        fig, axes = plt.subplots(n_rows, n_cols, figsize=(4*n_cols, 3*n_rows), sharey=True)
        fig.suptitle(f"{condition} - {title_jp} / {img_key} / 被験者間比較（折れ線）", fontsize=20, fontweight='bold')

        if n_subjects == 1:
            axes = np.array([[axes]])
        elif n_rows == 1:
            axes = axes.reshape(1, -1)

        for idx, subj in enumerate(subjects):
            row = idx // n_cols
            col = idx % n_cols
            ax = axes[row, col]

            subj_data = df_key[df_key['subject'] == subj]
            if len(subj_data) == 0 or f'z_{metric}' not in subj_data.columns:
                ax.text(0.5, 0.5, "No Data", ha='center', va='center', transform=ax.transAxes)
                ax.set_title(subj, fontsize=14)
                continue

            # 各processの平均
            means = []
            for proc in PROCS:
                vals = subj_data[subj_data['proc'] == proc][f'z_{metric}']
                means.append(vals.mean() if len(vals) > 0 else np.nan)

            ax.plot(range(len(PROCS)), means, 'o-', lw=1.5, markersize=6)
            ax.set_xticks(range(len(PROCS)))
            ax.set_xticklabels(PROCS, rotation=30, ha='right', fontsize=12)
            ax.axhline(0, color="gray", ls="--", lw=0.8, alpha=0.6)
            ax.grid(axis='y', alpha=0.3)
            ax.set_title(subj, fontsize=14, fontweight='bold')

        # 空のサブプロットを非表示
        for idx in range(n_subjects, n_rows * n_cols):
            row = idx // n_cols
            col = idx % n_cols
            axes[row, col].axis('off')

        # Y軸ラベル
        for row in range(n_rows):
            axes[row, 0].set_ylabel(ylabel, fontsize=14)

        plt.tight_layout()
        out_name = f"{condition}_{metric}_{img_key}_subjects_lines.png"
        plt.savefig(os.path.join(compare_dir, out_name), dpi=150, bbox_inches='tight')
        plt.close()

    print(f"    保存: subjects_by_imagekey/lines/ ({len(all_keys)} files)")


def plot_subjects_by_imagekey_bars(df, condition, metric, out_dir):
    """
    imagekey別に全被験者の平均棒グラフを比較表示
    各imagekeyにつき1ファイル、被験者ごとに1サブプロット
    """
    metric_info = {
        'miosis_rate': ('縮瞳率', 'z-scored Miosis Rate'),
        'diopter': ('輻輳 (D)', 'z-scored Diopter (D)'),
        'distance_mm': ('輻輳距離 (mm)', 'z-scored Diopter (D)'),
        'RT': ('ボタン反応時間 (ms)', 'z-scored RT (ms)'),
        'miosis_RT': ('縮瞳反応時間 (s)', 'z-scored Miosis RT (s)')
    }

    if metric not in metric_info:
        return

    title_jp, ylabel = metric_info[metric]

    # 出力ディレクトリ
    compare_dir = os.path.join(out_dir, "subjects_by_imagekey", "bars")
    os.makedirs(compare_dir, exist_ok=True)

    subjects = sorted(df['subject'].unique())
    n_subjects = len(subjects)

    # 行列レイアウトを計算
    n_cols = min(5, n_subjects)
    n_rows = (n_subjects + n_cols - 1) // n_cols

    # 各imagekeyについてファイルを作成
    all_keys = IMAGE_KEYS + ["ALL", "ALL_sun", "ALL_rain"]

    for img_key in all_keys:
        # データフィルタリング
        if img_key == "ALL":
            df_key = df[df["proc"].isin(PROCS)].copy()
        elif img_key == "ALL_sun":
            df_key = df[(df["image_key"].isin(["sun_empty", "sun_busy"])) & (df["proc"].isin(PROCS))].copy()
        elif img_key == "ALL_rain":
            df_key = df[(df["image_key"].isin(["rain_empty", "rain_busy"])) & (df["proc"].isin(PROCS))].copy()
        else:
            df_key = df[(df["image_key"] == img_key) & (df["proc"].isin(PROCS))].copy()

        # ディオプター関連の場合、範囲外を除外
        if metric in ['diopter', 'distance_mm'] and 'diopter_out_of_range' in df_key.columns:
            df_key = df_key[df_key['diopter_out_of_range'] == False].copy()

        if len(df_key) == 0:
            continue

        fig, axes = plt.subplots(n_rows, n_cols, figsize=(4*n_cols, 3*n_rows), sharey=True)
        fig.suptitle(f"{condition} - {title_jp} / {img_key} / 被験者間比較（棒グラフ）", fontsize=20, fontweight='bold')

        if n_subjects == 1:
            axes = np.array([[axes]])
        elif n_rows == 1:
            axes = axes.reshape(1, -1)

        bar_colors = ['steelblue', 'orange', 'green']

        for idx, subj in enumerate(subjects):
            row = idx // n_cols
            col = idx % n_cols
            ax = axes[row, col]

            subj_data = df_key[df_key['subject'] == subj]
            if len(subj_data) == 0 or f'z_{metric}' not in subj_data.columns:
                ax.text(0.5, 0.5, "No Data", ha='center', va='center', transform=ax.transAxes)
                ax.set_title(subj, fontsize=14)
                continue

            # 各processの平均とSEM
            means = subj_data.groupby('proc')[f'z_{metric}'].mean().reindex(PROCS)
            sems = subj_data.groupby('proc')[f'z_{metric}'].sem().reindex(PROCS)

            x_pos = np.arange(len(PROCS))
            ax.bar(x_pos, means, yerr=sems, capsize=3, alpha=0.75, color=bar_colors)
            ax.set_xticks(x_pos)
            ax.set_xticklabels(PROCS, rotation=30, ha='right', fontsize=12)
            ax.axhline(0, color="gray", ls="--", lw=0.8, alpha=0.6)
            ax.grid(axis='y', alpha=0.3)
            ax.set_title(subj, fontsize=14, fontweight='bold')

        # 空のサブプロットを非表示
        for idx in range(n_subjects, n_rows * n_cols):
            row = idx // n_cols
            col = idx % n_cols
            axes[row, col].axis('off')

        # Y軸ラベル
        for row in range(n_rows):
            axes[row, 0].set_ylabel(ylabel, fontsize=14)

        plt.tight_layout()
        out_name = f"{condition}_{metric}_{img_key}_subjects_bars.png"
        plt.savefig(os.path.join(compare_dir, out_name), dpi=150, bbox_inches='tight')
        plt.close()

    print(f"    保存: subjects_by_imagekey/bars/ ({len(all_keys)} files)")



def _plot_subject_lines_single(ax, sub, title, metric, subjects, colors):
    """被験者ごとの折れ線（全員重ね）"""
    if len(sub) == 0 or f'z_{metric}' not in sub.columns:
        ax.text(0.5, 0.5, "No Data", ha='center', va='center', transform=ax.transAxes)
        ax.set_title(title)
        return

    x_pos = np.arange(len(PROCS))

    # 第1パス：各被験者のラインを描画
    for i, subj in enumerate(subjects):
        subj_data = sub[sub['subject'] == subj]
        if len(subj_data) == 0:
            continue

        means = []
        for proc in PROCS:
            vals = subj_data[subj_data['proc'] == proc][f'z_{metric}']
            means.append(vals.mean() if len(vals) > 0 else np.nan)

        ax.plot(x_pos, means, 'o-', color=colors[i], lw=1.2, markersize=4, alpha=0.7)

    ax.set_xticks(x_pos)
    ax.set_xticklabels(PROCS, rotation=15, ha='right')
    ax.axhline(0, color="gray", ls="--", lw=0.8, alpha=0.6)
    ax.grid(axis='y', alpha=0.3)
    ax.set_title(title, fontsize=10, fontweight='bold')


def _plot_single(ax, sub, title, metric, test_type):
    if len(sub) == 0:
        ax.text(0.5, 0.5, "No Data", ha='center', va='center', transform=ax.transAxes)
        ax.set_title(title)
        return

    # ディオプター関連の指標の場合、範囲外データを除外
    if metric in ['diopter', 'distance_mm'] and 'diopter_out_of_range' in sub.columns:
        sub = sub[sub['diopter_out_of_range'] == False].copy()
        if len(sub) == 0:
            ax.text(0.5, 0.5, "No Data\n(all out of range)", ha='center', va='center', transform=ax.transAxes)
            ax.set_title(title)
            return

    # 指標のz-scoreがNaNのデータを除外（方向性フィルタや3σ外れ値によるもの）
    sub = sub.dropna(subset=[f"z_{metric}"]).copy()
    if len(sub) == 0:
        ax.text(0.5, 0.5, "No Data", ha='center', va='center', transform=ax.transAxes)
        ax.set_title(title)
        return

    means = sub.groupby("proc")[f"z_{metric}"].mean().reindex(PROCS)
    sems = sub.groupby("proc")[f"z_{metric}"].sem().reindex(PROCS)

    x_pos = np.arange(len(PROCS))
    colors = ['steelblue', 'orange', 'green']  # ここは既存維持（あなたの元コード通り）
    ax.bar(x_pos, means, yerr=sems, capsize=5, alpha=0.75, color=colors)
    ax.set_xticks(x_pos)
    ax.set_xticklabels(PROCS, rotation=0, ha='center', fontsize=FONT_SIZE_XLABEL)
    ax.tick_params(axis='y', labelsize=FONT_SIZE_TICK)

    # 基準線（0）とグリッドの太さを調整
    ax.axhline(0, color="gray", ls="--", lw=LINE_WIDTH_ZERO, alpha=0.8)
    ax.grid(axis='y', alpha=0.4, lw=LINE_WIDTH_GRID)

    # 外枠（Spines）を太くする
    for spine in ax.spines.values():
        spine.set_linewidth(LINE_WIDTH_SPINE)

    if test_type == 'oneway':
        F, p, tukey, eta_sq = run_anova(sub, metric)
        if F is None:
            ax.set_title(f"{title}\nInsufficient Data", fontsize=22, fontweight='bold')
            return

        df_between = len(PROCS) - 1
        df_within = len(sub) - len(PROCS)
        sig = " ***" if p < 0.001 else " **" if p < 0.01 else " *" if p < 0.05 else ""
        # 1行目: image_key, 2行目: ANOVA F値, 3行目: p値と効果量
        test_text = f"One-way ANOVA: F({df_between},{df_within})={F:.2f}\np={p:.3g}, η²={eta_sq:.3f}{sig}"
        ax.set_title(f"{title}\n{test_text}", fontsize=FONT_SIZE_TITLE, fontweight='bold')

        sig_pairs = []
        if tukey is not None:
            for res in tukey.summary().data[1:]:
                if len(res) >= 6:
                    g1, g2, _, pval, _, _ = res[:6]
                    try:
                        x1, x2 = PROCS.index(g1), PROCS.index(g2)
                        grp1 = sub[sub["proc"] == g1][f"z_{metric}"].values
                        grp2 = sub[sub["proc"] == g2][f"z_{metric}"].values
                        d = (np.mean(grp1) - np.mean(grp2)) / np.sqrt(
                            (np.std(grp1, ddof=1)**2 + np.std(grp2, ddof=1)**2) / 2
                        )
                        sig_pairs.append((x1, x2, pval, d))
                    except:
                        pass


        if sig_pairs:
            # p < 0.05 のペアのみ表示
            sig_pairs_filtered = [(x1, x2, p, d) for x1, x2, p, d in sig_pairs if p < 0.05]
            if sig_pairs_filtered:
                y_max = max(means + sems)
                add_sig_lines(ax, sig_pairs_filtered, y_max)

    else:  # RM-ANOVA
        rm_result = run_rm_anova(sub, metric)
        if rm_result is None:
            ax.set_title(f"{title}, RM-ANOVA: N/A", fontsize=FONT_SIZE_TITLE, fontweight='bold')
            return

        sig = " ***" if rm_result['p'] < 0.001 else " **" if rm_result['p'] < 0.01 else " *" if rm_result['p'] < 0.05 else ""
        test_text = (
            f"RM-ANOVA: F({rm_result['df_effect']:.0f},{rm_result['df_error']:.0f})={rm_result['F']:.2f}\n"
            f"p={rm_result['p']:.3g}, η²p={rm_result['eta_sq']:.3f}, N={rm_result['n_subjects']}{sig}"
        )
        ax.set_title(f"{title}\n{test_text}", fontsize=FONT_SIZE_TITLE, fontweight='bold')

        sig_pairs = []
        df_agg = sub.groupby(['subject', 'proc'])[f'z_{metric}'].mean().reset_index()
        subject_proc_counts = df_agg.groupby('subject')['proc'].nunique()
        complete_subjects = subject_proc_counts[subject_proc_counts == len(PROCS)].index
        df_complete = df_agg[df_agg['subject'].isin(complete_subjects)].copy()

        if len(df_complete) > 0:
            df_pivot = df_complete.pivot(index='subject', columns='proc', values=f'z_{metric}')
            for i, j in combinations(range(len(PROCS)), 2):
                g1 = df_pivot[PROCS[i]].values
                g2 = df_pivot[PROCS[j]].values
                t, p_pair = stats.ttest_rel(g1, g2)
                d = cohen_d(g1, g2)
                sig_pairs.append((i, j, p_pair, d))


        if sig_pairs:
            # p < 0.05 のペアのみ表示
            sig_pairs_filtered = [(x1, x2, p, d) for x1, x2, p, d in sig_pairs if p < 0.05]
            if sig_pairs_filtered:
                y_max = max(means + sems)
                add_sig_lines(ax, sig_pairs_filtered, y_max)


# =====================
# メイン処理
# =====================
def main():
    print(f"\n{'='*60}")
    print(f"統合分析（縮瞳・輻輳・反応速度）")
    print(f"パラメータ: {params}, n={n}")
    print(f"{'='*60}\n")

    for condition, file_path in DATA.items():
        print(f"\n{'='*60}")
        print(f"{condition} 条件の解析")
        print(f"{'='*60}")

        cond_out_dir = os.path.join(OUT_DIR, condition)
        os.makedirs(cond_out_dir, exist_ok=True)

        df_raw = pd.read_excel(file_path, engine='openpyxl')
        df = preprocess(df_raw, condition)

        exclude_list = EXCLUDE_SUBJECTS_MAP.get(condition, [])
        if exclude_list:
            print(f"  除外被験者: {exclude_list}")

        if len(df) == 0:
            print(f"  ERROR: データなし")
            continue

        print(f"  データ数: {len(df)} 行")
        print(f"  被験者数: {df['subject'].nunique()}")

        # ★使用する指標（マルチベースライン削除後）
        metrics = ['miosis_rate', 'diopter', 'distance_mm', 'RT', 'miosis_RT']
        available = [m for m in metrics if m in df.columns and f"z_{m}" in df.columns]
        print(f"  利用可能指標: {', '.join(available)}")

        # =========================
        # ★被験者ごとフォルダ出力（時間がかかるのでコメントアウト）
        # =========================
        # per_subject_root = os.path.join(cond_out_dir, "per_subject")
        # os.makedirs(per_subject_root, exist_ok=True)
        # print(f"  被験者別出力: {per_subject_root}")
        # for metric in available:
        #     df_metric_sub = df.dropna(subset=[f"z_{metric}"]).copy()
        #     plot_per_subject_metric_panels(df_metric_sub, condition, metric, per_subject_root)

        # =========================
        # 全体分析（検定あり）- フォルダを集約
        # =========================
        # One-way ANOVA フォルダ
        oneway_dir = os.path.join(cond_out_dir, "oneway")
        os.makedirs(oneway_dir, exist_ok=True)

        # RM-ANOVA フォルダ（対応ありCohen's dを使用）
        rm_dir = os.path.join(cond_out_dir, "rm")
        os.makedirs(rm_dir, exist_ok=True)

        for metric in available:
            print(f"\n  [{metric}] 分析中...")

            # その指標が有効（NaNでない）データのみで分析・プロットを行う
            df_metric = df.dropna(subset=[f"z_{metric}"]).copy()
            if len(df_metric) == 0:
                print(f"    警告: 有効なデータがありません")
                continue

            # One-way ANOVA（全指標を同じフォルダに出力）
            print(f"    One-way ANOVA:")
            plot_analysis(df_metric, condition, metric, 'oneway', None, oneway_dir)

            # RM-ANOVA（対応ありCohen's dを使用）
            print(f"    RM-ANOVA:")
            plot_analysis(df_metric, condition, metric, 'rm', None, rm_dir)

            # 以下の処理は時間がかかるためコメントアウト
            # # 被験者別推移（全員重ね）
            # print(f"    被験者別推移（全員重ね）:")
            # subject_dir = os.path.join(cond_out_dir, "subject_lines")
            # os.makedirs(subject_dir, exist_ok=True)
            # plot_subject_lines(df_metric, condition, metric, subject_dir)

            # # 被験者間比較（imagekey別）
            # print(f"    被験者間比較（imagekey別）:")
            # plot_subjects_by_imagekey_lines(df_metric, condition, metric, cond_out_dir)
            # plot_subjects_by_imagekey_bars(df_metric, condition, metric, cond_out_dir)

            # # 分布分析（箱ひげ図、ペア変化、ヒストグラム）
            # print(f"    分布分析:")
            # plot_distribution_analysis(df_metric, condition, metric, cond_out_dir)

        # RT vs miosis_RT 相関分析（コメントアウト）
        # print(f"\n  [RT vs miosis_RT] 相関分析...")
        # corr_dir = os.path.join(cond_out_dir, "correlation")
        # os.makedirs(corr_dir, exist_ok=True)
        # plot_rt_correlation(df, condition, corr_dir)

        # Trial進行プロット（時間がかかるのでコメントアウト）
        # plot_trial_progression_per_subject(df, condition, cond_out_dir)

    print(f"\n{'='*60}")
    print("[完了] 全解析完了")
    print(f"出力先: {OUT_DIR}")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()
