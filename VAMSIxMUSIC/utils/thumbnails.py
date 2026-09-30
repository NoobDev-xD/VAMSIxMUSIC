import os
from io import BytesIO

import aiohttp
from PIL import Image, ImageDraw, ImageFont

from config import YOUTUBE_IMG_URL

_SOURCES = ("maxresdefault", "sddefault", "hqdefault", "mqdefault")
_MIN_WIDTH = 300
_BAR_LIMIT = 24

_ASSETS = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets")
_BG_PATH = os.path.join(_ASSETS, "wolf_bg.png")
_FONT = os.path.join(_ASSETS, "font2.ttf")
_FONT2 = os.path.join(_ASSETS, "font.ttf")

W, H = 1280, 720

# circle position on wolf_bg (right side)
CIRCLE_SIZE = 340
CIRCLE_X = 820
CIRCLE_Y = 175


def _trim_bars(image):
    width, height = image.size
    bar = int(height * 0.125)
    if bar < 1:
        return image, False
    top = image.crop((0, 0, width, bar)).convert("L").getextrema()[1]
    bottom = image.crop((0, height - bar, width, height)).convert("L").getextrema()[1]
    if top < _BAR_LIMIT and bottom < _BAR_LIMIT:
        return image.crop((0, bar, width, height - bar)), True
    return image, False


async def _fetch(session, videoid, name):
    url = f"https://i.ytimg.com/vi/{videoid}/{name}.jpg"
    try:
        async with session.get(url) as resp:
            if resp.status != 200:
                return None
            raw = await resp.read()
    except Exception:
        return None
    try:
        image = Image.open(BytesIO(raw))
        image.load()
    except Exception:
        return None
    if image.width < _MIN_WIDTH:
        return None
    return raw, image


def _font(size, bold=False):
    path = _FONT2 if bold and os.path.isfile(_FONT2) else _FONT
    if os.path.isfile(path):
        try:
            return ImageFont.truetype(path, size)
        except Exception:
            pass
    return ImageFont.load_default()


def _circle_crop(im, size):
    """Strict circle — transparent outside, zero spill."""
    im = im.convert("RGBA")
    w, h = im.size
    side = min(w, h)
    left = (w - side) // 2
    top = (h - side) // 2
    im = im.crop((left, top, left + side, top + side))
    im = im.resize((size, size), Image.LANCZOS)

    # 4x mask for smooth edges
    big = size * 4
    mask_big = Image.new("L", (big, big), 0)
    d = ImageDraw.Draw(mask_big)
    d.ellipse((2, 2, big - 3, big - 3), fill=255)
    mask = mask_big.resize((size, size), Image.LANCZOS)

    out = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    out.paste(im, (0, 0), mask)
    return out


def _wrap(text, font, max_w, draw):
    words = text.split()
    lines, cur = [], ""
    for w in words:
        test = (cur + " " + w).strip()
        if draw.textlength(test, font=font) <= max_w:
            cur = test
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines[:3]


def _build_card(yt_img, title, duration):
    # base
    if os.path.isfile(_BG_PATH):
        try:
            canvas = Image.open(_BG_PATH).convert("RGBA")
            canvas = canvas.resize((W, H), Image.LANCZOS)
        except Exception:
            canvas = Image.new("RGBA", (W, H), (8, 8, 12, 255))
    else:
        canvas = Image.new("RGBA", (W, H), (8, 8, 12, 255))

    draw = ImageDraw.Draw(canvas)

    # dark left panel for text readability
    overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    od = ImageDraw.Draw(overlay)
    od.rounded_rectangle((24, 30, 610, 690), radius=30, fill=(10, 10, 14, 200))
    od.rounded_rectangle((24, 30, 610, 690), radius=30, outline=(180, 20, 50, 220), width=2)
    canvas = Image.alpha_composite(canvas, overlay)
    draw = ImageDraw.Draw(canvas)

    # NOW PLAYING badge
    draw.rounded_rectangle((50, 60, 270, 110), radius=12, fill=(180, 15, 40, 255))
    f_badge = _font(20, bold=True)
    draw.text((70, 72), "NOW PLAYING", font=f_badge, fill=(255, 255, 255, 255))

    # title
    f_title = _font(40, bold=True)
    clean = (title or "Unknown Track").strip()
    if len(clean) > 55:
        clean = clean[:52] + "..."
    lines = _wrap(clean, f_title, 520, draw)
    y = 150
    for line in lines:
        draw.text((50, y), line, font=f_title, fill=(255, 255, 255, 255))
        y += 50

    # time
    f_dur = _font(26)
    dur_text = f"Time  {duration}" if duration else "Time  --:--"
    draw.text((50, y + 16), dur_text, font=f_dur, fill=(220, 60, 80, 255))

    # equalizer bars
    bar_x, bar_y = 50, 530
    heights = [20, 36, 52, 30, 44, 24, 40, 56, 32, 22]
    for i, h in enumerate(heights):
        x0 = bar_x + i * 18
        draw.rectangle((x0, bar_y + 56 - h, x0 + 12, bar_y + 56), fill=(220, 25, 55, 255))

    # brand
    f_brand = _font(28, bold=True)
    draw.text((50, 610), "Wolf x Music", font=f_brand, fill=(220, 40, 70, 255))

    # YouTube thumb — STRICT inside circle only
    if yt_img is not None:
        try:
            circ = _circle_crop(yt_img, CIRCLE_SIZE)
            canvas.paste(circ, (CIRCLE_X, CIRCLE_Y), circ)
        except Exception:
            pass

    return canvas.convert("RGB")


async def get_thumb(videoid, title=None, duration=None):
    os.makedirs("cache", exist_ok=True)
    safe = (title or "track").replace("/", "_").replace(" ", "_")[:40]
    path = f"cache/{videoid}_{safe}.jpg"

    if os.path.isfile(path):
        try:
            os.remove(path)
        except Exception:
            pass

    yt_img = None
    try:
        timeout = aiohttp.ClientTimeout(total=10)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            for name in _SOURCES:
                got = await _fetch(session, videoid, name)
                if not got:
                    continue
                raw, image = got
                image, _ = _trim_bars(image)
                yt_img = image.convert("RGB")
                break
    except Exception:
        pass

    try:
        card = _build_card(yt_img, title or "Now Playing", duration or "")
        card.save(path, "JPEG", quality=93)
        return path
    except Exception:
        pass

    if yt_img is not None:
        try:
            plain = f"cache/{videoid}.jpg"
            yt_img.save(plain, "JPEG", quality=90)
            return plain
        except Exception:
            pass
    return YOUTUBE_IMG_URL
