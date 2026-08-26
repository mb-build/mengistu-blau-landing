# סרטון פתיחה מאויר למנגיסטו בלאו — ארבע סצנות עם דמויות.
# מצויר פרוצדורלית ב-Pillow. הכיווניות של העברית מטופלת ידנית (אין raqm).
import math, os
from PIL import Image, ImageDraw, ImageFont

W, H, FPS = 1920, 1080, 30
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "frames3")

INK      = (11, 18, 32)
INK_UP   = (26, 34, 52)
CANVAS   = (247, 245, 240)
GOLD     = (180, 137, 43)
GOLD_LT  = (210, 186, 132)
GOLD_PALE= (237, 229, 210)
GOLD_DK  = (112, 89, 39)
MUTED    = (101, 104, 111)
SKIN     = (222, 199, 170)
SKIN_2   = (176, 140, 108)

FDIR = "C:/Windows/Fonts/"
def font(px, bold=True):
    for n in (("arialbd.ttf",) if bold else ("arial.ttf",)):
        p = FDIR + n
        if os.path.exists(p): return ImageFont.truetype(p, px)
    raise SystemExit("no font")

f_big  = font(104); f_mid = font(58); f_small = font(30, False)
f_tiny = font(24, False); f_brand = font(46); f_role = font(20, False)
f_mono = font(44)

def _heb(c): return "\u0590" <= c <= "\u05FF"
def rtl(s):
    """\u05E1\u05D9\u05D3\u05D5\u05E8 \u05DC\u05EA\u05E6\u05D5\u05D2\u05D4 \u05DE\u05D9\u05DC\u05D4\u05BE\u05DE\u05D9\u05DC\u05D4: \u05E1\u05D3\u05E8 \u05D4\u05DE\u05D9\u05DC\u05D9\u05DD \u05DE\u05EA\u05D4\u05E4\u05DA, \u05D5\u05DE\u05D9\u05DC\u05D4 \u05E2\u05D1\u05E8\u05D9\u05EA \u05DE\u05EA\u05D4\u05E4\u05DB\u05EA \u05D1\u05EA\u05D5\u05DB\u05D4.
       \u05DE\u05E1\u05E4\u05E8\u05D9\u05DD \u05D5\u05DC\u05D8\u05D9\u05E0\u05D9\u05EA \u05E0\u05E9\u05D0\u05E8\u05D9\u05DD \u05DB\u05DE\u05D5 \u05E9\u05D4\u05DD, \u05D5\u05D4\u05E8\u05D5\u05D5\u05D7\u05D9\u05DD \u05E0\u05E9\u05DE\u05E8\u05D9\u05DD."""
    words = s.split(" ")
    out = []
    for w in reversed(words):
        out.append(w[::-1] if any(_heb(c) for c in w) else w)
    return " ".join(out)

def ease_out(t): return 1 - (1 - t) ** 3
def ease_io(t):  return 4*t*t*t if t < .5 else 1 - (-2*t + 2) ** 3 / 2
def seg(t, a, b):
    if t <= a: return 0.0
    if t >= b: return 1.0
    return (t - a) / float(b - a)
def mix(c1, c2, a): return tuple(int(c2[i] + (c1[i]-c2[i]) * a) for i in range(3))

def txt(d, xy, s, fnt, fill, ls=0, right=False, center=False):
    s = rtl(s)
    if ls:
        total = sum(d.textlength(c, font=fnt) + ls for c in s) - ls
    else:
        total = d.textlength(s, font=fnt)
    x = xy[0] - total if right else (xy[0] - total/2 if center else xy[0])
    if ls:
        for c in s:
            d.text((x, xy[1]), c, font=fnt, fill=fill); x += d.textlength(c, font=fnt) + ls
    else:
        d.text((x, xy[1]), s, font=fnt, fill=fill)
    return total

# ---------------- דמויות ----------------
def narc(d, x0, y0, x1, y1, st, en, fill, width):
    d.arc([min(x0, x1), min(y0, y1), max(x0, x1), max(y0, y1)], st, en, fill=fill, width=width)

