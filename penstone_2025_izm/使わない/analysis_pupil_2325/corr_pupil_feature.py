import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os
import numpy as np
from scipy import stats

# =====================
# 設定
# =====================
PUPIL_METRIC = "平均_変化率"

# スクリプトのディレクトリを基準にする
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

CATEGORIES = {
    "brightness": ["digit_brightness", "skewness_luminance"],
    "contrast": ["contrast_luminance", "brightness_ratio", "squared_mean_contrast"],
    "sharpness": ["sharpness_factor", "sobel_std_par_figure"]
}

FILES = {
    "Bright": os.path.join(SCRIPT_DIR, "merged_with_pupil.xlsx"),
    "Dark": os.path.join(SCRIPT_DIR, "merged_with_pupil_dark.xlsx")
}

OUT_DIR = os.path.join(SCRIPT_DIR, "plots_correlation")
MERGED_DIR = os.path.join(SCRIPT_DIR, "merged_scatter")

# =====================
# フォントサイズ定数（パワポ用に大きめに設定）
# =====================
FONT_SIZE_TITLE = 28        # タイトル
FONT_SIZE_SUPTITLE = 32     # 全体タイトル（merged用）
FONT_SIZE_LABEL = 24        # 軸ラベル
FONT_SIZE_TICK = 20         # 目盛り

# グラフ設定
plt.rcParams['font.family'] = 'MS Gothic'
plt.rcParams['axes.unicode_minus'] = False
plt.rcParams['font.size'] = FONT_SIZE_TICK

def plot_correlation(df, condition, category, feature, invert_pupil=False):
    """
    指定された特徴量と瞳孔指標の相関をプロット
    invert_pupil: Trueの場合、瞳孔指標の符号を反転
    """
    data = df[[feature, PUPIL_METRIC]].dropna().copy()
    if len(data) < 2:
        return None, None

    # 符号反転処理
    pupil_data = -data[PUPIL_METRIC] if invert_pupil else data[PUPIL_METRIC]
    pupil_label = f"-{PUPIL_METRIC}" if invert_pupil else PUPIL_METRIC
    suffix = "_inverted" if invert_pupil else ""

    # 保存先ディレクトリ
    save_dir = os.path.join(OUT_DIR + suffix, condition, category)
    os.makedirs(save_dir, exist_ok=True)

    plt.figure(figsize=(10, 8))

    # 散布図プロット
    plt.scatter(data[feature], pupil_data, alpha=0.5, c='steelblue')

    # 回帰直線
    r, p = stats.pearsonr(data[feature], pupil_data)
    sns.regplot(x=data[feature], y=pupil_data, scatter=False, color='darkred', line_kws={'ls':'--'})

    plt.title(f"{condition} Condition: {category}\n{feature} vs {pupil_label}\nr={r:.3f}, p={p:.3g}", fontsize=FONT_SIZE_TITLE, fontweight='bold')
    plt.xlabel(feature, fontsize=FONT_SIZE_LABEL)
    plt.ylabel(pupil_label, fontsize=FONT_SIZE_LABEL)
    plt.tick_params(labelsize=FONT_SIZE_TICK)

    out_path = os.path.join(save_dir, f"{condition}_{feature}_vs_pupil.png")
    plt.savefig(out_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"  [Save{' Inverted' if invert_pupil else ''}] {out_path} (r={r:.3f})")

    return r, p

