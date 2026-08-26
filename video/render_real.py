# סרטון הפתיחה מתצלומים אמיתיים של יועצי השקעות ולקוחות.
# תנועת קן-ברנס, גרייד לצבעי המותג, ווינייטה, וכיתובים בעברית.
import math, os
import numpy as np
from PIL import Image, ImageDraw, ImageFont

W, H, FPS = 1920, 1080, 30
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "frames_real")
PH = os.path.join(HERE, "photos")

INK = (11, 18, 32); CANVAS = (247, 245, 240)
GOLD = (180, 137, 43); GOLD_LT = (210, 186, 132)

FD = "C:/Windows/Fonts/"
def font(px, bold=True): return ImageFont.truetype(FD + ("arialbd.ttf" if bold else "arial.ttf"), px)
f_big = font(88); f_mid = font(44); f_brand = font(42); f_role = font(18, False); f_mono = font(40)

def _heb(c): return "֐" <= c <= "׿"
def rtl(s): return " ".join((w[::-1] if any(_heb(c) for c in w) else w) for w in reversed(s.split(" ")))
def eo(t): return 1-(1-t)**3
def eio(t): return 4*t*t*t if t < .5 else 1-(-2*t+2)**3/2
def seg(t, a, b): return 0.0 if t <= a else (1.0 if t >= b else (t-a)/float(b-a))
def mix(c1, c2, a): return tuple(int(c2[i]+(c1[i]-c2[i])*a) for i in range(3))

def txt(d, xy, s, fnt, fill, ls=0, right=False, center=False):
    s = rtl(s)
    tot = (sum(d.textlength(c, font=fnt)+ls for c in s)-ls) if ls else d.textlength(s, font=fnt)
    x = xy[0]-tot if right else (xy[0]-tot/2 if center else xy[0])
    if ls:
        for c in s:
            d.text((x, xy[1]), c, font=fnt, fill=fill); x += d.textlength(c, font=fnt)+ls
    else:
        d.text((x, xy[1]), s, font=fnt, fill=fill)