def head(d, cx, cy, r, skin, hair, hair_style="short", a=1.0, face=0):
    """face=0 חזית, 1 פרופיל ימינה, -1 פרופיל שמאלה."""
    sk = mix(skin, INK, a)
    d.ellipse([cx-r, cy-r, cx+r, cy+r], fill=sk)
    ink = mix((28, 24, 20), skin, a*0.9)
    if face == 0:
        for sx in (-1, 1):
            d.ellipse([cx+sx*r*0.36-r*0.085, cy-r*0.10, cx+sx*r*0.36+r*0.085, cy+r*0.10], fill=ink)
            d.line([(cx+sx*r*0.52, cy-r*0.34), (cx+sx*r*0.20, cy-r*0.30)],
                   fill=ink, width=max(1, int(r*0.075)))
        d.arc([cx-r*0.30, cy+r*0.14, cx+r*0.30, cy+r*0.56], 20, 160,
              fill=ink, width=max(1, int(r*0.085)))
    else:
        ex = cx + face*r*0.30
        d.ellipse([ex-r*0.085, cy-r*0.10, ex+r*0.085, cy+r*0.10], fill=ink)
        d.line([(ex+face*r*0.20, cy-r*0.34), (ex-face*r*0.14, cy-r*0.30)],
               fill=ink, width=max(1, int(r*0.075)))
        d.polygon([(cx+face*r*0.62, cy+r*0.02), (cx+face*r*0.94, cy+r*0.20),
                   (cx+face*r*0.60, cy+r*0.24)], fill=sk)
        narc(d, cx+face*r*0.10, cy+r*0.24, cx+face*r*0.70, cy+r*0.60, 20, 160,
             ink, max(1, int(r*0.085)))
    hc = mix(hair, INK, a)
    if hair_style == "short":
        d.pieslice([cx-r, cy-r, cx+r, cy+r], 180, 360, fill=hc)
        d.rectangle([cx-r, cy-r*0.28, cx-r*0.72, cy+r*0.14], fill=hc)
        d.rectangle([cx+r*0.72, cy-r*0.28, cx+r, cy+r*0.14], fill=hc)
    elif hair_style == "bun":
        d.pieslice([cx-r, cy-r, cx+r, cy+r], 180, 360, fill=hc)
        d.ellipse([cx-r*0.34, cy-r*1.62, cx+r*0.34, cy-r*0.94], fill=hc)
    else:
        d.pieslice([cx-r, cy-r*1.02, cx+r, cy+r*0.5], 195, 345, fill=hc)

def shadow(d, cx, y, w, a=1.0):
    """צל רך על הרצפה — מקרקע את הדמות."""
    for k, sc in enumerate((1.0, 0.72, 0.46)):
        d.ellipse([cx-w*sc/2, y-w*sc*0.10, cx+w*sc/2, y+w*sc*0.10],
                  fill=mix((4, 7, 14), INK_UP, a*(0.16+k*0.10)))

def torso(d, cx, top, w, h, col, a=1.0):
    c = mix(col, INK, a)
    d.polygon([(cx-w/2, top+h), (cx-w*0.44, top+h*0.10), (cx-w*0.30, top),
               (cx+w*0.30, top), (cx+w*0.44, top+h*0.10), (cx+w/2, top+h)], fill=c)

def arm(d, x0, y0, x1, y1, thick, col, a=1.0):
    c = mix(col, INK, a)
    d.line([(x0, y0), (x1, y1)], fill=c, width=thick)
    r = thick/2
    d.ellipse([x1-r, y1-r, x1+r, y1+r], fill=c)

