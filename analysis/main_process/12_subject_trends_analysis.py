# -*- coding: utf-8 -*-
"""
subject_trends_analysis.py
------------------------------------
被験者ごとの傾向分析（反応速度・縮瞳・輻輳）

【出力】
1. 被験者×処理方法のヒートマップ（3指標）
2. 被験者別の折れ線グラフ（処理方法比較）
3. 処理方法別の被験者間比較
4. 相関分析（3指標間の関係）
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
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
        item_path = os.path.join(base_dir, item)
        if os.path.isdir(item_path) and item.startswith("lag"):
            merged_dir = os.path.join(item_path, "merged")
            if os.path.exists(merged_dir):
                available_params.append(item)

if not available_params:
    raise FileNotFoundError(f"{base_dir} 内に利用可能なパラメータフォルダが見つかりません")

print("\n=== 利用可能な計算パラメータ ===")
for i, param in enumerate(available_params, 1):
    print(f"{i}. {param}")

param_idx = int(input(f"\n使用するパラメータを選択 (1-{len(available_params)}): ")) - 1
if param_idx < 0 or param_idx >= len(available_params):
    raise ValueError("無効な選択です")

params = available_params[param_idx]
print(f"\n選択されたパラメータ: {params}")

n = int(input("\n被験者何人入りのデータ使う？: "))

bright_file = f"../../data/log_with_emr_metrics/{params}/merged/integrated_bright_metrics_n{n}.xlsx"
dark_file = f"../../data/log_with_emr_metrics/{params}/merged/integrated_dark_metrics_n{n}.xlsx"

if not os.path.exists(bright_file) or not os.path.exists(dark_file):
    raise FileNotFoundError(f"統合ファイルが見つかりません")

DATA = {
    "Bright": bright_file,
    "Dark": dark_file,
}

OUT_DIR = os.path.join("../../data/statistics", params, f"n{n}", "subject_trends")
os.makedirs(OUT_DIR, exist_ok=True)


# =====================
# 前処理関数
# =====================
def preprocess_data(df):
    """3指標のデータを抽出・前処理"""
    df = df.copy()

    # FrontIsDigitのみ
    if 'FrontIsDigit_inferred' in df.columns:
        df = df[df['FrontIsDigit_inferred'] == True].copy()

    # カラム名統一
    rename_map = {
        'folder_name': 'subject',
        'process': 'proc',
        'pupil_both_change_rate_mean': 'miosis_rate',
        'diopter_delta': 'diopter',
        'Reaction_Time': 'RT'
    }
    df = df.rename(columns=rename_map)

    # 必要なカラムのみ抽出
    required_cols = ['subject', 'proc', 'miosis_rate', 'diopter', 'RT']
    df = df[[col for col in required_cols if col in df.columns]].copy()

    # 外れ値除去（3σ）
    for col in ['miosis_rate', 'diopter', 'RT']:
        if col in df.columns:
            df[f'{col}_z'] = df.groupby('subject')[col].transform(
                lambda x: (x - x.mean()) / x.std(ddof=1) if x.std() > 0 else 0
            )
            df = df[df[f'{col}_z'].abs() < 3].copy()

    return df


# =====================
# 被験者×処理方法のヒートマップ
# =====================
def plot_heatmap(df, metric, condition, out_dir):
    """被験者×処理方法のヒートマップ"""

    # 被験者×処理方法の平均値を計算
    pivot = df.pivot_table(values=metric, index='subject', columns='proc', aggfunc='mean')

    # 処理方法の順序を固定
    proc_order = ['original', 'brightonly', 'model']
    pivot = pivot[[col for col in proc_order if col in pivot.columns]]

    # ヒートマップ作成
    fig, ax = plt.subplots(figsize=(8, max(6, len(pivot)*0.4)))

    # z-score変換（被験者ごとの相対的な差を見る）
    pivot_z = pivot.sub(pivot.mean(axis=1), axis=0).div(pivot.std(axis=1, ddof=1), axis=0)

    # カラーマップ
    metric_info = {
        'RT': ('反応速度 (ms)', 'RdYlGn_r'),  # 遅い=赤、速い=緑
        'miosis_rate': ('縮瞳率', 'RdYlBu'),  # 小さい=赤、大きい=青
        'diopter': ('輻輳 (diopter)', 'RdYlBu')  # 小さい=赤、大きい=青
    }

    title, cmap = metric_info.get(metric, (metric, 'coolwarm'))

    sns.heatmap(pivot_z, annot=pivot, fmt='.2f', cmap=cmap, center=0,
                cbar_kws={'label': 'z-score (within subject)'},
                linewidths=0.5, ax=ax)

    ax.set_title(f'{condition} - {title}\n被験者×処理方法（数値は実測値、色はz-score）',
                 fontsize=12, fontweight='bold')
    ax.set_xlabel('処理方法', fontsize=11)
    ax.set_ylabel('被験者', fontsize=11)

    plt.tight_layout()
    out_path = os.path.join(out_dir, f'heatmap_{metric}_{condition}.png')
    plt.savefig(out_path, dpi=300, bbox_inches='tight')
    print(f"  保存: heatmap_{metric}_{condition}.png")
    plt.close()


# =====================
# 被験者別折れ線グラフ
# =====================
def plot_subject_lines(df, metric, condition, out_dir):
    """被験者別の折れ線グラフ（処理方法の比較）"""

    # 被験者×処理方法の平均値
    pivot = df.pivot_table(values=metric, index='subject', columns='proc', aggfunc='mean')

    proc_order = ['original', 'brightonly', 'model']
    pivot = pivot[[col for col in proc_order if col in pivot.columns]]

    # 被験者を3つのグループに分ける（1行に表示しきれない場合）
    subjects = pivot.index.tolist()
    n_per_plot = 10
    n_plots = (len(subjects) + n_per_plot - 1) // n_per_plot

    for plot_idx in range(n_plots):
        start_idx = plot_idx * n_per_plot
        end_idx = min(start_idx + n_per_plot, len(subjects))
        subjects_subset = subjects[start_idx:end_idx]

        fig, ax = plt.subplots(figsize=(10, 6))

        # 各被験者の折れ線を描画
        for subject in subjects_subset:
            values = pivot.loc[subject].values
            ax.plot(range(len(values)), values, marker='o', label=subject, alpha=0.7)

        ax.set_xticks(range(len(pivot.columns)))
        ax.set_xticklabels(pivot.columns)
        ax.set_xlabel('処理方法', fontsize=11)

        metric_info = {
            'RT': '反応速度 (ms)',
            'miosis_rate': '縮瞳率',
            'diopter': '輻輳 (diopter)'
        }
        ylabel = metric_info.get(metric, metric)
        ax.set_ylabel(ylabel, fontsize=11)

        title = f'{condition} - {ylabel}\n被験者別の傾向'
        if n_plots > 1:
            title += f' (グループ{plot_idx+1}/{n_plots})'
        ax.set_title(title, fontsize=12, fontweight='bold')

        ax.legend(bbox_to_anchor=(1.05, 1), loc='upper left', fontsize=8)
        ax.grid(True, alpha=0.3)

        plt.tight_layout()
        suffix = f'_part{plot_idx+1}' if n_plots > 1 else ''
        out_path = os.path.join(out_dir, f'lines_{metric}_{condition}{suffix}.png')
        plt.savefig(out_path, dpi=300, bbox_inches='tight')
        print(f"  保存: lines_{metric}_{condition}{suffix}.png")
        plt.close()


# =====================
# 処理方法別の被験者間比較（箱ひげ図）
# =====================
def plot_proc_comparison(df, metric, condition, out_dir):
    """処理方法別の被験者間ばらつき"""

    fig, ax = plt.subplots(figsize=(10, 6))

    proc_order = ['original', 'brightonly', 'model']
    data_to_plot = []
    labels = []

    for proc in proc_order:
        proc_data = df[df['proc'] == proc].groupby('subject')[metric].mean()
        if len(proc_data) > 0:
            data_to_plot.append(proc_data.values)
            labels.append(proc)

    bp = ax.boxplot(data_to_plot, labels=labels, patch_artist=True,
                    boxprops=dict(facecolor='lightblue', alpha=0.6),
                    medianprops=dict(color='red', linewidth=2))

    # 各被験者のデータ点をオーバーレイ
    for i, proc in enumerate(labels):
        proc_data = df[df['proc'] == proc].groupby('subject')[metric].mean()
        x = np.random.normal(i+1, 0.04, size=len(proc_data))
        ax.scatter(x, proc_data.values, alpha=0.5, s=30, color='black')

    metric_info = {
        'RT': '反応速度 (ms)',
        'miosis_rate': '縮瞳率',
        'diopter': '輻輳 (diopter)'
    }
    ylabel = metric_info.get(metric, metric)

    ax.set_ylabel(ylabel, fontsize=11)
    ax.set_xlabel('処理方法', fontsize=11)
    ax.set_title(f'{condition} - {ylabel}\n処理方法別の被験者間分布',
                 fontsize=12, fontweight='bold')
    ax.grid(axis='y', alpha=0.3)

    plt.tight_layout()
    out_path = os.path.join(out_dir, f'boxplot_{metric}_{condition}.png')
    plt.savefig(out_path, dpi=300, bbox_inches='tight')
    print(f"  保存: boxplot_{metric}_{condition}.png")
    plt.close()


# =====================
# 3指標間の相関分析
# =====================
def plot_correlation_analysis(df, condition, out_dir):
    """3指標間の相関分析（処理方法別）"""

    metrics = ['RT', 'miosis_rate', 'diopter']
    # データに存在する指標のみを使用
    available_metrics = [m for m in metrics if m in df.columns]

    if len(available_metrics) < 2:
        print(f"  警告: 相関分析に必要な指標が不足しています（{len(available_metrics)}個のみ）")
        return

    metric_names = {
        'RT': '反応速度',
        'miosis_rate': '縮瞳率',
        'diopter': '輻輳'
    }

    proc_order = ['original', 'brightonly', 'model']

    fig, axes = plt.subplots(1, 3, figsize=(18, 5))

    for ax, proc in zip(axes, proc_order):
        if proc not in df['proc'].values:
            continue

        # 処理方法ごとの被験者平均値
        proc_df = df[df['proc'] == proc].groupby('subject')[available_metrics].mean().reset_index()

        # 相関行列
        corr_matrix = proc_df[available_metrics].corr()

        # ヒートマップ
        sns.heatmap(corr_matrix, annot=True, fmt='.3f', cmap='coolwarm',
                    center=0, vmin=-1, vmax=1, square=True, ax=ax,
                    xticklabels=[metric_names[m] for m in available_metrics],
                    yticklabels=[metric_names[m] for m in available_metrics])

        ax.set_title(f'{proc}\n(n={len(proc_df)} subjects)', fontsize=11, fontweight='bold')

    fig.suptitle(f'{condition} - 3指標間の相関係数（被験者平均値ベース）',
                 fontsize=13, fontweight='bold')

    plt.tight_layout()
    out_path = os.path.join(out_dir, f'correlation_3metrics_{condition}.png')
    plt.savefig(out_path, dpi=300, bbox_inches='tight')
    print(f"  保存: correlation_3metrics_{condition}.png")
    plt.close()


# =====================
# 散布図行列（全体傾向）
# =====================
def plot_scatter_matrix(df, condition, out_dir):
    """3指標の散布図行列"""

    metrics = ['RT', 'miosis_rate', 'diopter']
    # データに存在する指標のみを使用
    available_metrics = [m for m in metrics if m in df.columns]

    if len(available_metrics) < 2:
        print(f"  警告: 散布図行列に必要な指標が不足しています（{len(available_metrics)}個のみ）")
        return

    metric_names = {
        'RT': '反応速度 (ms)',
        'miosis_rate': '縮瞳率',
        'diopter': '輻輳 (diopter)'
    }

    # 被験者×処理方法の平均値
    agg_df = df.groupby(['subject', 'proc'])[available_metrics].mean().reset_index()

    # 散布図行列
    n = len(available_metrics)
    fig, axes = plt.subplots(n, n, figsize=(5*n, 5*n))
    if n == 1:
        axes = np.array([[axes]])
    elif n == 2:
        axes = axes.reshape(n, n)

    proc_colors = {'original': 'steelblue', 'brightonly': 'orange', 'model': 'green'}

    for i, metric_y in enumerate(available_metrics):
        for j, metric_x in enumerate(available_metrics):
            ax = axes[i, j]

            if i == j:
                # 対角線：ヒストグラム
                for proc in ['original', 'brightonly', 'model']:
                    proc_data = agg_df[agg_df['proc'] == proc][metric_x]
                    ax.hist(proc_data, alpha=0.5, label=proc, color=proc_colors.get(proc, 'gray'), bins=15)
                ax.set_ylabel('度数', fontsize=9)
                if i == 0:
                    ax.legend(fontsize=8)
            else:
                # 非対角線：散布図
                for proc in ['original', 'brightonly', 'model']:
                    proc_data = agg_df[agg_df['proc'] == proc]
                    ax.scatter(proc_data[metric_x], proc_data[metric_y],
                              alpha=0.6, s=30, label=proc if i == 0 and j == 1 else "",
                              color=proc_colors.get(proc, 'gray'))

                # 相関係数を表示
                if len(agg_df[[metric_x, metric_y]].dropna()) > 2:
                    r, p = stats.pearsonr(agg_df[metric_x].dropna(), agg_df[metric_y].dropna())
                    ax.text(0.05, 0.95, f'r={r:.3f}', transform=ax.transAxes,
                           fontsize=8, va='top')

            if i == 2:
                ax.set_xlabel(metric_names[metric_x], fontsize=9)
            if j == 0:
                ax.set_ylabel(metric_names[metric_y], fontsize=9)

            ax.grid(True, alpha=0.3)

    fig.suptitle(f'{condition} - 3指標の散布図行列（被験者×処理方法の平均値）',
                 fontsize=13, fontweight='bold')
    plt.tight_layout()

    out_path = os.path.join(out_dir, f'scatter_matrix_{condition}.png')
    plt.savefig(out_path, dpi=300, bbox_inches='tight')
    print(f"  保存: scatter_matrix_{condition}.png")
    plt.close()


# =====================
# 統計サマリーの出力
# =====================
def save_summary_stats(df, condition, out_dir):
    """統計サマリーをテキストファイルに出力"""

    out_path = os.path.join(out_dir, f'summary_stats_{condition}.txt')

    with open(out_path, 'w', encoding='utf-8') as f:
        f.write(f"{'='*60}\n")
        f.write(f"被験者ごとの傾向分析 - 統計サマリー ({condition})\n")
        f.write(f"{'='*60}\n\n")

        metrics = ['RT', 'miosis_rate', 'diopter']
        # データに存在する指標のみを使用
        available_metrics = [m for m in metrics if m in df.columns]

        metric_names = {
            'RT': '反応速度 (ms)',
            'miosis_rate': '縮瞳率',
            'diopter': '輻輳 (diopter)'
        }

        # 被験者数
        n_subjects = df['subject'].nunique()
        f.write(f"被験者数: {n_subjects}\n")
        f.write(f"処理方法: {', '.join(df['proc'].unique())}\n")
        f.write(f"利用可能な指標: {', '.join([metric_names[m] for m in available_metrics])}\n\n")

        # 各指標の統計量（処理方法別）
        for metric in available_metrics:

            f.write(f"\n{'='*60}\n")
            f.write(f"{metric_names[metric]}\n")
            f.write(f"{'='*60}\n\n")

            for proc in ['original', 'brightonly', 'model']:
                if proc not in df['proc'].values:
                    continue

                # 被験者平均値
                subject_means = df[df['proc'] == proc].groupby('subject')[metric].mean()

                f.write(f"[{proc}]\n")
                f.write(f"  被験者平均値の平均: {subject_means.mean():.3f}\n")
                f.write(f"  被験者平均値のSD: {subject_means.std():.3f}\n")
                f.write(f"  被験者平均値の範囲: {subject_means.min():.3f} ~ {subject_means.max():.3f}\n")
                f.write(f"  被験者数: {len(subject_means)}\n\n")

        # 指標間の相関（処理方法別）
        if len(available_metrics) >= 2:
            f.write(f"\n{'='*60}\n")
            f.write(f"指標間の相関係数（被験者平均値ベース）\n")
            f.write(f"{'='*60}\n\n")

            for proc in ['original', 'brightonly', 'model']:
                if proc not in df['proc'].values:
                    continue

                proc_df = df[df['proc'] == proc].groupby('subject')[available_metrics].mean()

                f.write(f"[{proc}]\n")
                # 利用可能な指標ペアのみ相関を計算
                if 'RT' in available_metrics and 'miosis_rate' in available_metrics:
                    f.write(f"  RT vs 縮瞳率: r={proc_df['RT'].corr(proc_df['miosis_rate']):.3f}\n")
                if 'RT' in available_metrics and 'diopter' in available_metrics:
                    f.write(f"  RT vs 輻輳: r={proc_df['RT'].corr(proc_df['diopter']):.3f}\n")
                if 'miosis_rate' in available_metrics and 'diopter' in available_metrics:
                    f.write(f"  縮瞳率 vs 輻輳: r={proc_df['miosis_rate'].corr(proc_df['diopter']):.3f}\n")
                f.write("\n")

    print(f"  保存: summary_stats_{condition}.txt")


# =====================
# メイン処理
# =====================
def main():
    print(f"\n{'='*60}")
    print(f"被験者ごとの傾向分析（反応速度・縮瞳・輻輳）")
    print(f"パラメータ: {params}, n={n}")
    print(f"{'='*60}\n")

    for condition, file_path in DATA.items():
        print(f"\n{'='*60}")
        print(f"{condition} 条件の解析")
        print(f"{'='*60}")

        # データ読み込み・前処理
        df_raw = pd.read_excel(file_path, engine='openpyxl')
        df = preprocess_data(df_raw)

        if len(df) == 0:
            print(f"  ERROR: データなし")
            continue

        print(f"  データ数: {len(df)} 行")
        print(f"  被験者数: {df['subject'].nunique()}")
        print(f"  処理方法: {', '.join(df['proc'].unique())}")

        # 各指標について解析
        metrics = ['RT', 'miosis_rate', 'diopter']
        available_metrics = [m for m in metrics if m in df.columns]
        print(f"  利用可能な指標: {', '.join(available_metrics)}")

        print(f"\n  ヒートマップ作成中...")
        for metric in available_metrics:
            plot_heatmap(df, metric, condition, OUT_DIR)

        print(f"\n  折れ線グラフ作成中...")
        for metric in available_metrics:
            plot_subject_lines(df, metric, condition, OUT_DIR)

        print(f"\n  箱ひげ図作成中...")
        for metric in available_metrics:
            plot_proc_comparison(df, metric, condition, OUT_DIR)

        print(f"\n  相関分析中...")
        plot_correlation_analysis(df, condition, OUT_DIR)
        plot_scatter_matrix(df, condition, OUT_DIR)

        print(f"\n  統計サマリー出力中...")
        save_summary_stats(df, condition, OUT_DIR)

    print(f"\n{'='*60}")
    print(f"[完了] すべての解析が完了しました")
    print(f"出力先: {OUT_DIR}")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()
