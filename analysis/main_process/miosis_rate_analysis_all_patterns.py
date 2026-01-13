# -*- coding: utf-8 -*-
"""
miosis_rate_analysis_all_patterns.py
------------------------------------
縮瞳率の統計解析 - 全パターン対応版

【検定パターン】
- ABC: original, brightonly, model の3群
- BC: brightonly, model の2群
- AB: original, brightonly の2群
- AC: original, model の2群

【検定方法】
- One-way ANOVA (通常の分散分析)
- RM-ANOVA (Repeated Measures ANOVA)

【出力】
- 各パターン×各検定方法で、カギ括弧あり/なしの2種類のグラフ
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy import stats
from statsmodels.stats.anova import AnovaRM
from statsmodels.stats.multicomp import pairwise_tukeyhsd
import os
import warnings
warnings.filterwarnings('ignore')

plt.rcParams['font.family'] = 'MS Gothic'
plt.rcParams['axes.unicode_minus'] = False

# =====================
# 設定
# =====================
# 最新の統合ファイルを自動検出
import glob
import re
n = int(input("被験者何人入りのデータ使う？: "))
bright_file = f"../../data/integrated_2025_metrics/merged/integrated_bright_metrics_n{n}.xlsx"
dark_file = f"../../data/integrated_2025_metrics/merged/integrated_dark_metrics_n{n}.xlsx"

# ファイル存在確認
if not os.path.exists(bright_file) or not os.path.exists(dark_file):
    raise FileNotFoundError(f"統合ファイルが見つかりません: {bright_file}, {dark_file}\nintegrate_metrics.pyを先に実行してください。")

DATA = {
    "Bright": bright_file,
    "Dark": dark_file,
}

IMAGE_KEYS = ["sun_empty", "sun_busy", "rain_empty", "rain_busy"]

# 検定パターン
TEST_PATTERNS = {
    "ABC": ["original", "brightonly", "model"],
    "BC": ["brightonly", "model"],
    "AB": ["original", "brightonly"],
    "AC": ["original", "model"]
}

# n{num}フォルダを作成（data/statistics/内）
OUT_DIR = os.path.join("../../data/statistics", f"n{n}")
os.makedirs(OUT_DIR, exist_ok=True)


# =====================
# 前処理関数
# =====================
def preprocess(df, value_col='pupil_both_change_rate_mean'):
    """前処理：FrontIsDigit抽出、z-score標準化、外れ値除去"""
    df = df.copy()

    if 'FrontIsDigit_inferred' in df.columns:
        df = df[df['FrontIsDigit_inferred'] == True].copy()

    def extract_image_key(row):
        if 'filename' in df.columns and pd.notna(row.get('filename')):
            path_str = str(row['filename'])
            for key in IMAGE_KEYS:
                if key in path_str:
                    return key

        if 'Back_Image_Name_Used' in df.columns and pd.notna(row.get('Back_Image_Name_Used')):
            name_str = str(row['Back_Image_Name_Used'])
            for key in IMAGE_KEYS:
                if key in name_str:
                    return key
        return None

    df['image_key'] = df.apply(extract_image_key, axis=1)

    rename_map = {
        'folder_name': 'subject',
        'process': 'proc',
        value_col: 'miosis_rate'
    }
    df = df.rename(columns=rename_map)

    required_cols = ['subject', 'image_key', 'proc', 'miosis_rate']
    df = df[required_cols].copy()
    df = df.dropna(subset=['miosis_rate', 'image_key', 'proc'])

    # 被験者内z-score標準化
    df['z_miosis'] = df.groupby('subject')['miosis_rate'].transform(
        lambda x: (x - x.mean()) / x.std(ddof=1) if x.std() > 0 else 0
    )

    # 3σ外れ値除去
    df = df[df['z_miosis'].abs() < 3].copy()

    return df


# =====================
# Cohen's d 効果量
# =====================
def cohen_d(group1, group2):
    """Cohen's d効果量を計算（対応あり）"""
    diff = group1 - group2
    return np.mean(diff) / np.std(diff, ddof=1)