def plot_merged_scatter(df_bright, df_dark, category, feature, invert_pupil=False):
    """
    BrightとDarkの散布図を横に並べて1枚の画像として出力
    タイトル付きとタイトルなしの2バージョンを別フォルダに保存
    invert_pupil: Trueの場合、瞳孔指標の符号を反転
    """
    pupil_label = f"-{PUPIL_METRIC}" if invert_pupil else PUPIL_METRIC
    suffix = "_inverted" if invert_pupil else ""

    # タイトル付きバージョン用のディレクトリ
    save_dir = os.path.join(MERGED_DIR + suffix, category)
    os.makedirs(save_dir, exist_ok=True)

    # タイトルなしバージョン用のディレクトリ
    save_dir_notitle = os.path.join(SCRIPT_DIR, f"merged_scatter_notitle{suffix}", category)
    os.makedirs(save_dir_notitle, exist_ok=True)

    fig, axes = plt.subplots(1, 2, figsize=(18, 8), sharey=True)

    for ax, (condition, df) in zip(axes, [("Bright", df_bright), ("Dark", df_dark)]):
        data = df[[feature, PUPIL_METRIC]].dropna().copy()
        if len(data) < 2:
            ax.text(0.5, 0.5, "No Data", ha='center', va='center', transform=ax.transAxes)
            ax.set_title(f"{condition} - {feature}")
            continue

        pupil_data = -data[PUPIL_METRIC] if invert_pupil else data[PUPIL_METRIC]
        ax.scatter(data[feature], pupil_data, alpha=0.5, c='steelblue')

        r, p = stats.pearsonr(data[feature], pupil_data)
        sns.regplot(x=data[feature], y=pupil_data, scatter=False, ax=ax, color='darkred', line_kws={'ls':'--'})

        ax.set_title(f"{condition}\n{feature} vs {pupil_label}\nr={r:.3f}, p={p:.3g}", fontsize=FONT_SIZE_TITLE, fontweight='bold')
        ax.set_xlabel(feature, fontsize=FONT_SIZE_LABEL)
        ax.set_ylabel(pupil_label if ax == axes[0] else "", fontsize=FONT_SIZE_LABEL)
        ax.tick_params(labelsize=FONT_SIZE_TICK)

    # タイトル付きバージョンを保存
    plt.suptitle(f"Comparison: {category} - {feature}", fontsize=FONT_SIZE_SUPTITLE, fontweight='bold')
    plt.tight_layout()

    out_path = os.path.join(save_dir, f"merged_{feature}_vs_pupil.png")
    plt.savefig(out_path, dpi=300, bbox_inches='tight')
    print(f"  [Merged{' Inverted' if invert_pupil else ''}] {out_path}")

    # タイトルを削除してタイトルなしバージョンを保存
    fig.suptitle("")  # タイトルを空にする
    plt.tight_layout()

    out_path_notitle = os.path.join(save_dir_notitle, f"merged_{feature}_vs_pupil.png")
    plt.savefig(out_path_notitle, dpi=300, bbox_inches='tight')
    print(f"  [Merged NoTitle{' Inverted' if invert_pupil else ''}] {out_path_notitle}")

    plt.close()

def main():
    print("=== Pupil & Image Feature Correlation Analysis ===")

    os.makedirs(OUT_DIR, exist_ok=True)
    os.makedirs(MERGED_DIR, exist_ok=True)

    # 両条件のデータを読み込み
    dfs = {}
    for condition, filename in FILES.items():
        if not os.path.exists(filename):
            print(f"\n[Warning] ファイルが見つかりません: {filename}")
            continue

        print(f"\n--- {condition} 条件の解析中 ---")
        df = pd.read_excel(filename)
        df[PUPIL_METRIC] = pd.to_numeric(df[PUPIL_METRIC], errors='coerce')
        df = df.dropna(subset=[PUPIL_METRIC])

        # 通常版と反転版の両方を生成
        for invert in [False, True]:
            if invert:
                print(f"\n  [反転版の生成]")
            # 各カテゴリーの相関係数プロット（個別）
            for category, features in CATEGORIES.items():
                print(f"  Category: {category}")
                for feature in features:
                    if feature in df.columns:
                        plot_correlation(df, condition, category, feature, invert_pupil=invert)

        dfs[condition] = df

    # BrightとDarkを並べた統合散布図を出力（通常版と反転版）
    if "Bright" in dfs and "Dark" in dfs:
        for invert in [False, True]:
            if invert:
                print("\n--- Merged Scatter Plots (Inverted) ---")
            else:
                print("\n--- Merged Scatter Plots ---")
            for category, features in CATEGORIES.items():
                for feature in features:
                    if feature in dfs["Bright"].columns and feature in dfs["Dark"].columns:
                        plot_merged_scatter(dfs["Bright"], dfs["Dark"], category, feature, invert_pupil=invert)

    print("\n[Done] 全ての解析が完了しました。")

if __name__ == "__main__":
    main()
