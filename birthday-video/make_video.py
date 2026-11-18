#!/usr/bin/env python3
"""동생 생일 축하 동영상 생성기 (1080x1920 세로, 30fps, ~25초, 오르골 'Happy Birthday' BGM)

사용법: python3 make_video.py [--name 이름] [--out 파일.mp4]
"""
import argparse, math, os, random, subprocess, wave
from functools import lru_cache
from multiprocessing import Pool

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

W, H, FPS, DUR = 1080, 1920, 30, 25.0
NFRAMES = int(DUR * FPS)
FD = "/usr/share/fonts/truetype/nanum/"
F_TITLE = FD + "NanumSquareRoundEB.ttf"
F_BODY = FD + "NanumSquareRoundB.ttf"
F_HAND = FD + "NanumPen.ttf"
F_BRUSH = FD + "NanumBrush.ttf"

GOLD = (255, 214, 110)
PINK = (255, 143, 184)
CREAM = (255, 246, 232)
MINT = (150, 230, 210)
LAV = (200, 170, 255)

NAME = "우리 동생"

# ---------------------------------------------------------------- easing
def clamp(x, a=0.0, b=1.0): return max(a, min(b, x))
def prog(t, t0, t1): return clamp((t - t0) / (t1 - t0))
def ease_out(x): return 1 - (1 - x) ** 3
def ease_in_out(x): return 3 * x * x - 2 * x * x * x
def ease_back(x, s=1.7):
    x -= 1
    return x * x * ((s + 1) * x + s) + 1

# ---------------------------------------------------------------- cached assets
@lru_cache(None)
def background():
    y = np.linspace(0, 1, H)[:, None]
    top = np.array([22, 16, 58]); mid = np.array([58, 28, 92]); bot = np.array([120, 46, 110])
    c = np.where(y < 0.55, top + (mid - top) * (y / 0.55), mid + (bot - mid) * ((y - 0.55) / 0.45))
    img = np.repeat(c[:, None, :], W, axis=1).reshape(H, W, 3)
    return Image.fromarray(img.astype(np.uint8)).convert("RGBA")

@lru_cache(None)
def bokeh_sprite(r, color):
    s = r * 4
    im = Image.new("RGBA", (s, s), (0, 0, 0, 0))
    ImageDraw.Draw(im).ellipse((r, r, 3 * r, 3 * r), fill=color + (90,))
    return im.filter(ImageFilter.GaussianBlur(r * 0.35))

@lru_cache(None)
def text_img(text, font, size, color, glow=0, stroke=0):
    f = ImageFont.truetype(font, size)
    bbox = f.getbbox(text, stroke_width=stroke)
    pad = glow * 3 + 20
    w, h = bbox[2] - bbox[0] + pad * 2, bbox[3] - bbox[1] + pad * 2
    layer = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    d.text((pad - bbox[0], pad - bbox[1]), text, font=f, fill=color + (255,),
           stroke_width=stroke, stroke_fill=(255, 255, 255, 255) if stroke else None)
    if glow:
        g = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        ImageDraw.Draw(g).text((pad - bbox[0], pad - bbox[1]), text, font=f, fill=color + (200,),
                               stroke_width=stroke + 4)
        g = g.filter(ImageFilter.GaussianBlur(glow))
        g.alpha_composite(layer)
        layer = g
    return layer

def with_alpha(im, a):
    if a >= 0.999: return im
    im = im.copy()
    alpha = im.getchannel("A").point(lambda v: int(v * a))
    im.putalpha(alpha)
    return im

def put(canvas, im, cx, cy, alpha=1.0, scale=1.0, rot=0.0):
    if alpha <= 0.003: return
    if scale != 1.0:
        im = im.resize((max(1, int(im.width * scale)), max(1, int(im.height * scale))), Image.BICUBIC)
    if rot:
        im = im.rotate(rot, resample=Image.BICUBIC, expand=True)
    im = with_alpha(im, alpha)
    canvas.alpha_composite(im, (int(cx - im.width / 2), int(cy - im.height / 2)))

