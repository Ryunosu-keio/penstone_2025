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
import os
import warnings
warnings.filterwarnings('ignore')

plt.rcParams['font.family'] = 'MS Gothic'
plt.rcParams['axes.unicode_minus'] = False


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

DATA = {"Bright": bright_file, "Dark": dark_file}
IMAGE_KEYS = ["sun_empty", "sun_busy", "rain_empty", "rain_busy"]
PROCS = ["original", "brightonly", "model"]

# 出力先
total_excluded = len(EXCLUDE_SUBJECTS_BRIGHT) + len(EXCLUDE_SUBJECTS_DARK)
if total_excluded > 0:
    exclude_suffix = f"_excludeB{len(EXCLUDE_SUBJECTS_BRIGHT)}D{len(EXCLUDE_SUBJECTS_DARK)}"
    OUT_DIR = os.path.join("../../data/statistics", params, f"n{n}{exclude_suffix}", "integrated")
else:
    OUT_DIR = os.path.join("../../data/statistics", params, f"n{n}", "integrated")
os.makedirs(OUT_DIR, exist_ok=True)


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
        df['distance_mm'] = 1000.0 / df['diopter']
    else:
        df['distance_mm'] = np.nan

    # 必要なカラム
    required = ['subject', 'image_key', 'proc', 'miosis_rate', 'diopter', 'distance_mm', 'RT', 'miosis_RT']
    df = df[[col for col in required if col in df.columns]].copy()
    df = df.dropna(subset=['image_key', 'proc'])

    # 各指標をz-score標準化（被験者内）
    for metric in ['miosis_rate', 'diopter', 'distance_mm', 'RT', 'miosis_RT']:
        if metric in df.columns:
            df[f'z_{metric}'] = df.groupby('subject')[metric].transform(
                lambda x: (x - x.mean()) / x.std(ddof=1) if x.std(ddof=1) > 0 else 0
            )
            # 3σ外れ値除去（指標ごとに適用）
            df = df[df[f'z_{metric}'].abs() < 3].copy()

    return df


# =====================
# 統計検定
# =====================
def cohen_d(g1, g2):
    diff = g1 - g2
    sd = np.std(diff, ddof=1)
    return np.mean(diff) / sd if sd > 0 else 0

def run_anova(df_sub, metric):
    groups = [df_sub[df_sub["proc"] == p][f"z_{metric}"] for p in PROCS]
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
    step = 0.25
    for i, (x1, x2, p, d) in enumerate(pairs):
        y = y_max + step * (i + 0.5)
        ax.plot([x1, x1, x2, x2], [y, y+0.05, y+0.05, y], lw=1.2, c="black")

        sig = "***" if p < 0.001 else "**" if p < 0.01 else "*" if p < 0.05 else "n.s."
        ax.text((x1+x2)/2, y+0.06, f"{sig}\np={p:.3f}, d={d:.2f}",
                ha="center", va="bottom", fontsize=8, fontweight='bold')


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
        ax.set_title(title, fontsize=10, fontweight='bold')
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
    ax.set_xticklabels(PROCS, rotation=15, ha='right', fontsize=8)
    ax.axhline(0, color="gray", ls="--", lw=0.8, alpha=0.6)
    ax.grid(axis='y', alpha=0.25)
    ax.set_title(title, fontsize=10, fontweight='bold')


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
        fig.suptitle(f"{condition} / {safe_subj} - {title_jp}（ABC差：被験者内傾向）", fontsize=14, fontweight='bold')

        # imagekey別4枚
        for ax, img_key in zip(axes[:4], IMAGE_KEYS):
            sub = df_s[(df_s["image_key"] == img_key) & (df_s["proc"].isin(PROCS))].copy()
            _plot_single_subject_no_test(ax, sub, img_key, metric)

        # ALL
        sub_all = df_s[df_s["proc"].isin(PROCS)].copy()
        _plot_single_subject_no_test(axes[4], sub_all, "ALL", metric)

        axes[0].set_ylabel(ylabel, fontsize=11)
        plt.tight_layout()

        out_name = f"{condition}_{metric}_panels.png"
        plt.savefig(os.path.join(subj_dir, out_name), dpi=300, bbox_inches='tight')
        plt.close(fig)


