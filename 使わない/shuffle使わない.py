import pandas as pd
import random
import os
import glob
from tqdm import tqdm

# ==========================================
# ユーザー設定エリア
# ==========================================

# 1. マスターデータ（元となるExcelファイル）が入っているフォルダ
#    ※ main2025.py で "Master" や "999" などのIDで作ったフォルダを指定してください
MASTER_DIR = r"./imageCreationExcel/back/Bright/Master"

# 2. 出力先（この中に被験者IDごとのフォルダが作られます）
OUTPUT_ROOT = r"./imageCreationExcel/back/Bright"

# 3. 作成したい被験者IDのリスト（人数に関わらずここに追記すればOK）
#    例: 5人の場合 -> ["101", "102", "103", "104", "105"]
#    例: 10人の場合 -> [str(i) for i in range(101, 111)]  # 101-110
SUBJECT_IDS = ["101", "102", "103", "104", "105"]

# ==========================================
# ロジック（変更不要）
# ==========================================

def reshuffle_rows_with_gap_logic(df):
    """
    データフレームを受け取り、
    「数字(Target)が連続しない」ように並べ替える関数
    """
    targets = []
    ignores = []

    # 1. データをターゲットとIgnoreに分離
    for _, row in df.iterrows():
        # status列の表記ゆれに対応 (1/2/"Match"/"Mismatch" がターゲット)
        s = str(row['status']).strip()
        if s in ["Match", "Mismatch", "1", "2"]:
            targets.append(row)
        else:
            ignores.append(row)

    # 2. それぞれをシャッフル
    random.shuffle(targets)
    random.shuffle(ignores)

    # 3. Gap法による再配置
    # IgnoreがN個あれば、その間と両端に N+1 個の「隙間」がある
    n_ignore = len(ignores)
    n_target = len(targets)

    # ターゲット数が隙間数より多いと必ず連続してしまうため警告
    if n_ignore + 1 < n_target:
        print(f"【警告】Ignore({n_ignore})に対してTarget({n_target})が多すぎます。"
              "連続を回避できない可能性があります。")

    # 隙間のリストを作成
    gaps = [[] for _ in range(n_ignore + 1)]

    # ターゲットを入れる隙間のインデックスをランダムに選ぶ（重複なし＝1つの隙間に1個まで）
    # これにより「Ignore - Target - Ignore」が保証される
    available_indices = list(range(n_ignore + 1))
    selected_indices = random.sample(available_indices, k=n_target)

    for t_row, idx in zip(targets, selected_indices):
        gaps[idx].append(t_row)

    # 4. リストを結合して新しい順序を作る
    new_trials = []
    for i in range(n_ignore):
        new_trials.extend(gaps[i])      # 隙間のターゲット（あれば）
        new_trials.append(ignores[i])   # Ignore
    new_trials.extend(gaps[n_ignore])   # 最後の隙間のターゲット（あれば）

    return pd.DataFrame(new_trials)

def main():
    print("=== 被験者データ生成・シャッフルツール ===")

    # パスチェック
    if not os.path.exists(MASTER_DIR):
        print(f"エラー: マスターフォルダが見つかりません: {MASTER_DIR}")
        print("設定エリアの 'MASTER_DIR' を確認してください。")
        return

    # Excelファイル取得
    excel_files = glob.glob(os.path.join(MASTER_DIR, "*.xlsx"))
    if not excel_files:
        print(f"エラー: 指定フォルダにExcelファイルがありません: {MASTER_DIR}")
        return

    print(f"マスターファイル数: {len(excel_files)} (Set)")
    print(f"生成対象人数: {len(SUBJECT_IDS)} 人 {SUBJECT_IDS}")
    print("-" * 40)

    # 全ファイルをループ (Set0, Set1, ...)
    for master_file in tqdm(excel_files, desc="Processing Sets"):
        try:
            # マスター読み込み
            df_master = pd.read_excel(master_file)

            # ファイル名からセット番号などを取得 (例: Master_0.xlsx -> 0)
            base_name = os.path.splitext(os.path.basename(master_file))[0]
            parts = base_name.split('_')
            set_num = parts[-1] if len(parts) > 1 else "0"

            # 全被験者に対してループ
            for sub_id in SUBJECT_IDS:
                # 1. 行のシャッフル（ルール適用）
                df_new = reshuffle_rows_with_gap_logic(df_master)

                # 2. ID情報の書き換え
                # folder_name, trial_id, task_num を更新
                df_new['folder_name'] = sub_id
                df_new['file_name'] = set_num

                # タスク番号を連番で振り直し
                new_task_nums = range(1, len(df_new) + 1)
                df_new['task_num'] = new_task_nums

                # trial_id = ID_Set_TaskNum
                df_new['trial_id'] = [f"{sub_id}_{set_num}_{t}" for t in new_task_nums]

                # 3. 保存
                # 保存先フォルダ: Output/ID/
                sub_dir = os.path.join(OUTPUT_ROOT, str(sub_id))
                os.makedirs(sub_dir, exist_ok=True)

                # ファイル名: ID_Set.xlsx
                save_name = f"{sub_id}_{set_num}.xlsx"
                save_path = os.path.join(sub_dir, save_name)

                # 書き出し
                df_new.to_excel(save_path, index=False)

        except Exception as e:
            print(f"\n[Error] ファイル処理中にエラー: {master_file}")
            print(e)

    print("\n完了しました！すべての被験者データが生成されました。")

if __name__ == "__main__":
    main()
