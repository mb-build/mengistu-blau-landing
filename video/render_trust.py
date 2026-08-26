# סרטון פתיחה למנגיסטו בלאו — קשת של אמון: ספק, הקשבה, בהירות, לחיצת יד.
# דרמה נבנית מתאורת מפתח חמה, רים־לייט זהב על הדמויות, ווינייטה ועומק.
import math, os
from PIL import Image, ImageDraw, ImageFont, ImageFilter

W, H, FPS = 1920, 1080, 30
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "frames_trust")

INK      = (11, 18, 32)
INK_UP   = (20, 27, 42)
NAVY     = (30, 38, 58)      # חליפה
NAVY_DK  = (18, 24, 38)
SHIRT    = (238, 236, 231)
CANVAS   = (247, 245, 240)
GOLD     = (180, 137, 43)
GOLD_LT  = (210, 186, 132)
GOLD_PALE= (237, 229, 210)
GOLD_DK  = (112, 89, 39)
MUTED    = (120, 124, 132)
SKIN_A   = (214, 186, 154)
SKIN_B   = (166, 128, 96)
HAIR_A   = (32, 27, 23)
HAIR_B   = (46, 36, 28)

FDIR = "C:/Windows/Fonts/"
def font(px, bold=True):
    p = FDIR + ("arialbd.ttf" if bold else "arial.ttf")
    return ImageFont.truetype(p, px)

f_big = font(96); f_mid = font(50); f_sm = font(28, False)
f_brand = font(44); f_role = font(19, False); f_mono = font(42)

def _heb(c): return "֐" <= c <= "׿"
def rtl(s):
    return " ".join((w[::-1] if any(_heb(c) for c in w) else w) for w in reversed(s.split(" ")))

def eo(t): return 1 - (1-t)**3
def eio(t): return 4*t*t*t if t < .5 else 1 - (-2*t+2)**3/2
def seg(t, a, b):
    if t <= a: return 0.0
    if t >= b: return 1.0
    return (t-a)/float(b-a)
def mix(c1, c2, a): return tuple(int(c2[i] + (c1[i]-c2[i])*a) for i in range(3))

def txt(d, xy, s, fnt, fill, ls=0, right=False, center=False):
    s = rtl(s)
    total = (sum(d.textlength(c, font=fnt)+ls for c in s)-ls) if ls else d.textlength(s, font=fnt)
    x = xy[0]-total if right else (xy[0]-total/2 if center else xy[0])
    if ls:
        for c in s:
            d.text((x, xy[1]), c, font=fnt, fill=fill); x += d.textlength(c, font=fnt)+ls
    else:
        d.text((x, xy[1]), s, font=fnt, fill=fill)

def R(d, x0, y0, x1, y1, fill):
    d.rectangle([min(x0,x1), min(y0,y1), max(x0,x1), max(y0,y1)], fill=fill)

# ---------- אווירה ----------
def radial(size, cx, cy, rx, ry, power=1.8):
    sw, sh = 120, 68
    g = Image.new("L", (sw, sh), 0); px = g.load()
    for y in range(sh):
        for x in range(sw):
            dx = (x/sw - cx)/rx; dy = (y/sh - cy)/ry
            v = max(0.0, 1.0 - math.sqrt(dx*dx+dy*dy))
            px[x, y] = int(255*(v**power))
    return g.resize(size, Image.BICUBIC)

KEY   = radial((W, H), 0.50, 0.86, 0.40, 0.52, 1.7)   # תאורת מפתח חמה מלמטה
KEY_R = radial((W, H), 0.72, 0.42, 0.34, 0.46, 2.0)   # מקור צד ימני
VIG   = radial((W, H), 0.50, 0.50, 0.78, 0.86, 1.15)
VIGN  = Image.eval(VIG, lambda v: 255-v)

def stage(warm=0.42, side=0.0):
    img = Image.new("RGB", (W, H), INK)
    d = ImageDraw.Draw(img)
    d.rectangle([0, int(H*0.78), W, H], fill=INK_UP)
    for x in range(0, W, 260):
        d.line([(x, int(H*0.06)), (x, int(H*0.78))], fill=mix(INK_UP, INK, .5), width=1)
    if warm:
        img.paste(Image.new("RGB", (W, H), GOLD), (0, 0), Image.eval(KEY, lambda v: int(v*warm)))
    if side:
        img.paste(Image.new("RGB", (W, H), GOLD_LT), (0, 0), Image.eval(KEY_R, lambda v: int(v*side)))
    return img

