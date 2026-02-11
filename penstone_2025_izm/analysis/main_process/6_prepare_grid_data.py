# -*- coding: utf-8 -*-
"""
6_prepare_grid_data.py
----------------------
merged メトリクスExcel（param1/param2/param3 の縦持ち形式）を
graph_grid スクリプトが期待する横持ち形式に変換する。

入力:  data/log_with_emr_metrics/{params}/merged/integrated_{cond}_metrics_n{N}.xlsx
出力:  data/merged_for_grid/{Bright,Dark}/grid_data_{cond}.xlsx

変換内容:
  - param1/param1_value, param2/param2_value, param3/param3_value
    → gamma, contrast, sharpness, brightness, equalization の列に展開
  - diopter_peak_value → diopter 列として追加
  - Skip_Task == True の行を除外
  - FrontIsDigit_inferred == True の行のみ使用（数字タスクのみ）
"""

import os
import glob
import pandas as pd
import numpy as np


# graph_grid で使う5パラメータ
PARAM_COLUMNS = ["gamma", "contrast", "sharpness", "brightness", "equalization"]

# 各パラメータのデフォルト値（加工なし = 元画像の状態）
PARAM_DEFAULTS = {
    "gamma": 1.0,
    "contrast": 1.0,
    "sharpness": 0.0,
    "brightness": 0.0,
    "equalization": 0.0,
}


def pivot_params(df: pd.DataFrame) -> pd.DataFrame:
    """
    param1/param1_value ~ param3/param3_value を
    gamma, contrast, sharpness, brightness, equalization の横持ちに変換。
    未指定のパラメータはデフォルト値で埋める。
    """
    # まずデフォルト値で初期化
    for col in PARAM_COLUMNS:
        df[col] = PARAM_DEFAULTS[col]

    # param1~3 を展開
    for i in [1, 2, 3]:
        name_col = f"param{i}"
        val_col = f"param{i}_value"

        if name_col not in df.columns or val_col not in df.columns:
            continue

        for idx in df.index:
            pname = df.loc[idx, name_col]
            pval = df.loc[idx, val_col]

            if pd.isna(pname) or pd.isna(pval):
                continue

            pname_str = str(pname).strip().lower()
            if pname_str in PARAM_COLUMNS:
                df.loc[idx, pname_str] = float(pval)

    return df


def process_one_file(input_path: str, output_dir: str, cond: str) -> str:
    """1つのmerged Excelを変換して保存"""
    print(f"[INFO] Reading: {input_path}")
    df = pd.read_excel(input_path)
    n_total = len(df)
    print(f"  Total rows: {n_total}")

    # Skip_Task == True を除外
    if "Skip_Task" in df.columns:
        df = df[df["Skip_Task"] != True].copy()
        print(f"  After removing Skip_Task: {len(df)} rows")

    # 数字タスクのみ
    if "FrontIsDigit_inferred" in df.columns:
        df = df[df["FrontIsDigit_inferred"] == True].copy()
        print(f"  After digit filter: {len(df)} rows")

    # パラメータを横持ちに変換
    df = pivot_params(df)

    # diopter 列を作成（graph_grid が参照する列名）
    if "diopter_peak_value" in df.columns:
        df["diopter"] = df["diopter_peak_value"]
    elif "diopter_delta" in df.columns:
        df["diopter"] = df["diopter_delta"]
    else:
        print("  [WARN] diopter関連列が見つかりません")
        df["diopter"] = np.nan

    # 出力列を選定（graph_gridに必要な列 + 参照用の追加情報）
    grid_cols = PARAM_COLUMNS + ["diopter"]
    extra_cols = [
        "trial_id", "folder_name", "file_name", "front", "image_name",
        "diopter_baseline", "diopter_peak_value", "diopter_delta",
        "pupil_both_baseline", "pupil_both_miosis_mean", "pupil_both_miosis_min",
        "pupil_both_change_rate_mean", "pupil_both_change_rate_min",
        "Accuracy", "Reaction_Time",
    ]
    # 実際に存在する列のみ追加
    extra_cols = [c for c in extra_cols if c in df.columns]
    output_cols = grid_cols + extra_cols

    df_out = df[output_cols].copy()
    df_out = df_out.reset_index(drop=True)

    # 保存
    os.makedirs(output_dir, exist_ok=True)
    out_path = os.path.join(output_dir, f"grid_data_{cond.lower()}.xlsx")
    df_out.to_excel(out_path, index=False, sheet_name=cond)
    print(f"  [OK] Saved: {out_path}  ({len(df_out)} rows, {len(output_cols)} cols)")

    return out_path


def main():
    input_root = "../../data/log_with_emr_metrics"
    output_root = "../../data/merged_for_grid"

    # パラメータフォルダを一覧表示して選択
    candidates = []
    if os.path.isdir(input_root):
        for d in sorted(os.listdir(input_root)):
            merged_path = os.path.join(input_root, d, "merged")
            if os.path.isdir(merged_path):
                candidates.append((d, merged_path))

    if not candidates:
        print(f"[ERROR] merged/ ディレクトリが見つかりません: {input_root}")
        return

    print("\n=== 利用可能な計算パラメータ ===")
    for i, (name, _) in enumerate(candidates, 1):
        print(f"  {i}. {name}")

    choice = input(f"\n使用するパラメータを選択 (1-{len(candidates)}): ").strip()
    idx = int(choice) - 1
    if idx < 0 or idx >= len(candidates):
        print("[ERROR] 無効な選択です")
        return

    chosen_name, merged_dir = candidates[idx]
    print(f"  → {chosen_name}")

    # 被験者数 N を入力
    n = input("\n被験者何人入りのデータ使う？: ").strip()

    print(f"\n[INFO] Source: {merged_dir}")
    print(f"[INFO] Output: {output_root}/{chosen_name}/")

    # Bright / Dark それぞれ処理
    for cond in ["Bright", "Dark"]:
        # N指定があればそのファイル、なければ最新
        if n:
            target = os.path.join(merged_dir, f"integrated_{cond.lower()}_metrics_n{n}.xlsx")
            if os.path.exists(target):
                files = [target]
            else:
                print(f"[SKIP] {cond}: n{n} のファイルなし ({target})")
                continue
        else:
            pattern = os.path.join(merged_dir, f"integrated_{cond.lower()}_metrics_*.xlsx")
            files = sorted(glob.glob(pattern))

        if not files:
            print(f"[SKIP] {cond}: ファイルなし")
            continue

        latest = files[-1]
        output_dir = os.path.join(output_root, chosen_name, cond)
        process_one_file(latest, output_dir, cond)

    print("\n[COMPLETE] grid用データの生成完了")


if __name__ == "__main__":
    main()

