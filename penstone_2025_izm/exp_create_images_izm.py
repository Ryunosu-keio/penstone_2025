# -*- coding: utf-8 -*-
"""
exp_create_images.py  (penstone_2025_izumiguchi)
=================================================
penstone/main.py の画像リスト・パラメータグリッド生成と、
penstone_2025/exp_create_images.py の繰り返し・ログ機構を統合した改善版。

変更点（penstone_2025 版からの差分）:
- 元画像: base_keys 4枚固定 → ディレクトリスキャンで自動取得（枚数任意）
- パラメータ: stimuli_xlsx → make_all_grid_dics() で自動生成
- process: original/model/brightonly → original/processed の2種
- similar_char_list: 不使用
- digit 出現確率: 1/3
- 出力ドライブ: input() で指定
"""

import os
import random
import shutil
from itertools import combinations, product
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import cv2
import numpy as np
import pandas as pd
from PIL import Image
from tqdm import tqdm


# ==========================================
# 設定（ここだけ編集）
# ==========================================
SEED = 42                 # 乱数シード。None=毎回ランダム / int=再現可能な固定シード
N_SETS = 10               # 1被験者あたりのセット数（各セットで異なる試行・パラメータが生成される）
N_SUBJECTS = 20           # 1条件あたりの被験者数
SUBJECT_PREFIX = "S"      # 被験者IDの接頭辞（Bright: S01〜S20 / Dark: S101〜S120）
JPEG_QUALITY = 95         # 出力画像のJPEG品質（0〜100）
TARGET_SIZE = (1500, 434) # 出力画像サイズ (幅, 高さ) ピクセル。元画像はこのサイズにリサイズ+黒帯で統一

# 1セットの試行数（固定）
# 数字試行(digit): front に数字を表示 → match/unmatch を判定する本番試行
# フィラー試行(filler): front にアルファベットを表示 → 判定不要のダミー試行
N_TRIALS = 48             # 1セットの総試行数
N_DIGIT = 16              # うち数字試行（全体の1/3）：8 match + 8 unmatch
N_FILLER = 32             # うちフィラー試行（全体の2/3）


OUT_EXCEL_ROOT = Path("./imageCreationExcel_izm")  # 試行情報Excelの出力先ディレクトリ

# Master excelを保存したければ True（現在は被験者ごと独立生成のため未使用）
SAVE_MASTER_EXCEL = False


# デフォルトパス（Enter で採用。実行時に変更可能）
DEFAULT_DRIVE = "F"                                                     # 画像出力先ドライブ
DEFAULT_SOURCE_BRIGHT = r"F:\pictures\original_data\roomBright_figureDark"  # Bright条件の元画像ディレクトリ
DEFAULT_SOURCE_DARK   = r"F:\pictures\original_data\roomDark_figureBright"  # Dark条件の元画像ディレクトリ


# ==========================================
# パラメータグリッド生成 (from penstone/back_rate.py)
# ==========================================
ADJUST_PARAMS = {
    "brightness": [0, 30],
    "contrast": [0.8, 1.2],
    "gamma": [0.5, 1.1],
    "sharpness": [0, 1.0],
    "equalization": [4, 32],
}


def make_all_grid_dics() -> List[Dict[str, Tuple[float, float]]]:
    """5パラメータから3つ選び、各レンジを3分割した全組合せを生成。
    brightness と equalization は同時に選ばない。"""
    three_key_combos = list(combinations(ADJUST_PARAMS.keys(), 3))
    three_key_combos = [
        c for c in three_key_combos
        if not ("brightness" in c and "equalization" in c)
    ]

    def split_into_three(r):
        lo, hi = r
        return [
            (round(lo + (hi - lo) * i / 3, 4), round(lo + (hi - lo) * (i + 1) / 3, 4))
            for i in range(3)
        ]

    all_combos = []
    for combo in three_key_combos:
        ranges = [split_into_three(ADJUST_PARAMS[k]) for k in combo]
        for values in product(*ranges):
            dic = {combo[i]: values[i] for i in range(3)}
            all_combos.append(dic)

    return all_combos


