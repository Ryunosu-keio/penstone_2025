import pandas as pd
import numpy as np
import cv2
import os
import glob
import random
from tqdm import tqdm
from PIL import Image

# ==========================================
# 設定
# ==========================================
SOURCE_ROOT = r"F:\pictures_verify\transformed_verify"     # クロップ済み画像の場所
IMAGE_OUTPUT_ROOT = "F:\\"                 # 実験画像の保存先ルート
EXCEL_OUTPUT_ROOT = "."                    # Excel保存先
SIM_PARAM_DIR = os.path.join(EXCEL_OUTPUT_ROOT, "simulated_param_list")

CONDITIONS = [
    {"folder": "roomBright_figureDark", "label": "Bright"},
    {"folder": "roomDark_figureBright", "label": "Dark"}
]

TRIALS_PER_SET = 48
TARGET_SIZE = (1536, 1024)

# ★ Status定義の更新
STATUS_LABEL_MAP = {
    1: "Match",
    2: "Mismatch",
    4: "Filler",
    5: "Ignore"  # アルファベット条件
}

# ==========================================
# ヘルパー関数
# ==========================================
def imread_japanese_path(filename, flags=cv2.IMREAD_COLOR):
    """日本語パスを含む画像を読み込む"""
    try:
        n = np.fromfile(filename, np.uint8)
        img = cv2.imdecode(n, flags)
        return img
    except Exception as e:
        return None

# ==========================================
# 画像処理関数群
# ==========================================
def slide_brightness(image, shift):
    img_np = np.array(image).astype('float32') / 255.0
    hsv = cv2.cvtColor(img_np, cv2.COLOR_RGB2HSV)
    hsv[:,:,2] = hsv[:,:,2] + shift / 255.0
    hsv[:,:,2] = np.clip(hsv[:,:,2], 0, 1)
    img_np = cv2.cvtColor(hsv, cv2.COLOR_HSV2RGB)
    image = Image.fromarray(np.round(img_np * 255).astype('uint8'))
    return image

def adjust_contrast_adachi(image, scale):
    img_np = np.array(image)
    hsv = cv2.cvtColor(img_np, cv2.COLOR_RGB2HSV)
    hsv[:,:,2] = cv2.convertScaleAbs(hsv[:,:,2], alpha=scale)
    img_np = cv2.cvtColor(hsv, cv2.COLOR_HSV2RGB)
    image = Image.fromarray(img_np.astype('uint8'))
    return image

def adjust_sharpness(image, sharpness):
    img_array = np.array(image)
    kernel = np.array([[-sharpness, -sharpness, -sharpness],
                       [-sharpness, 1 + 8 * sharpness, -sharpness],
                       [-sharpness, -sharpness, -sharpness]])
    img_sharpness = cv2.filter2D(img_array, -1, kernel)
    image = Image.fromarray(img_sharpness)
    return image

def adjust_blur(image, kernel_size):
    k = int(kernel_size)
    if k % 2 == 0: k += 1
    if k < 1: k = 1
    img_array = np.array(image)
    img_blur = cv2.blur(img_array, (k, k))
    image = Image.fromarray(img_blur)
    return image

def adjust_gamma(image, gamma):
    lookup = []
    for i in range(256):
        lookup.append(int(((i / 255.0) ** gamma) * 255))
    lookup = lookup * 3
    image = image.point(lookup)
    return image

def stretch_rgb_clahe(image, clipLimit=2.0, tile=8):
    img_np = np.array(image).astype('float32') / 255.0
    tile = int(tile)
    clahe = cv2.createCLAHE(clipLimit=clipLimit, tileGridSize=(tile,tile))
    for i in range(3):
        channel = (img_np[:,:,i] * 255).astype('uint8')
        img_np[:,:,i] = clahe.apply(channel) / 255.0
    image = Image.fromarray(np.round(img_np * 255).astype('uint8'))
    return image