def text_anim(canvas, t, t_in, t_out, text, font, size, color, cy, glow=8, kind="rise", dur=0.7):
    """텍스트 등장/퇴장 애니메이션"""
    if t < t_in or t > t_out + 0.6: return
    pin = prog(t, t_in, t_in + dur)
    pout = prog(t, t_out, t_out + 0.6)
    a = ease_out(pin) * (1 - pout)
    im = text_img(text, font, size, color, glow)
    if kind == "rise":
        put(canvas, im, W / 2, cy + 60 * (1 - ease_out(pin)) - 40 * ease_in_out(pout), a)
    elif kind == "pop":
        s = 0.3 + 0.7 * ease_back(pin) if pin < 1 else 1 + 0.025 * math.sin((t - t_in) * 4)
        put(canvas, im, W / 2, cy, a, s * (1 + 0.15 * pout))
    elif kind == "fade":
        put(canvas, im, W / 2, cy, a)

# ---------------------------------------------------------------- cake
CAKE_W, CAKE_H = 760, 760
CANDLES_X = [-180, -90, 0, 90, 180]
CANDLE_TOP = 250  # y (cake-local) of candle wick

@lru_cache(None)
def cake_img():
    im = Image.new("RGBA", (CAKE_W, CAKE_H), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    cx = CAKE_W // 2
    # plate
    d.ellipse((cx - 360, 650, cx + 360, 740), fill=(235, 235, 250, 255))
    d.ellipse((cx - 340, 655, cx + 340, 725), fill=(210, 210, 235, 255))
    # bottom tier
    d.rounded_rectangle((cx - 300, 480, cx + 300, 690), 40, fill=(247, 161, 196, 255))
    d.rectangle((cx - 300, 600, cx + 300, 620), fill=(255, 220, 235, 255))
    # drips bottom
    d.rounded_rectangle((cx - 300, 470, cx + 300, 520), 25, fill=CREAM + (255,))
    rnd = random.Random(3)
    for x in range(cx - 280, cx + 281, 48):
        h = rnd.randint(30, 70)
        d.rounded_rectangle((x - 16, 490, x + 16, 500 + h), 16, fill=CREAM + (255,))
    # top tier
    d.rounded_rectangle((cx - 210, 320, cx + 210, 500), 36, fill=(160, 225, 210, 255))
    d.rounded_rectangle((cx - 210, 310, cx + 210, 355), 22, fill=CREAM + (255,))
    for x in range(cx - 190, cx + 191, 42):
        h = rnd.randint(22, 52)
        d.rounded_rectangle((x - 14, 330, x + 14, 335 + h), 14, fill=CREAM + (255,))
    # sprinkles & berries
    cols = [(255, 214, 110), (255, 120, 160), (140, 180, 255), (255, 255, 255), (190, 140, 255)]
    for _ in range(70):
        x = rnd.randint(cx - 270, cx + 270); y = rnd.randint(540, 670)
        if 595 < y < 625: continue
        ang = rnd.random() * math.pi; L = 9
        d.line((x - L * math.cos(ang), y - L * math.sin(ang), x + L * math.cos(ang), y + L * math.sin(ang)),
               fill=rnd.choice(cols) + (255,), width=6)
    for _ in range(36):
        x = rnd.randint(cx - 185, cx + 185); y = rnd.randint(395, 485)
        d.ellipse((x - 5, y - 5, x + 5, y + 5), fill=rnd.choice(cols) + (255,))
    for x in range(cx - 240, cx + 241, 120):
        d.ellipse((x - 20, 470, x + 20, 510), fill=(220, 40, 80, 255))
        d.ellipse((x - 8, 478, x + 2, 488), fill=(255, 160, 180, 255))
    # candles
    for i, dx in enumerate(CANDLES_X):
        x = cx + dx
        c1 = [PINK, GOLD, MINT, LAV, PINK][i]
        d.rounded_rectangle((x - 13, CANDLE_TOP + 15, x + 13, 330), 6, fill=(255, 255, 255, 255))
        for k in range(CANDLE_TOP + 22, 325, 22):
            d.polygon([(x - 13, k), (x + 13, k - 9), (x + 13, k + 1), (x - 13, k + 10)], fill=c1 + (255,))
        d.line((x, CANDLE_TOP, x, CANDLE_TOP + 16), fill=(60, 50, 40, 255), width=4)
    return im

@lru_cache(None)
def flame_sprite(h):
    w = int(h * 0.55)
    s = Image.new("RGBA", (w * 4, h * 3), (0, 0, 0, 0))
    d = ImageDraw.Draw(s)
    ox, oy = w * 2, h * 2
    glow = Image.new("RGBA", s.size, (0, 0, 0, 0))
    ImageDraw.Draw(glow).ellipse((ox - w * 1.6, oy - h * 1.3, ox + w * 1.6, oy + h * 0.5), fill=(255, 190, 80, 120))
    glow = glow.filter(ImageFilter.GaussianBlur(h * 0.35))
    s.alpha_composite(glow)
    d = ImageDraw.Draw(s)
    def drop(sc, col):
        pts = []
        for k in range(40):
            a = 2 * math.pi * k / 40
            r = 1 - 0.55 * (1 + math.sin(a)) / 2
            pts.append((ox + math.cos(a) * w / 2 * sc * r * 1.1, oy - h * sc * 0.5 + math.sin(a) * h * sc * 0.5))
        d.polygon(pts, fill=col)
    drop(1.0, (255, 160, 40, 255)); drop(0.75, (255, 220, 90, 255)); drop(0.45, (255, 255, 230, 255))
    return s

def draw_cake(canvas, t, cx, cy, alpha, lit):
    put(canvas, cake_img(), cx, cy, alpha)
    if lit <= 0: return
    for i, dx in enumerate(CANDLES_X):
        fl = 1 + 0.12 * math.sin(t * 17 + i * 1.7) + 0.06 * math.sin(t * 29 + i)
        h = max(4, int(56 * lit * fl))
        sp = flame_sprite(56)
        sp = sp.resize((max(1, int(sp.width * h / 56 * (0.95 + 0.05 * math.sin(t * 13 + i)))), max(1, int(sp.height * h / 56))))
        x = cx - CAKE_W / 2 + CAKE_W / 2 + dx
        wick_y = cy - CAKE_H / 2 + CANDLE_TOP + 4
        canvas.alpha_composite(with_alpha(sp, alpha), (int(x - sp.width / 2), int(wick_y - sp.height * 2 / 3)))

# ---------------------------------------------------------------- particles
CONF_COLS = [GOLD, PINK, MINT, LAV, (130, 190, 255), (255, 255, 255), (255, 120, 90)]
def make_confetti(seed, t0, ox, oy, n, angle_c, spread):
    r = random.Random(seed); ps = []
    for _ in range(n):
        a = math.radians(angle_c + r.uniform(-spread, spread)); v = r.uniform(900, 2000)
        ps.append(dict(t0=t0 + r.uniform(0, 0.15), x=ox, y=oy, vx=math.cos(a) * v, vy=-math.sin(a) * v,
                       c=r.choice(CONF_COLS), w=r.uniform(14, 26), h=r.uniform(7, 13),
                       spin=r.uniform(4, 12), ph=r.uniform(0, 6.28), sh=r.choice(["r", "r", "c"])))
    return ps

CONFETTI = (make_confetti(1, 10.0, -20, 1250, 110, 62, 20) + make_confetti(2, 10.0, W + 20, 1250, 110, 118, 20)
            + make_confetti(5, 21.0, W / 2, 2000, 130, 90, 28))

def draw_confetti(d, t):
    for p in CONFETTI:
        dt = t - p["t0"]
        if dt < 0: continue
        drag = 1.6
        f = (1 - math.exp(-drag * dt)) / drag
        x = p["x"] + p["vx"] * f + 40 * math.sin(dt * 2 + p["ph"])
        y = p["y"] + p["vy"] * f + 420 * (dt - f) * 1.4
        if y > H + 60 or dt > 9: continue
        a = int(255 * clamp(1 - (dt - 6) / 2))
        if p["sh"] == "c":
            r = p["h"] * 0.7
            d.ellipse((x - r, y - r, x + r, y + r), fill=p["c"] + (a,)); continue
        ang = p["ph"] + dt * p["spin"]
        flip = abs(math.cos(dt * p["spin"] * 0.7 + p["ph"]))
        hw, hh = p["w"] / 2, p["h"] / 2 * (0.25 + 0.75 * flip)
        ca, sa = math.cos(ang), math.sin(ang)
        pts = [(x + ca * px - sa * py, y + sa * px + ca * py) for px, py in [(-hw, -hh), (hw, -hh), (hw, hh), (-hw, hh)]]
        d.polygon(pts, fill=p["c"] + (a,))

STARS = [(random.Random(i).uniform(0, W), random.Random(i + 999).uniform(0, H * 0.75),
          random.Random(i + 77).uniform(1.5, 4), random.Random(i + 55).uniform(0, 6.28)) for i in range(90)]
BOKEH = [(random.Random(i).uniform(0, W), random.Random(i + 3).uniform(0, H), random.Random(i + 5).choice([40, 60, 90]),
          random.Random(i + 7).choice([PINK, GOLD, LAV, MINT]), random.Random(i + 9).uniform(-25, -60)) for i in range(22)]

BALLOON_COLS = [PINK, GOLD, MINT, LAV, (130, 190, 255), (255, 130, 100)]
BALLOONS = [(random.Random(i).uniform(80, W - 80), random.Random(i + 1).uniform(0, 3.0), random.Random(i + 2).uniform(42, 70),
             random.Random(i + 3).choice(BALLOON_COLS)) for i in range(18)]

def draw_balloon(d, x, y, s, col, a):
    """풍선: 몸통 + 매듭 + 줄 + 하이라이트 (x, y = 몸통 중심)"""
    A = int(255 * a)
    bh = s * 1.2
    pts = [(x + 6 * math.sin(k * 0.6), y + bh + 10 + k * 12) for k in range(14)]
    d.line(pts, fill=(255, 255, 255, int(150 * a)), width=3)
    d.polygon([(x, y + bh - 4), (x - 10, y + bh + 14), (x + 10, y + bh + 14)], fill=col + (A,))
    d.ellipse((x - s, y - bh, x + s, y + bh), fill=col + (A,))
    d.ellipse((x - s * 0.55, y - bh * 0.7, x - s * 0.2, y - bh * 0.25), fill=(255, 255, 255, int(110 * a)))

def sparkle(d, x, y, r, a, col=(255, 255, 255)):
    d.polygon([(x, y - r), (x + r * 0.22, y - r * 0.22), (x + r, y), (x + r * 0.22, y + r * 0.22),
               (x, y + r), (x - r * 0.22, y + r * 0.22), (x - r, y), (x - r * 0.22, y - r * 0.22)], fill=col + (int(255 * a),))

# ---------------------------------------------------------------- frame
def render(fi):
    t = fi / FPS
    c = background().copy()
    # bokeh
    for (x, y, r, col, vy) in BOKEH:
        yy = (y + vy * t) % (H + 300) - 150
        put(c, bokeh_sprite(r, col), x + 30 * math.sin(t * 0.4 + x), yy)
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(ov)
    for (x, y, r, ph) in STARS:
        a = 0.35 + 0.65 * (0.5 + 0.5 * math.sin(t * 2.2 + ph))
        d.ellipse((x - r, y - r, x + r, y + r), fill=(255, 255, 240, int(200 * a)))
    c.alpha_composite(ov)

    # --- Scene 1: 0 ~ 4.2
    text_anim(c, t, 0.4, 3.6, "오늘은", F_BODY, 96, CREAM, 820)
    text_anim(c, t, 1.2, 3.6, "특별한 날이야", F_TITLE, 130, GOLD, 980, glow=14, kind="pop")
    if 1.4 < t < 4.2:
        ov = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(ov)
        for k, (sx, sy) in enumerate([(180, 900), (900, 860), (860, 1100), (230, 1090), (540, 690)]):
            a = clamp(math.sin((t - 1.4 - k * 0.2) * 3)) * (1 - prog(t, 3.6, 4.2))
            sparkle(d, sx, sy, 34, a, GOLD)
        c.alpha_composite(ov)

    # --- Scene 2: 4.2 ~ 8.4
    text_anim(c, t, 4.5, 7.8, "오늘의 주인공은 바로", F_BODY, 84, CREAM, 820)
    text_anim(c, t, 5.3, 7.8, NAME, F_TITLE, 170 if len(NAME) <= 5 else 130, PINK, 1010, glow=18, kind="pop")
    if 5.3 < t < 8.4:
        ov = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(ov)
        pa = ease_out(prog(t, 5.5, 6.2)) * (1 - prog(t, 7.8, 8.4))
        for k in range(8):
            ang = k * math.pi / 4 + t * 0.6
            tw = 0.6 + 0.4 * math.sin(t * 5 + k)
            sparkle(d, W / 2 + math.cos(ang) * 430, 1010 + math.sin(ang) * 230, 26 * tw + 8, pa, GOLD)
        c.alpha_composite(ov)

    # --- Scene 3: 8.4 ~ 14.6  cake
    if 8.4 <= t < 15.2:
        pin = ease_out(prog(t, 8.4, 9.5)); pout = prog(t, 14.2, 14.9)
        cy = 1330 + 700 * (1 - pin) + 30 * math.sin(t * 1.5) * pin
        lit = ease_out(prog(t, 9.5, 10.0))
        draw_cake(c, t, W / 2, cy, 1 - pout, lit)
    text_anim(c, t, 9.7, 14.2, "Happy Birthday", F_BRUSH, 170, GOLD, 520, glow=14, kind="rise")
    text_anim(c, t, 10.3, 14.2, "생일 축하해!", F_TITLE, 140, CREAM, 720, glow=16, kind="pop")

    # --- Scene 4: 14.8 ~ 20.6  message
    lines = ["벌써 이만큼 컸네", "올해도 하고 싶은 거 다 하고", "아프지 말고 건강하게 지내", "맛있는 거 많이 먹어!"]
    for k, ln in enumerate(lines):
        col = GOLD if k == 3 else CREAM
        text_anim(c, t, 15.0 + k * 1.15, 20.0, ln, F_HAND, 128 if k < 3 else 150, col, 640 + k * 210, glow=10 if k == 3 else 6)

    # --- Scene 5: 20.6 ~ 25  finale
    if t > 20.6:
        ov = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(ov)
        for (bx, bd, bs, bc) in BALLOONS:
            dt = t - 20.6 - bd
            if dt < 0: continue
            y = H + 120 - dt * 300
            draw_balloon(d, bx + 30 * math.sin(dt * 1.5 + bx), y, bs, bc, 0.9 * clamp(dt * 2))
        c.alpha_composite(ov)
    text_anim(c, t, 20.8, 30, "HAPPY", F_TITLE, 190, GOLD, 760, glow=18, kind="pop")
    text_anim(c, t, 21.1, 30, "BIRTHDAY", F_TITLE, 160, PINK, 940, glow=18, kind="pop")
    text_anim(c, t, 21.9, 30, "즐거운 하루 보내!", F_TITLE, 100, CREAM, 1140, glow=10)

    # confetti on top
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0)); draw_confetti(ImageDraw.Draw(ov), t); c.alpha_composite(ov)

    # global fade in / out
    fade = min(prog(t, 0, 0.5), 1 - prog(t, DUR - 1.0, DUR))
    out = c.convert("RGB")
    if fade < 1:
        out = Image.blend(Image.new("RGB", (W, H)), out, fade)
    return out.tobytes()

