# פתיח־סיפור מארבעת הקליפים: פריצה → מערבולת הכסף → השוק נופל →
# היריב מופיע → קרב → ניצחון והגרפים עולים → כרטיס מותג.
import os, math, subprocess as sp
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
SRCDIR = os.path.join(ROOT, "וידאו שלי")
C1 = os.path.join(SRCDIR, "Robot_superhero_stabilizing_fina…_202609021649 (1).mp4")
C2 = os.path.join(SRCDIR, "Robot_superhero_stabilizing_fina…_202609021649 (2).mp4")
C3 = os.path.join(SRCDIR, "Robot_superhero_stabilizing_fina…_202609021649 (3).mp4")
C4 = os.path.join(SRCDIR, "Robot_superhero_stabilizing_fina…_202609021649.mp4")
OUT = os.path.join(ROOT, "media", "intro-v2.mp4")
AUD = os.path.join(HERE, "story_audio.m4a")

W, H, FPS = 1280, 720, 24
CARD_SEC = 2.7
N_CARD = int(FPS * CARD_SEC)

# רשימת החיתוך: (קלט, פריים־התחלה, פריים־סיום)
CUTS = [
    (0,   0,  34),   # פריצה דרך הזכוכית            1.42s
    (0,  44, 104),   # טיסה מעל העיר + מערבולת הכסף 2.50s
    (0, 118, 142),   # נחיתה בשוק — הגרף האדום נופל 1.00s
    (1, 134, 164),   # היריב האדום מופיע ותוקף      1.25s
    (2,  28, 104),   # הקרב — התנגשות קרניים        3.17s
    (2, 194, 240),   # ניצחון — עמודות ירוקות עולות 1.92s
]
N_SRC = sum(b-a for (_, a, b) in CUTS)
N = N_SRC + N_CARD

INK = (11, 18, 32); CANVAS = (247, 245, 240)
GOLD = (180, 137, 43); GOLD_LT = (210, 186, 132)

FD = "C:/Windows/Fonts/"
def font(px, bold=True): return ImageFont.truetype(FD + ("arialbd.ttf" if bold else "arial.ttf"), px)
f_big = font(58); f_sub = font(27, False); f_brand = font(30); f_role = font(13, False)
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

INKn = np.array(INK, dtype=np.float32); GOLDn = np.array(GOLD, dtype=np.float32)
def grade(a):
    lum = (a[..., 0]*.2126 + a[..., 1]*.7152 + a[..., 2]*.0722)[..., None]
    a = lum + (a-lum)*0.58
    w_s = (1.0 - lum/255.0)**1.5 * 0.44
    a = a*(1-w_s) + INKn*w_s
    w_h = (lum/255.0)**2.2 * 0.28
    a = a*(1-w_h) + GOLDn*w_h
    return np.clip((a-9)*1.12 + 6, 0, 255)

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
VIG_L = Image.new("RGB", (W, H), (0, 0, 0)); INK_L = Image.new("RGB", (W, H), INK)

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

# הכיתובים — סיפור אחד, ארבעה משפטים
CAPS = [
    (0.55, 3.95, "בשוק יש מלחמה על הכסף שלך", "כל יום. גם כשאתה לא מסתכל."),
    (4.30, 6.85, "מי שלא שומר עליו — מאבד אותו", "עמלות, פאניקה, ועצות של אחרים"),
    (7.15, 9.35, "צריך מישהו בצד שלך",          "שיודע מתי נלחמים ומתי מוותרים"),
    (9.60, 11.20, "וזה מה שנשאר בסוף",           "תוכנית שמחזיקה גם כשהשוק זז"),
]
def caption(d, t):
    for (a, b, title, sub) in CAPS:
        if not (a - .01 <= t <= b + .01):
            continue
        al = eo(seg(t, a, a+.50)) * (1 - seg(t, b-.40, b))
        if al <= 0.001:
            continue
        off = int((1-eo(seg(t, a, a+.50)))*22)
        txt(d, (W-96, 490+off), title, f_big, mix(CANVAS, INK, al), right=True)
        txt(d, (W-96, 566+off), sub, f_sub, mix(GOLD_LT, INK, al*.92), right=True)
        wln = int(150*eo(seg(t, a+.18, a+.85)))
        if wln > 2:
            d.rectangle([W-96-wln, 612+off, W-96, 614+off], fill=mix(GOLD, INK, al))