EFFECTS_MAP = {
    'brightness':   {'func': slide_brightness,       'range': (-50, 50),    'type': 'int'},
    'contrast':     {'func': adjust_contrast_adachi, 'range': (0.5, 1.5),   'type': 'float'},
    'gamma':        {'func': adjust_gamma,           'range': (0.5, 1.8),   'type': 'float'},
    'sharpness':    {'func': adjust_sharpness,       'range': (0.0, 2.0),   'type': 'float'},
    'blur':         {'func': adjust_blur,            'range': (1, 5),       'type': 'int'},
    'equalization': {'func': stretch_rgb_clahe,      'range': (1.0, 4.0),   'type': 'float'}
}

def apply_specified_effects(pil_image, params_list):
    current_image = pil_image.copy()
    for name, val in params_list:
        if name in EFFECTS_MAP:
            func = EFFECTS_MAP[name]['func']
            if name == 'equalization':
                current_image = func(current_image, clipLimit=val, tile=8)
            else:
                current_image = func(current_image, val)
    return current_image

def apply_random_effects(pil_image):
    selected_keys = random.sample(list(EFFECTS_MAP.keys()), 3)
    param_info = []
    current_image = pil_image.copy()
    for key in selected_keys:
        effect = EFFECTS_MAP[key]
        min_v, max_v = effect['range']
        if effect['type'] == 'int':
            val = random.randint(int(min_v), int(max_v))
        else:
            val = round(random.uniform(min_v, max_v), 3)

        if key == 'equalization':
            current_image = effect['func'](current_image, clipLimit=val, tile=8)
        else:
            current_image = effect['func'](current_image, val)
        param_info.append((key, val))
    return current_image, param_info

def load_simulation_parameters(sim_dir, condition_label):
    if not os.path.exists(sim_dir):
        return None
    files = glob.glob(os.path.join(sim_dir, "*.xlsx"))
    if not files:
        return None

    target_file = None
    for f in files:
        if condition_label.lower() in os.path.basename(f).lower():
            target_file = f
            break

    if target_file is None:
        target_file = files[0]
        print(f"Warning: パラメータファイル代替 -> {os.path.basename(target_file)}")
    else:
        print(f"パラメータファイル使用: {os.path.basename(target_file)}")

    try:
        df = pd.read_excel(target_file)
        param_dict = {}
        for _, row in df.iterrows():
            fname = str(row['filename'])
            key = os.path.splitext(os.path.basename(fname))[0]
            params = []
            if 'param1' in row and pd.notna(row['param1']):
                params.append((row['param1'], row['param1_value']))
            if 'param2' in row and pd.notna(row['param2']):
                params.append((row['param2'], row['param2_value']))
            if 'param3' in row and pd.notna(row['param3']):
                params.append((row['param3'], row['param3_value']))
            param_dict[key] = params
        return param_dict
    except Exception as e:
        print(f"エラー: {e}")
        return None