class ParamQueue:
    """パラメータグリッドの消費管理。pop で消費し、空になったら再シャッフル補充。"""

    def __init__(self, grid: List[dict], rng: random.Random):
        self._original = grid.copy()
        self._rng = rng
        self._queue: List[dict] = grid.copy()
        self._rng.shuffle(self._queue)

    def pop(self) -> dict:
        """1つ消費して返す。空なら再補充。"""
        if not self._queue:
            self._queue = self._original.copy()
            self._rng.shuffle(self._queue)
        return self._queue.pop(0)

    def choice(self) -> dict:
        """消費せずランダムに1つ返す。"""
        if not self._queue:
            self._queue = self._original.copy()
            self._rng.shuffle(self._queue)
        return self._rng.choice(self._queue)

    def sample_params(self, dic: dict) -> Tuple:
        """辞書の各キーのレンジから uniform サンプリングし、
        (param1, param1_value, param2, param2_value, param3, param3_value) を返す。"""
        keys = list(dic.keys())
        # equalization を末尾に移動（他のパラメータの後に適用するため）
        if "equalization" in keys:
            keys.remove("equalization")
            keys.append("equalization")

        result = []
        for k in keys:
            lo, hi = dic[k]
            val = self._rng.uniform(lo, hi)
            result.extend([k, val])

        # 2パラメータの場合は3つ目を NaN で埋める
        while len(result) < 6:
            result.extend([np.nan, np.nan])

        return tuple(result[:6])


# ==========================================
# ドライブ/パス選択ヘルパ
# ==========================================
def ask_drive() -> Path:
    """出力先ドライブを input() で質問して返す。デフォルト: DEFAULT_DRIVE"""
    drive = input(f"出力先ドライブ文字を入力してください [{DEFAULT_DRIVE}]: ").strip().upper()
    if not drive:
        drive = DEFAULT_DRIVE
    root = Path(f"{drive}:\\")
    if not root.exists():
        raise FileNotFoundError(f"ドライブが見つかりません: {root}")
    return root





# ==========================================
# 画像整形（横幅一致 + 上下黒帯）
# ==========================================
def letterbox_to_target(img_bgr: np.ndarray, target_w: int, target_h: int) -> np.ndarray:
    h, w = img_bgr.shape[:2]
    if w <= 0 or h <= 0:
        return np.zeros((target_h, target_w, 3), np.uint8)

    scale = target_w / float(w)
    new_h = int(round(h * scale))
    resized = cv2.resize(img_bgr, (target_w, new_h), interpolation=cv2.INTER_LANCZOS4)

    if new_h == target_h:
        return resized
    if new_h < target_h:
        pad_total = target_h - new_h
        pad_top = pad_total // 2
        pad_bot = pad_total - pad_top
        return cv2.copyMakeBorder(
            resized, pad_top, pad_bot, 0, 0,
            borderType=cv2.BORDER_CONSTANT, value=(0, 0, 0),
        )
    crop_top = (new_h - target_h) // 2
    return resized[crop_top : crop_top + target_h, :, :]


# ==========================================
# 画像スキャン
# ==========================================
def scan_source_images(source_root: Path) -> List[Path]:
    """source_root 以下の全画像ファイルを収集。"""
    exts = {".jpg", ".jpeg", ".png"}
    files = sorted(p for p in source_root.rglob("*") if p.suffix.lower() in exts)
    if not files:
        raise RuntimeError(f"画像が見つかりません: {source_root}")
    print(f"[INFO] {len(files)} 枚の画像を検出: {source_root}")
    return files


# ==========================================
# 画像処理関数 (from penstone_2025/exp_create_images.py)
# ==========================================
def slide_brightness(image, shift):
    img_np = np.array(image).astype("float32") / 255.0
    hsv = cv2.cvtColor(img_np, cv2.COLOR_RGB2HSV)
    hsv[:, :, 2] = np.clip(hsv[:, :, 2] + shift / 255.0, 0, 1)
    img_np = cv2.cvtColor(hsv, cv2.COLOR_HSV2RGB)
    return Image.fromarray(np.round(img_np * 255).astype("uint8"))


def adjust_contrast_adachi(image, scale):
    img_np = np.array(image)
    hsv = cv2.cvtColor(img_np, cv2.COLOR_RGB2HSV)
    hsv[:, :, 2] = cv2.convertScaleAbs(hsv[:, :, 2], alpha=scale)
    img_np = cv2.cvtColor(hsv, cv2.COLOR_HSV2RGB)
    return Image.fromarray(img_np.astype("uint8"))


def adjust_sharpness(image, sharpness):
    img_array = np.array(image)
    kernel = np.array(
        [[-sharpness, -sharpness, -sharpness],
         [-sharpness, 1 + 8 * sharpness, -sharpness],
         [-sharpness, -sharpness, -sharpness]]
    )
    img_sharpness = cv2.filter2D(img_array, -1, kernel)
    return Image.fromarray(img_sharpness)


def adjust_blur(image, kernel_size):
    img_array = np.array(image)
    k = max(1, int(kernel_size))
    img_blur = cv2.blur(img_array, (k, k))
    return Image.fromarray(img_blur)