def person_standing(d, cx, base, h, shirt, hair, hair_style="short",
                    skin=SKIN, a=1.0, arm_pose=0.0, tie=False, breath=0.0):
    shadow(d, cx, base+h*0.012, h*0.34, a)
    hr = h*0.088
    hip = base - h*0.44
    d.rectangle([cx-h*0.055, hip, cx-h*0.006, base], fill=mix(INK_UP, INK, a))
    d.rectangle([cx+h*0.006, hip, cx+h*0.055, base], fill=mix(INK_UP, INK, a))
    d.ellipse([cx-h*0.062, base-h*0.022, cx-h*0.0, base+h*0.012], fill=mix(GOLD_DK, INK, a))
    d.ellipse([cx+h*0.0, base-h*0.022, cx+h*0.062, base+h*0.012], fill=mix(GOLD_DK, INK, a))
    tw, th = h*0.30, h*0.34
    torso(d, cx, hip-th, tw, th, shirt, a)
    sy = hip-th+h*0.045
    ax = h*0.16 + arm_pose*h*0.07
    arm(d, cx-tw*0.44, sy, cx-ax, hip-h*0.02, int(h*0.055), shirt, a)
    arm(d, cx+tw*0.44, sy, cx+ax, hip-h*0.02, int(h*0.055), shirt, a)
    d.ellipse([cx-ax-h*0.028, hip-h*0.05, cx-ax+h*0.028, hip+h*0.006], fill=mix(skin, INK, a))
    d.ellipse([cx+ax-h*0.028, hip-h*0.05, cx+ax+h*0.028, hip+h*0.006], fill=mix(skin, INK, a))
    if tie:
        d.polygon([(cx, hip-th), (cx-h*0.020, hip-th+h*0.05), (cx, hip-th+h*0.20),
                   (cx+h*0.020, hip-th+h*0.05)], fill=mix(GOLD, INK, a))
    d.rectangle([cx-h*0.028, hip-th-h*0.035, cx+h*0.028, hip-th+h*0.012], fill=mix(skin, INK, a))
    head(d, cx, hip-th-h*0.035-hr+breath, hr, skin, (34, 30, 26), hair_style, a, 0)

def rect(d, x0, y0, x1, y1, fill):
    """מלבן שסובל קואורדינטות בכל סדר — נדרש לדמות שפונה שמאלה."""
    d.rectangle([min(x0, x1), min(y0, y1), max(x0, x1), max(y0, y1)], fill=fill)

def person_seated(d, cx, seat_y, h, shirt, hair, hair_style="short",
                  face=1, skin=SKIN, a=1.0, lean=0.0, breath=0.0):
    """יושב בפרופיל. face=1 פונה ימינה, face=-1 שמאלה."""
    shadow(d, cx, seat_y+h*0.055, h*0.30, a)
    hr = h*0.088
    tw, th = h*0.30, h*0.32
    top = seat_y - th
    rect(d, cx-h*0.05, seat_y, cx+h*0.05, seat_y+h*0.045, mix(INK_UP, INK, a))
    rect(d, cx+face*h*0.02, seat_y, cx+face*h*0.20, seat_y+h*0.055, mix(INK_UP, INK, a))
    rect(d, cx+face*h*0.16, seat_y+h*0.02, cx+face*h*0.21, seat_y+h*0.24, mix(INK_UP, INK, a))
    lx = cx + face*lean*h*0.05
    torso(d, lx, top, tw, th, shirt, a)
    sy = top + h*0.05
    hx = lx + face*h*0.19
    arm(d, lx + face*tw*0.30, sy, hx, seat_y - h*0.02, int(h*0.055), shirt, a)
    d.ellipse([hx-h*0.026, seat_y-h*0.05, hx+h*0.026, seat_y+h*0.002], fill=mix(skin, INK, a))
    rect(d, lx-h*0.026, top-h*0.032, lx+h*0.026, top+h*0.012, mix(skin, INK, a))
    hcx = lx + face*h*0.012
    head(d, hcx, top-h*0.032-hr+breath, hr, skin, (34, 30, 26), hair_style, a, face)

# ---------------- אביזרים ----------------
def bubble(d, cx, cy, w, h, col, tail_dir=1, a=1.0, txt_s=None, fnt=None, tcol=None):
    c = mix(col, INK, a)
    d.rounded_rectangle([cx-w/2, cy-h/2, cx+w/2, cy+h/2], radius=h*0.34, fill=c)
    d.polygon([(cx+tail_dir*w*0.16, cy+h/2-2), (cx+tail_dir*w*0.30, cy+h/2+h*0.34),
               (cx+tail_dir*w*0.02, cy+h/2-2)], fill=c)
    if txt_s and a > .5:
        txt(d, (cx, cy-fnt.size*0.62), txt_s, fnt, mix(tcol, c, (a-.5)/.5), center=True)