def finish(img, vig=0.55):
    img.paste(Image.new("RGB", (W, H), (0, 0, 0)), (0, 0), Image.eval(VIGN, lambda v: int(v*vig)))
    return img

def with_rim(base, fn, dx=-7, dy=-5, col=GOLD_LT, strength=210):
    """מצייר דמות על שכבה, ומדביק מתחתיה עותק זהב מוסט — קו אור על הקצה."""
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    fn(ImageDraw.Draw(layer))
    a = layer.getchannel("A")
    glow = Image.new("RGBA", (W, H), col + (0,))
    glow.putalpha(a.point(lambda v: int(v*strength/255)))
    base.paste(glow, (dx, dy), glow)
    base.paste(layer, (0, 0), layer)

def shadow(d, cx, y, w, a=1.0):
    for k, sc in enumerate((1.0, 0.70, 0.44)):
        d.ellipse([cx-w*sc/2, y-w*sc*0.11, cx+w*sc/2, y+w*sc*0.11],
                  fill=(2, 4, 9, int(255*a*(0.20+k*0.13))))

# ---------- דמות בחליפה ----------
def face(d, cx, cy, r, skin, hair, style, glasses, a, prof=0):
    sk = skin + (int(255*a),)
    d.ellipse([cx-r, cy-r, cx+r, cy+r], fill=sk)
    ink = (26, 22, 18, int(235*a))
    if prof == 0:
        for s in (-1, 1):
            d.ellipse([cx+s*r*.34-r*.075, cy-r*.06, cx+s*r*.34+r*.075, cy+r*.12], fill=ink)
            d.line([(cx+s*r*.52, cy-r*.32), (cx+s*r*.18, cy-r*.27)], fill=ink, width=max(1, int(r*.07)))
        d.arc([cx-r*.28, cy+r*.16, cx+r*.28, cy+r*.54], 18, 162, fill=ink, width=max(1, int(r*.08)))
    else:
        ex = cx+prof*r*.28
        d.ellipse([ex-r*.075, cy-r*.06, ex+r*.075, cy+r*.12], fill=ink)
        d.line([(ex+prof*r*.20, cy-r*.32), (ex-prof*r*.12, cy-r*.27)], fill=ink, width=max(1, int(r*.07)))
        d.polygon([(cx+prof*r*.60, cy+r*.00), (cx+prof*r*.96, cy+r*.20), (cx+prof*r*.58, cy+r*.24)], fill=sk)
        x0, x1 = sorted([cx+prof*r*.08, cx+prof*r*.66])
        d.arc([x0, cy+r*.26, x1, cy+r*.58], 18, 162, fill=ink, width=max(1, int(r*.08)))
    hc = hair + (int(255*a),)
    if style == "short":
        d.pieslice([cx-r, cy-r, cx+r, cy+r], 180, 360, fill=hc)
        R(d, cx-r, cy-r*.26, cx-r*.70, cy+r*.16, hc); R(d, cx+r*.70, cy-r*.26, cx+r, cy+r*.16, hc)
    elif style == "bun":
        d.pieslice([cx-r, cy-r, cx+r, cy+r], 180, 360, fill=hc)
        d.ellipse([cx-r*.32, cy-r*1.60, cx+r*.32, cy-r*.92], fill=hc)
    else:
        d.pieslice([cx-r, cy-r*1.04, cx+r, cy+r*.44], 196, 344, fill=hc)
    if glasses:
        g = GOLD_LT + (int(230*a),)
        wdt = max(2, int(r*.07))
        if prof == 0:
            for s in (-1, 1):
                d.ellipse([cx+s*r*.34-r*.24, cy-r*.20, cx+s*r*.34+r*.24, cy+r*.26], outline=g, width=wdt)
            d.line([(cx-r*.10, cy+r*.03), (cx+r*.10, cy+r*.03)], fill=g, width=wdt)
        else:
            ex = cx+prof*r*.28
            d.ellipse([ex-r*.26, cy-r*.20, ex+r*.26, cy+r*.26], outline=g, width=wdt)
            d.line([(ex-prof*r*.26, cy+r*.03), (cx-prof*r*.55, cy-r*.06)], fill=g, width=wdt)