def adjust_gamma(image, gamma):
    image = image.convert("RGB")
    gamma = float(gamma)
    gamma_correction = lambda value: int(((value / 255.0) ** gamma) * 255)
    return image.point(gamma_correction)


def stretch_rgb_clahe(image, clipLimit=2.0, tile=8):
    img_np = np.array(image).astype("float32") / 255.0
    tile = max(1, int(tile))
    clahe = cv2.createCLAHE(clipLimit, tileGridSize=(tile, tile))
    for i in range(3):
        img_np[:, :, i] = clahe.apply((img_np[:, :, i] * 255).astype("uint8")) / 255.0
    return Image.fromarray(np.round(img_np * 255).astype("uint8"))


def apply_one(pil: Image.Image, name: str, val: float) -> Image.Image:
    name = str(name).strip().lower()
    if name == "brightness":
        return slide_brightness(pil, float(val))
    if name == "contrast":
        return adjust_contrast_adachi(pil, float(val))
    if name == "sharpness":
        return adjust_sharpness(pil, float(val))
    if name == "blur":
        return adjust_blur(pil, int(round(float(val))))
    if name == "gamma":
        return adjust_gamma(pil, float(val))
    if name == "equalization":
        return stretch_rgb_clahe(pil, clipLimit=2.0, tile=max(1, int(round(float(val)))))
    return pil


def apply_params(pil: Image.Image, p1, v1, p2, v2, p3, v3) -> Image.Image:
    out = pil
    for p, v in [(p1, v1), (p2, v2), (p3, v3)]:
        if pd.isna(p) or pd.isna(v):
            continue
        out = apply_one(out, str(p), float(v))
    return out


# ==========================================
# front 文字列生成
# ==========================================
LETTERS = list("ABCDEFGJLPQRSTU")  # 15文字
DIGITS = list("0123456789")


def make_front_sequence(n: int, rng: random.Random) -> List[str]:
    """n 文字のフロント列を生成。1/DIGIT_DENOM の確率で数字、残りは文字。
    同一文字の連続を禁止。"""
    out: List[str] = []
    prev = None
    for _ in range(n):
        is_digit = rng.randint(1, DIGIT_DENOM) == DIGIT_DENOM
        while True:
            if is_digit:
                ch = rng.choice(DIGITS)
            else:
                ch = rng.choice(LETTERS)
            if ch != prev:
                break
        out.append(ch)
        prev = ch
    return out


# ==========================================
# 試行設計（48試行固定）
# ==========================================
def make_trial_pool(
    image_list: List[Path],
    n_digit: int,
    n_filler: int,
    rng: random.Random,
) -> Tuple[List[dict], List[dict]]:
    """digit と filler の試行プールを生成。画像はプールからランダム選択。"""
    # --- digit ---
    digit_trials = []
    for i in range(n_digit):
        img_path = rng.choice(image_list)
        back_digit = rng.choice(DIGITS)
        # match/unmatch を半々
        if i < n_digit // 2:
            status = "match"
            front = back_digit
        else:
            status = "unmatch"
            front = rng.choice([d for d in DIGITS if d != back_digit])
        digit_trials.append({
            "front": front,
            "status": status,
            "back": back_digit,
            "image_key": img_path.stem,
            "image_path": img_path,
            "trial_type": "digit",
        })

    # --- filler ---
    filler_trials = []
    for i in range(n_filler):
        img_path = rng.choice(image_list)
        filler_trials.append({
            "front": rng.choice(LETTERS),
            "status": "filler",
            "back": rng.choice(DIGITS),
            "image_key": img_path.stem,
            "image_path": img_path,
            "trial_type": "filler",
        })

    rng.shuffle(digit_trials)
    rng.shuffle(filler_trials)
    return digit_trials, filler_trials


def make_slot_plan(n_digit: int, n_filler: int, rng: random.Random) -> List[str]:
    """digit が連続しないようにスロット計画を生成。"""
    n_total = n_digit + n_filler
    # digit の間に必ず filler を1つ挟む → 最低 n_digit - 1 個の filler が必要
    if n_filler < n_digit - 1:
        raise RuntimeError(
            f"filler ({n_filler}) が不足: digit ({n_digit}) の間に挟めません"
        )

    # gaps[i] = i番目の digit の前に入る filler 数 (i=0 は先頭、i=n_digit は末尾)
    n_gaps = n_digit + 1
    gaps = [0] * n_gaps
    # まず digit 間の隙間に filler を1つずつ配置
    for i in range(1, n_digit):
        gaps[i] = 1
    remaining = n_filler - (n_digit - 1)
    # 残りをランダムに分配
    for _ in range(remaining):
        gaps[rng.randrange(n_gaps)] += 1

    slots: List[str] = []
    slots += ["filler"] * gaps[0]
    for i in range(n_digit):
        slots.append("digit")
        slots += ["filler"] * gaps[i + 1]

    assert len(slots) == n_total, f"slots={len(slots)} != total={n_total}"
    # 検証: digit が連続しないこと
    for i in range(len(slots) - 1):
        assert not (slots[i] == "digit" and slots[i + 1] == "digit")

    return slots


