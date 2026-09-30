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
    # center square crop first (no stretch)
    im = im.convert("RGBA")
    w, h = im.size
    side = min(w, h)
    left = (w - side) // 2
    top = (h - side) // 2
    im = im.crop((left, top, left + side, top + side))
    im = im.resize((size, size), Image.LANCZOS)

    # clean circle mask (stays inside)
    mask = Image.new("L", (size, size), 0)
    d = ImageDraw.Draw(mask)
    d.ellipse((1, 1, size - 2, size - 2), fill=255)

    out = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    out.paste(im, (0, 0), mask)

    # red ring outside — art never spills
    ring_size = size + 20
    ring = Image.new("RGBA", (ring_size, ring_size), (0, 0, 0, 0))
    rd = ImageDraw.Draw(ring)
    rd.ellipse((2, 2, ring_size - 3, ring_size - 3), outline=(220, 20, 60, 255), width=5)
    rd.ellipse((8, 8, ring_size - 9, ring_size - 9), outline=(40, 0, 10, 200), width=2)

    offset = (ring_size - size) // 2
    ring.paste(out, (offset, offset), out)
    return ring


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
    canvas = Image.new("RGB", (W, H), (8, 8, 12))
    draw = ImageDraw.Draw(canvas)

    if os.path.isfile(_BG_PATH):
        try:
            bg = Image.open(_BG_PATH).convert("RGB")
            bg = bg.resize((W, H), Image.LANCZOS)
            canvas.paste(bg, (0, 0))
            overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
            od = ImageDraw.Draw(overlay)
            od.rectangle((0, 0, 620, H), fill=(0, 0, 0, 180))
            canvas = Image.alpha_composite(canvas.convert("RGBA"), overlay).convert("RGB")
            draw = ImageDraw.Draw(canvas)
        except Exception:
            pass

    panel = (28, 40, 600, 680)
    draw.rounded_rectangle(panel, radius=28, fill=(18, 18, 24), outline=(180, 20, 50), width=2)

    draw.rounded_rectangle((55, 70, 260, 115), radius=14, fill=(160, 15, 40))
    f_badge = _font(22, bold=True)
    draw.text((75, 80), "NOW PLAYING", font=f_badge, fill=(255, 255, 255))

    f_title = _font(42, bold=True)
    clean = (title or "Unknown Track").strip()
    if len(clean) > 60:
        clean = clean[:57] + "..."
    lines = _wrap(clean, f_title, 500, draw)
    y = 160
    for line in lines:
        draw.text((55, y), line, font=f_title, fill=(255, 255, 255))
        y += 52

    f_dur = _font(28)
    dur_text = f"Time  {duration}" if duration else "Time  --:--"
    draw.text((55, y + 20), dur_text, font=f_dur, fill=(220, 60, 80))

    bar_x, bar_y = 55, 520
    heights = [18, 32, 48, 28, 40, 22, 36, 50, 30, 20]
    for i, h in enumerate(heights):
        x0 = bar_x + i * 18
        draw.rectangle((x0, bar_y + 50 - h, x0 + 12, bar_y + 50), fill=(200, 25, 55))

    f_brand = _font(30, bold=True)
    draw.text((55, 600), "Wolf x Music", font=f_brand, fill=(220, 40, 70))

    if yt_img is not None:
        try:
            circ = _circle_crop(yt_img, 320)
            canvas.paste(circ, (790, 180), circ)
        except Exception:
            pass

    return canvas


async def get_thumb(videoid, title=None, duration=None):
    os.makedirs("cache", exist_ok=True)
    safe_title = (title or "track").replace("/", "_")[:40]
    path = f"cache/{videoid}_{safe_title}.jpg"

    # old cache delete — new circle apply avvali
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
        card.save(path, "JPEG", quality=92)
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