# =====================
# グラフ作成（全体/画像別 + 検定あり）
# =====================
def plot_analysis(df, condition, metric, test_type, split_by_imagekey, out_dir):
    """
    split_by_imagekey: True=imagekey別、False=全体統合
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

    if split_by_imagekey:
        fig, axes = plt.subplots(1, 4, figsize=(18, 4.5), sharey=True)
        fig.suptitle(f"{condition} - {title_jp} / ABC / {test_name} (imagekey別)",
                     fontsize=14, fontweight='bold')

        for ax, img_key in zip(axes, IMAGE_KEYS):
            sub = df[(df["image_key"] == img_key) & (df["proc"].isin(PROCS))].copy()
            _plot_single(ax, sub, img_key, metric, test_type)

        axes[0].set_ylabel(ylabel, fontsize=11)
        out_name = f"{condition}_{metric}_ABC_{test_type}_imagekey.png"
    else:
        fig, ax = plt.subplots(1, 1, figsize=(6, 5))
        fig.suptitle(f"{condition} - {title_jp} / ABC / {test_name} (全体)",
                     fontsize=14, fontweight='bold')

        sub = df[df["proc"].isin(PROCS)].copy()
        _plot_single(ax, sub, "ALL", metric, test_type)
        ax.set_ylabel(ylabel, fontsize=11)
        out_name = f"{condition}_{metric}_ABC_{test_type}_all.png"

    plt.tight_layout()
    plt.savefig(os.path.join(out_dir, out_name), dpi=300, bbox_inches='tight')
    print(f"    保存: {out_name}")
    plt.close()


def plot_subject_lines(df, condition, metric, out_dir):
    """被験者ごとの折れ線グラフ（全員重ね）: imagekey別 + all"""
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
    df_use = df.copy()

    fig, axes = plt.subplots(1, 5, figsize=(22, 4.5), sharey=True)
    fig.suptitle(f"{condition} - {title_jp} / 被験者別推移（全員重ね）", fontsize=14, fontweight='bold')

    subjects = sorted(df_use['subject'].unique())
    colors = plt.cm.tab20(np.linspace(0, 1, len(subjects)))

    for ax, img_key in zip(axes[:4], IMAGE_KEYS):
        sub = df_use[(df_use["image_key"] == img_key) & (df_use["proc"].isin(PROCS))].copy()
        _plot_subject_lines_single(ax, sub, img_key, metric, subjects, colors)

    sub_all = df_use[df_use["proc"].isin(PROCS)].copy()
    _plot_subject_lines_single(axes[4], sub_all, "ALL", metric, subjects, colors)

    axes[0].set_ylabel(ylabel, fontsize=11)

    handles = [plt.Line2D([0], [0], color=colors[i], lw=1.5, label=s)
               for i, s in enumerate(subjects)]
    axes[4].legend(handles=handles, loc='center left', bbox_to_anchor=(1.02, 0.5),
                   fontsize=7, title='Subject')

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
    fig.suptitle(f"{condition} - ボタン反応時間 vs 縮瞳反応時間", fontsize=14, fontweight='bold')

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
        ax.set_title(f"{title}\nr={r:.3f}{sig}, ρ={rho:.3f}, n={len(data)}", fontsize=10)
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
                   fontsize=7, title='Subject')

    plt.tight_layout()
    out_name = f"{condition}_RT_vs_miosisRT_correlation.png"
    plt.savefig(os.path.join(out_dir, out_name), dpi=300, bbox_inches='tight')
    print(f"    保存: {out_name}")
    plt.close()

    # proc別
    fig, axes = plt.subplots(1, 3, figsize=(15, 5))
    fig.suptitle(f"{condition} - ボタン反応時間 vs 縮瞳反応時間 (処理別)", fontsize=14, fontweight='bold')

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
            ax.set_title(f"{proc}\nr={r:.3f}{sig}, n={len(sub)}", fontsize=11)
        else:
            ax.set_title(f"{proc}\nNo Data", fontsize=11)

        ax.set_xlabel("ボタン反応時間 (ms)")
        ax.grid(alpha=0.3)

    axes[0].set_ylabel("縮瞳反応時間 (s)")
    plt.tight_layout()
    out_name = f"{condition}_RT_vs_miosisRT_by_proc.png"
    plt.savefig(os.path.join(out_dir, out_name), dpi=300, bbox_inches='tight')
    print(f"    保存: {out_name}")
    plt.close()


def _plot_subject_lines_single(ax, sub, title, metric, subjects, colors):
    """被験者ごとの折れ線（全員重ね）"""
    if len(sub) == 0 or f'z_{metric}' not in sub.columns:
        ax.text(0.5, 0.5, "No Data", ha='center', va='center', transform=ax.transAxes)
        ax.set_title(title)
        return

    x_pos = np.arange(len(PROCS))

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

    means = sub.groupby("proc")[f"z_{metric}"].mean().reindex(PROCS)
    sems = sub.groupby("proc")[f"z_{metric}"].sem().reindex(PROCS)

    x_pos = np.arange(len(PROCS))
    colors = ['steelblue', 'orange', 'green']  # ここは既存維持（あなたの元コード通り）
    ax.bar(x_pos, means, yerr=sems, capsize=5, alpha=0.75, color=colors)
    ax.set_xticks(x_pos)
    ax.set_xticklabels(PROCS, rotation=15, ha='right')
    ax.axhline(0, color="gray", ls="--", lw=0.8, alpha=0.6)
    ax.grid(axis='y', alpha=0.3)

    if test_type == 'oneway':
        F, p, tukey, eta_sq = run_anova(sub, metric)
        if F is None:
            ax.set_title(f"{title}\nInsufficient Data", fontsize=10, fontweight='bold')
            return

        df_between = len(PROCS) - 1
        df_within = len(sub) - len(PROCS)
        sig = " ***" if p < 0.001 else " **" if p < 0.01 else " *" if p < 0.05 else ""
        test_text = f"F({df_between},{df_within})={F:.2f}, p={p:.3g}, η²={eta_sq:.3f}{sig}"
        ax.set_title(f"{title}\n{test_text}", fontsize=10, fontweight='bold')

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
            y_max = max(means + sems)
            add_sig_lines(ax, sig_pairs, y_max)

    else:  # RM-ANOVA
        rm_result = run_rm_anova(sub, metric)
        if rm_result is None:
            ax.set_title(f"{title}\nRM-ANOVA: N/A", fontsize=10, fontweight='bold')
            return

        sig = " ***" if rm_result['p'] < 0.001 else " **" if rm_result['p'] < 0.01 else " *" if rm_result['p'] < 0.05 else ""
        test_text = (
            f"F({rm_result['df_effect']:.0f},{rm_result['df_error']:.0f})={rm_result['F']:.2f}, "
            f"p={rm_result['p']:.3g}, η²p={rm_result['eta_sq']:.3f}, N={rm_result['n_subjects']}{sig}"
        )
        ax.set_title(f"{title}\n{test_text}", fontsize=10, fontweight='bold')

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
            y_max = max(means + sems)
            add_sig_lines(ax, sig_pairs, y_max)


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

        metrics = ['miosis_rate', 'diopter', 'distance_mm', 'RT', 'miosis_RT']
        available = [m for m in metrics if m in df.columns and f"z_{m}" in df.columns]
        print(f"  利用可能指標: {', '.join(available)}")

        # =========================
        # ★被験者ごとフォルダ出力（傾向確認用）
        # =========================
        per_subject_root = os.path.join(cond_out_dir, "per_subject")
        os.makedirs(per_subject_root, exist_ok=True)
        print(f"  被験者別出力: {per_subject_root}")

        for metric in available:
            plot_per_subject_metric_panels(df, condition, metric, per_subject_root)

        # =========================
        # 以降：従来の全体分析（検定あり）
        # =========================
        for metric in available:
            print(f"\n  [{metric}] 分析中...")

            # One-way ANOVA
            print(f"    One-way ANOVA:")
            oneway_dir = os.path.join(cond_out_dir, "oneway")
            os.makedirs(oneway_dir, exist_ok=True)
            plot_analysis(df, condition, metric, 'oneway', True, oneway_dir)
            plot_analysis(df, condition, metric, 'oneway', False, oneway_dir)

            # RM-ANOVA
            print(f"    RM-ANOVA:")
            rm_dir = os.path.join(cond_out_dir, "rm")
            os.makedirs(rm_dir, exist_ok=True)
            plot_analysis(df, condition, metric, 'rm', True, rm_dir)
            plot_analysis(df, condition, metric, 'rm', False, rm_dir)

            # 被験者別推移（全員重ね）
            print(f"    被験者別推移（全員重ね）:")
            subject_dir = os.path.join(cond_out_dir, "subject_lines")
            os.makedirs(subject_dir, exist_ok=True)
            plot_subject_lines(df, condition, metric, subject_dir)

        # RT vs miosis_RT 相関分析
        print(f"\n  [RT vs miosis_RT] 相関分析...")
        corr_dir = os.path.join(cond_out_dir, "correlation")
        os.makedirs(corr_dir, exist_ok=True)
        plot_rt_correlation(df, condition, corr_dir)

    print(f"\n{'='*60}")
    print("[完了] 全解析完了")
    print(f"出力先: {OUT_DIR}")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()