def sheet(d, cx, cy, w, h, a=1.0, lines=5, gold_line=True):
    d.rectangle([cx-w/2, cy-h/2, cx+w/2, cy+h/2], fill=mix(CANVAS, INK, a))
    for k in range(lines):
        y = cy-h/2 + h*(0.18 + k*0.145)
        ww = w*(0.66 if k % 3 else 0.46)
        d.rounded_rectangle([cx-w/2+w*0.11, y, cx-w/2+w*0.11+ww, y+h*0.035],
                            radius=h*0.018, fill=mix(MUTED, CANVAS, a*0.55))
    if gold_line:
        pts = [(cx-w*0.32, cy+h*0.30), (cx-w*0.12, cy+h*0.18),
               (cx+w*0.08, cy+h*0.23), (cx+w*0.32, cy+h*0.03)]
        d.line(pts, fill=mix(GOLD, CANVAS, a), width=max(2, int(h*0.022)), joint="curve")

def coin_stack(d, cx, base, n, rise, rw=104, rh=36, thick=13):
    shown = n * rise
    for i in range(n):
        k = shown - i
        if k <= 0: break
        a = min(1.0, k)
        y = base - i*thick - (1-ease_out(a))*20
        d.ellipse([cx-rw/2, y-rh/2+5, cx+rw/2, y+rh/2+5], fill=mix(GOLD_DK, INK, a))
        d.ellipse([cx-rw/2, y-rh/2, cx+rw/2, y+rh/2], fill=mix(GOLD, INK, a))
        d.ellipse([cx-rw/2+14, y-rh/2+5, cx-rw/2+48, y-rh/2+15], fill=mix(GOLD_PALE, GOLD, a*0.5))

def arrow(d, x0, y0, ang, ln, col, a=1.0, wdt=7):
    c = mix(col, INK, a)
    x1 = x0 + math.cos(ang)*ln; y1 = y0 + math.sin(ang)*ln
    d.line([(x0, y0), (x1, y1)], fill=c, width=wdt)
    hl = 26
    for s in (2.5, -2.5):
        d.line([(x1, y1), (x1+math.cos(ang+s)*hl, y1+math.sin(ang+s)*hl)], fill=c, width=wdt)

FLOOR = int(H*0.80)          # קו הרצפה — הטקסט מעליו, האיור מתחתיו

def room(img, warm=0.5):
    d = ImageDraw.Draw(img)
    d.rectangle([0, 0, W, H], fill=INK)
    d.rectangle([0, FLOOR, W, H], fill=INK_UP)
    d.line([(0, FLOOR), (W, FLOOR)], fill=mix(GOLD_DK, INK_UP, .5), width=2)
    for x in range(0, W, 220):
        d.line([(x, int(H*0.10)), (x, FLOOR)], fill=mix(INK_UP, INK, .55), width=1)
    if warm:
        gl = Image.new("L", (96, 54), 0); px = gl.load()
        for y in range(54):
            for x in range(96):
                dx = (x-48)/40.0; dy = (y-40)/30.0
                v = max(0.0, 1.0 - math.sqrt(dx*dx+dy*dy))
                px[x, y] = int(255*(v**1.9)*warm)
        img.paste(Image.new("RGB", (W, H), GOLD), (0, 0), gl.resize((W, H), Image.BICUBIC))

def frame_marks(d, a=0.45):
    L, ins = 34, 54
    c = mix(GOLD_LT, INK, a)
    for (x, y, sx, sy) in ((ins, ins, 1, 1), (W-ins, ins, -1, 1),
                           (ins, H-ins, 1, -1), (W-ins, H-ins, -1, -1)):
        d.line([(x, y), (x+L*sx, y)], fill=c, width=2)
        d.line([(x, y), (x, y+L*sy)], fill=c, width=2)

def brandbar(d, a=1.0):
    ccx, ccy, r = W-190, 88, 42
    d.ellipse([ccx-r, ccy-r, ccx+r, ccy+r], fill=mix(GOLD, INK, a))
    m = rtl("מב"); bb = d.textbbox((0, 0), m, font=f_mono)
    d.text((ccx-(bb[2]-bb[0])/2-bb[0], ccy-(bb[3]-bb[1])/2-bb[1]), m, font=f_mono, fill=mix(INK, GOLD, a))
    txt(d, (W-252, 58), "מנגיסטו בלאו", f_brand, mix(CANVAS, INK, a), right=True)
    txt(d, (W-252, 110), "ייעוץ וליווי השקעות", f_role, mix(GOLD_LT, INK, a*.85), ls=5, right=True)

# ---------------- סצנות ----------------
TX = W - 140          # קצה ימני לטקסט
TY1, TY2 = 250, 392   # כותרת ומשנה — מעל קו הרצפה, לא נוגעות באיור

