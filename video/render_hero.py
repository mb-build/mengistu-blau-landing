# פתיח מהפוטג׳ של הלקוח: פריצה → מערבולת → גרף עולה → כרטיס מותג.
# מקור אחד נשאר עמוד השדרה כדי שלא ייווצרו קפיצות בין טייקים זהים.
import os, math, subprocess as sp
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
SRCDIR = os.path.join(ROOT, "וידאו שלי")
SRC = os.path.join(SRCDIR, "Robot_superhero_stabilizing_fina…_202609021649.mp4")
OUTDIR = os.path.join(ROOT, "media")
OUT = os.path.join(OUTDIR, "intro-v2.mp4")

W, H, FPS = 1280, 720, 24
SRC_SEC = 10.0
CARD_SEC = 2.7
N_SRC = int(FPS * SRC_SEC)
N_CARD = int(FPS * CARD_SEC)
N = N_SRC + N_CARD

INK = (11, 18, 32); CANVAS = (247, 245, 240)
GOLD = (180, 137, 43); GOLD_LT = (210, 186, 132)

FD = "C:/Windows/Fonts/"
def font(px, bold=True): return ImageFont.truetype(FD + ("arialbd.ttf" if bold else "arial.ttf"), px)
f_big = font(62); f_sub = font(29, False); f_brand = font(30); f_role = font(13, False)
f_mono = font(28); f_card = font(52); f_cardsub = font(24); f_pill = font(24)

def _heb(c): return "֐" <= c <= "׿"
def rtl(s): return " ".join((w[::-1] if any(_heb(c) for c in w) else w) for w in reversed(s.split(" ")))
def eo(t): return 1 - (1 - t) ** 3
def eio(t): return 4*t*t*t if t < .5 else 1 - (-2*t+2)**3/2
def seg(t, a, b): return 0.0 if t <= a else (1.0 if t >= b else (t-a)/float(b-a))
def mix(c1, c2, a): return tuple(int(c2[i] + (c1[i]-c2[i])*a) for i in range(3))

def txt(d, xy, s, fnt, fill, ls=0, right=False, center=False):
    s = rtl(s)
    tot = (sum(d.textlength(c, font=fnt)+ls for c in s)-ls) if ls else d.textlength(s, font=fnt)
    x = xy[0]-tot if right else (xy[0]-tot/2 if center else xy[0])
    if ls:
        for c in s:
            d.text((x, xy[1]), c, font=fnt, fill=fill); x += d.textlength(c, font=fnt)+ls
    else:
        d.text((x, xy[1]), s, font=fnt, fill=fill)

# ---------- גרייד לצבעי המותג ----------
INKn = np.array(INK, dtype=np.float32)
GOLDn = np.array(GOLD, dtype=np.float32)
def grade(a):
    lum = (a[..., 0]*.2126 + a[..., 1]*.7152 + a[..., 2]*.0722)[..., None]
    a = lum + (a-lum)*0.55                                   # הפחתת רוויה
    w_s = (1.0 - lum/255.0)**1.5 * 0.46
    a = a*(1-w_s) + INKn*w_s                                 # צללים אל הכחול־פחם
    w_h = (lum/255.0)**2.2 * 0.30
    a = a*(1-w_h) + GOLDn*w_h                                # אורות אל הזהב
    return np.clip((a-9)*1.13 + 6, 0, 255)

# ---------- ווינייטה וסקרים, מחושבים פעם אחת ----------
def radial(cx, cy, rx, ry, p=1.15):
    sw, sh = 128, 72
    g = Image.new("L", (sw, sh), 0); px = g.load()
    for y in range(sh):
        for x in range(sw):
            dx = (x/sw-cx)/rx; dy = (y/sh-cy)/ry
            px[x, y] = int(255*max(0.0, 1-math.sqrt(dx*dx+dy*dy))**p)
    return g.resize((W, H), Image.BICUBIC)

VIGN = Image.eval(radial(.5, .5, .82, .90), lambda v: 255-v)
SCRIM = Image.new("L", (1, H))
for y in range(H):
    SCRIM.putpixel((0, y), int(255*max(0.0, min(1.0, (y/H-0.42)/0.58))**1.45*0.88))
SCRIM = SCRIM.resize((W, H))
VIG_L = Image.new("RGB", (W, H), (0, 0, 0))
INK_L = Image.new("RGB", (W, H), INK)

def brandbar(d, a=1.0):
    ccx, ccy, r = W-118, 58, 26
    d.ellipse([ccx-r, ccy-r, ccx+r, ccy+r], fill=mix(GOLD, INK, a))
    m = rtl("מב"); bb = d.textbbox((0, 0), m, font=f_mono)
    d.text((ccx-(bb[2]-bb[0])/2-bb[0], ccy-(bb[3]-bb[1])/2-bb[1]), m, font=f_mono, fill=mix(INK, GOLD, a))
    txt(d, (W-158, 38), "מנגיסטו בלאו", f_brand, mix(CANVAS, INK, a), right=True)
    txt(d, (W-158, 74), "ייעוץ וליווי השקעות", f_role, mix(GOLD_LT, INK, a*.85), ls=4, right=True)

def marks(d, a=.42):
    L, ins = 26, 38; c = mix(GOLD_LT, INK, a)
    for (x, y, sx, sy) in ((ins, ins, 1, 1), (W-ins, ins, -1, 1), (ins, H-ins, 1, -1), (W-ins, H-ins, -1, -1)):
        d.line([(x, y), (x+L*sx, y)], fill=c, width=2); d.line([(x, y), (x, y+L*sy)], fill=c, width=2)

