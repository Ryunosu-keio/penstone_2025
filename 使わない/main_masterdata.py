# -*- coding: utf-8 -*-
"""
main_masterdata.py (Bright+Dark, Master作成→被験者10人分シャッフルExcel作成)
================================================================================

要件:
- Bright と Dark を一度に生成
- Excel 出力:
    imageCreationExcel/Bright/<被験者番号>/0..19.xlsx
    imageCreationExcel/Dark/<被験者番号>/0..19.xlsx
- 画像 出力:
    F:\\experiment_images_verify\\Bright\\<被験者番号>\\0..19\\*.jpg
    F:\\experiment_images_verify\\Dark\\<被験者番号>\\0..19\\*.jpg
  ※ Master画像を一旦作って、被験者フォルダへ hardlink/copy で配布

48試行仕様（各セット）:
- front: 1/3 数字(16回), 2/3 アルファベット(32回)
- 数字は連続しない（digit試行同士が隣接しない）
- status:
    - digit試行: match/unmatch を半々（8/8）
    - filler試行: "filler"
- back:
    - match: frontと同じ数字
    - unmatch: frontと異なる数字
    - filler: ランダム数字
- process: True/False が半々（24/24）
    - digit試行: base_keyごとに (raw/proc)×(match/unmatch) = 4本 → 16本
    - filler試行: base_keyごとに 8本（raw4/proc4） → 32本
- filename: 元画像（絶対パス）
- param1..3: process=True のとき stimuli_xlsx から引用。無ければ「変化が出る」仮値を決定的に入れる。
- image_name: 元画像に param を適用して保存した画像のファイル名（実際に生成）

注意:
- Bright は day_* の base_key 4つのみ
- Dark は night_* の base_key 4つのみ（混在なし）
"""

import os
import re
import shutil
import random
import hashlib
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import numpy as np
import pandas as pd
import cv2
from PIL import Image
from tqdm import tqdm


# ==========================================
# 設定（ここだけ編集）
# ==========================================
SEED = None           # None=毎回ランダム / 固定したければ int
N_SETS = 20
N_SUBJECTS = 10
SUBJECT_PREFIX = "S"  # S01..S10
JPEG_QUALITY = 95

# TARGET_SIZE = (1536, 1024)  # (W,H)
TARGET_SIZE = (1500, 434)  # (W,H)

OUT_IMAGES_ROOT = Path(r"F:\experiment_images_verify")
OUT_EXCEL_ROOT  = Path(r"C:\Users\きよた\code\penstone_2025\imageCreationExcel")

# stimuli_xlsx（無ければダミーに落ちる）
SIM_PARAM_DIR = Path(r".\simulated_param_list")

CONDITIONS = [
    {
        "name": "Bright",
        "source_root": Path(r"F:\pictures_verify\transformed_verify\roomBright_figureDark"),
        "param_xlsx": SIM_PARAM_DIR / "Bright.xlsx",
        "base_keys": ["day_sun_busy", "day_sun_empty", "day_rain_busy", "day_rain_empty"],
    },
    {
        "name": "Dark",
        "source_root": Path(r"F:\pictures_verify\transformed_verify\roomDark_figureBright"),
        "param_xlsx": SIM_PARAM_DIR / "Dark.xlsx",
        "base_keys": ["night_sun_busy", "night_sun_empty", "night_rain_busy", "night_rain_empty"],
    },
]

# Master excelを保存したければ True
SAVE_MASTER_EXCEL = False
# ==========================================


# ==========================================
# 日本語パス対応 I/O
# ==========================================
def imread_japanese(path: Path, flags=cv2.IMREAD_COLOR):
    n = np.fromfile(str(path), np.uint8)
    img = cv2.imdecode(n, flags)
    return img