def violates_local_constraints(seq: List[dict], cand: dict) -> bool:
    """制約チェック: front 同一文字連続禁止。"""
    if not seq:
        return False
    last = seq[-1]
    # front 同一文字連続禁止
    if (not str(last["front"]).isdigit()) and (not str(cand["front"]).isdigit()):
        if str(last["front"]) == str(cand["front"]):
            return True
    return False


def construct_sequence(
    digit_pool: List[dict],
    filler_pool: List[dict],
    n_digit: int,
    n_filler: int,
    rng: random.Random,
    tries: int = 5000,
) -> List[dict]:
    """制約付きでシーケンスを構築。"""
    n_total = n_digit + n_filler
    for _ in range(tries):
        dp = digit_pool.copy()
        fp = filler_pool.copy()
        rng.shuffle(dp)
        rng.shuffle(fp)

        slots = make_slot_plan(n_digit, n_filler, rng)
        seq: List[dict] = []
        ok = True

        for slot in slots:
            pool = dp if slot == "digit" else fp
            candidates = [t for t in pool if not violates_local_constraints(seq, t)]
            if not candidates:
                # 制約を満たす候補がない場合、制約を緩和してプールから選択
                candidates = list(pool)
            if not candidates:
                ok = False
                break
            cand = rng.choice(candidates)
            seq.append(cand)
            pool.remove(cand)

        if ok and len(seq) == n_total:
            return seq

    raise RuntimeError(
        f"{tries}回の試行で制約付きシーケンス ({n_total}試行) を構築できませんでした。"
    )


# ==========================================
# パラメータタグ（ファイル名用）
# ==========================================
def _format_param_tag(p, v) -> str:
    if pd.isna(p) or pd.isna(v):
        return ""
    try:
        return f"_{str(p)}{float(v):.3f}"
    except Exception:
        return f"_{str(p)}{v}"


# ==========================================
# 被験者ごとの画像生成（Master方式なし）
# ==========================================
def generate_subject_set(
    condition_name: str,
    subject_id: str,
    set_num: int,
    seq: List[dict],
    param_queue: ParamQueue,
    out_images_root: Path,
) -> pd.DataFrame:
    """被験者×セット 単位で画像を生成し、DataFrame を返す。"""
    rows = []
    img_dir = out_images_root / condition_name / subject_id / str(set_num)
    img_dir.mkdir(parents=True, exist_ok=True)

    target_w, target_h = TARGET_SIZE

    for trial in range(1, len(seq) + 1):
        t = seq[trial - 1]
        image_key = t["image_key"]
        image_path = t["image_path"]
        front = str(t["front"])
        status = str(t["status"])
        back = str(t["back"])

        filename_abs = str(image_path.resolve())

        # 読み込み → letterbox
        img_bgr = cv2.imread(str(image_path), cv2.IMREAD_COLOR)
        if img_bgr is None:
            raise RuntimeError(f"画像読み込み失敗: {image_path}")
        img_bgr = letterbox_to_target(img_bgr, target_w, target_h)
        pil_orig = Image.fromarray(cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB))

        # 加工: digit では pop（消費）、filler では choice
        if t["trial_type"] == "digit":
            param_dic = param_queue.pop()
        else:
            param_dic = param_queue.choice()
        (param1, param1_value, param2, param2_value,
         param3, param3_value) = param_queue.sample_params(param_dic)
        processed = apply_params(
            pil_orig, param1, param1_value,
            param2, param2_value, param3, param3_value,
        )
        ptag = (
            _format_param_tag(param1, param1_value)
            + _format_param_tag(param2, param2_value)
            + _format_param_tag(param3, param3_value)
        )
        image_name = f"{subject_id}_{set_num}_{trial}_{front}_{status}_{back}_{image_key}{ptag}.jpg"

        out_path = img_dir / image_name
        out_bgr = cv2.cvtColor(np.array(processed), cv2.COLOR_RGB2BGR)
        cv2.imwrite(str(out_path), out_bgr, [cv2.IMWRITE_JPEG_QUALITY, int(JPEG_QUALITY)])

        rows.append({
            "trial_id": f"{subject_id}_{set_num}_{trial}",
            "folder_name": subject_id,
            "file_name": set_num,
            "trial": trial,
            "front": front,
            "status": status,
            "back": back,
            "filename": filename_abs,
            "param1": param1, "param1_value": param1_value,
            "param2": param2, "param2_value": param2_value,
            "param3": param3, "param3_value": param3_value,
            "image_name": image_name,
        })

    return pd.DataFrame(rows)


