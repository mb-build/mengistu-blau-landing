# פתיח־סיפור, גרסה מהודקת: קצב קצר יותר, האטה על רגע השיא,
# מד תיק שנופל ועולה, ריזר וחבטה בפסקול, וכרטיס סיום עם הוכחות.
import os, math, wave, subprocess as sp
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
SRCDIR = os.path.join(ROOT, "וידאו שלי")
C2 = os.path.join(SRCDIR, "Robot_superhero_stabilizing_fina…_202609021649 (2).mp4")
C3 = os.path.join(SRCDIR, "Robot_superhero_stabilizing_fina…_202609021649 (3).mp4")
C4 = os.path.join(SRCDIR, "Robot_superhero_stabilizing_fina…_202609021649.mp4")
OUT = os.path.join(ROOT, "media", "intro-v2.mp4")
SFX = os.path.join(HERE, "story_sfx.wav")
AUD = os.path.join(HERE, "story_audio.m4a")

W, H, FPS = 1280, 720, 24
CARD_SEC = 2.6
N_CARD = int(FPS * CARD_SEC)

# (קלט, פריים־התחלה, פריים־סיום, האטה)
CUTS = [
    (0,   0,  26, 1),   # פריצה דרך הזכוכית
    (0,  46,  90, 1),   # העיר ומערבולת הכסף
    (0, 120, 140, 1),   # השוק נופל — הגרף האדום
    (1, 136, 162, 1),   # היריב האדום מופיע
    (2,  24,  76, 1),   # הדו־קרב נפתח
    (2, 168, 192, 2),   # השיא — התנגשות הקרניים, בהאטה
    (2, 200, 238, 1),   # ניצחון — הגרפים עולים
]
SRCS = [C4, C2, C3]
N_SRC = sum(b-a for (_, a, b, _) in CUTS)
N_OUT_SRC = sum((b-a)*r for (_, a, b, r) in CUTS)
N = N_OUT_SRC + N_CARD

# תוכנית פריימים: לכל פריים־קלט מספר החזרות, וסימון האם הוא בקטע הניצחון
REPS, ISWIN = [], []
for (_, a, b, r) in CUTS:
    win = (a == 200)
    REPS += [r]*(b-a); ISWIN += [win]*(b-a)

INK = (11, 18, 32); CANVAS = (247, 245, 240)
GOLD = (180, 137, 43); GOLD_LT = (210, 186, 132); MUTED = (142, 151, 172)

FD = "C:/Windows/Fonts/"
def font(px, bold=True): return ImageFont.truetype(FD + ("arialbd.ttf" if bold else "arial.ttf"), px)
f_big = font(56); f_mid = font(46); f_sub = font(26, False); f_brand = font(30); f_role = font(13, False)
f_mono = font(28); f_card = font(52); f_cardsub = font(23); f_pill = font(24)
f_hud = font(15, False); f_hudn = font(30); f_hudd = font(15); f_stat = font(27); f_statl = font(12, False)

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
def grade(a, gold_push=0.0):
    lum = (a[..., 0]*.2126 + a[..., 1]*.7152 + a[..., 2]*.0722)[..., None]
    a = lum + (a-lum)*(0.58 - gold_push*0.30)          # הניצחון מאבד רוויה כדי לא להישאר ירוק
    w_s = (1.0 - lum/255.0)**1.5 * 0.44
    a = a*(1-w_s) + INKn*w_s
    w_h = (lum/255.0)**2.0 * (0.28 + gold_push*0.34)   # ואז נמשך אל הזהב
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
    SCRIM.putpixel((0, y), int(255*max(0.0, min(1.0, (y/H-0.44)/0.56))**1.45*0.90))
SCRIM = SCRIM.resize((W, H))
TOPSCRIM = Image.new("L", (1, H))
for y in range(H):
    TOPSCRIM.putpixel((0, y), int(255*max(0.0, 1-y/190.0)**1.3*0.55))
TOPSCRIM = TOPSCRIM.resize((W, H))
VIG_L = Image.new("RGB", (W, H), (0, 0, 0)); INK_L = Image.new("RGB", (W, H), INK)

