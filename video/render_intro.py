# רינדור סרטון הפתיחה של מנגיסטו בלאו — פריים אחר פריים.
# אין raqm במערכת, לכן הכיווניות של העברית מטופלת ידנית ב-rtl().
import math, os, unicodedata
from PIL import Image, ImageDraw, ImageFont

W, H, FPS, DUR = 1920, 1080, 30, 9.0
N = int(FPS * DUR)
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "frames")

INK = (11, 18, 32)
CANVAS = (247, 245, 240)
GOLD = (180, 137, 43)
GOLD_LT = (210, 186, 132)
GOLD_PALE = (237, 229, 210)
GOLD_DK = (112, 89, 39)
MUTED = (101, 104, 111)

FDIR = "C:/Windows/Fonts/"
def font(px, bold=True):
    for name in (("arialbd.ttf", "seguibl.ttf") if bold else ("arial.ttf", "segoeui.ttf")):
        p = FDIR + name
        if os.path.exists(p):
            return ImageFont.truetype(p, px)
    raise SystemExit("no font")

# ---------- כיווניות ----------
def _heb(ch):
    return "\u0590" <= ch <= "\u05FF"

def rtl(s):
    """סידור מחדש לתצוגה: רצפי עברית מתהפכים, מספרים ולטינית נשארים."""
    runs, cur, cur_is = [], "", None
    for ch in s:
        is_h = _heb(ch) or ch in "\u05F3\u05F4"
        if cur and is_h != cur_is:
            runs.append((cur_is, cur)); cur = ""
        cur_is, cur = is_h, cur + ch
    if cur:
        runs.append((cur_is, cur))
    out = []
    for is_h, run in reversed(runs):
        out.append(run[::-1] if is_h else run)
    return "".join(out)

# ---------- עזרי ציור ----------
def ease_out(t):   return 1 - (1 - t) ** 3
def ease_in_out(t): return 4*t*t*t if t < .5 else 1 - (-2*t + 2) ** 3 / 2

def seg(f, a, b):
    """התקדמות 0..1 של קטע בין פריים a ל-b."""
    if f <= a: return 0.0
    if f >= b: return 1.0
    return (f - a) / float(b - a)

def blend(c, bg, a):
    return tuple(int(bg[i] + (c[i] - bg[i]) * a) for i in range(3))

def text_ls(d, xy, s, fnt, fill, ls=0, anchor_right=False):
    """טקסט עם ריווח אותיות. anchor_right — הקצה הימני ב-x."""
    s = rtl(s)
    if ls == 0:
        w = d.textlength(s, font=fnt)
        x = xy[0] - w if anchor_right else xy[0]
        d.text((x, xy[1]), s, font=fnt, fill=fill)
        return w
    total = sum(d.textlength(c, font=fnt) + ls for c in s) - ls
    x = xy[0] - total if anchor_right else xy[0]
    for c in s:
        d.text((x, xy[1]), c, font=fnt, fill=fill)
        x += d.textlength(c, font=fnt) + ls
    return total

# הילת זהב תחתונה — נבנית פעם אחת בקטן ונמתחת
def build_glow():
    sw, sh = 96, 54
    g = Image.new("L", (sw, sh), 0)
    px = g.load()
    cx, cy = sw / 2.0, sh * 1.02
    for y in range(sh):
        for x in range(sw):
            dx = (x - cx) / (sw * 0.52)
            dy = (y - cy) / (sh * 0.62)
            r = math.sqrt(dx * dx + dy * dy)
            v = max(0.0, 1.0 - r)
            px[x, y] = int(255 * (v ** 1.7))
    return g.resize((W, H), Image.BICUBIC)

GLOW = build_glow()

def dotgrid(img):
    d = ImageDraw.Draw(img, "RGBA")
    for y in range(0, H, 40):
        for x in range(0, W, 40):
            d.point((x, y), fill=(210, 186, 132, 30))

def corners(d, inset, a):
    if a <= 0: return
    L = 34
    c = (int(210*a + INK[0]*(1-a)), int(186*a + INK[1]*(1-a)), int(132*a + INK[2]*(1-a)))
    for (x, y, sx, sy) in ((inset, inset, 1, 1), (W-inset, inset, -1, 1),
                           (inset, H-inset, 1, -1), (W-inset, H-inset, -1, -1)):
        d.line([(x, y), (x + L*sx, y)], fill=c, width=2)
        d.line([(x, y), (x, y + L*sy)], fill=c, width=2)

def coin_stack(d, cx, base_y, count, rise, rw=132, rh=46, thick=17):
    """ערימת מטבעות איזומטרית — דיסקה כהה מתחת ובהירה מעל."""
    shown = count * rise
    for i in range(count):
        k = shown - i
        if k <= 0: break
        a = min(1.0, k)
        y = base_y - i * thick - (1 - ease_out(a)) * 26
        e = blend(GOLD_DK, INK, a)
        d.ellipse([cx - rw/2, y - rh/2 + 6, cx + rw/2, y + rh/2 + 6], fill=e)
        f = blend(GOLD, INK, a)
        d.ellipse([cx - rw/2, y - rh/2, cx + rw/2, y + rh/2], fill=f)
        hl = blend(GOLD_PALE, f, .45 * a)
        d.ellipse([cx - rw/2 + 18, y - rh/2 + 7, cx - rw/2 + 62, y - rh/2 + 20], fill=hl)

SPARK = [(0,124),(62,110),(124,116),(186,78),(248,88),(310,40),(368,18)]

