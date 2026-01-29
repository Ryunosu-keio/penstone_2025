import pandas as pd
import os

# ===== 読み込み =====
# df_pupil = pd.read_excel("final_recalculated_pupil.xlsx")
# df_feature = pd.read_excel("./final_recent_bright_add_entropy_skewgray2_michaelson_sf_mse_sf2_luminance_sobel_std_par_figure.xlsx")

df_pupil = pd.read_excel("./darkfinal_recalculated_pupil.xlsx")
df_feature = pd.read_excel("./darkfinal_recent_dark_add_entropy_fft_color_skewgray2_michaelson_sf_mse_luminance_sobel_std_par_figure.xlsx")
KEYS = ["folder_name", "file_name", "frame"]

# ===== 型合わせ（ズレ防止）=====
for c in KEYS:
    df_pupil[c] = pd.to_numeric(df_pupil[c], errors="coerce").astype("Int64")
    df_feature[c] = pd.to_numeric(df_feature[c], errors="coerce").astype("Int64")

# ===== 追加したい瞳孔列 =====
pupil_cols = [
    "左眼[mm]", "右眼[mm]", "平均[mm]",
    "左眼_ベースライン[mm]", "右眼_ベースライン[mm]", "平均_ベースライン[mm]",
    "左眼_変化率", "右眼_変化率", "平均_変化率"
]

# ===== キー重複チェック =====
dup_pupil = df_pupil.duplicated(KEYS).sum()
dup_feature = df_feature.duplicated(KEYS).sum()

print("=== Key重複チェック ===")
print(f"pupil側 重複数: {dup_pupil}")
print(f"feature側 重複数: {dup_feature}")

if dup_pupil > 0:
    print("⚠ pupil側でキーが重複してるので、mergeで行が増殖する可能性あり")

if dup_feature > 0:
    print("⚠ feature側でキーが重複してる（元から複数行ある）ので、想定通りか確認して")

# ===== マージ =====
df_merge = df_feature.merge(
    df_pupil[KEYS + pupil_cols],
    on=KEYS,
    how="left"
)

# ===== 結合成功/失敗数チェック =====
# 「追加した列が全部NaN = 結合失敗」と判定
merge_failed = df_merge[pupil_cols].isna().all(axis=1).sum()
merge_success = len(df_merge) - merge_failed

print("\n=== Merge結果 ===")
print(f"featureデータ行数: {len(df_feature)}")
print(f"マージ後行数: {len(df_merge)}")
print(f"結合成功: {merge_success}")
print(f"結合失敗(追加列が全NaN): {merge_failed}")
print(f"成功率: {merge_success/len(df_merge)*100:.2f}%")

# ===== 結合失敗の例を表示（確認用）=====
if merge_failed > 0:
    print("\n--- 結合失敗の先頭5件（キー）---")
    print(df_merge.loc[df_merge[pupil_cols].isna().all(axis=1), KEYS].head(5))

# ===== 保存 =====
out_path = "merged_with_pupil_dark.xlsx"
df_merge.to_excel(out_path, index=False)
print(f"\n保存しました: {out_path}")