def card(d, t):
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
        txt(d, (W//2, 398), "ייעוץ וליווי השקעות", f_cardsub, mix(GOLD_LT, INK, b*.9), ls=6, center=True)
    c = eo(seg(t, .85, 1.55))
    if c > 0:
        lab = "לשיחת אבחון ללא עלות"
        tw = sum(d.textlength(ch, font=f_pill) for ch in rtl(lab))
        pw, ph = tw+72, 58
        d.rounded_rectangle([W//2-pw/2, 482, W//2+pw/2, 482+ph], radius=ph/2, fill=mix(GOLD, INK, c))
        if c > .6:
            txt(d, (W//2, 496), lab, f_pill, mix(INK, GOLD, (c-.6)/.4), center=True)

# ---------- פסקול: חצי ראשון מקליפ 4, הקרב מקליפ 3 ----------
sp.run(["ffmpeg", "-y", "-v", "error", "-i", C4, "-i", C3,
        "-filter_complex",
        "[0:a]atrim=0:5.4,asetpts=N/SR/TB[a1];"
        "[1:a]atrim=0.6:8.2,asetpts=N/SR/TB[a2];"
        "[a1][a2]acrossfade=d=0.55:c1=tri:c2=tri,"
        "afade=t=in:st=0:d=0.5,afade=t=out:st=11.0:d=1.4,volume=0.92[ao]",
        "-map", "[ao]", "-c:a", "aac", "-b:a", "128k", AUD], check=True)

# ---------- הרכבת התמונה ----------
SRCS = [C4, C2, C3]
fc = ""
for i, (src, a, b) in enumerate(CUTS):
    fc += "[%d:v]trim=start_frame=%d:end_frame=%d,setpts=PTS-STARTPTS[v%d];" % (src, a, b, i)
fc += "".join("[v%d]" % i for i in range(len(CUTS))) + "concat=n=%d:v=1:a=0[out]" % len(CUTS)

dec_cmd = ["ffmpeg", "-v", "error"]
for s in SRCS:
    dec_cmd += ["-i", s]
dec_cmd += ["-filter_complex", fc, "-map", "[out]",
            "-f", "rawvideo", "-pix_fmt", "rgb24", "-"]

dec = sp.Popen(dec_cmd, stdout=sp.PIPE)
enc = sp.Popen(["ffmpeg", "-y", "-v", "error",
                "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", "%dx%d" % (W, H), "-r", str(FPS), "-i", "-",
                "-i", AUD, "-map", "0:v", "-map", "1:a",
                "-c:v", "libx264", "-preset", "slow", "-crf", "23", "-pix_fmt", "yuv420p",
                "-profile:v", "high", "-movflags", "+faststart",
                "-c:a", "aac", "-b:a", "128k", "-t", str(N/FPS), OUT], stdin=sp.PIPE)

# גבולות החיתוכים — הבזק זהב קצר על כל מעבר, כדי שהקאט ייקרא ככוונה
BOUNDS = []
_acc = 0
for (_, a, b) in CUTS[:-1]:
    _acc += b-a; BOUNDS.append(_acc)

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

    # הבזק זהב על גבול חיתוך
    for bfr in BOUNDS:
        k = i - bfr
        if 0 <= k < 4:
            img = Image.blend(img, Image.new("RGB", (W, H), GOLD_LT), (4-k)/4.0*0.22)

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
