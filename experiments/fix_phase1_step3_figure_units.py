from __future__ import annotations

import argparse
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
SOURCE: Path
OUTPUT_DIR: Path
MAIN_OUTPUT: Path
A_OUTPUT: Path
B_OUTPUT: Path

EXPECTED_SIZE = (2100, 1050)
FONT_PATH: Path | None = None
FONT_SIZE = 38
UNIT = "\N{MICRO SIGN}g/cm\N{SUPERSCRIPT TWO}/h"


def draw_centered_x_label(
    image: Image.Image,
    draw: ImageDraw.ImageDraw,
    font: ImageFont.FreeTypeFont,
) -> None:
    draw.rectangle((350, 962, 850, 1025), fill="white")
    label = f"Silicone J ({UNIT})"
    box = draw.textbbox((0, 0), label, font=font)
    width = box[2] - box[0]
    draw.text((582 - width / 2 - box[0], 970), label, font=font, fill="black")


def draw_rotated_y_label(
    image: Image.Image,
    draw: ImageDraw.ImageDraw,
    font: ImageFont.FreeTypeFont,
) -> None:
    label = f"Skin J ({UNIT})"
    box = font.getbbox(label)
    width = box[2] - box[0]
    height = box[3] - box[1]
    label_layer = Image.new("RGBA", (width, height), (255, 255, 255, 0))
    label_draw = ImageDraw.Draw(label_layer)
    label_draw.text((-box[0], -box[1]), label, font=font, fill="black")
    rotated = label_layer.rotate(
        90,
        expand=True,
        resample=Image.Resampling.BICUBIC,
    )

    draw.rectangle((20, 330, 82, 665), fill="white")
    image.alpha_composite(rotated, (37, 350))


def main() -> None:
    global SOURCE, OUTPUT_DIR, MAIN_OUTPUT, A_OUTPUT, B_OUTPUT, FONT_PATH
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=ROOT / "demos" / "demo1" / "outputs",
    )
    parser.add_argument("--font-path", type=Path, default=None)
    args = parser.parse_args()
    SOURCE = args.source.resolve()
    OUTPUT_DIR = args.output_dir.resolve()
    MAIN_OUTPUT = OUTPUT_DIR / "figure_step3_main.png"
    A_OUTPUT = OUTPUT_DIR / "figure_step3_A_no_title.png"
    B_OUTPUT = OUTPUT_DIR / "figure_step3_B_no_title.png"
    FONT_PATH = args.font_path.resolve() if args.font_path else None
    if not SOURCE.exists():
        raise FileNotFoundError(f"Missing source image: {SOURCE}")
    if FONT_PATH is not None and not FONT_PATH.exists():
        raise FileNotFoundError(f"Missing requested Arial font: {FONT_PATH}")

    image = Image.open(SOURCE).convert("RGBA")
    if image.size != EXPECTED_SIZE:
        raise ValueError(f"Unexpected source size: {image.size}; expected {EXPECTED_SIZE}")

    draw = ImageDraw.Draw(image)
    font = ImageFont.truetype(str(FONT_PATH), FONT_SIZE) if FONT_PATH else ImageFont.load_default()
    draw_centered_x_label(image, draw, font)
    draw_rotated_y_label(image, draw, font)

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    image.save(MAIN_OUTPUT, dpi=(300, 300))

    # The panel titles end above y=80. Cropping from y=80 retains both axes,
    # labels, annotations, and legends while excluding the A/B titles.
    image.crop((0, 80, 1050, 1050)).save(A_OUTPUT, dpi=(300, 300))
    image.crop((1050, 80, 2100, 1050)).save(B_OUTPUT, dpi=(300, 300))


if __name__ == "__main__":
    main()