# ==========================================
# データ生成関数 (Status更新版)
# ==========================================
def generate_trial_data(num_trials, available_images):
    # --- 比率設定 (合計1.0になるように) ---
    # Match: 30%, Mismatch: 30%, Filler: 20%, Ignore: 20%
    n_match = int(num_trials * 0.3)
    n_mismatch = int(num_trials * 0.3)
    n_ignore = int(num_trials * 0.2)
    # 端数はFillerで調整
    n_filler = num_trials - (n_match + n_mismatch + n_ignore)

    # ステータスリスト作成
    status_list = ([1] * n_match) + \
                  ([2] * n_mismatch) + \
                  ([4] * n_filler) + \
                  ([5] * n_ignore)
    random.shuffle(status_list)

    trials = []
    digits = "0123456789"
    letters = "ABCDEFGIJLPQRSTU"
    prev_char = None

    for status in status_list:
        row = {}
        row['status'] = status

        # --- Ignore (Front = Alphabet) ---
        if status == 5:
            # Frontはアルファベット
            available_letters = [c for c in letters if c != prev_char]
            front_char = random.choice(available_letters)
            row['front_char'] = front_char

            # Backは比較対象ではないが画像を表示する (ランダムな数字)
            dummy_digit = random.choice(digits)
            if available_images[dummy_digit]:
                row['image_path'] = random.choice(available_images[dummy_digit])
            else:
                row['image_path'] = "dummy.jpg"

        # --- Match / Mismatch / Filler (Front = Digit) ---
        else:
            available_digits = [d for d in digits if d != prev_char]
            front_char = random.choice(available_digits)
            row['front_char'] = front_char

            if status == 1: # Match (一致)
                target_digit = front_char
            else: # Mismatch(2) or Filler(4) (不一致)
                other_digits = [d for d in digits if d != front_char]
                target_digit = random.choice(other_digits)

            if available_images[target_digit]:
                row['image_path'] = random.choice(available_images[target_digit])
            else:
                row['image_path'] = "dummy.jpg"

        prev_char = front_char
        trials.append(row)

    return pd.DataFrame(trials)

