"""生成 Chrome 扩展图标：深色圆角方块 + 「外链」字形 + 抖音青/红错位描边。

用法:  python tools/make-icons.py   （需先 pip install -r tools/requirements.txt）
输出:  icons/icon-{16,32,48,128}.png
"""

from pathlib import Path

from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parent.parent  # 仓库根目录
S = 512  # 超采样尺寸，再缩小得到各规格
OUT_DIR = ROOT / "icons"

BG = (17, 17, 20, 255)
CYAN = (37, 244, 238)
RED = (254, 44, 85)


def glyph_mask(stroke):
    mask = Image.new("L", (S, S), 0)
    d = ImageDraw.Draw(mask)
    lw = int(stroke * S)

    d.rounded_rectangle(
        [0.18 * S, 0.36 * S, 0.58 * S, 0.78 * S], radius=0.075 * S, outline=255, width=lw
    )
    # 挖掉方块右上角，让箭头像是从框内穿出
    d.rectangle([0.50 * S, 0.28 * S, 0.68 * S, 0.46 * S], fill=0)
    d.line([0.36 * S, 0.60 * S, 0.80 * S, 0.22 * S], fill=255, width=lw)
    d.line(
        [(0.58 * S, 0.22 * S), (0.82 * S, 0.22 * S), (0.82 * S, 0.46 * S)],
        fill=255,
        width=lw,
        joint="curve",
    )
    return mask


def color_layer(mask, color, dx=0, dy=0):
    shifted = Image.new("L", (S, S), 0)
    shifted.paste(mask, (dx, dy))
    solid = Image.new("RGBA", (S, S), color + (0,))
    solid.putalpha(shifted)
    return solid


# 小尺寸去掉彩色错位并加粗笔画，否则缩到 16px 会糊成一团
VARIANTS = {16: (0, 0.085), 32: (0, 0.075), 48: (12, 0.065), 128: (18, 0.062)}


def compose(offset, stroke):
    tile = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    ImageDraw.Draw(tile).rounded_rectangle(
        [0, 0, S - 1, S - 1], radius=0.22 * S, fill=BG
    )

    mask = glyph_mask(stroke)
    if not offset:
        return Image.alpha_composite(tile, color_layer(mask, (255, 255, 255)))

    # 先红后青再白：白字居中，右上露红边、左下露青边
    art = Image.alpha_composite(tile, color_layer(mask, RED, offset, -offset))
    art = Image.alpha_composite(art, color_layer(mask, CYAN, -offset, offset))
    return Image.alpha_composite(art, color_layer(mask, (255, 255, 255)))


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    for size, (offset, stroke) in VARIANTS.items():
        compose(offset, stroke).resize((size, size), Image.LANCZOS).save(
            OUT_DIR / f"icon-{size}.png"
        )
    print("icons:", [p.name for p in sorted(OUT_DIR.iterdir())])


if __name__ == "__main__":
    main()
