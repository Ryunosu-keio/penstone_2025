# -*- coding: utf-8 -*-
"""
4_task_window_combined.py
------------------------------------
Pages画像とTask Windows画像を統合して保存するスクリプト

- Bright: S01～S19, seg 0～9
- Dark: S101～S119, seg 0～9

出力先: ../../data/task_windows_combined/{params}/{Condition}/{SubjectID}/
"""

import os
import glob
from PIL import Image
import matplotlib.pyplot as plt
from tqdm import tqdm


def combine_images(condition, subject_id, segment, params, input_base_dir, output_base_dir):
    """
    Pages画像とTask Windows画像を統合して保存

    Parameters:
    -----------
    condition : str
        "Bright" or "Dark"
    subject_id : str
        被験者ID（例: "S01", "S101"）
    segment : int
        セグメント番号（0～9）
    params : str
        パラメータフォルダ名（例: "lag0p0_mioF100_BLstim120_markers"）
    input_base_dir : str
        入力画像のベースディレクトリ
    output_base_dir : str
        出力先のベースディレクトリ
    """
    # ファイルパスを構築
    # Pages: data/graphs/pages/{Condition}/{SubjectID}/{SubjectID}_{seg}_with_emr/
    pages_pattern = os.path.join(
        input_base_dir, "graphs", "pages", condition, subject_id,
        f"{subject_id}_{segment}_with_emr", f"{subject_id}_{segment}_with_emr_page_*.png"
    )

    # Task Windows: data/task_windows/{params}/{Condition}/{SubjectID}/{SubjectID}_{seg}_grid_4x16.png
    task_windows_pattern = os.path.join(
        input_base_dir, "task_windows", params, condition, subject_id,
        f"{subject_id}_{segment}_grid_4x16.png"
    )

    pages_files = sorted(glob.glob(pages_pattern))
    task_windows_files = sorted(glob.glob(task_windows_pattern))

    if not pages_files and not task_windows_files:
        return False, "画像なし"

    # 全体のレイアウトを計算
    n_pages = min(len(pages_files), 3)  # 最大3枚
    n_task_windows = len(task_windows_files)

    # 行数を決定（Pages行 + Task Windows行）
    n_rows = (1 if n_pages > 0 else 0) + (1 if n_task_windows > 0 else 0)

    if n_rows == 0:
        return False, "画像なし"

    fig = plt.figure(figsize=(24, 8 * n_rows))

    current_row = 1

    # Pages画像を上段に横並び
    if n_pages > 0:
        for i, img_path in enumerate(pages_files[:3]):
            ax = plt.subplot(n_rows, 3, i + 1)
            try:
                img = Image.open(img_path)
                ax.imshow(img)
            except Exception as e:
                ax.text(0.5, 0.5, f"Error: {e}", ha='center', va='center', transform=ax.transAxes)
            ax.axis('off')
            ax.set_title(os.path.basename(img_path), fontsize=10)
        current_row += 1

    # Task Windows画像を下段に表示
    if n_task_windows > 0:
        for j, img_path in enumerate(task_windows_files):
            # 下段は全幅を使用
            ax = plt.subplot(n_rows, 1, current_row + j)
            try:
                img = Image.open(img_path)
                ax.imshow(img)
            except Exception as e:
                ax.text(0.5, 0.5, f"Error: {e}", ha='center', va='center', transform=ax.transAxes)
            ax.axis('off')
            ax.set_title(os.path.basename(img_path), fontsize=10)

    plt.suptitle(f"{condition} {subject_id} seg={segment}", fontsize=14, y=0.98)
    plt.tight_layout(rect=[0, 0, 1, 0.97])

    # 画像を保存（被験者ごとのフォルダ）
    save_dir = os.path.join(output_base_dir, params, condition, subject_id)
    os.makedirs(save_dir, exist_ok=True)
    save_path = os.path.join(save_dir, f"{subject_id}_{segment}_combined.png")

    fig.savefig(save_path, dpi=150, bbox_inches='tight', pad_inches=0.3)
    plt.close()

    return True, save_path


def main():
    # ベースディレクトリ
    input_base_dir = "../../data"
    output_base_dir = "../../data/task_windows_combined"

    # 利用可能なパラメータフォルダを探索
    task_windows_base = os.path.join(input_base_dir, "task_windows")
    available_params = []
    if os.path.exists(task_windows_base):
        for item in os.listdir(task_windows_base):
            if os.path.isdir(os.path.join(task_windows_base, item)):
                available_params.append(item)

    if not available_params:
        print("エラー: task_windowsフォルダにパラメータフォルダが見つかりません")
        return

    print("\n=== 利用可能なパラメータ ===")
    for i, param in enumerate(available_params, 1):
        print(f"{i}. {param}")

    param_idx = int(input(f"\n使用するパラメータを選択 (1-{len(available_params)}): ")) - 1
    params = available_params[param_idx]

    # 処理リストを作成
    configs = []
    for s in range(1, 20):
        for seg in range(0, 10):
            configs.append(("Bright", f"S{s:02d}", seg))
    for s in range(101, 120):
        for seg in range(0, 10):
            configs.append(("Dark", f"S{s:03d}", seg))

    print(f"\n{'='*60}")
    print(f"🔄 Pages + Task Windows 統合処理")
    print(f"{'='*60}")
    print(f"  パラメータ: {params}")
    print(f"  処理対象: {len(configs)} 件")
    print(f"  Bright: S01～S19 × seg 0～9")
    print(f"  Dark: S101～S119 × seg 0～9")
    print(f"  出力先: {os.path.abspath(output_base_dir)}/{params}/")
    print(f"{'='*60}\n")

    success_count = 0
    skip_count = 0
    error_count = 0

    for condition, subject_id, segment in tqdm(configs, desc="処理中"):
        try:
            success, result = combine_images(
                condition, subject_id, segment, params, input_base_dir, output_base_dir
            )

            if success:
                success_count += 1
            else:
                skip_count += 1

        except Exception as e:
            error_count += 1
            print(f"\n  ❌ エラー ({condition} {subject_id} seg={segment}): {e}")
            continue

    print(f"\n{'='*60}")
    print("🎉 全処理完了")
    print(f"  ✅ 成功: {success_count} 件")
    print(f"  ⚠️  スキップ: {skip_count} 件")
    print(f"  ❌ エラー: {error_count} 件")
    print(f"  📁 保存先: {os.path.abspath(output_base_dir)}/{params}/")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()