# ---------- הכיתובים ----------
CAPS = [
    (0.55, 3.25, "לפרוץ את המחסום",  "הכסף שלך תקוע מאחורי זכוכית"),
    (3.70, 6.45, "לעבור את הרעש",     "מאות אפשרויות, כיוון אחד נכון"),
    (6.90, 9.95, "ולצאת עם תוכנית",   "מסלול אחד, ברור, מותאם לך"),
]
def caption(d, t):
    for (a, b, title, sub) in CAPS:
        if not (a - .01 <= t <= b + .01):
            continue
        al = eo(seg(t, a, a+.55)) * (1 - seg(t, b-.45, b))
        if al <= 0.001:
            continue
        off = int((1-eo(seg(t, a, a+.55)))*22)
        txt(d, (W-96, 486+off), title, f_big, mix(CANVAS, INK, al), right=True)
        txt(d, (W-96, 566+off), sub, f_sub, mix(GOLD_LT, INK, al*.92), right=True)
        # קו זהב שנמתח מתחת לכותרת
        wln = int(150*eo(seg(t, a+.2, a+.9)))
        if wln > 2:
            d.rectangle([W-96-wln, 613+off, W-96, 615+off], fill=mix(GOLD, INK, al))

def card(d, t):                                  # t מ-0 עד CARD_SEC
    a = eo(seg(t, .10, .80))
    ccx, ccy, r = W//2, 236, 52*a
    if r > 1:
        d.ellipse([ccx-r, ccy-r, ccx+r, ccy+r], fill=mix(GOLD, INK, a))
    if a > .55:
        m = rtl("מב"); bb = d.textbbox((0, 0), m, font=f_card)
        d.text((ccx-(bb[2]-bb[0])/2-bb[0], ccy-(bb[3]-bb[1])/2-bb[1]), m,
               font=f_card, fill=mix(INK, GOLD, (a-.55)/.45))
    b = eo(seg(t, .40, 1.10))
    if b > 0:
        txt(d, (W//2, 322), "מנגיסטו בלאו", f_big, mix(CANVAS, INK, b), center=True)
        txt(d, (W//2, 404), "ייעוץ וליווי השקעות", f_cardsub, mix(GOLD_LT, INK, b*.9), ls=6, center=True)
    c = eo(seg(t, .85, 1.55))
    if c > 0:
        lab = "לשיחת אבחון ללא עלות"
        tw = sum(d.textlength(ch, font=f_pill) for ch in rtl(lab))
        pw, ph = tw+72, 58
        d.rounded_rectangle([W//2-pw/2, 486, W//2+pw/2, 486+ph], radius=ph/2, fill=mix(GOLD, INK, c))
        if c > .6:
            txt(d, (W//2, 500), lab, f_pill, mix(INK, GOLD, (c-.6)/.4), center=True)

# ---------- הזרמה: פענוח → עיבוד → קידוד ----------
dec = sp.Popen(["ffmpeg", "-v", "error", "-i", SRC, "-t", str(SRC_SEC),
                "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], stdout=sp.PIPE)
enc = sp.Popen(["ffmpeg", "-y", "-v", "error",
                "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", "%dx%d" % (W, H), "-r", str(FPS), "-i", "-",
                "-i", SRC,
                "-map", "0:v", "-map", "1:a",
                "-af", "afade=t=out:st=%.2f:d=1.2,volume=0.9" % (SRC_SEC-1.4),
                "-c:v", "libx264", "-preset", "slow", "-crf", "23", "-pix_fmt", "yuv420p",
                "-profile:v", "high", "-movflags", "+faststart",
                "-c:a", "aac", "-b:a", "128k", "-shortest" if False else "-t", str(N/FPS),
                OUT], stdin=sp.PIPE)

FRAME = W*H*3
last = None
for i in range(N):
    t = i/float(FPS)
    if i < N_SRC:
        raw = dec.stdout.read(FRAME)
        if len(raw) < FRAME:
            break
        a = np.frombuffer(raw, dtype=np.uint8).reshape(H, W, 3).astype(np.float32)
        img = Image.fromarray(grade(a).astype(np.uint8))
        last = img
        ct = t
    else:
        k = (i-N_SRC)/float(FPS)
        img = last.filter(ImageFilter.GaussianBlur(min(14, 3+k*11)))
        img = Image.blend(img, Image.new("RGB", (W, H), INK), min(.72, .28+k*.30))
        ct = None

    img.paste(INK_L, (0, 0), Image.eval(SCRIM, lambda v: int(v*0.9)))
    img.paste(VIG_L, (0, 0), Image.eval(VIGN, lambda v: int(v*0.46)))
    d = ImageDraw.Draw(img)
    marks(d)
    brandbar(d, eo(seg(t, .30, 1.00)))
    if ct is not None:
        caption(d, ct)
    else:
        card(d, (i-N_SRC)/float(FPS))

    fade = min(eio(seg(i, 0, 9)), 1-seg(i, N-7, N))
    if fade < 1:
        img = Image.blend(Image.new("RGB", (W, H), (0, 0, 0)), img, max(0.0, fade))
    enc.stdin.write(img.tobytes())
    if i % 48 == 0:
        print("frame", i, "/", N, flush=True)

enc.stdin.close(); enc.wait(); dec.wait()
print("done", OUT, round(N/FPS, 2), "s")
