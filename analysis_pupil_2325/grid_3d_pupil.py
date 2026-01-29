# -*- coding: utf-8 -*-
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
import numpy as np
import pandas as pd
import itertools
import matplotlib.pyplot as plt
import os


# =========================
# グリッド定義（加工パラメータ）
# =========================
grid_dicts = {
    "brightness":   {"0": 0,    "1": 10,   "2": 20,   "3": 30},
    "contrast":     {"0": 0.8,  "1": 0.933,"2": 1.066,"3": 1.2},
    "gamma":        {"0": 0.5,  "1": 0.7,  "2": 0.9,  "3": 1.1},
    "sharpness":    {"0": 0.0,  "1": 0.33, "2": 0.66, "3": 1.0},
    "equalization": {"0": 4,    "1": 13,   "2": 22,   "3": 32}
}

# 3特徴量の組み合わせ（3D軸の組み合わせ）
columns = ["gamma", "contrast", "sharpness", "brightness", "equalization"]
combinations_3 = list(itertools.combinations(columns, 3))


# =========================
# そのグリッドセル内で「縮瞳が強い下位10%」がどのくらいあるか
# =========================
def calculate_grid_ratio(df, x_feature, y_feature, z_feature, metric_col,
                         x_range, y_range, z_range, quantiles):
    """
    指定セルに入っているデータのうち
    metric_col <= 下位10%（quantiles['lower']）の割合を返す
    """
    filtered = df[
        (df[x_feature] >= x_range[0]) & (df[x_feature] <= x_range[1]) &
        (df[y_feature] >= y_range[0]) & (df[y_feature] <= y_range[1]) &
        (df[z_feature] >= z_range[0]) & (df[z_feature] <= z_range[1])
    ].copy()

    if len(filtered) == 0:
        return None

    # 下位10%（強い縮瞳側）に入る割合
    lower_group = filtered[filtered[metric_col] <= quantiles["lower"]]
    ratio = len(lower_group) / len(filtered)
    return ratio