# ==========================================
# メイン処理 (main2025)
# ==========================================
def main():
    try:
        import shutil
        _, _, free = shutil.disk_usage(IMAGE_OUTPUT_ROOT)
        if free // (2**30) < 2:
            print("【警告】ドライブの容量が残りわずかです！")
    except:
        pass

    print("\n=== main2025: 実験セット生成 (Status更新・Front文字ファイル名版) ===")
    sub_id = input("被験者番号を入力してください (例: 101): ")

    final_img_dir = os.path.join(IMAGE_OUTPUT_ROOT, "experiment_images_verify")
    final_excel_dir = os.path.abspath(os.path.join(EXCEL_OUTPUT_ROOT, "imageCreationExcel"))

    print(f"\n・読込元: {SOURCE_ROOT}")
    print(f"・画像保存先: {final_img_dir}")
    print(f"・Excel保存先: {final_excel_dir}")

    for cond in CONDITIONS:
        folder_name = cond["folder"]
        cond_label = cond["label"] # Bright or Dark

        print(f"\nTarget Condition: {folder_name} ({cond_label})")

        src_dir = os.path.join(SOURCE_ROOT, folder_name)
        if not os.path.exists(src_dir):
            print(f"【スキップ】フォルダなし: {src_dir}")
            continue

        all_files = glob.glob(os.path.join(src_dir, "*"))
        image_dict = {str(d): [] for d in range(10)}
        count = 0
        for f in all_files:
            basename = os.path.basename(f)
            if basename[0].isdigit():
                image_dict[basename[0]].append(f)
                count += 1

        if count == 0:
            print(f"【スキップ】画像なし: {src_dir}")
            continue

        sim_params_dict = load_simulation_parameters(SIM_PARAM_DIR, cond_label)

        for set_num in tqdm(range(20), desc=f"Processing {cond_label}"):

            # 画像フォルダ名 (重複防止: ID_Set_Cond)
            folder_unique_name = f"{sub_id}_{set_num}_{cond_label}"
            save_img_dir = os.path.join(final_img_dir, folder_unique_name)
            os.makedirs(save_img_dir, exist_ok=True)

            # Excelファイル名 (シンプル: ID_Set)
            excel_simple_name = f"{sub_id}_{set_num}"

            # ★ 更新された generate_trial_data を呼ぶ
            df = generate_trial_data(TRIALS_PER_SET, image_dict)

            excel_rows_back = []
            excel_rows_front = []

            for i, row in tqdm(df.iterrows(), total=len(df), desc=f"Set {set_num}", leave=False):
                # ID生成
                task_num = i + 1
                trial_id = f"{sub_id}_{set_num}_{task_num}"
                src_path = row['image_path']

                # Frontに表示される文字を取得
                front_char = str(row['front_char'])

                processed_img_cv2 = None
                param_info = []
                original_file_path = ""
                original_name_no_ext = ""

                FIXED_PARAMS_FOR_DUMMY = [('brightness', 0), ('contrast', 1), ('gamma', 1)]

                if src_path == "dummy.jpg":
                    original_file_path = "dummy"
                    original_name_no_ext = "dummy"
                    processed_img_cv2 = np.zeros((TARGET_SIZE[1], TARGET_SIZE[0], 3), np.uint8)
                    param_info = FIXED_PARAMS_FOR_DUMMY
                else:
                    original_file_path = os.path.abspath(src_path)
                    original_name_no_ext = os.path.splitext(os.path.basename(src_path))[0]
                    img = imread_japanese_path(src_path)

                    if img is not None:
                        pil_img = Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
                        if sim_params_dict and original_name_no_ext in sim_params_dict:
                            specified_params = sim_params_dict[original_name_no_ext]
                            processed_pil = apply_specified_effects(pil_img, specified_params)
                            param_info = specified_params
                        else:
                            processed_pil, param_info = apply_random_effects(pil_img)
                        processed_img_cv2 = cv2.cvtColor(np.array(processed_pil), cv2.COLOR_RGB2BGR)
                    else:
                        processed_img_cv2 = np.zeros((TARGET_SIZE[1], TARGET_SIZE[0], 3), np.uint8)
                        param_info = FIXED_PARAMS_FOR_DUMMY

                effect_suffix = ""
                for name, val in param_info:
                    effect_suffix += f"_{name}{val}"

                # ファイル名に front_char を追加 (trial_id_frontChar_originalName...)
                save_filename = f"{trial_id}_{front_char}_{original_name_no_ext}{effect_suffix}.jpg"
                save_path = os.path.join(save_img_dir, save_filename)

                try:
                    cv2.imwrite(save_path, processed_img_cv2, [cv2.IMWRITE_JPEG_QUALITY, 95])
                except:
                    pass

                status_val = row['status']
                status_str = STATUS_LABEL_MAP.get(status_val, str(status_val))

                data_row = {
                    "trial_id": trial_id,
                    "folder_name": sub_id,
                    "file_name": set_num,
                    "task_num": task_num,
                    "filename": original_file_path,
                    "status": status_str,
                    "image_name": save_filename
                }
                for idx, (p_name, p_val) in enumerate(param_info):
                    if idx < 3:
                        p_num = idx + 1
                        data_row[f"param{p_num}"] = p_name
                        data_row[f"param{p_num}_value"] = p_val

                excel_rows_back.append(data_row)
                excel_rows_front.append({"files": row['front_char']})

            # ★ Excel保存ディレクトリ構造 (back/条件/ID/...)
            excel_back_dir = os.path.join(EXCEL_OUTPUT_ROOT, "imageCreationExcel", "back", cond_label, sub_id)
            excel_front_dir = os.path.join(EXCEL_OUTPUT_ROOT, "imageCreationExcel", "front", cond_label, sub_id)

            os.makedirs(excel_back_dir, exist_ok=True)
            os.makedirs(excel_front_dir, exist_ok=True)

            cols_back = [
                "trial_id", "folder_name", "file_name", "task_num",
                "filename", "param1", "param1_value",
                "param2", "param2_value", "param3", "param3_value",
                "status", "image_name"
            ]

            df_back_out = pd.DataFrame(excel_rows_back)
            df_back_out = df_back_out.reindex(columns=cols_back, fill_value="")

            # シンプルなファイル名で保存
            df_back_out.to_excel(os.path.join(excel_back_dir, f"{excel_simple_name}.xlsx"), index=False)

            df_front_out = pd.DataFrame(excel_rows_front)
            df_front_out.to_excel(os.path.join(excel_front_dir, f"{excel_simple_name}_front.xlsx"), index=False)

    print("\n全条件の生成が完了しました。")

if __name__ == "__main__":
    main()
