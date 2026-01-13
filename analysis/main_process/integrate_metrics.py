import pandas as pd
import glob
import os

def integrate_metrics(csv_files):
    if not csv_files:
        return pd.DataFrame()
    dfs = [pd.read_csv(f, encoding="utf-8-sig") for f in csv_files]
    return pd.concat(dfs, ignore_index=True)

def subject_folder_name(path: str) -> str:
    # .../Bright/<SUBJ>/<file>.csv の <SUBJ> を取る（OS依存しない）
    return os.path.basename(os.path.dirname(path))

# データのルートパス
DATA_ROOT = "../../data/integrated_2025_metrics"

bright_files = glob.glob(os.path.join(DATA_ROOT, "Bright", "*", "*.csv"))
dark_files   = glob.glob(os.path.join(DATA_ROOT, "Dark",   "*", "*.csv"))

# 除外する被験者（必要に応じてコメント解除）
# drop_bright = {"S01", "S02", "S03", "S04"}
# drop_dark   = {"S101", "S102", "S103", "S104"}
drop_bright = set()
drop_dark   = set()

bright_files = [f for f in bright_files if subject_folder_name(f) not in drop_bright]
dark_files   = [f for f in dark_files   if subject_folder_name(f) not in drop_dark]

integrated_bright = integrate_metrics(bright_files)
integrated_dark   = integrate_metrics(dark_files)

# 被験者数をカウント
n_bright = len(set(subject_folder_name(f) for f in bright_files))
n_dark = len(set(subject_folder_name(f) for f in dark_files))

# 出力先（data/integrated_2025_metrics/merged/）
OUT_DIR = os.path.join(DATA_ROOT, "merged")
os.makedirs(OUT_DIR, exist_ok=True)

out_bright = os.path.join(OUT_DIR, f"integrated_bright_metrics_n{n_bright}.xlsx")
out_dark = os.path.join(OUT_DIR, f"integrated_dark_metrics_n{n_dark}.xlsx")

# Excel保存
with pd.ExcelWriter(out_bright, engine="openpyxl") as writer:
    integrated_bright.to_excel(writer, index=False, sheet_name="Bright")

with pd.ExcelWriter(out_dark, engine="openpyxl") as writer:
    integrated_dark.to_excel(writer, index=False, sheet_name="Dark")

print(f"[OK] Bright: {len(bright_files)} files, {n_bright} subjects -> {len(integrated_bright)} rows")
print(f"     保存: {out_bright}")
print(f"[OK] Dark: {len(dark_files)} files, {n_dark} subjects -> {len(integrated_dark)} rows")
print(f"     保存: {out_dark}")