# ==========================================
# 条件ごとの処理
# ==========================================
def run_one_condition(
    cond: dict,
    cond_index: int,
    out_images_root: Path,
):
    cond_name = cond["name"]
    source_root = Path(cond["source_root"])

    print(f"\n====================")
    print(f" Condition: {cond_name}")
    print(f" Source  : {source_root}")
    print(f"====================")

    if not source_root.exists():
        raise FileNotFoundError(f"{cond_name} source_root が見つかりません: {source_root}")

    # 画像スキャン
    image_list = scan_source_images(source_root)
    n_images = len(image_list)
    print(f"[INFO] 画像数={n_images} → digit={N_DIGIT}, filler={N_FILLER}, total={N_TRIALS}")

    # パラメータグリッド生成
    grid = make_all_grid_dics()
    print(f"[INFO] パラメータグリッド: {len(grid)} パターン")

    # Excel root
    cond_excel_root = OUT_EXCEL_ROOT / cond_name
    cond_excel_root.mkdir(parents=True, exist_ok=True)

    # --- 被験者ごとに独立生成 ---
    for s in tqdm(range(1, N_SUBJECTS + 1), desc=f"[{cond_name}] Subjects", unit="subj"):
        if cond_name.lower() == "dark":
            sid_num = s + 100
            subject_id = f"{SUBJECT_PREFIX}{sid_num:03d}"
        else:
            sid_num = s
            subject_id = f"{SUBJECT_PREFIX}{sid_num:02d}"

        subj_excel_dir = cond_excel_root / subject_id
        subj_excel_dir.mkdir(parents=True, exist_ok=True)

        for set_num in tqdm(range(N_SETS), desc=f"[{cond_name}] {subject_id}", unit="set", leave=False):
            rng = random.Random()
            if SEED is None:
                rng.seed(random.randrange(1 << 30))
            else:
                rng.seed(int(SEED) + 10000 * (cond_index + 1) + 1000 * s + set_num)

            param_queue = ParamQueue(grid, rng)
            digit_pool, filler_pool = make_trial_pool(image_list, N_DIGIT, N_FILLER, rng)
            seq = construct_sequence(digit_pool, filler_pool, N_DIGIT, N_FILLER, rng)

            df = generate_subject_set(
                condition_name=cond_name,
                subject_id=subject_id,
                set_num=set_num,
                seq=seq,
                param_queue=param_queue,
                out_images_root=out_images_root,
            )

            # Excel
            col_order = [
                "trial_id", "folder_name", "file_name", "trial",
                "front", "status", "back", "filename",
                "param1", "param1_value", "param2", "param2_value",
                "param3", "param3_value", "image_name",
            ]
            df[col_order].to_excel(subj_excel_dir / f"{set_num}.xlsx", index=False)


    print(f"[DONE] Condition completed: {cond_name}")


# ==========================================
# 実行
# ==========================================
def run():
    OUT_EXCEL_ROOT.mkdir(parents=True, exist_ok=True)

    # 出力先ドライブ
    out_drive = ask_drive()
    out_images_root = out_drive / "experiment_images"
    out_images_root.mkdir(parents=True, exist_ok=True)

    if SEED is not None:
        random.seed(int(SEED))
        np.random.seed(int(SEED))

    # 条件設定（Enter でデフォルトパスを使用）
    bright_input = input(
        f"Bright 条件の画像ディレクトリパスを入力 [{DEFAULT_SOURCE_BRIGHT}]: "
    ).strip().strip('"')
    dark_input = input(
        f"Dark 条件の画像ディレクトリパスを入力 [{DEFAULT_SOURCE_DARK}]: "
    ).strip().strip('"')

    conditions = [
        {
            "name": "Bright",
            "source_root": bright_input if bright_input else DEFAULT_SOURCE_BRIGHT,
        },
        {
            "name": "Dark",
            "source_root": dark_input if dark_input else DEFAULT_SOURCE_DARK,
        },
    ]

    for i, cond in enumerate(tqdm(conditions, desc="Conditions", unit="cond")):
        run_one_condition(cond, cond_index=i, out_images_root=out_images_root)

    print("\nALL DONE (Bright + Dark)")


if __name__ == "__main__":
    run()