def caption(d, t, a0, title, sub):
    a = ease_out(seg(t, a0, a0+.7))
    if a <= 0: return
    txt(d, (TX, TY1), title, f_big, mix(CANVAS, INK, a), right=True)
    txt(d, (TX, TY2), sub, f_mid, mix(MUTED, INK, a), right=True)

def s1(t):
    """הבלבול — אדם מוקף בעצות סותרות."""
    img = Image.new("RGB", (W, H)); room(img, .26)
    d = ImageDraw.Draw(img)
    frame_marks(d); brandbar(d, ease_out(seg(t, .1, .8)))
    cx, base = 400, H-70
    person_standing(d, cx, base, 540, CANVAS, None, "short", SKIN,
                    ease_out(seg(t, .15, .8)), arm_pose=.45, breath=math.sin(t*2.1)*2.2)
    labels = [("קרן השתלמות", -2.30), ("קריפטו", -1.92), ("נדל״ן", -1.54),
              ("מניות", -1.16), ("פיקדון", -0.78)]
    ox, oy = cx+265, base-350          # מחוץ לגוף, כדי שהחצים לא יחצו את הפנים
    for k, (s, ang) in enumerate(labels):
        a = ease_out(seg(t, .30 + k*.11, .70 + k*.11))
        if a <= 0: continue
        L = 170*a
        arrow(d, ox, oy, ang, L, GOLD_LT if k % 2 else GOLD, a*.8, 6)
        bx = ox + math.cos(ang)*(L+118); by = oy + math.sin(ang)*(L+118)
        bubble(d, bx, by, 232, 68, CANVAS, -1, a, s, f_small, INK)
    caption(d, t, 0.90, "יותר מדי כיוונים", "וכולם נשמעים משכנעים")
    return img

def s2(t):
    """הפגישה — יועץ ולקוח משני צדי שולחן."""
    img = Image.new("RGB", (W, H)); room(img, .5)
    d = ImageDraw.Draw(img)
    frame_marks(d); brandbar(d, 1)
    ty = FLOOR + 36
    td = ease_out(seg(t, .0, .55))
    if td > 0:
        half = 150 + 330*td
        rect(d, 760-half, ty-8, 760+half, ty+18, mix(GOLD_DK, INK, td))
        rect(d, 640, ty+18, 664, ty+150, mix(GOLD_DK, INK, td*.8))
        rect(d, 858, ty+18, 882, ty+150, mix(GOLD_DK, INK, td*.8))
    person_seated(d, 420, ty, 520, CANVAS, None, "short", 1, SKIN,
                  ease_out(seg(t, .1, .7)), lean=.5, breath=math.sin(t*2.0)*2.0)
    person_seated(d, 1105, ty, 520, GOLD_LT, None, "bun", -1, SKIN_2,
                  ease_out(seg(t, .26, .86)), lean=.5, breath=math.sin(t*2.0+1.4)*2.0)
    sa = ease_out(seg(t, .55, 1.05))
    if sa > 0: sheet(d, 760, ty-62, 196, 136, sa)
    caption(d, t, 0.95, "45 דקות של הקשבה", "לפני מילה אחת על השקעה")
    return img

def s3(t):
    """התוכנית — הלקוח מול הצמיחה."""
    img = Image.new("RGB", (W, H)); room(img, .58)
    d = ImageDraw.Draw(img)
    frame_marks(d); brandbar(d, 1)
    base = H-70
    sp = ease_out(seg(t, .30, 1.20))
    if sp > 0:
        pts = [(760, 806), (900, 762), (1040, 778), (1180, 700), (1320, 720), (1460, 630)]
        segs = len(pts)-1; total = sp*segs; drawn = [pts[0]]
        for i in range(segs):
            k = min(1.0, max(0.0, total-i))
            if k <= 0: break
            drawn.append((pts[i][0]+(pts[i+1][0]-pts[i][0])*k,
                          pts[i][1]+(pts[i+1][1]-pts[i][1])*k))
        if len(drawn) > 1: d.line(drawn, fill=GOLD, width=6, joint="curve")
        hx, hy = drawn[-1]; d.ellipse([hx-11, hy-11, hx+11, hy+11], fill=GOLD_PALE)
    for cx, n, st in ((1130, 4, .10), (1330, 7, .26), (1530, 11, .42)):
        r = ease_out(seg(t, st, st+.6))
        if r > 0: coin_stack(d, cx, base-20, n, r)
    person_standing(d, 400, base, 540, CANVAS, None, "short", SKIN,
                    ease_out(seg(t, .05, .7)), arm_pose=.12, tie=True, breath=math.sin(t*2.1)*2.2)
    caption(d, t, 0.95, "תוכנית אחת. ברורה.", "מותאמת לך, לא לתבנית")
    return img

