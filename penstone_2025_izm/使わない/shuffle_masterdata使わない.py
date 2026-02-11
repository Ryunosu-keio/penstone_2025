# -*- coding: utf-8 -*-
"""
shuffle.py（Master並べ替え対応版）
=================================
目的:
- main_masterdata.py で作った Master Excel を元に、
  被験者ごとの提示順（Excelのみ）を生成する。
- 画像ファイルは Master 作成時点で生成済みなので、ここでは作らない。

ポイント:
- 「Frontが数字（ターゲット）」が連続しない制約を維持したまま並べ替え。
- back Excel を作った順序に合わせて front Excel（files列）も生成する。
"""
import os
import re
import glob
import random
from typing import List, Dict, Tuple, Optional

import pandas as pd

# ==========================================
# 入力パース
# ==========================================
def parse_subject_ids(s: str) -> List[str]:
    """
    例:
      "101,102,105" -> ["101","102","105"]
      "101-105"     -> ["101","102","103","104","105"]
      "101-105,110" -> ...
    """
    s = s.strip()
    if not s:
        return []
    parts = [p.strip() for p in s.split(",") if p.strip()]
    out = []
    for p in parts:
        m = re.fullmatch(r"(\d+)\s*-\s*(\d+)", p)
        if m:
            a, b = int(m.group(1)), int(m.group(2))
            step = 1 if a <= b else -1
            for v in range(a, b + step, step):
                out.append(str(v))
        else:
            out.append(p)
    return out

def safe_int_input(prompt: str, default: int) -> int:
    s = input(f"{prompt} (default={default}): ").strip()
    if s == "":
        return default
    try:
        return int(s)
    except Exception:
        print("入力が不正なので default を使います。")
        return default

# ==========================================
# 並べ替え（ターゲット連続禁止を維持）
# ==========================================
def is_digit_front(x) -> bool:
    return str(x).isdigit()

def reshuffle_rows_keep_no_consecutive_digit(df: pd.DataFrame, front_col="front_char") -> pd.DataFrame:
    """
    既存の行を並べ替えるだけ（行を増減しない）。
    ルール:
      - Frontが数字の試行が隣接しない（必ず間にアルファベットが入る）
    方法:
      - digit行と non-digit行に分け、non-digitの隙間にdigitを散らす
    """
    if front_col not in df.columns:
        raise ValueError(f"front_col '{front_col}' not found in df")

    digit_df = df[df[front_col].map(is_digit_front)].sample(frac=1).reset_index(drop=True)
    other_df = df[~df[front_col].map(is_digit_front)].sample(frac=1).reset_index(drop=True)

    n_digit = len(digit_df)
    n_other = len(other_df)

    # 隙間は n_other+1 個、各隙間に digit を最大1個ずつ置けば digit 連続なし
    if n_digit > n_other + 1:
        # ここに引っかかるなら、元のデータ設計（digit比率）を見直す必要がある
        raise RuntimeError(f"digit trials too many to separate: digit={n_digit}, other={n_other}")

    gaps = [[] for _ in range(n_other + 1)]
    gap_indices = random.sample(range(n_other + 1), k=n_digit)
    for i, gi in enumerate(gap_indices):
        gaps[gi].append(digit_df.iloc[i])

    rows = []
    for i in range(n_other):
        rows.extend(gaps[i])
        rows.append(other_df.iloc[i])
    rows.extend(gaps[n_other])

    out = pd.DataFrame(rows).reset_index(drop=True)

    # check
    for i in range(len(out) - 1):
        if is_digit_front(out.loc[i, front_col]) and is_digit_front(out.loc[i + 1, front_col]):
            raise RuntimeError("Internal error: consecutive digit trials detected")
    return out

# ==========================================
# 生成
# ==========================================
def infer_set_num_from_filename(path: str) -> Optional[int]:
    """Master_12.xlsx や Master_12_any.xlsx から 12 を推定"""
    base = os.path.splitext(os.path.basename(path))[0]
    m = re.search(r"_(\d+)\b", base)
    if not m:
        return None
    return int(m.group(1))

def build_subject_excels(
    base_root: str,
    condition_label: str,
    master_id: str,
    subject_ids: List[str],
    seed: Optional[int] = None,
):
    if seed is not None:
        random.seed(seed)

    master_back_dir = os.path.join(base_root, "back", condition_label, master_id)
    master_files = sorted(glob.glob(os.path.join(master_back_dir, "*.xlsx")))

    if not master_files:
        raise FileNotFoundError(f"Master back Excel が見つかりません: {master_back_dir}")

    for subj in subject_ids:
        out_back_dir = os.path.join(base_root, "back", condition_label, subj)
        out_front_dir = os.path.join(base_root, "front", condition_label, subj)
        os.makedirs(out_back_dir, exist_ok=True)
        os.makedirs(out_front_dir, exist_ok=True)

        for master_path in master_files:
            df_master = pd.read_excel(master_path)

            # 並べ替え（ターゲット連続禁止）
            df_new = reshuffle_rows_keep_no_consecutive_digit(df_master, front_col="front_char")

            set_num = infer_set_num_from_filename(master_path)
            if set_num is None:
                # 最後の保険：file_name列から取る
                try:
                    set_num = int(df_master["file_name"].iloc[0])
                except Exception:
                    set_num = 0

            # ID関連を上書き（画像名は Master のまま使う）
            df_new = df_new.copy()
            df_new["folder_name"] = str(subj)
            df_new["file_name"] = int(set_num)
            df_new["task_num"] = list(range(1, len(df_new) + 1))
            df_new["trial_id"] = [f"{subj}_{set_num}_{i}" for i in df_new["task_num"]]

            # back 保存
            out_back_path = os.path.join(out_back_dir, f"{subj}_{set_num}.xlsx")
            df_new.to_excel(out_back_path, index=False)

            # front は df_new の front_char 順に作る（files列）
            df_front = pd.DataFrame({"files": df_new["front_char"].astype(str).tolist()})
            out_front_path = os.path.join(out_front_dir, f"{subj}_{set_num}_front.xlsx")
            df_front.to_excel(out_front_path, index=False)

    print(f"[OK] condition={condition_label} Master={master_id} -> subjects={len(subject_ids)}")

def main():
    print("\n=== shuffle.py: Master並べ替え（被験者Excel作成） ===")
    base_root = input("Excelルート (default=./imageCreationExcel): ").strip() or "./imageCreationExcel"
    master_id = input("Master ID (default=Master): ").strip() or "Master"
    cond_in = input("Condition (Bright/Dark/Both) (default=Both): ").strip().lower() or "both"
    subject_in = input("被験者ID（例: 101-110,201）: ").strip()
    if not subject_in:
        raise ValueError("被験者IDが空です。")
    subject_ids = parse_subject_ids(subject_in)

    seed = input("shuffle seed（空=ランダム）: ").strip()
    seed_int = int(seed) if seed else None

    conds = []
    if cond_in in ("bright", "b"):
        conds = ["Bright"]
    elif cond_in in ("dark", "d"):
        conds = ["Dark"]
    else:
        conds = ["Bright", "Dark"]

    for c in conds:
        build_subject_excels(
            base_root=base_root,
            condition_label=c,
            master_id=master_id,
            subject_ids=subject_ids,
            seed=seed_int,
        )

    print("\n完了。")

if __name__ == "__main__":
    main()