# ---------------------------------------------------------------- music (오르골풍 Happy Birthday, 퍼블릭 도메인 멜로디)
SR = 44100
def midi_hz(m): return 440 * 2 ** ((m - 69) / 12)
def note_wave(m, dur, vol, kind="box"):
    n = int(SR * dur); tt = np.arange(n) / SR; f = midi_hz(m)
    if kind == "box":
        w = (np.sin(2 * np.pi * f * tt) + 0.35 * np.sin(2 * np.pi * 2 * f * tt) * np.exp(-tt * 6)
             + 0.18 * np.sin(2 * np.pi * 3.01 * f * tt) * np.exp(-tt * 9) + 0.08 * np.sin(2 * np.pi * 4.2 * f * tt) * np.exp(-tt * 14))
        env = np.exp(-tt * 2.6) * np.minimum(1, tt / 0.004)
    else:  # soft pad
        w = np.sin(2 * np.pi * f * tt) + 0.2 * np.sin(2 * np.pi * 2 * f * tt)
        env = np.minimum(1, tt / 0.08) * np.exp(-tt * 1.2)
    return w * env * vol

def make_audio(path):
    total = np.zeros(int(SR * (DUR + 1)))
    def add(start, sig):
        i = int(start * SR); j = min(len(total), i + len(sig)); total[i:j] += sig[: j - i]
    G4, A4, B4, C5, D5, E5, F5, G5 = 67, 69, 71, 72, 74, 76, 77, 79
    mel = [(G4, .75), (G4, .25), (A4, 1), (G4, 1), (C5, 1), (B4, 2),
           (G4, .75), (G4, .25), (A4, 1), (G4, 1), (D5, 1), (C5, 2),
           (G4, .75), (G4, .25), (G5, 1), (E5, 1), (C5, 1), (B4, 1), (A4, 1),
           (F5, .75), (F5, .25), (E5, 1), (C5, 1), (D5, 1), (C5, 3)]
    beat = 0.74
    start = 1.6
    # intro arpeggio
    for k, m in enumerate([60, 64, 67, 72, 76, 79]):
        add(0.15 + k * 0.2, note_wave(m, 3, 0.16))
    tcur = start
    for m, b in mel:
        add(tcur, note_wave(m, max(1.6, b * beat + 1.2), 0.34))
        add(tcur, note_wave(m + 12, 1.2, 0.06))
        tcur += b * beat
    # chords per bar (bar = 3 beats, after 1-beat pickup)
    chords = [[48, 55, 64], [43, 55, 65], [43, 55, 65], [48, 55, 64], [48, 55, 64], [41, 57, 65], [43, 55, 64], [48, 55, 64]]
    for k, ch in enumerate(chords):
        bt = start + (1 + 3 * k) * beat
        for m in ch:
            add(bt, note_wave(m, 3 * beat + 1.0, 0.10, "pad"))
        add(bt + beat, note_wave(ch[1] + 12, 1.5, 0.05)); add(bt + 2 * beat, note_wave(ch[2] + 12, 1.5, 0.05))
    end = tcur
    # outro sparkle
    for k, m in enumerate([84, 88, 91, 96]):
        add(end + 0.8 + k * 0.15, note_wave(m, 2.0, 0.07))
    # simple reverb (feedback delays)
    out = total.copy()
    for dl, g in [(0.031, .35), (0.047, .28), (0.071, .22), (0.113, .16)]:
        k = int(dl * SR); out[k:] += total[:-k] * g
    out = out[: int(SR * DUR)]
    fade = np.ones_like(out); fl = int(SR * 1.0); fade[-fl:] = np.linspace(1, 0, fl)
    out *= fade
    out = out / np.max(np.abs(out)) * 0.85
    pcm = (out * 32767).astype(np.int16)
    st = np.repeat(pcm[:, None], 2, axis=1)
    with wave.open(path, "wb") as wf:
        wf.setnchannels(2); wf.setsampwidth(2); wf.setframerate(SR); wf.writeframes(st.tobytes())
    print(f"melody ends at {end:.2f}s")

def init(name):
    global NAME
    NAME = name

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--name", default="우리 동생")
    ap.add_argument("--out", default="birthday.mp4")
    ap.add_argument("--preview", type=str, default="", help="comma-separated seconds to dump PNG stills")
    a = ap.parse_args()
    init(a.name)
    if a.preview:
        for s in a.preview.split(","):
            Image.frombytes("RGB", (W, H), render(int(float(s) * FPS))).save(f"preview_{s}.png")
        raise SystemExit
    wav = a.out + ".wav"
    make_audio(wav)
    ff = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
                           "-r", str(FPS), "-i", "-", "-i", wav, "-c:v", "libx264", "-preset", "medium", "-crf", "20",
                           "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k", "-shortest", "-movflags", "+faststart", a.out],
                          stdin=subprocess.PIPE)
    with Pool(os.cpu_count(), initializer=init, initargs=(a.name,)) as pool:
        for k, fr in enumerate(pool.imap(render, range(NFRAMES), chunksize=4)):
            ff.stdin.write(fr)
            if k % 75 == 0: print(f"frame {k}/{NFRAMES}", flush=True)
    ff.stdin.close(); ff.wait()
    os.remove(wav)
    print("done:", a.out)