def suit_front(d, cx, base, h, a=1.0, skin=SKIN_A, hair=HAIR_A, style="short",
               glasses=False, tie=GOLD, breath=0.0, gesture=0.0, reach=None):
    A = int(255*a)
    hr = h*.086
    hip = base - h*.46
    shadow(d, cx, base+h*.014, h*.36, a)
    R(d, cx-h*.058, hip, cx-h*.007, base, NAVY_DK+(A,))
    R(d, cx+h*.007, hip, cx+h*.058, base, NAVY_DK+(A,))
    d.ellipse([cx-h*.066, base-h*.020, cx-h*.002, base+h*.014], fill=(14, 12, 10, A))
    d.ellipse([cx+h*.002, base-h*.020, cx+h*.066, base+h*.014], fill=(14, 12, 10, A))
    tw, th = h*.33, h*.36
    top = hip-th+breath*0.4
    # חולצה מתחת לחליפה
    d.polygon([(cx-tw*.30, top), (cx+tw*.30, top), (cx+tw*.26, top+th*.62), (cx-tw*.26, top+th*.62)],
              fill=SHIRT+(A,))
    # עניבה
    if tie:
        d.polygon([(cx, top+h*.012), (cx-h*.021, top+h*.055), (cx, top+h*.215),
                   (cx+h*.021, top+h*.055)], fill=tie+(A,))
    # מקטורן — שתי דשים
    for s in (-1, 1):
        d.polygon([(cx+s*tw*.50, top+th), (cx+s*tw*.46, top+th*.09), (cx+s*tw*.30, top),
                   (cx+s*tw*.10, top+th*.30), (cx+s*tw*.17, top+th)], fill=NAVY+(A,))
        d.polygon([(cx+s*tw*.30, top), (cx+s*tw*.10, top+th*.30), (cx+s*tw*.20, top+th*.34)],
                  fill=mix(NAVY, CANVAS, .82)+(A,))
    sy = top+h*.055
    ax = h*.175 + gesture*h*.055
    ay = hip - h*.03 - gesture*h*.10
    for s in (-1, 1):
        shx, shy = cx+s*tw*.44, sy
        rx, ry = cx+s*ax, ay
        if reach and ((reach[0] > cx) == (s > 0)):
            rx, ry = reach                      # הזרוע הפנימית מושטת ללחיצה
        d.line([(shx, shy), (rx, ry)], fill=NAVY+(A,), width=int(h*.058))
        # שרוול חולצה לאורך הזרוע, לא כתם מרחף
        vx, vy = shx-rx, shy-ry
        vl = max(1.0, math.hypot(vx, vy)); vx, vy = vx/vl, vy/vl
        cxx, cyy = rx+vx*h*.036, ry+vy*h*.036
        d.line([(cxx, cyy), (cxx+vx*h*.022, cyy+vy*h*.022)], fill=SHIRT+(A,), width=int(h*.052))
        d.ellipse([rx-h*.028, ry-h*.028, rx+h*.028, ry+h*.028], fill=skin+(A,))
    R(d, cx-h*.026, top-h*.034, cx+h*.026, top+h*.012, skin+(A,))
    face(d, cx, top-h*.034-hr+breath, hr, skin, hair, style, glasses, a, 0)