def s4(t):
    """סגירה — נעילת מותג."""
    img = Image.new("RGB", (W, H)); room(img, .72)
    d = ImageDraw.Draw(img)
    frame_marks(d)
    for cx, n, st in ((300, 4, .5), (452, 7, .62), (604, 11, .74)):
        r = ease_out(seg(t, st, st+.5))
        if r > 0: coin_stack(d, cx, H-88, n, r, rw=84, rh=29, thick=11)
    for cx, n, st in ((1316, 11, .74), (1468, 7, .62), (1620, 4, .5)):
        r = ease_out(seg(t, st, st+.5))
        if r > 0: coin_stack(d, cx, H-88, n, r, rw=84, rh=29, thick=11)
    a = ease_out(seg(t, .05, .7))
    ccx, ccy, r = W//2, 300, 92*a
    d.ellipse([ccx-r, ccy-r, ccx+r, ccy+r], fill=mix(GOLD, INK, a))
    if a > .55:
        big = font(96); m = rtl("מב"); bb = d.textbbox((0, 0), m, font=big)
        d.text((ccx-(bb[2]-bb[0])/2-bb[0], ccy-(bb[3]-bb[1])/2-bb[1]), m, font=big,
               fill=mix(INK, GOLD, (a-.55)/.45))
    b = ease_out(seg(t, .45, 1.1))
    if b > 0:
        txt(d, (W//2, 440), "מנגיסטו בלאו", f_big, mix(CANVAS, INK, b), center=True)
        txt(d, (W//2, 574), "ייעוץ וליווי השקעות", f_mid, mix(GOLD_LT, INK, b*.9), ls=8, center=True)
    c = ease_out(seg(t, 1.0, 1.6))
    if c > 0:
        label = "לשיחת אבחון ללא עלות"
        tw = sum(d.textlength(ch, font=f_mid) for ch in rtl(label))
        pw, ph = tw+120, 104
        d.rounded_rectangle([W//2-pw/2, 690, W//2+pw/2, 690+ph], radius=ph/2, fill=mix(GOLD, INK, c))
        if c > .6: txt(d, (W//2, 716), label, f_mid, mix(INK, GOLD, (c-.6)/.4), center=True)
    return img

SCENES = [(s1, 2.5), (s2, 2.5), (s3, 2.5), (s4, 2.2)]
XF = 0.38
TOTAL = sum(s[1] for s in SCENES)
N = int(FPS*TOTAL)

def compose(tg):
    acc = 0.0
    for i, (fn, dur) in enumerate(SCENES):
        if tg < acc + dur or i == len(SCENES)-1:
            lt = tg - acc
            img = fn(min(lt, dur))
            if i+1 < len(SCENES) and lt > dur-XF:
                k = ease_io((lt-(dur-XF))/XF)
                img = Image.blend(img, SCENES[i+1][0](0.0), k)
            return img
        acc += dur
    return SCENES[-1][0](SCENES[-1][1])

os.makedirs(OUT, exist_ok=True)
for i in range(N):
    tg = i/float(FPS)
    img = compose(tg)
    k = 0.012 + 0.030 * (tg / TOTAL)          # דחיפה איטית פנימה
    dx, dy = int(W*k), int(H*k)
    img = img.crop((dx, dy, W-dx, H-dy)).resize((W, H), Image.LANCZOS)
    fade = min(ease_io(seg(i, 0, 10)), 1-seg(i, N-12, N))
    if fade < 1:
        img = Image.blend(Image.new("RGB", (W, H), (0, 0, 0)), img, max(0.0, fade))
    img.save(os.path.join(OUT, "f%04d.png" % i))
    if i % 30 == 0: print("frame", i, "/", N, flush=True)
print("done", N)