# =====================
# One-Way ANOVA
# =====================
def run_anova(df_sub, procs):
    """One-way ANOVA + Tukey HSD"""
    groups = [df_sub[df_sub["proc"] == p]["z_miosis"] for p in procs]

    if any(len(g) == 0 for g in groups):
        return None, None, None

    # 2群の場合はt検定、3群以上はANOVA
    if len(procs) == 2:
        # 独立2標本t検定
        t_stat, p_val = stats.ttest_ind(groups[0], groups[1])
        F = t_stat ** 2  # t^2 = F
        tukey = None  # 2群なのでpost-hocは不要
    else:
        F, p_val = stats.f_oneway(*groups)
        tukey = pairwise_tukeyhsd(
            endog=df_sub["z_miosis"],
            groups=df_sub["proc"],
            alpha=0.05
        )

    return F, p_val, tukey


# =====================
# Repeated Measures ANOVA
# =====================
def run_rm_anova(df_sub, procs):
    """Repeated Measures ANOVA + 効果量"""
    subject_proc_counts = df_sub.groupby('subject')['proc'].nunique()
    complete_subjects = subject_proc_counts[subject_proc_counts == len(procs)].index

    df_complete = df_sub[df_sub['subject'].isin(complete_subjects)].copy()

    if len(df_complete) == 0 or len(complete_subjects) == 0:
        return None

    # 2群の場合は対応のあるt検定
    if len(procs) == 2:
        df_agg = df_complete.groupby(['subject', 'proc'])['z_miosis'].mean().reset_index()
        df_pivot = df_agg.pivot(index='subject', columns='proc', values='z_miosis')

        if len(df_pivot) < 2:
            return None

        g1 = df_pivot[procs[0]].values
        g2 = df_pivot[procs[1]].values

        t_stat, p_val = stats.ttest_rel(g1, g2)
        F = t_stat ** 2

        # 効果量（Cohen's d）
        d = cohen_d(g1, g2)

        return {
            'F': F,
            'p': p_val,
            'eta_sq': d ** 2 / (d ** 2 + len(complete_subjects)),  # 近似
            'n_subjects': len(complete_subjects),
            'table': None
        }

    try:
        df_agg = df_complete.groupby(['subject', 'proc'])['z_miosis'].mean().reset_index()

        aovrm = AnovaRM(df_agg, depvar='z_miosis', subject='subject', within=['proc'])
        res = aovrm.fit()

        anova_table = res.anova_table
        f_stat = anova_table.loc['proc', 'F Value']
        p_val = anova_table.loc['proc', 'Pr > F']

        df_effect = anova_table.loc['proc', 'Num DF']
        df_error = anova_table.loc['proc', 'Den DF']
        partial_eta_sq = (f_stat * df_effect) / (f_stat * df_effect + df_error)

        return {
            'F': f_stat,
            'p': p_val,
            'eta_sq': partial_eta_sq,
            'n_subjects': len(complete_subjects),
            'table': anova_table
        }
    except Exception as e:
        print(f"    RM-ANOVA Error: {e}")
        return None


# =====================
# 有意差線描画
# =====================
def add_sig_lines(ax, pairs, y_max):
    """有意な組み合わせにカギカッコとp値、効果量を描画"""
    step = 0.25
    for i, (x1, x2, p, d) in enumerate(pairs):
        y = y_max + step * (i + 0.5)
        ax.plot([x1, x1, x2, x2], [y, y+0.05, y+0.05, y], lw=1.2, c="black")

        if p < 0.001:
            sig_text = "***"
        elif p < 0.01:
            sig_text = "**"
        elif p < 0.05:
            sig_text = "*"
        else:
            sig_text = "n.s."

        # p値と効果量を表示
        text = f"{sig_text}\np={p:.3f}, d={d:.2f}"
        ax.text((x1+x2)/2, y+0.06, text, ha="center", va="bottom",
               fontsize=8, fontweight='bold')