def suit_seated(d, cx, seat, h, a=1.0, prof=1, skin=SKIN_A, hair=HAIR_A, style="short",
                glasses=False, tie=GOLD, breath=0.0, lean=.5):
    A = int(255*a)
    hr = h*.086
    tw, th = h*.33, h*.34
    top = seat-th+breath*0.4
    shadow(d, cx, seat+h*.06, h*.32, a)
    R(d, cx-h*.05, seat, cx+h*.05, seat+h*.05, NAVY_DK+(A,))
    R(d, cx+prof*h*.02, seat, cx+prof*h*.21, seat+h*.06, NAVY_DK+(A,))
    R(d, cx+prof*h*.17, seat+h*.02, cx+prof*h*.22, seat+h*.26, NAVY_DK+(A,))
    lx = cx+prof*lean*h*.05
    d.polygon([(lx-tw*.28, top), (lx+tw*.28, top), (lx+tw*.24, top+th*.60), (lx-tw*.24, top+th*.60)],
              fill=SHIRT+(A,))
    if tie:
        d.polygon([(lx, top+h*.012), (lx-h*.019, top+h*.05), (lx, top+h*.19),
                   (lx+h*.019, top+h*.05)], fill=tie+(A,))
    d.polygon([(lx-tw*.50, top+th), (lx-tw*.44, top+th*.08), (lx-tw*.26, top),
               (lx+tw*.26, top), (lx+tw*.44, top+th*.08), (lx+tw*.50, top+th)], fill=NAVY+(A,))
    hx = lx+prof*h*.20
    d.line([(lx+prof*tw*.28, top+h*.055), (hx, seat-h*.03)], fill=NAVY+(A,), width=int(h*.058))
    d.ellipse([hx-h*.028, seat-h*.058, hx+h*.028, seat-h*.002], fill=skin+(A,))
    R(d, lx-h*.026, top-h*.032, lx+h*.026, top+h*.012, skin+(A,))
    face(d, lx+prof*h*.012, top-h*.032-hr+breath, hr, skin, hair, style, glasses, a, prof)

# ---------- אביזרים ----------
def certificates(d, x, y, a=1.0, n=3):
    A = int(255*a)
    for k in range(n):
        cx = x + k*128
        R(d, cx, y, cx+96, y+124, mix(INK_UP, INK, .8)+(A,))
        d.rectangle([cx, y, cx+96, y+124], outline=GOLD_DK+(A,), width=3)
        for r in range(3):
            R(d, cx+18, y+34+r*20, cx+78, y+40+r*20, mix(MUTED, INK_UP, .45)+(A,))
        d.ellipse([cx+34, y+88, cx+62, y+114], fill=GOLD+(int(A*.75),))

def desk(d, cx, y, half, a=1.0):
    A = int(255*a)
    R(d, cx-half, y-9, cx+half, y+19, GOLD_DK+(A,))
    R(d, cx-half, y+19, cx+half, y+27, mix(GOLD_DK, INK, .55)+(A,))
    R(d, cx-half*.72, y+27, cx-half*.66, y+165, mix(GOLD_DK, INK, .7)+(A,))
    R(d, cx+half*.66, y+27, cx+half*.72, y+165, mix(GOLD_DK, INK, .7)+(A,))

def laptop(d, cx, y, a=1.0):
    A = int(255*a)
    d.polygon([(cx-64, y), (cx+64, y), (cx+52, y-72), (cx-52, y-72)], fill=NAVY_DK+(A,))
    d.polygon([(cx-46, y-6), (cx+46, y-6), (cx+38, y-64), (cx-38, y-64)], fill=mix(GOLD, INK, .35)+(A,))
    R(d, cx-74, y, cx+74, y+9, mix(NAVY, INK, .8)+(A,))

def plan_sheet(d, cx, cy, w, h, a=1.0):
    A = int(255*a)
    R(d, cx-w/2, cy-h/2, cx+w/2, cy+h/2, CANVAS+(A,))
    for k in range(4):
        yy = cy-h/2+h*(.19+k*.15)
        R(d, cx-w*.34, yy, cx-w*.34+w*(.60 if k % 2 else .40), yy+h*.036, mix(MUTED, CANVAS, .5)+(A,))
    pts = [(cx-w*.32, cy+h*.32), (cx-w*.10, cy+h*.20), (cx+w*.10, cy+h*.25), (cx+w*.32, cy+h*.05)]
    d.line(pts, fill=GOLD+(A,), width=max(2, int(h*.026)), joint="curve")