def brandbar(d, a=1.0):
    ccx, ccy, r = W-118, 56, 25
    d.ellipse([ccx-r, ccy-r, ccx+r, ccy+r], fill=mix(GOLD, INK, a))
    m = rtl("מב"); bb = d.textbbox((0, 0), m, font=f_mono)
    d.text((ccx-(bb[2]-bb[0])/2-bb[0], ccy-(bb[3]-bb[1])/2-bb[1]), m, font=f_mono, fill=mix(INK, GOLD, a))
    txt(d, (W-156, 36), "מנגיסטו בלאו", f_brand, mix(CANVAS, INK, a), right=True)
    txt(d, (W-156, 72), "ייעוץ וליווי השקעות", f_role, mix(GOLD_LT, INK, a*.85), ls=4, right=True)

def marks(d, a=.42):
    L, ins = 26, 36; c = mix(GOLD_LT, INK, a)
    for (x, y, sx, sy) in ((ins, ins, 1, 1), (W-ins, ins, -1, 1), (ins, H-ins, 1, -1), (W-ins, H-ins, -1, -1)):
        d.line([(x, y), (x+L*sx, y)], fill=c, width=2); d.line([(x, y), (x, y+L*sy)], fill=c, width=2)

# ---------- מד התיק: הכסף שעליו נלחמים ----------
START_V = 412000.0
def portfolio(t):
    if t < 2.90:  return START_V, 0
    if t < 4.85:  return START_V - 74000*eio(seg(t, 2.90, 4.85)), -1
    if t < 8.95:  return 338000 + 5000*math.sin((t-4.85)*4.2), -1
    return 338000 + 209000*eo(seg(t, 8.95, 10.55)), 1

def hud(d, t, a):
    if a <= .01: return
    x0, y0 = 56, 46
    txt(d, (x0, y0), "התיק שלך", f_hud, mix(GOLD_LT, INK, a*.85))
    v, dirn = portfolio(t)
    d.text((x0, y0+22), "%s%s" % ("\u20aa", "{:,.0f}".format(v)), font=f_hudn, fill=mix(CANVAS, INK, a))
    pct = (v/START_V - 1) * 100
    col = GOLD_LT if pct >= 0 else (196, 122, 106)
    arw = "\u25b2" if pct >= 0 else "\u25bc"
    d.text((x0, y0+60), "%s %+.1f%%" % (arw, pct), font=f_hudd, fill=mix(col, INK, a*.95))
    # ספארקליין קטן
    pts = []
    for k in range(34):
        tk = max(0.0, t - (33-k)*0.09)
        vv, _ = portfolio(tk)
        pts.append((x0+k*4.6, y0+118 - (vv-320000)/240000.0*42))
    if len(pts) > 1:
        d.line(pts, fill=mix(col, INK, a*.75), width=2)