# =====================
# グラフ描画関数
# =====================
def plot_pattern(df, cond, pattern_name, procs, test_type, draw_sig_lines, out_dir):
    """
    指定されたパターンと検定方法でグラフを作成

    Parameters:
    -----------
    df : DataFrame
        データ
    cond : str
        条件名 (Bright/Dark)
    pattern_name : str
        検定パターン名 (ABC/BC/AB/AC)
    procs : list
        処理方法のリスト
    test_type : str
        'oneway' or 'rm'
    draw_sig_lines : bool
        有意差線を描画するか
    out_dir : str
        出力ディレクトリ
    """
    fig, axes = plt.subplots(1, 4, figsize=(18, 4.5), sharey=True)

    # タイトル
    test_name = "One-way ANOVA" if test_type == 'oneway' else "RM-ANOVA"
    sig_suffix = "with_sig" if draw_sig_lines else "no_sig"
    title = f"{cond} / {pattern_name} ({', '.join(procs)}) / {test_name}"
    fig.suptitle(title, fontsize=14, fontweight='bold')

    results_dict = {}

    for ax, img_key in zip(axes, IMAGE_KEYS):
        sub = df[(df["image_key"] == img_key) & (df["proc"].isin(procs))].copy()

        if len(sub) == 0:
            ax.text(0.5, 0.5, "No Data", ha='center', va='center',
                   transform=ax.transAxes)
            ax.set_title(img_key)
            continue

        # 記述統計
        means = sub.groupby("proc")["z_miosis"].mean().reindex(procs)
        sems = sub.groupby("proc")["z_miosis"].sem().reindex(procs)
        ns = sub.groupby("proc")["z_miosis"].count().reindex(procs)

        # 棒グラフ描画
        x_pos = np.arange(len(procs))
        colors = {'original': 'steelblue', 'brightonly': 'orange', 'model': 'green'}
        bar_colors = [colors[p] for p in procs]

        ax.bar(x_pos, means, yerr=sems, capsize=5, alpha=0.75, color=bar_colors)
        ax.set_xticks(x_pos)
        ax.set_xticklabels(procs, rotation=15, ha='right')
        ax.axhline(0, color="gray", ls="--", lw=0.8, alpha=0.6)
        ax.grid(axis='y', alpha=0.3)

        # 統計検定
        if test_type == 'oneway':
            F, p, tukey = run_anova(sub, procs)

            if F is None:
                ax.set_title(f"{img_key}\nInsufficient Data", fontsize=11, fontweight='bold')
                continue

            # 自由度
            df_between = len(procs) - 1
            n_total = len(sub)
            df_within = n_total - len(procs)

            # 結果表示
            sig_mark = ""
            if p < 0.001:
                sig_mark = " ***"
            elif p < 0.01:
                sig_mark = " **"
            elif p < 0.05:
                sig_mark = " *"

            test_text = f"One-way ANOVA: F({df_between}, {df_within})={F:.2f}, p={p:.3g}{sig_mark}"
            # タイトルに統計情報を含める
            ax.set_title(f"{img_key}\n{test_text}", fontsize=10, fontweight='bold')

            # 有意差線描画
            if draw_sig_lines:
                sig_pairs = []

                if len(procs) == 2:
                    # 2群比較
                    g1 = sub[sub["proc"] == procs[0]]["z_miosis"].values
                    g2 = sub[sub["proc"] == procs[1]]["z_miosis"].values
                    d = np.mean(g1 - g2) / np.std(g1 - g2, ddof=1) if len(g1) == len(g2) else 0
                    sig_pairs.append((0, 1, p, d))
                else:
                    # 3群比較 - Tukey HSD結果から（有意でなくてもp値表示）
                    if tukey is not None:
                        for res in tukey.summary().data[1:]:
                            if len(res) >= 6:
                                g1, g2, _, pval, _, reject = res[:6]
                            else:
                                continue

                            # 有意差に関わらず全ペアを表示
                            try:
                                x1 = procs.index(g1)
                                x2 = procs.index(g2)
                                # Cohen's d計算
                                grp1 = sub[sub["proc"] == g1]["z_miosis"].values
                                grp2 = sub[sub["proc"] == g2]["z_miosis"].values
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
            rm_result = run_rm_anova(sub, procs)

            if rm_result is None:
                ax.set_title(f"{img_key}\nRM-ANOVA: Not applicable", fontsize=11, fontweight='bold')
                continue

            sig_mark = ""
            if rm_result['p'] < 0.001:
                sig_mark = " ***"
            elif rm_result['p'] < 0.01:
                sig_mark = " **"
            elif rm_result['p'] < 0.05:
                sig_mark = " *"

            test_text = f"RM-ANOVA: F={rm_result['F']:.2f}, p={rm_result['p']:.3g}"
            test_text += f", η²p={rm_result['eta_sq']:.3f}, N={rm_result['n_subjects']}{sig_mark}"

            # タイトルに統計情報を含める
            ax.set_title(f"{img_key}\n{test_text}", fontsize=10, fontweight='bold')

            # 有意差線描画（RM-ANOVAでも対応あるt検定のペアを表示）
            if draw_sig_lines:
                sig_pairs = []

                # 各被験者の平均値を取得
                df_agg = sub.groupby(['subject', 'proc'])['z_miosis'].mean().reset_index()
                subject_proc_counts = df_agg.groupby('subject')['proc'].nunique()
                complete_subjects = subject_proc_counts[subject_proc_counts == len(procs)].index
                df_complete = df_agg[df_agg['subject'].isin(complete_subjects)].copy()

                if len(procs) == 2:
                    # 2群の場合
                    df_pivot = df_complete.pivot(index='subject', columns='proc', values='z_miosis')
                    g1 = df_pivot[procs[0]].values
                    g2 = df_pivot[procs[1]].values
                    d = cohen_d(g1, g2)
                    sig_pairs.append((0, 1, rm_result['p'], d))
                else:
                    # 3群の場合 - 全ペア対応のあるt検定（有意差に関わらず表示）
                    from itertools import combinations
                    for i, j in combinations(range(len(procs)), 2):
                        df_pivot = df_complete.pivot(index='subject', columns='proc', values='z_miosis')
                        g1 = df_pivot[procs[i]].values
                        g2 = df_pivot[procs[j]].values
                        t, p_pair = stats.ttest_rel(g1, g2)
                        d = cohen_d(g1, g2)
                        sig_pairs.append((i, j, p_pair, d))

                if sig_pairs:
                    y_max = max(means + sems)
                    add_sig_lines(ax, sig_pairs, y_max)

    axes[0].set_ylabel("z-scored Miosis Rate", fontsize=11)
    plt.tight_layout()

    # パターン別のサブフォルダを作成
    pattern_out_dir = os.path.join(out_dir, pattern_name)
    os.makedirs(pattern_out_dir, exist_ok=True)

    # 保存
    out_file = f"{cond}_{pattern_name}_{test_type}_{sig_suffix}.png"
    out_path = os.path.join(pattern_out_dir, out_file)
    plt.savefig(out_path, dpi=300, bbox_inches='tight')
    print(f"    保存: {pattern_name}/{out_file}")
    plt.close()