def coins(d, cx, base, n, rise, rw=100, rh=34, th=13):
    shown = n*rise
    for i in range(n):
        k = shown-i
        if k <= 0: break
        a = min(1.0, k); A = int(255*a)
        y = base-i*th-(1-eo(a))*18
        d.ellipse([cx-rw/2, y-rh/2+5, cx+rw/2, y+rh/2+5], fill=GOLD_DK+(A,))
        d.ellipse([cx-rw/2, y-rh/2, cx+rw/2, y+rh/2], fill=GOLD+(A,))
        d.ellipse([cx-rw/2+13, y-rh/2+5, cx-rw/2+45, y-rh/2+14], fill=GOLD_PALE+(int(A*.55),))

def frame_marks(d, a=.42):
    L, ins = 34, 54
    c = mix(GOLD_LT, INK, a)
    for (x, y, sx, sy) in ((ins, ins, 1, 1), (W-ins, ins, -1, 1), (ins, H-ins, 1, -1), (W-ins, H-ins, -1, -1)):
        d.line([(x, y), (x+L*sx, y)], fill=c, width=2); d.line([(x, y), (x, y+L*sy)], fill=c, width=2)

def brandbar(d, a=1.0):
    ccx, ccy, r = W-186, 86, 40
    d.ellipse([ccx-r, ccy-r, ccx+r, ccy+r], fill=mix(GOLD, INK, a))
    m = rtl("מב"); bb = d.textbbox((0, 0), m, font=f_mono)
    d.text((ccx-(bb[2]-bb[0])/2-bb[0], ccy-(bb[3]-bb[1])/2-bb[1]), m, font=f_mono, fill=mix(INK, GOLD, a))
    txt(d, (W-244, 56), "מנגיסטו בלאו", f_brand, mix(CANVAS, INK, a), right=True)
    txt(d, (W-244, 106), "ייעוץ וליווי השקעות", f_role, mix(GOLD_LT, INK, a*.85), ls=5, right=True)

TX, TY1, TY2 = W-140, 236, 372
def caption(d, t, a0, title, sub):
    a = eo(seg(t, a0, a0+.75))
    if a <= 0: return
    txt(d, (TX, TY1), title, f_big, mix(CANVAS, INK, a), right=True)
    txt(d, (TX, TY2), sub, f_mid, mix(GOLD_LT, INK, a*.8), right=True)

# ---------- סצנות ----------
def sc_doubt(t):
    """לילה. אדם לבד מול מסך. ספק."""
    img = stage(.30, .10)
    d = ImageDraw.Draw(img); frame_marks(d); brandbar(d, eo(seg(t, .1, .8)))
    base = H-72
    a = eo(seg(t, .1, .8))
    with_rim(img, lambda L: (desk(L, 470, base-250, 300, a), laptop(L, 470, base-256, a)),
             -6, -4, GOLD_LT, 120)
    with_rim(img, lambda L: suit_seated(L, 300, base-250, 500, a, 1, SKIN_A, HAIR_A,
                                        "short", False, None, math.sin(t*1.7)*2.0, .35),
             -8, -5, GOLD_LT, 190)
    caption(d, t, .85, "מול המסך, לבד", "כל אפשרות נשמעת נכונה")
    return finish(img, .40)

def sc_meeting(t):
    """המשרד. שני אנשים, תעודות על הקיר, הקשבה."""
    img = stage(.62, .28)
    d = ImageDraw.Draw(img); frame_marks(d); brandbar(d, 1)
    cw = eo(seg(t, .05, .6))
    if cw > 0:
        cl = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        certificates(ImageDraw.Draw(cl), 250, 470, cw*.85)
        img.paste(cl, (0, 0), cl)
    seat = int(H*.78)+34
    dk = eo(seg(t, 0, .5))
    with_rim(img, lambda L: desk(L, 760, seat, 130+310*dk, dk), -6, -4, GOLD_LT, 130)
    with_rim(img, lambda L: suit_seated(L, 430, seat, 520, eo(seg(t, .12, .72)), 1,
                                        SKIN_A, HAIR_A, "short", False, GOLD,
                                        math.sin(t*1.9)*2.0, .55), -8, -5, GOLD_LT, 200)
    with_rim(img, lambda L: suit_seated(L, 1095, seat, 520, eo(seg(t, .26, .86)), -1,
                                        SKIN_B, HAIR_B, "bun", True, GOLD,
                                        math.sin(t*1.9+1.5)*2.0, .55), 8, -5, GOLD_LT, 200)
    sa = eo(seg(t, .55, 1.05))
    if sa > 0:
        pl = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        plan_sheet(ImageDraw.Draw(pl), 760, seat-58, 190, 132, sa)
        img.paste(pl, (0, 0), pl)
    caption(d, t, .95, "45 דקות של הקשבה", "לפני מילה אחת על השקעה")
    return finish(img, .32)