# =========================
# 3Dグリッド描画 + 赤グリッド内の点は赤点
# =========================
def plot_3d_grid_color_pupil(df, x_feature, y_feature, z_feature,
                             grid_dicts, quantiles,
                             metric_col="平均_変化率",
                             red_ratio_th=0.6,
                             out_dir="../pic/3d_grid_plots_pupil"):
    """
    - グリッドセルを ratio に応じて赤/青で塗る
    - 赤セル内の点は赤、青セル内の点は青で描く
    """

    # 軸用の区切り（4点 -> 3セル）
    x_values = np.linspace(min(grid_dicts[x_feature].values()),
                           max(grid_dicts[x_feature].values()), 4)
    y_values = np.linspace(min(grid_dicts[y_feature].values()),
                           max(grid_dicts[y_feature].values()), 4)
    z_values = np.linspace(min(grid_dicts[z_feature].values()),
                           max(grid_dicts[z_feature].values()), 4)

    fig = plt.figure(figsize=(10, 8))
    ax = fig.add_subplot(111, projection="3d")

    # 全点を「青」で描く（後で赤セル点だけ重ねて赤にする）
    # ※先に描いておくと赤点が上に出る
    ax.scatter(df[x_feature], df[y_feature], df[z_feature],
               s=10, alpha=0.15, c="blue")

    # 赤セル点を集める（まとめて最後に描画）
    red_points = []

    for i in range(3):
        for j in range(3):
            for k in range(3):
                x_range = (x_values[i], x_values[i + 1])
                y_range = (y_values[j], y_values[j + 1])
                z_range = (z_values[k], z_values[k + 1])

                ratio = calculate_grid_ratio(
                    df, x_feature, y_feature, z_feature, metric_col,
                    x_range, y_range, z_range, quantiles
                )

                # ratio が一定以上なら赤セル
                if ratio is not None and ratio >= red_ratio_th:
                    cell_color = "red"
                    is_red_cell = True
                else:
                    cell_color = "blue"
                    is_red_cell = False

                # セル内点を抽出（赤セルなら赤点にする）
                if is_red_cell:
                    cell_points = df[
                        (df[x_feature] >= x_range[0]) & (df[x_feature] <= x_range[1]) &
                        (df[y_feature] >= y_range[0]) & (df[y_feature] <= y_range[1]) &
                        (df[z_feature] >= z_range[0]) & (df[z_feature] <= z_range[1])
                    ][[x_feature, y_feature, z_feature]].values
                    if len(cell_points) > 0:
                        red_points.append(cell_points)

                # 立方体の面を作る
                vertices = [
                    (x_range[0], y_range[0], z_range[0]),
                    (x_range[0], y_range[1], z_range[0]),
                    (x_range[1], y_range[0], z_range[0]),
                    (x_range[1], y_range[1], z_range[0]),
                    (x_range[0], y_range[0], z_range[1]),
                    (x_range[0], y_range[1], z_range[1]),
                    (x_range[1], y_range[0], z_range[1]),
                    (x_range[1], y_range[1], z_range[1]),
                ]

                faces = [
                    [vertices[0], vertices[1], vertices[5], vertices[4]],
                    [vertices[7], vertices[6], vertices[2], vertices[3]],
                    [vertices[0], vertices[1], vertices[3], vertices[2]],
                    [vertices[7], vertices[6], vertices[4], vertices[5]],
                    [vertices[7], vertices[3], vertices[1], vertices[5]],
                    [vertices[0], vertices[4], vertices[6], vertices[2]],
                ]

                ax.add_collection3d(
                    Poly3DCollection(
                        faces,
                        linewidths=1,
                        edgecolors="gray",
                        alpha=0.25,
                        facecolors=cell_color
                    )
                )

    # 赤セル点を最後に重ね描き（目立たせる）
    if len(red_points) > 0:
        red_points = np.vstack(red_points)
        ax.scatter(red_points[:, 0], red_points[:, 1], red_points[:, 2],
                   s=25, alpha=0.85, c="red")

    ax.set_xlabel(x_feature)
    ax.set_ylabel(y_feature)
    ax.set_zlabel(z_feature)
    plt.title(f"{x_feature}, {y_feature}, {z_feature} (Pupil: {metric_col})")

    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, f"{x_feature}_{y_feature}_{z_feature}_pupil.png")
    plt.savefig(out_path, dpi=200, bbox_inches="tight")
    plt.close(fig)

    print(f"Saved: {out_path}")


# =========================
# 実行部
# =========================
if __name__ == "__main__":

    # ★元データ（あなたがアップしたやつ）
    path = "merged_with_pupil.xlsx"
    df = pd.read_excel(path)

    # 必須カラムチェック
    metric_col = "平均_変化率"
    need_cols = set(columns + [metric_col])
    missing = [c for c in need_cols if c not in df.columns]
    if missing:
        raise ValueError(f"必要な列がありません: {missing}")

    # NaN除去（最低限）
    df = df.dropna(subset=columns + [metric_col]).copy()

    # 下位10% / 上位10%（今回は lower を使う）
    quantiles = {
        "upper": df[metric_col].quantile(0.9),
        "lower": df[metric_col].quantile(0.1)
    }
    print(f"[quantiles] upper={quantiles['upper']:.6f}, lower={quantiles['lower']:.6f}")

    # 全組み合わせを出力
    for combo in combinations_3:
        plot_3d_grid_color_pupil(
            df,
            x_feature=combo[0],
            y_feature=combo[1],
            z_feature=combo[2],
            grid_dicts=grid_dicts,
            quantiles=quantiles,
            metric_col=metric_col,
            red_ratio_th=0.6,
            out_dir="../pic/3d_grid_plots_pupil"
        )

    print("Done.")