def imwrite_japanese_jpg(path: Path, img_bgr: np.ndarray, quality: int = 95):
    ok, buf = cv2.imencode(".jpg", img_bgr, [cv2.IMWRITE_JPEG_QUALITY, int(quality)])
    if not ok:
        raise RuntimeError(f"Failed to encode jpg: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "wb") as f:
        buf.tofile(f)

def link_or_copy(src: Path, dst: Path):
    dst.parent.mkdir(parents=True, exist_ok=True)
    if dst.exists():
        return
    try:
        os.link(str(src), str(dst))  # hardlink（同一ドライブなら高速）
    except Exception:
        shutil.copy2(str(src), str(dst))


# ==========================================
# 画像整形（横幅一致 + 上下黒帯）
# ==========================================
def letterbox_to_target(img_bgr: np.ndarray, target_w: int, target_h: int) -> np.ndarray:
    h, w = img_bgr.shape[:2]
    if w <= 0 or h <= 0:
        return np.zeros((target_h, target_w, 3), np.uint8)

    scale = target_w / float(w)        # 横幅を必ず一致
    new_h = int(round(h * scale))
    resized = cv2.resize(img_bgr, (target_w, new_h), interpolation=cv2.INTER_LANCZOS4)

    if new_h == target_h:
        return resized
    if new_h < target_h:
        pad_total = target_h - new_h
        pad_top = pad_total // 2
        pad_bot = pad_total - pad_top
        return cv2.copyMakeBorder(resized, pad_top, pad_bot, 0, 0,
                                  borderType=cv2.BORDER_CONSTANT, value=(0, 0, 0))
    # 高さ超過なら上下だけクロップ（横は絶対クロップしない）
    crop_top = (new_h - target_h) // 2
    return resized[crop_top:crop_top + target_h, :, :]


# ==========================================
# index作成（parser依存しない）
# - digit: stem内の最初の0-9
# - base_key: base_keys のいずれが stem に含まれるか
# ==========================================
def extract_digit_basekey(path: Path, base_keys: List[str]) -> Tuple[Optional[str], Optional[str]]:
    stem = path.stem
    m = re.search(r'([0-9])', stem)
    digit = m.group(1) if m else None

    base_key = None
    for bk in base_keys:
        if bk in stem:
            base_key = bk
            break

    return digit, base_key

def build_index(source_root: Path, base_keys: List[str]) -> Dict[str, Dict[str, Path]]:
    index: Dict[str, Dict[str, Path]] = {bk: {} for bk in base_keys}
    files = [p for p in source_root.rglob("*") if p.suffix.lower() in [".jpg", ".jpeg", ".png"]]
    if not files:
        raise RuntimeError(f"No image files found under {source_root}")

    used = 0
    skipped = 0
    for p in files:
        d, bk = extract_digit_basekey(p, base_keys)
        if d is None or bk is None:
            skipped += 1
            continue
        index[bk][d] = p
        used += 1

    print(f"[INFO] indexed under {source_root}: used={used}, skipped={skipped}, scanned={len(files)}")

    if used == 0:
        sample = [x.name for x in files[:10]]
        raise RuntimeError(
            f"No usable images found under {source_root}\n"
            f"Sample files: {sample}\n"
            f"Expected base_keys in filename: {base_keys}"
        )

    for bk in base_keys:
        if len(index[bk]) == 0:
            raise RuntimeError(f"Missing any images for base_key={bk} under {source_root}")
    return index


# ==========================================
# stimuli param 読み込み / 無ければダミー（変化が出る）
# ==========================================
def load_param_map(param_xlsx: Path) -> Dict[str, Tuple]:
    df = pd.read_excel(param_xlsx)
    need = {"filename", "param1", "param1_value", "param2", "param2_value", "param3", "param3_value"}
    if not need.issubset(df.columns):
        raise RuntimeError(f"PARAM_XLSX must include columns: {sorted(list(need))}")

    mp: Dict[str, Tuple] = {}
    for _, r in df.iterrows():
        key = Path(str(r["filename"])).stem  # stem照合

        def _p(x):
            return (np.nan if pd.isna(x) else str(x))

        def _v(x):
            return (np.nan if pd.isna(x) else float(x))

        mp[key] = (
            _p(r["param1"]), _v(r["param1_value"]),
            _p(r["param2"]), _v(r["param2_value"]),
            _p(r["param3"]), _v(r["param3_value"]),
        )
    print(f"[INFO] loaded stimuli params: {len(mp)} rows from {param_xlsx}")
    return mp

def _stable_hash01(s: str) -> float:
    h = hashlib.md5(s.encode("utf-8")).hexdigest()
    return int(h[:8], 16) / float(0xFFFFFFFF)

def build_dummy_param_map_from_index(index: Dict[str, Dict[str, Path]]) -> Dict[str, Tuple]:
    """
    stimuli_xlsx が無いとき用（変化が出る範囲にする、かつ決定的）
    brightness: -18..+18
    contrast  : 1.05..1.25
    gamma     : 0.85..1.05
    """
    dummy = {}
    for bk, digit_map in index.items():
        for d, p in digit_map.items():
            key = p.stem
            r1 = _stable_hash01(key)
            r2 = _stable_hash01(key + "_c")
            r3 = _stable_hash01(key + "_g")
            brightness = -18.0 + 36.0 * r1
            contrast   = 1.05 + 0.20 * r2
            gamma      = 0.85 + 0.20 * r3
            dummy[key] = (
                "brightness", float(round(brightness, 3)),
                "contrast",   float(round(contrast, 3)),
                "gamma",      float(round(gamma, 3)),
            )
    print(f"[WARN] stimuli_xlsx not found -> using dummy params for {len(dummy)} images (visible change).")
    return dummy


# ==========================================
# 画像処理（param1..3適用）
# ==========================================
def slide_brightness(pil: Image.Image, shift: float) -> Image.Image:
    img = np.array(pil).astype("float32") / 255.0
    hsv = cv2.cvtColor(img, cv2.COLOR_RGB2HSV)
    hsv[:, :, 2] = np.clip(hsv[:, :, 2] + float(shift) / 255.0, 0, 1)
    out = cv2.cvtColor(hsv, cv2.COLOR_HSV2RGB)
    return Image.fromarray(np.round(out * 255).astype("uint8"))

def adjust_contrast(pil: Image.Image, scale: float) -> Image.Image:
    img = np.array(pil)
    hsv = cv2.cvtColor(img, cv2.COLOR_RGB2HSV)
    hsv[:, :, 2] = cv2.convertScaleAbs(hsv[:, :, 2], alpha=float(scale))
    out = cv2.cvtColor(hsv, cv2.COLOR_HSV2RGB)
    return Image.fromarray(out.astype("uint8"))

def adjust_gamma(pil: Image.Image, gamma: float) -> Image.Image:
    gamma = float(gamma)
    lut = np.array([((i / 255.0) ** gamma) * 255 for i in range(256)]).astype("uint8")
    out = cv2.LUT(np.array(pil), lut)
    return Image.fromarray(out.astype("uint8"))

def apply_one(pil: Image.Image, name: str, val: float) -> Image.Image:
    name = str(name).strip().lower()
    if name == "brightness":
        return slide_brightness(pil, val)
    if name == "contrast":
        return adjust_contrast(pil, val)
    if name == "gamma":
        return adjust_gamma(pil, val)
    return pil

def apply_1to3(pil: Image.Image, p1, v1, p2, v2, p3, v3) -> Image.Image:
    out = pil
    for p, v in [(p1, v1), (p2, v2), (p3, v3)]:
        if pd.isna(p) or pd.isna(v):
            continue
        out = apply_one(out, str(p), float(v))
    return out


# ==========================================
# 48試行の設計（pool→sequence）
# ==========================================
def make_letters_no_repeat(n: int, rng: random.Random) -> List[str]:
    letters = list("ABCDEFGIJLPQRSTU")
    out = []
    prev = None
    for _ in range(n):
        cand = [c for c in letters if c != prev]
        ch = rng.choice(cand)
        out.append(ch)
        prev = ch
    return out

def make_trial_pool_48(base_keys: List[str], rng: random.Random) -> Tuple[List[dict], List[dict]]:
    digits = list("0123456789")

    # digit 16: base_keyごとに (raw/proc)×(match/unmatch)=4本 → 合計16
    digit_trials = []
    for bk in base_keys:
        for proc in [False, True]:
            for status in ["match", "unmatch"]:
                back = rng.choice(digits)
                front = back if status == "match" else rng.choice([d for d in digits if d != back])
                digit_trials.append({
                    "front": front,
                    "status": status,
                    "back": back,
                    "process": proc,
                    "base_key": bk,
                    "trial_type": "digit",
                })

    # filler 32: base_keyごとに8本、raw4/proc4
    filler_trials = []
    letters = make_letters_no_repeat(32, rng)
    li = 0
    for bk in base_keys:
        for _ in range(4):
            filler_trials.append({
                "front": letters[li],
                "status": "filler",
                "back": rng.choice(digits),
                "process": False,
                "base_key": bk,
                "trial_type": "filler",
            })
            li += 1
        for _ in range(4):
            filler_trials.append({
                "front": letters[li],
                "status": "filler",
                "back": rng.choice(digits),
                "process": True,
                "base_key": bk,
                "trial_type": "filler",
            })
            li += 1

    rng.shuffle(digit_trials)
    rng.shuffle(filler_trials)
    return digit_trials, filler_trials

def make_slot_plan_48(rng: random.Random) -> List[str]:
    # digitが連続しないように digitの間に必ずfillerを挟む
    gaps = [0] * 17
    for i in range(1, 16):
        gaps[i] = 1
    remaining = 32 - 15  # 17
    for _ in range(remaining):
        gaps[rng.randrange(17)] += 1

    slots: List[str] = []
    slots += ["filler"] * gaps[0]
    for i in range(16):
        slots.append("digit")
        slots += ["filler"] * gaps[i + 1]

    if len(slots) != 48:
        raise RuntimeError("Internal error: slot length != 48")
    for i in range(47):
        if slots[i] == "digit" and slots[i + 1] == "digit":
            raise RuntimeError("Internal error: consecutive digit slot")
    return slots

def violates_local_constraints(seq: List[dict], cand: dict) -> bool:
    if not seq:
        return False
    last = seq[-1]

    # process 3連続禁止
    if len(seq) >= 2 and (seq[-1]["process"] == seq[-2]["process"] == cand["process"]):
        return True

    # base_key 3連続禁止
    if len(seq) >= 2 and (seq[-1]["base_key"] == seq[-2]["base_key"] == cand["base_key"]):
        return True

    # 同一(base_key,process) 連続禁止
    if (last["base_key"] == cand["base_key"]) and (last["process"] == cand["process"]):
        return True

    # アルファベット同一連続禁止（念のため）
    if (not str(last["front"]).isdigit()) and (not str(cand["front"]).isdigit()):
        if str(last["front"]) == str(cand["front"]):
            return True
    return False

def construct_sequence_48(digit_pool: List[dict], filler_pool: List[dict],
                          rng: random.Random, tries: int = 5000) -> List[dict]:
    for _ in range(tries):
        dp = digit_pool.copy()
        fp = filler_pool.copy()
        rng.shuffle(dp)
        rng.shuffle(fp)

        slots = make_slot_plan_48(rng)
        seq: List[dict] = []
        ok = True

        for slot in slots:
            pool = dp if slot == "digit" else fp
            candidates = [t for t in pool if not violates_local_constraints(seq, t)]
            if not candidates:
                ok = False
                break
            cand = rng.choice(candidates)
            seq.append(cand)
            pool.remove(cand)

        if ok and len(seq) == 48:
            return seq

    raise RuntimeError("Failed to construct 48-trial sequence under constraints.")


# ==========================================
# Master画像とMaster行の作成
# ==========================================
def make_master_set(
    condition_name: str,
    master_id: str,
    set_num: int,
    seq: List[dict],
    index: Dict[str, Dict[str, Path]],
    param_map: Dict[str, Tuple],
) -> pd.DataFrame:
    rows = []
    master_img_dir = OUT_IMAGES_ROOT / condition_name / master_id / str(set_num)
    master_img_dir.mkdir(parents=True, exist_ok=True)

    target_w, target_h = TARGET_SIZE

    for trial in tqdm(range(1, 49), desc=f"[{condition_name}] set{set_num} images", unit="trial", leave=False):
        t = seq[trial - 1]
        base_key = t["base_key"]
        back = str(t["back"])
        front = str(t["front"])
        status = str(t["status"])
        proc = bool(t["process"])

        if base_key not in index or back not in index[base_key]:
            raise RuntimeError(f"Missing image: base_key={base_key}, digit={back}")

        src_path = index[base_key][back]
        filename_abs = str(src_path.resolve())

        # 読み込み→letterbox
        img_bgr = imread_japanese(src_path, cv2.IMREAD_COLOR)
        if img_bgr is None:
            raise RuntimeError(f"Failed to read: {src_path}")
        img_bgr = letterbox_to_target(img_bgr, target_w, target_h)
        pil = Image.fromarray(cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB))

        # param列
        param1 = param1_value = param2 = param2_value = param3 = param3_value = np.nan

        tag = "PROC" if proc else "RAW"
        if proc:
            key = src_path.stem
            if key not in param_map:
                raise RuntimeError(f"Param missing for {key} (need stimuli_xlsx row or dummy map)")
            (param1, param1_value, param2, param2_value, param3, param3_value) = param_map[key]
            processed = apply_1to3(pil, param1, param1_value, param2, param2_value, param3, param3_value)

            ptag = ""
            for p, v in [(param1, param1_value), (param2, param2_value), (param3, param3_value)]:
                if pd.isna(p) or pd.isna(v):
                    continue
                ptag += f"_{p}{v}"
            image_name = f"M_{set_num}_{trial}_{front}_{status}_{back}_{base_key}_{tag}{ptag}.jpg"
        else:
            processed = pil
            image_name = f"M_{set_num}_{trial}_{front}_{status}_{back}_{base_key}_{tag}.jpg"

        out_path = master_img_dir / image_name
        out_bgr = cv2.cvtColor(np.array(processed), cv2.COLOR_RGB2BGR)
        imwrite_japanese_jpg(out_path, out_bgr, quality=JPEG_QUALITY)

        rows.append({
            "trial_id": f"M_{set_num}_{trial}",
            "folder_name": "MASTER",
            "file_name": set_num,
            "trial": trial,
            "front": front,
            "status": status,
            "back": back,
            "process": proc,
            "filename": filename_abs,
            "param1": param1, "param1_value": param1_value,
            "param2": param2, "param2_value": param2_value,
            "param3": param3, "param3_value": param3_value,
            "image_name": image_name,
            "_base_key": base_key,  # 内部用
        })

    return pd.DataFrame(rows)


