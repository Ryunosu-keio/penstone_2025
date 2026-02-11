import cv2
import os
import glob
from tqdm import tqdm

# ==========================================
# 設定
# ==========================================
SOURCE_ROOT = r"G:\pictures_verify\original_data_verify"
OUTPUT_ROOT = r"G:\pictures_verify\transformed_verify"

# 処理対象のサブフォルダ
TARGET_FOLDERS = ["roomBright_figureDark_std", "roomDark_figureBright_std"]

# ==========================================
# クロップ処理関数
# ==========================================
def process_crop(img, crop_mode, crop_params):
    height, width = img.shape[:2]

    if crop_mode == 'A':
        # A: 自動検出 (黒背景除去)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        _, thresh = cv2.threshold(gray, 10, 255, cv2.THRESH_BINARY)
        coords = cv2.findNonZero(thresh)
        if coords is not None:
            x, y, w, h = cv2.boundingRect(coords)
            return img[y:y+h, x:x+w]
        return img

    elif crop_mode == 'B':
        # B: 固定値指定
        top, bottom = crop_params
        if top + bottom < height:
            return img[top : height - bottom, :]
        return img

    else:
        return img

def main():
    print("--- 全画像クロップ処理ツール ---")

    if not os.path.exists(SOURCE_ROOT):
        print(f"エラー: 元画像フォルダが見つかりません -> {SOURCE_ROOT}")
        return

    # --- クロップ設定入力 ---
    print("\n設定を選択してください:")
    print("A: 自動検出 (黒帯を除去)")
    print("B: 固定値指定 (上下を指定ピクセルカット)")
    crop_mode = input("選択 (A or B): ").upper()

    crop_params = []
    if crop_mode == 'B':
        try:
            top = int(input("上部カット量 (px): "))
            bottom = int(input("下部カット量 (px): "))
            crop_params = [top, bottom]
        except ValueError:
            print("数値で入力してください。")
            return

    print(f"\n処理を開始します。保存先: {OUTPUT_ROOT}")

    # --- フォルダごとのループ ---
    for folder in TARGET_FOLDERS:
        src_dir = os.path.join(SOURCE_ROOT, folder)
        dst_dir = os.path.join(OUTPUT_ROOT, folder)

        if not os.path.exists(src_dir):
            print(f"スキップ: フォルダがありません {src_dir}")
            continue

        os.makedirs(dst_dir, exist_ok=True)

        # 画像取得
        files = glob.glob(os.path.join(src_dir, "*"))
        # 数字で始まるファイルのみ対象（不要なファイルを除外）
        image_files = [f for f in files if os.path.basename(f)[0].isdigit()]

        print(f"\nProcessing {folder} ({len(image_files)} files)...")

        for f in tqdm(image_files):
            basename = os.path.basename(f)
            save_path = os.path.join(dst_dir, basename)

            img = cv2.imread(f)
            if img is not None:
                # クロップ実行
                cropped_img = process_crop(img, crop_mode, crop_params)
                # 保存
                cv2.imwrite(save_path, cropped_img, [cv2.IMWRITE_JPEG_QUALITY, 100])
            else:
                print(f"読込失敗: {basename}")

    print("\n全てのクロップ処理が完了しました。")

if __name__ == "__main__":
    main()