# ---------- הכנה: חיתוך ל-16:9 ברזולוציה שמאפשרת קן-ברנס ----------
BW, BH = 2400, 1350
def prep(name):
    im = Image.open(os.path.join(PH, name)).convert("RGB")
    w, h = im.size
    tr = BW/float(BH)
    if w/float(h) > tr:                       # רחב מדי — חותכים בצדדים
        nw = int(h*tr); im = im.crop(((w-nw)//2, 0, (w-nw)//2+nw, h))
    else:                                     # גבוה מדי — חותכים למעלה, שומרים פנים
        nh = int(w/tr); top = int((h-nh)*0.28)
        im = im.crop((0, top, w, top+nh))
    return im.resize((BW, BH), Image.LANCZOS)

PHOTOS = {k: prep(v) for k, v in (
    ("doubt", "s1_doubt.jpg"), ("listen", "s2_listen.jpg"),
    ("plan", "s3_plan.jpg"), ("trust", "s4_trust.jpg"))}

# ---------- גרייד לצבעי המותג ----------
INKn = np.array(INK, dtype=np.float32)
GOLDn = np.array(GOLD, dtype=np.float32)
def grade(im, warm=1.0):
    a = np.asarray(im, dtype=np.float32)
    lum = (a[..., 0]*.2126 + a[..., 1]*.7152 + a[..., 2]*.0722)[..., None]
    a = lum + (a-lum)*0.58                                  # הפחתת רוויה
    w_s = (1.0 - lum/255.0)**1.5 * 0.42                     # צללים אל הכחול־פחם
    a = a*(1-w_s) + INKn*w_s
    w_h = (lum/255.0)**2.2 * 0.26 * warm                    # אורות אל הזהב
    a = a*(1-w_h) + GOLDn*w_h
    a = np.clip((a-8)*1.10 + 6, 0, 255)                     # קונטרסט
    return Image.fromarray(a.astype(np.uint8))

def radial(cx, cy, rx, ry, p=1.15):
    sw, sh = 120, 68
    g = Image.new("L", (sw, sh), 0); px = g.load()
    for y in range(sh):
        for x in range(sw):
            dx = (x/sw-cx)/rx; dy = (y/sh-cy)/ry
            px[x, y] = int(255*max(0.0, 1-math.sqrt(dx*dx+dy*dy))**p)
    return g.resize((W, H), Image.BICUBIC)
VIGN = Image.eval(radial(.5, .5, .80, .88), lambda v: 255-v)
SCRIM = Image.new("L", (1, H))
for y in range(H):
    SCRIM.putpixel((0, y), int(255*max(0.0, min(1.0, (y/H-0.40)/0.60))**1.4*0.90))
SCRIM = SCRIM.resize((W, H))

def kenburns(key, p, zoom0=1.06, zoom1=1.16, pan=(0.0, 0.0)):
    """p מ-0 עד 1 — זום איטי פנימה עם הסטה עדינה."""
    src = PHOTOS[key]
    z = zoom0 + (zoom1-zoom0)*eio(p)
    cw, ch = BW/z, BH/z
    cx = BW/2 + pan[0]*(BW-cw)/2*(p-0.5)*2
    cy = BH/2 + pan[1]*(BH-ch)/2*(p-0.5)*2
    cx = max(cw/2, min(BW-cw/2, cx)); cy = max(ch/2, min(BH-ch/2, cy))
    return src.crop((int(cx-cw/2), int(cy-ch/2), int(cx+cw/2), int(cy+ch/2))).resize((W, H), Image.LANCZOS)

def brandbar(d, a=1.0):
    ccx, ccy, r = W-182, 84, 38
    d.ellipse([ccx-r, ccy-r, ccx+r, ccy+r], fill=mix(GOLD, INK, a))
    m = rtl("מב"); bb = d.textbbox((0, 0), m, font=f_mono)
    d.text((ccx-(bb[2]-bb[0])/2-bb[0], ccy-(bb[3]-bb[1])/2-bb[1]), m, font=f_mono, fill=mix(INK, GOLD, a))
    txt(d, (W-238, 56), "מנגיסטו בלאו", f_brand, mix(CANVAS, INK, a), right=True)
    txt(d, (W-238, 104), "ייעוץ וליווי השקעות", f_role, mix(GOLD_LT, INK, a*.85), ls=5, right=True)

def marks(d, a=.40):
    L, ins = 32, 52; c = mix(GOLD_LT, INK, a)
    for (x, y, sx, sy) in ((ins, ins, 1, 1), (W-ins, ins, -1, 1), (ins, H-ins, 1, -1), (W-ins, H-ins, -1, -1)):
        d.line([(x, y), (x+L*sx, y)], fill=c, width=2); d.line([(x, y), (x, y+L*sy)], fill=c, width=2)

def photo_scene(key, t, dur, title, sub, pan=(0, 0), warm=1.0):
    img = grade(kenburns(key, min(1.0, t/dur), pan=pan), warm)
    img.paste(Image.new("RGB", (W, H), INK), (0, 0), Image.eval(SCRIM, lambda v: int(v*0.92)))
    img.paste(Image.new("RGB", (W, H), (0, 0, 0)), (0, 0), Image.eval(VIGN, lambda v: int(v*0.42)))
    d = ImageDraw.Draw(img); marks(d); brandbar(d, 1)
    a = eo(seg(t, .25, 1.05))
    if a > 0:
        off = int((1-a)*26)
        txt(d, (W-130, 738+off), title, f_big, mix(CANVAS, INK, a), right=True)
        txt(d, (W-130, 862+off), sub, f_mid, mix(GOLD_LT, INK, a*.9), right=True)
    return img

def brand_card(t):
    img = grade(kenburns("trust", min(1.0, t/2.3), 1.18, 1.28, (0, 0)), 1.15)
    img.paste(Image.new("RGB", (W, H), INK), (0, 0), Image.eval(radial(.5, .5, 1.0, 1.0, .6), lambda v: int(v*0.86)))
    img.paste(Image.new("RGB", (W, H), (0, 0, 0)), (0, 0), Image.eval(VIGN, lambda v: int(v*0.40)))
    d = ImageDraw.Draw(img); marks(d)
    a = eo(seg(t, .05, .7))
    ccx, ccy, r = W//2, 318, 90*a
    d.ellipse([ccx-r, ccy-r, ccx+r, ccy+r], fill=mix(GOLD, INK, a))
    if a > .55:
        big = font(92); m = rtl("מב"); bb = d.textbbox((0, 0), m, font=big)
        d.text((ccx-(bb[2]-bb[0])/2-bb[0], ccy-(bb[3]-bb[1])/2-bb[1]), m, font=big, fill=mix(INK, GOLD, (a-.55)/.45))
    b = eo(seg(t, .4, 1.0))
    if b > 0:
        txt(d, (W//2, 452), "מנגיסטו בלאו", f_big, mix(CANVAS, INK, b), center=True)
        txt(d, (W//2, 574), "ייעוץ וליווי השקעות", f_mid, mix(GOLD_LT, INK, b*.9), ls=8, center=True)
    c = eo(seg(t, .85, 1.45))
    if c > 0:
        lab = "לשיחת אבחון ללא עלות"
        tw = sum(d.textlength(ch, font=f_mid) for ch in rtl(lab))
        pw, ph = tw+110, 94
        d.rounded_rectangle([W//2-pw/2, 700, W//2+pw/2, 700+ph], radius=ph/2, fill=mix(GOLD, INK, c))
        if c > .6: txt(d, (W//2, 722), lab, f_mid, mix(INK, GOLD, (c-.6)/.4), center=True)
    return img

SCENES = [
    (lambda t: photo_scene("doubt", t, 2.6, "מול המסך, לבד", "כל אפשרות נשמעת נכונה", (-.6, 0), .8), 2.6),
    (lambda t: photo_scene("listen", t, 2.6, "45 דקות של הקשבה", "לפני מילה אחת על השקעה", (.5, .2), 1.0), 2.6),
    (lambda t: photo_scene("plan", t, 2.6, "תוכנית אחת. ברורה.", "מותאמת לך, לא לתבנית", (-.4, .1), 1.05), 2.6),
    (lambda t: photo_scene("trust", t, 2.6, "כאן מתחיל האמון", "מלווה אחד, לאורך כל הדרך", (.3, -.2), 1.1), 2.6),
    (brand_card, 2.3),
]
XF = 0.55
STARTS, _a = [], 0.0
for _i, (_f, _d) in enumerate(SCENES):
    STARTS.append(_a); _a += _d - (XF if _i < len(SCENES)-1 else 0)
TOTAL = STARTS[-1] + SCENES[-1][1]
N = int(FPS*TOTAL)

def compose(tg):
    act = []
    for i, (fn, dur) in enumerate(SCENES):
        lt = tg-STARTS[i]
        if -1e-6 <= lt <= dur+1e-6: act.append((fn, min(max(lt, 0.0), dur)))
    if not act: return SCENES[-1][0](SCENES[-1][1])
    if len(act) == 1: return act[0][0](act[0][1])
    (f0, l0), (f1, l1) = act[0], act[1]
    return Image.blend(f0(l0), f1(l1), eio(max(0.0, min(1.0, l1/XF))))

os.makedirs(OUT, exist_ok=True)
for i in range(N):
    img = compose(i/float(FPS))
    fade = min(eio(seg(i, 0, 11)), 1-seg(i, N-13, N))
    if fade < 1: img = Image.blend(Image.new("RGB", (W, H), (0, 0, 0)), img, max(0.0, fade))
    img.save(os.path.join(OUT, "f%04d.png" % i))
    if i % 30 == 0: print("frame", i, "/", N, flush=True)
print("done", N, "total", round(TOTAL, 2), "s")