# ==========================================
# Masterを被験者用にシャッフル（48内の制約維持）
# ==========================================
def reorder_master_df_for_subject(df_master: pd.DataFrame, rng: random.Random) -> pd.DataFrame:
    digit_pool = []
    filler_pool = []

    rows = df_master.to_dict("records")
    for r in rows:
        is_digit_front = str(r["front"]).isdigit()
        item = {
            "front": r["front"],
            "status": r["status"],
            "back": r["back"],
            "process": bool(r["process"]),
            "base_key": r["_base_key"],
            "trial_type": "digit" if is_digit_front else "filler",
            "_row": r,
        }
        if item["trial_type"] == "digit":
            digit_pool.append(item)
        else:
            filler_pool.append(item)

    seq = construct_sequence_48(digit_pool, filler_pool, rng)
    out_rows = [x["_row"] for x in seq]
    return pd.DataFrame(out_rows)


# ==========================================
# 条件ごとの処理
# ==========================================
def run_one_condition(cond: dict, cond_index: int):
    cond_name = cond["name"]
    source_root = Path(cond["source_root"])
    param_xlsx = Path(cond["param_xlsx"])
    base_keys = cond["base_keys"]

    print(f"\n====================")
    print(f" Condition: {cond_name}")
    print(f" Source  : {source_root}")
    print(f" Stimuli : {param_xlsx}")
    print(f" BaseKeys: {base_keys}")
    print(f"====================")

    if not source_root.exists():
        raise FileNotFoundError(f"{cond_name} SOURCE_ROOT not found: {source_root}")

    index = build_index(source_root, base_keys)

    if param_xlsx.exists():
        param_map = load_param_map(param_xlsx)
    else:
        param_map = build_dummy_param_map_from_index(index)

    # Excel root: imageCreationExcel/<Bright|Dark>/
    cond_excel_root = OUT_EXCEL_ROOT / cond_name
    cond_excel_root.mkdir(parents=True, exist_ok=True)
    if SAVE_MASTER_EXCEL:
        (cond_excel_root / "Master").mkdir(parents=True, exist_ok=True)

    # --- Master生成（20セット） ---
    master_dfs: List[pd.DataFrame] = []
    for set_num in tqdm(range(N_SETS), desc=f"[{cond_name}] Master sets", unit="set"):
        rng_set = random.Random()
        if SEED is None:
            rng_set.seed(random.randrange(1 << 30))
        else:
            rng_set.seed(int(SEED) + 10000 * (cond_index + 1) + 10 + set_num)

        digit_pool, filler_pool = make_trial_pool_48(base_keys, rng_set)
        seq = construct_sequence_48(digit_pool, filler_pool, rng_set)

        df_master = make_master_set(
            condition_name=cond_name,
            master_id="MASTER_IMAGES",
            set_num=set_num,
            seq=seq,
            index=index,
            param_map=param_map,
        )
        master_dfs.append(df_master)

        if SAVE_MASTER_EXCEL:
            out_master_xlsx = cond_excel_root / "Master" / f"MASTER_{set_num}.xlsx"
            df_master.drop(columns=["_base_key"]).to_excel(out_master_xlsx, index=False)

    # --- 被験者ごとにExcel作成 + 画像配布 ---
    for s in tqdm(range(1, N_SUBJECTS + 1), desc=f"[{cond_name}] Subjects", unit="subj"):
        subject_id = f"{SUBJECT_PREFIX}{s:02d}"
        subj_excel_dir = cond_excel_root / subject_id
        subj_excel_dir.mkdir(parents=True, exist_ok=True)

        for set_num in tqdm(range(N_SETS), desc=f"[{cond_name}] {subject_id} sets", unit="set", leave=False):
            df_master = master_dfs[set_num].copy()

            subj_rng = random.Random()
            if SEED is None:
                subj_rng.seed(random.randrange(1 << 30))
            else:
                subj_rng.seed(int(SEED) + 10000 * (cond_index + 1) + 1000 + s * 100 + set_num)

            df_sub = reorder_master_df_for_subject(df_master, subj_rng)

            # trial 1..48 に振り直し
            df_sub["trial"] = list(range(1, 49))
            df_sub["folder_name"] = subject_id
            df_sub["file_name"] = set_num
            df_sub["trial_id"] = [f"{subject_id}_{set_num}_{t}" for t in df_sub["trial"].tolist()]

            # 画像を被験者フォルダへ（Master→Subjectへ配布）
            master_img_dir = OUT_IMAGES_ROOT / cond_name / "MASTER_IMAGES" / str(set_num)
            subj_img_dir = OUT_IMAGES_ROOT / cond_name / subject_id / str(set_num)
            subj_img_dir.mkdir(parents=True, exist_ok=True)

            for img_name in df_sub["image_name"].tolist():
                src = master_img_dir / str(img_name)
                dst = subj_img_dir / str(img_name)
                if not src.exists():
                    raise FileNotFoundError(f"Master image missing: {src}")
                link_or_copy(src, dst)

            # Excel列順を指定通りに
            df_out = df_sub.drop(columns=["_base_key"])
            df_out = df_out[
                [
                    "trial_id",
                    "folder_name",
                    "file_name",
                    "trial",
                    "front",
                    "status",
                    "back",
                    "process",
                    "filename",
                    "param1", "param1_value",
                    "param2", "param2_value",
                    "param3", "param3_value",
                    "image_name",
                ]
            ]

            out_xlsx = subj_excel_dir / f"{set_num}.xlsx"
            df_out.to_excel(out_xlsx, index=False)

    print(f"[DONE] Condition completed: {cond_name}")


# ==========================================
# 実行
# ==========================================
def run():
    OUT_EXCEL_ROOT.mkdir(parents=True, exist_ok=True)
    OUT_IMAGES_ROOT.mkdir(parents=True, exist_ok=True)

    # seed Noneなら毎回ランダム → “ドリフト対策”の再現性が欲しい場合はSEEDを固定する
    if SEED is not None:
        random.seed(int(SEED))
        np.random.seed(int(SEED))

    for i, cond in enumerate(tqdm(CONDITIONS, desc="Conditions", unit="cond")):
        run_one_condition(cond, cond_index=i)

    print("\nALL DONE (Bright + Dark)")


if __name__ == "__main__":
    run()