# =====================
# メイン処理
# =====================
def main():
    for cond, path in DATA.items():
        print(f"\n{'='*60}")
        print(f"{cond} 条件の解析")
        print(f"{'='*60}")

        # 条件ごとの出力フォルダ (n{num}/Bright or n{num}/Dark)
        cond_out_dir = os.path.join(OUT_DIR, cond)
        os.makedirs(cond_out_dir, exist_ok=True)

        # データ読み込み・前処理
        df = pd.read_excel(path)
        df = preprocess(df)

        if len(df) == 0:
            print(f"  ERROR: データなし")
            continue

        print(f"  データ数: {len(df)} 行")

        # 全パターンを実行
        for pattern_name, procs in TEST_PATTERNS.items():
            print(f"\n  [{pattern_name}] {', '.join(procs)}")

            # One-way ANOVA
            print(f"    One-way ANOVA:")
            plot_pattern(df, cond, pattern_name, procs, 'oneway', True, cond_out_dir)
            plot_pattern(df, cond, pattern_name, procs, 'oneway', False, cond_out_dir)

            # RM-ANOVA
            print(f"    RM-ANOVA:")
            plot_pattern(df, cond, pattern_name, procs, 'rm', True, cond_out_dir)
            plot_pattern(df, cond, pattern_name, procs, 'rm', False, cond_out_dir)

    print(f"\n{'='*60}")
    print("[完了] 全パターンの解析が完了しました")
    print(f"{'='*60}")


if __name__ == '__main__':
    main()