# ---------- הכיתובים ----------
CAPS = [
    (0.55, 2.80, "בשוק יש מלחמה על הכסף שלך", "כל יום. גם כשאתה לא מסתכל.", "r"),
    (3.10, 4.75, "מי שלא שומר עליו — מאבד אותו", "עמלות, פאניקה, ועצות של אחרים", "r"),
    (5.15, 6.90, "צריך מישהו בצד שלך", "שיודע מתי נלחמים ומתי מוותרים", "c"),
    (9.25, 10.55, "וזה מה שנשאר בסוף", "תוכנית שמחזיקה גם כשהשוק זז", "r"),
]
def caption(d, t):
    for (a, b, title, sub, pos) in CAPS:
        if not (a - .01 <= t <= b + .01): continue
        al = eo(seg(t, a, a+.45)) * (1 - seg(t, b-.35, b))
        if al <= 0.001: continue
        off = int((1-eo(seg(t, a, a+.45)))*20)
        if pos == "c":
            txt(d, (W//2, 452+off), title, f_big, mix(CANVAS, INK, al), center=True)
            txt(d, (W//2, 528+off), sub, f_sub, mix(GOLD_LT, INK, al*.92), center=True)
            wln = int(180*eo(seg(t, a+.16, a+.8)))
            if wln > 2: d.rectangle([W//2-wln//2, 572+off, W//2+wln//2, 574+off], fill=mix(GOLD, INK, al))
        else:
            txt(d, (W-92, 492+off), title, f_mid, mix(CANVAS, INK, al), right=True)
            txt(d, (W-92, 558+off), sub, f_sub, mix(GOLD_LT, INK, al*.92), right=True)
            wln = int(140*eo(seg(t, a+.16, a+.8)))
            if wln > 2: d.rectangle([W-92-wln, 602+off, W-92, 604+off], fill=mix(GOLD, INK, al))

STATS = [("12+", "שנות ניסיון"), ("1,400+", "תוכניות"), ("\u20aa380M", "בליווי")]
def card(d, t):
    a = eo(seg(t, .08, .74))
    ccx, ccy, r = W//2, 208, 50*a
    if r > 1: d.ellipse([ccx-r, ccy-r, ccx+r, ccy+r], fill=mix(GOLD, INK, a))
    if a > .55:
        m = rtl("מב"); bb = d.textbbox((0, 0), m, font=f_card)
        d.text((ccx-(bb[2]-bb[0])/2-bb[0], ccy-(bb[3]-bb[1])/2-bb[1]), m,
               font=f_card, fill=mix(INK, GOLD, (a-.55)/.45))
    b = eo(seg(t, .34, 1.00))
    if b > 0:
        txt(d, (W//2, 288), "מנגיסטו בלאו", f_big, mix(CANVAS, INK, b), center=True)
        txt(d, (W//2, 360), "ייעוץ וליווי השקעות", f_cardsub, mix(GOLD_LT, INK, b*.9), ls=6, center=True)
    s = eo(seg(t, .62, 1.28))
    if s > 0:
        d.line([(W//2-190, 404), (W//2+190, 404)], fill=mix(GOLD, INK, s*.4), width=1)
        for k, (num, lab) in enumerate(STATS):
            cx = W//2 + (1-k)*168
            txt(d, (cx, 420), num, f_stat, mix(GOLD_LT, INK, s), center=True)
            txt(d, (cx, 456), lab, f_statl, mix(MUTED, INK, s), center=True)
    c = eo(seg(t, .95, 1.62))
    if c > 0:
        lab = "לשיחת אבחון ללא עלות"
        tw = sum(d.textlength(ch, font=f_pill) for ch in rtl(lab))
        pw, ph = tw+72, 56
        d.rounded_rectangle([W//2-pw/2, 512, W//2+pw/2, 512+ph], radius=ph/2, fill=mix(GOLD, INK, c))
        if c > .6: txt(d, (W//2, 525), lab, f_pill, mix(INK, GOLD, (c-.6)/.4), center=True)

# ---------- פסקול: מקור + ריזר לשיא + חבטה לניצחון ----------
SR = 44100
DUR = N/float(FPS)
n = int(SR*DUR); tt = np.arange(n)/SR
sfx = np.zeros(n)
def place(sig, t0, amp=1.0):
    i0 = int(t0*SR); i1 = min(n, i0+len(sig))
    if i0 < n: sfx[i0:i1] += sig[:i1-i0]*amp

k = np.arange(int(SR*1.15))/SR                       # ריזר אל השיא בשנייה 7.0
sweep = 150*(1500/150.0)**(k/1.15)
rng = np.random.default_rng(11)
noise = np.convolve(rng.normal(0, 1, len(k)), np.ones(40)/40, mode="same")
place((0.55*np.sin(2*np.pi*np.cumsum(sweep)/SR) + 0.45*noise) * (k/1.15)**2.3, 5.85, 0.34)

k = np.arange(int(SR*2.6))/SR                        # חבטה על חיתוך הניצחון
body = np.sin(2*np.pi*np.cumsum(140*np.exp(-4.2*k)+32)/SR)*np.exp(-1.9*k)
crack = np.random.default_rng(5).normal(0, 1, len(k))*np.exp(-24*k)*0.30
place(body+crack, 8.95, 0.55)

fade = np.ones(n); fo = int(SR*1.0)
fade[-fo:] = np.linspace(1, 0, fo)
sfx = np.tanh(sfx*1.2)*0.8*fade
with wave.open(SFX, "w") as wv:
    wv.setnchannels(1); wv.setsampwidth(2); wv.setframerate(SR)
    wv.writeframes((sfx*32767).astype(np.int16).tobytes())

sp.run(["ffmpeg", "-y", "-v", "error", "-i", C4, "-i", C3, "-i", SFX,
        "-filter_complex",
        "[0:a]atrim=0:4.6,asetpts=N/SR/TB[a1];"
        "[1:a]atrim=0.6:8.4,asetpts=N/SR/TB[a2];"
        "[a1][a2]acrossfade=d=0.5:c1=tri:c2=tri[src];"
        "[src]afade=t=in:st=0:d=0.4,afade=t=out:st=%.2f:d=1.2,volume=0.85[sv];"
        "[2:a]volume=1.0[fx];"
        "[sv][fx]amix=inputs=2:duration=longest:normalize=0[ao]" % (DUR-1.5),
        "-map", "[ao]", "-c:a", "aac", "-b:a", "128k", AUD], check=True)

# ---------- הרכבה ----------
fc = ""
for i, (src, a, b, _) in enumerate(CUTS):
    fc += "[%d:v]trim=start_frame=%d:end_frame=%d,setpts=PTS-STARTPTS[v%d];" % (src, a, b, i)
fc += "".join("[v%d]" % i for i in range(len(CUTS))) + "concat=n=%d:v=1:a=0[out]" % len(CUTS)

dec_cmd = ["ffmpeg", "-v", "error"]
for s in SRCS: dec_cmd += ["-i", s]
dec_cmd += ["-filter_complex", fc, "-map", "[out]", "-f", "rawvideo", "-pix_fmt", "rgb24", "-"]

dec = sp.Popen(dec_cmd, stdout=sp.PIPE)
enc = sp.Popen(["ffmpeg", "-y", "-v", "error",
                "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", "%dx%d" % (W, H), "-r", str(FPS), "-i", "-",
                "-i", AUD, "-map", "0:v", "-map", "1:a",
                "-c:v", "libx264", "-preset", "slow", "-crf", "23", "-pix_fmt", "yuv420p",
                "-profile:v", "high", "-movflags", "+faststart",
                "-c:a", "aac", "-b:a", "128k", "-t", str(DUR), OUT], stdin=sp.PIPE)

BOUNDS, _acc = [], 0
for (_, a, b, r) in CUTS[:-1]:
    _acc += (b-a)*r; BOUNDS.append(_acc)

FRAME = W*H*3
out_i = 0; last = None
for src_i in range(N_SRC):
    raw = dec.stdout.read(FRAME)
    if len(raw) < FRAME: break
    a = np.frombuffer(raw, dtype=np.uint8).reshape(H, W, 3).astype(np.float32)
    gp = 0.50 if ISWIN[src_i] else 0.0
    base = Image.fromarray(grade(a, gp).astype(np.uint8))
    for _ in range(REPS[src_i]):
        t = out_i/float(FPS)
        img = base.copy()
        img.paste(INK_L, (0, 0), Image.eval(SCRIM, lambda v: int(v*0.9)))
        img.paste(INK_L, (0, 0), Image.eval(TOPSCRIM, lambda v: int(v*0.85)))
        img.paste(VIG_L, (0, 0), Image.eval(VIGN, lambda v: int(v*0.46)))
        for bfr in BOUNDS:
            kk = out_i - bfr
            if 0 <= kk < 4:
                img = Image.blend(img, Image.new("RGB", (W, H), GOLD_LT), (4-kk)/4.0*0.20)
        d = ImageDraw.Draw(img)
        marks(d); brandbar(d, eo(seg(t, .25, .95)))
        hud(d, t, eo(seg(t, .8, 1.6)))
        caption(d, t)
        fade_v = eio(seg(out_i, 0, 9))
        if fade_v < 1:
            img = Image.blend(Image.new("RGB", (W, H), (0, 0, 0)), img, max(0.0, fade_v))
        enc.stdin.write(img.tobytes())
        out_i += 1
        last = base
    if src_i % 40 == 0: print("src", src_i, "/", N_SRC, "out", out_i, flush=True)

for j in range(N_CARD):
    k = j/float(FPS)
    img = last.filter(ImageFilter.GaussianBlur(min(15, 3+k*12)))
    img = Image.blend(img, Image.new("RGB", (W, H), INK), min(.76, .30+k*.32))
    img.paste(VIG_L, (0, 0), Image.eval(VIGN, lambda v: int(v*0.46)))
    d = ImageDraw.Draw(img)
    marks(d); brandbar(d, 1.0); card(d, k)
    f = 1 - seg(j, N_CARD-7, N_CARD)
    if f < 1: img = Image.blend(Image.new("RGB", (W, H), (0, 0, 0)), img, max(0.0, f))
    enc.stdin.write(img.tobytes())

enc.stdin.close(); enc.wait(); dec.wait()
print("done", OUT, round(DUR, 2), "s")
