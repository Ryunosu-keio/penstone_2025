# run_plate_only.py
import base64
import urllib.request
from pathlib import Path

from PIL import Image
from tqdm import tqdm
from openai import OpenAI

client = OpenAI()

# =====================
# ベース画像の探索先
# =====================
SCENE_DIR_PRIMARY = Path("inputs/scenes")
SCENE_DIR_FALLBACK = Path("outputs/_scenes")

# =====================
# 条件（4通り）
# weather: sun/rain
# congestion: busy/empty
# =====================
SCENARIOS = [
    ("sun",  "empty"),
    ("sun",  "busy"),
    ("rain", "empty"),
    ("rain", "busy"),
]

DIGITS = list("0123456789")

API_SIZE = "1536x1024"   # 指定どおり固定
FINAL_WIDTH = 1500       # JPEG保存時の横幅（必要なら変更）
N_PER_CALL = 1

OUT_DIR = Path("outputs")
TMP_DIR = OUT_DIR / "_tmp"
FINAL_DIR = OUT_DIR / "final"  # ここに {digit}_{tod}_{weather}_{cong}.jpg を出す


# =====================
# 保存ユーティリティ
# =====================
def save_image_item(item, out_path: Path) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)

    b64 = getattr(item, "b64_json", None)
    if b64:
        out_path.write_bytes(base64.b64decode(b64))
        return

    url = getattr(item, "url", None)
    if url:
        urllib.request.urlretrieve(url, out_path)
        return

    raise RuntimeError("No b64_json or url in response item")


def save_as_jpeg_width(png_path: Path, jpg_path: Path, width: int = 1500, quality: int = 95) -> None:
    img = Image.open(png_path).convert("RGB")
    w, h = img.size
    new_h = int(round(h * (width / w)))
    img = img.resize((width, new_h), Image.LANCZOS)
    jpg_path.parent.mkdir(parents=True, exist_ok=True)
    img.save(jpg_path, format="JPEG", quality=quality, optimize=True)


# =====================
# ベース画像の自動発見
# =====================
def find_base_scene(tod: str, weather: str, cong: str) -> Path:
    """
    期待するベース（例）:
      inputs/scenes/day_sun_busy.jpg
      inputs/scenes/day/sun_busy.jpg
    fallback:
      outputs/_scenes/...
    """
    roots = [SCENE_DIR_PRIMARY, SCENE_DIR_FALLBACK]
    candidates = []

    for root in roots:
        # 1) root/{tod}_{weather}_{cong}.jpg
        p1 = root / f"{tod}_{weather}_{cong}.jpg"
        if p1.exists():
            candidates.append(p1)

        # 2) root/{tod}/{weather}_{cong}.jpg
        p2 = root / tod / f"{weather}_{cong}.jpg"
        if p2.exists():
            candidates.append(p2)

        # 3) 万一 png の場合も拾う（同名）
        p3 = root / f"{tod}_{weather}_{cong}.png"
        if p3.exists():
            candidates.append(p3)

        p4 = root / tod / f"{weather}_{cong}.png"
        if p4.exists():
            candidates.append(p4)

    if not candidates:
        raise FileNotFoundError(
            f"base scene not found: ({tod}, {weather}, {cong}).\n"
            f"Looked for e.g.\n"
            f"  {SCENE_DIR_PRIMARY}/{tod}_{weather}_{cong}.jpg\n"
            f"  {SCENE_DIR_PRIMARY}/{tod}/{weather}_{cong}.jpg\n"
            f"  {SCENE_DIR_FALLBACK}/{tod}_{weather}_{cong}.jpg\n"
            f"  {SCENE_DIR_FALLBACK}/{tod}/{weather}_{cong}.jpg"
        )

    return candidates[0]


# =====================
# プロンプト（プレートのみ）
# =====================
def prompt_plate(digit: str) -> str:
#     return f"""入力画像を編集する。

# 変更するのは前方車両のナンバープレート部分のみ。他の画素（車体・背景・道路・照明・ブレ・圧縮ノイズ・構図・遠近感・天気・時間帯・周辺車両の有無・上下の黒帯を含む）は一切変更しない。

# ナンバープレートの表記を 一桁の数字「{digit}」のみ に置き換える。
# 数字はプレート中央に配置し、実写のプレート印字らしいフォント・太さ・エッジ・微小なブレ/にじみ・反射を自然に合わせる。
# 既存のプレートの照明条件・陰影・汚れ・反射・ノイズに完全に馴染ませ、編集痕が見えないようにする。

# 出力サイズは 1536×1024 固定。
# 横方向の切り取りは禁止（左右を絶対にクロップしない）。画角変更・ズーム・再構図は禁止。
# """
    return f"""Edit the input image.Edit the input image.

Only modify the license plate area of the front vehicle. Do not change any other pixels (vehicle body, background, road, lighting, motion blur, compression noise, composition, perspective/depth, weather, time of day, presence/absence of surrounding vehicles, or the top/bottom black letterbox bars).

Replace the license plate text with a single digit “{digit}” only.
Center the digit on the plate, and match it naturally to a real photographed plate print: realistic font, stroke weight, edges, and subtle micro blur/bleeding and reflections consistent with the original.
Blend perfectly with the existing plate’s lighting conditions, shading, dirt, reflections, and noise so that no editing artifacts are visible.

Output size must be fixed at 1536×1024.
Horizontal cropping is prohibited (never crop the left/right sides). No changes to camera framing, no zooming, and no recomposition.
"""


# =====================
# メイン処理（プレート生成のみ）
# =====================
def main():
    tasks = []
    for tod in ["day", "night"]:
        for weather, cong in SCENARIOS:
            base_scene = find_base_scene(tod, weather, cong)
            for d in DIGITS:
                tasks.append((tod, base_scene, d, weather, cong))

    pbar = tqdm(tasks, desc="Plates only", unit="call")
    for tod, base_scene, d, weather, cong in pbar:
        with open(base_scene, "rb") as f:
            resp = client.images.edit(
                image=f,
                prompt=prompt_plate(d),
                model="gpt-image-1.5",
                n=N_PER_CALL,
                size=API_SIZE,
                quality="auto",
                background="auto",
                input_fidelity="high",
            )


        # 出力ファイル名：{digit}_{day/night}_{sun/rain}_{busy/empty}_{k}.jpg
        for k, item in enumerate(resp.data, start=1):
            tmp_png = TMP_DIR / f"{d}_{tod}_{weather}_{cong}_{k}.png"
            save_image_item(item, tmp_png)

            out_jpg = FINAL_DIR / f"{d}_{tod}_{weather}_{cong}_{k}.jpg"
            save_as_jpeg_width(tmp_png, out_jpg, width=FINAL_WIDTH, quality=95)

            try:
                tmp_png.unlink(missing_ok=True)
            except Exception:
                pass

    print("DONE")


if __name__ == "__main__":
    main()