def sc_plan(t):
    """התוכנית — היועץ מציג, הצמיחה מאחור."""
    img = stage(.66, .30)
    d = ImageDraw.Draw(img); frame_marks(d); brandbar(d, 1)
    base = H-72
    sp = eo(seg(t, .2, 1.1))
    if sp > 0:
        pts = [(800, 800), (940, 756), (1080, 772), (1220, 692), (1360, 712), (1500, 618)]
        n = len(pts)-1; tot = sp*n; dr = [pts[0]]
        for i in range(n):
            k = min(1.0, max(0.0, tot-i))
            if k <= 0: break
            dr.append((pts[i][0]+(pts[i+1][0]-pts[i][0])*k, pts[i][1]+(pts[i+1][1]-pts[i][1])*k))
        if len(dr) > 1: d.line(dr, fill=GOLD, width=7, joint="curve")
        hx, hy = dr[-1]; d.ellipse([hx-12, hy-12, hx+12, hy+12], fill=GOLD_PALE)
    cl = Image.new("RGBA", (W, H), (0, 0, 0, 0)); cd = ImageDraw.Draw(cl)
    for cx, n, st in ((1180, 4, .06), (1360, 7, .22), (1540, 11, .38)):
        r = eo(seg(t, st, st+.55))
        if r > 0: coins(cd, cx, base-22, n, r)
    img.paste(cl, (0, 0), cl)
    with_rim(img, lambda L: suit_front(L, 430, base, 540, eo(seg(t, .05, .7)), SKIN_A, HAIR_A,
                                       "short", True, GOLD, math.sin(t*1.8)*2.2, gesture=.55),
             -9, -6, GOLD_LT, 215)
    caption(d, t, .95, "תוכנית אחת. ברורה.", "מותאמת לך, לא לתבנית")
    return finish(img, .32)

def sc_trust(t):
    """לחיצת היד — רגע האמון."""
    img = stage(.72, .34)
    d = ImageDraw.Draw(img); frame_marks(d); brandbar(d, 1)
    base = H-64
    a = eo(seg(t, .05, .6))
    g = eo(seg(t, .40, 1.05))
    HH = 580
    mid = (700+1220)/2.0
    my = base - HH*.40
    lr = (mid - 120*(1-g), my)          # יד ימין מתקרבת מהשמאלית
    rr = (mid + 120*(1-g), my)
    with_rim(img, lambda L: suit_front(L, 700, base, HH, a, SKIN_A, HAIR_A, "short",
                                       True, GOLD, math.sin(t*1.8)*2.0, gesture=.1, reach=lr),
             -9, -6, GOLD_LT, 225)
    with_rim(img, lambda L: suit_front(L, 1220, base, HH, a, SKIN_B, HAIR_B, "bun",
                                       False, GOLD, math.sin(t*1.8+1.4)*2.0, gesture=.1, reach=rr),
             9, -6, GOLD_LT, 225)
    if g > .55:
        k = (g-.55)/.45
        hl = Image.new("RGBA", (W, H), (0, 0, 0, 0)); hd = ImageDraw.Draw(hl)
        hd.ellipse([mid-56, my-40, mid+56, my+40], fill=SKIN_A+(255,))
        hd.ellipse([mid-34, my-30, mid+50, my+34], fill=SKIN_B+(240,))
        img.paste(hl, (0, 0), hl)
        gl = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        ImageDraw.Draw(gl).ellipse([mid-165, my-165, mid+165, my+165], fill=GOLD+(int(85*k),))
        gl = gl.filter(ImageFilter.GaussianBlur(46))
        img.paste(gl, (0, 0), gl)
    caption(d, t, .95, "כאן מתחיל האמון", "מלווה אחד, לאורך כל הדרך")
    return finish(img, .34)