def sparkline(d, ox, oy, sx, sy, prog, a):
    if prog <= 0 or a <= 0: return
    pts = [(ox + p[0]*sx, oy + p[1]*sy) for p in SPARK]
    segs = len(pts) - 1
    total = prog * segs
    drawn = [pts[0]]
    for i in range(segs):
        t = min(1.0, max(0.0, total - i))
        if t <= 0: break
        x = pts[i][0] + (pts[i+1][0] - pts[i][0]) * t
        y = pts[i][1] + (pts[i+1][1] - pts[i][1]) * t
        drawn.append((x, y))
    if len(drawn) > 1:
        d.line(drawn, fill=blend(GOLD, INK, a), width=5, joint="curve")
    hx, hy = drawn[-1]
    r = 9 * a
    d.ellipse([hx-r, hy-r, hx+r, hy+r], fill=blend(GOLD_PALE, INK, a))

# ---------- הפריים ----------
F_BRAND, F_NAME = 14, 30
F_H1, F_H2 = 52, 78
F_STACK, F_SPARK = 104, 128
F_CTA = 190

f_head = font(132); f_sub = font(40, False); f_brand = font(52)
f_name = font(44); f_role = font(22, False); f_cta = font(34); f_eyebrow = font(22)

def frame(i):
    img = Image.new("RGB", (W, H), INK)

    glow_a = 0.34 + 0.06 * math.sin(i / 26.0)
    img.paste(Image.new("RGB", (W, H), GOLD), (0, 0), GLOW.point(lambda v: int(v * glow_a)))
    dotgrid(img)
    d = ImageDraw.Draw(img, "RGBA")

    corners(d, 54, ease_out(seg(i, 6, 34)) * .5)

    # קו זהב עליון שנמתח
    hl = ease_in_out(seg(i, 0, 46))
    if hl > 0:
        d.line([(W/2 - (W/2 - 54) * hl, 150), (W/2 + (W/2 - 54) * hl, 150)],
               fill=blend(GOLD_LT, INK, .35), width=1)

    # לוגו ושם
    a = ease_out(seg(i, F_BRAND, F_BRAND + 26))
    if a > 0:
        ccx, ccy, r = W - 200, 92, 46 * a
        d.ellipse([ccx - r, ccy - r, ccx + r, ccy + r], fill=blend(GOLD, INK, a))
        if a > .55:
            mono = rtl("מב")
            bb = d.textbbox((0, 0), mono, font=f_brand)
            d.text((ccx - (bb[2] - bb[0]) / 2 - bb[0], ccy - (bb[3] - bb[1]) / 2 - bb[1]),
                   mono, font=f_brand, fill=blend(INK, GOLD, (a - .55) / .45))
    a = ease_out(seg(i, F_NAME, F_NAME + 26))
    if a > 0:
        off = int((1 - a) * 22)
        text_ls(d, (W - 268 + off, 62), "מנגיסטו בלאו", f_name, blend(CANVAS, INK, a), anchor_right=True)
        text_ls(d, (W - 268 + off, 116), "ייעוץ וליווי השקעות", f_role,
                blend(GOLD_LT, INK, a * .8), ls=6, anchor_right=True)

    # כותרת
    a = ease_out(seg(i, F_H1, F_H1 + 30))
    if a > 0:
        text_ls(d, (W - 150, 372 + int((1 - a) * 40)), "הכסף שלך צריך תוכנית.",
                f_head, blend(CANVAS, INK, a), anchor_right=True)
    a = ease_out(seg(i, F_H2, F_H2 + 30))
    if a > 0:
        text_ls(d, (W - 150, 520 + int((1 - a) * 40)), "לא עוד דעה.",
                f_head, blend(MUTED, INK, a), anchor_right=True)

    # ערימות מטבעות
    for k, (cx, cnt, st) in enumerate(((360, 4, 0), (530, 7, 12), (700, 11, 24))):
        rise = ease_out(seg(i, F_STACK + st, F_STACK + st + 46))
        if rise > 0:
            coin_stack(d, cx, 830, cnt, rise)

    # גרף
    sp = ease_out(seg(i, F_SPARK, F_SPARK + 62))
    sparkline(d, 980, 700, 1.6, 1.35, sp, ease_out(seg(i, F_SPARK, F_SPARK + 20)))

    # קריאה לפעולה
    a = ease_out(seg(i, F_CTA, F_CTA + 30))
    if a > 0:
        label = "לשיחת אבחון ללא עלות"
        tw = sum(d.textlength(c, font=f_cta) for c in rtl(label))
        pw, ph = tw + 92, 84
        x1 = W - 150; x0 = x1 - pw * a
        y0 = 900
        d.rounded_rectangle([x0, y0, x1, y0 + ph], radius=ph/2, fill=blend(GOLD, INK, a))
        if a > .6:
            text_ls(d, ((x0 + x1)/2 - tw/2, y0 + 22), label, f_cta,
                    blend(INK, GOLD, (a-.6)/.4))

    # החשכה בכניסה וביציאה
    fade = min(ease_in_out(seg(i, 0, 12)), 1 - seg(i, N - 14, N))
    if fade < 1:
        img = Image.blend(Image.new("RGB", (W, H), (0, 0, 0)), img, max(0.0, fade))
    return img

os.makedirs(OUT, exist_ok=True)
for i in range(N):
    frame(i).save(os.path.join(OUT, "f%04d.png" % i))
    if i % 30 == 0:
        print("frame", i, "/", N, flush=True)
print("done", N, "frames")