def sc_brand(t):
    img = stage(.70, .26)
    d = ImageDraw.Draw(img); frame_marks(d)
    cl = Image.new("RGBA", (W, H), (0, 0, 0, 0)); cd = ImageDraw.Draw(cl)
    for cx, n, st in ((300, 4, .45), (452, 7, .56), (604, 11, .67)):
        r = eo(seg(t, st, st+.45))
        if r > 0: coins(cd, cx, H-86, n, r, 82, 28, 11)
    for cx, n, st in ((1316, 11, .67), (1468, 7, .56), (1620, 4, .45)):
        r = eo(seg(t, st, st+.45))
        if r > 0: coins(cd, cx, H-86, n, r, 82, 28, 11)
    img.paste(cl, (0, 0), cl)
    a = eo(seg(t, .05, .65))
    ccx, ccy, r = W//2, 300, 92*a
    d.ellipse([ccx-r, ccy-r, ccx+r, ccy+r], fill=mix(GOLD, INK, a))
    if a > .55:
        big = font(94); m = rtl("מב"); bb = d.textbbox((0, 0), m, font=big)
        d.text((ccx-(bb[2]-bb[0])/2-bb[0], ccy-(bb[3]-bb[1])/2-bb[1]), m, font=big,
               fill=mix(INK, GOLD, (a-.55)/.45))
    b = eo(seg(t, .4, 1.0))
    if b > 0:
        txt(d, (W//2, 442), "מנגיסטו בלאו", f_big, mix(CANVAS, INK, b), center=True)
        txt(d, (W//2, 572), "ייעוץ וליווי השקעות", f_mid, mix(GOLD_LT, INK, b*.9), ls=8, center=True)
    c = eo(seg(t, .85, 1.45))
    if c > 0:
        lab = "לשיחת אבחון ללא עלות"
        tw = sum(d.textlength(ch, font=f_mid) for ch in rtl(lab))
        pw, ph = tw+120, 100
        d.rounded_rectangle([W//2-pw/2, 690, W//2+pw/2, 690+ph], radius=ph/2, fill=mix(GOLD, INK, c))
        if c > .6: txt(d, (W//2, 714), lab, f_mid, mix(INK, GOLD, (c-.6)/.4), center=True)
    return finish(img, .30)

SCENES = [(sc_doubt, 2.3), (sc_meeting, 2.6), (sc_plan, 2.4), (sc_trust, 2.6), (sc_brand, 2.2)]
XF = 0.40

# ציר זמן חופף: הסצנה הנכנסת כבר מתקדמת בזמן שהיוצאת דועכת
STARTS, _acc = [], 0.0
for _i, (_fn, _dur) in enumerate(SCENES):
    STARTS.append(_acc)
    _acc += _dur - (XF if _i < len(SCENES)-1 else 0)
TOTAL = STARTS[-1] + SCENES[-1][1]
N = int(FPS*TOTAL)

def compose(tg):
    act = []
    for i, (fn, dur) in enumerate(SCENES):
        lt = tg - STARTS[i]
        if -1e-6 <= lt <= dur + 1e-6:
            act.append((fn, min(max(lt, 0.0), dur)))
    if not act:
        return SCENES[-1][0](SCENES[-1][1])
    if len(act) == 1:
        return act[0][0](act[0][1])
    (f0, l0), (f1, l1) = act[0], act[1]
    k = eio(max(0.0, min(1.0, l1/XF)))    # ההתקדמות של הנכנסת היא גם הקרוספייד
    return Image.blend(f0(l0), f1(l1), k)

os.makedirs(OUT, exist_ok=True)
for i in range(N):
    tg = i/float(FPS)
    img = compose(tg)
    k = 0.010 + 0.028*(tg/TOTAL)
    dx, dy = int(W*k), int(H*k)
    img = img.crop((dx, dy, W-dx, H-dy)).resize((W, H), Image.LANCZOS)
    fade = min(eio(seg(i, 0, 11)), 1-seg(i, N-13, N))
    if fade < 1:
        img = Image.blend(Image.new("RGB", (W, H), (0, 0, 0)), img, max(0.0, fade))
    img.save(os.path.join(OUT, "f%04d.png" % i))
    if i % 30 == 0: print("frame", i, "/", N, flush=True)
print("done", N)
