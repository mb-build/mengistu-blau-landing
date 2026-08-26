# פסקול דרמטי לסרטון הפתיחה — מסונתז מקומית, בלה מינור.
# הקשת: ספק (דופק נמוך) -> הקשבה (פאד חם) -> בהירות (עלייה) -> אמון (חבטה) -> מותג (פתרון)
import math, wave, struct, os
import numpy as np

SR = 44100
DUR = 10.5                       # תואם לאורך הסרטון אחרי המעברים החופפים
n = int(SR*DUR)
t = np.arange(n)/SR
mixL = np.zeros(n); mixR = np.zeros(n)

def env(t0, atk, hold, rel):
    """מעטפת ADSR פשוטה על ציר הזמן המלא."""
    e = np.zeros(n)
    a0, a1 = int(t0*SR), int((t0+atk)*SR)
    h1 = int((t0+atk+hold)*SR)
    r1 = int((t0+atk+hold+rel)*SR)
    a0, a1, h1, r1 = [max(0, min(n, x)) for x in (a0, a1, h1, r1)]
    if a1 > a0: e[a0:a1] = np.linspace(0, 1, a1-a0)
    if h1 > a1: e[a1:h1] = 1.0
    if r1 > h1: e[h1:r1] = np.linspace(1, 0, r1-h1)
    return e

def place(sig, t0, amp=1.0, pan=0.0):
    """שם אות בציר, עם פאן פשוט."""
    i0 = int(t0*SR)
    i1 = min(n, i0+len(sig))
    if i0 >= n: return
    seg = sig[:i1-i0]*amp
    l = math.sqrt(max(0.0, (1-pan)/2)); r = math.sqrt(max(0.0, (1+pan)/2))
    mixL[i0:i1] += seg*l*1.414
    mixR[i0:i1] += seg*r*1.414

def bell(f, dur, amp=1.0, decay=3.2, parts=(1, 2, 3, 4.2)):
    """צליל עם דעיכה — פסנתר/פעמון."""
    k = np.arange(int(SR*dur))/SR
    out = np.zeros(len(k))
    for i, p in enumerate(parts):
        out += np.sin(2*np.pi*f*p*k) * math.exp(-i*0.75) * np.exp(-decay*k*(1+i*0.30))
    return out*amp

def pad(f, dur, amp=1.0, det=0.55):
    """פאד מיתרים — שלוש שכבות מפולפלות קלות."""
    k = np.arange(int(SR*dur))/SR
    out = np.zeros(len(k))
    for d in (-det, 0.0, det):
        out += np.sin(2*np.pi*(f+d)*k + 0.6*np.sin(2*np.pi*0.20*k))
    out += 0.30*np.sin(2*np.pi*f*2*k)
    return out*amp/3.4

def sub(f, dur, amp=1.0):
    k = np.arange(int(SR*dur))/SR
    return (np.sin(2*np.pi*f*k) + 0.30*np.sin(2*np.pi*f*2*k))*amp

def riser(dur, amp=1.0, f0=180, f1=1500):
    """עלייה — רעש מסונן שעולה בגובה ובעוצמה."""
    k = np.arange(int(SR*dur))/SR
    sweep = f0*(f1/f0)**(k/dur)
    ph = 2*np.pi*np.cumsum(sweep)/SR
    noise = np.random.default_rng(7).normal(0, 1, len(k))
    b = np.convolve(noise, np.ones(40)/40, mode="same")
    return (0.55*np.sin(ph) + 0.45*b*np.sin(ph*0.5)) * (k/dur)**2.2 * amp

def impact(dur=2.6, amp=1.0):
    """חבטה — סווייפ יורד עם זנב."""
    k = np.arange(int(SR*dur))/SR
    sweep = 150*np.exp(-4.5*k) + 34
    ph = 2*np.pi*np.cumsum(sweep)/SR
    body = np.sin(ph)*np.exp(-2.0*k)
    rng = np.random.default_rng(3)
    crack = rng.normal(0, 1, len(k))*np.exp(-26*k)*0.32
    return (body + crack)*amp

A2, C3, E3, F3, G3 = 110.0, 130.81, 164.81, 174.61, 196.00
A3, C4, E4, F4, G4, A4 = 220.0, 261.63, 329.63, 349.23, 392.00, 440.0

# --- שכבת יסוד: דרון נמוך לכל האורך ---
base = sub(A2/2, DUR, 0.22) * (env(0, 1.6, 6.4, 2.5)*0.9 + 0.1)
place(base, 0, 1.0, 0.0)

# --- 1. ספק (0.0-2.3): דופק נמוך ואיטי, ריק ---
for i, tt in enumerate((0.15, 0.95, 1.75)):
    place(sub(A2, 0.55, 0.30)*np.exp(-5.5*np.arange(int(SR*0.55))/SR), tt, 1.0, -0.15)
place(pad(A3, 2.6, 0.10)*env(0.1, 1.1, 0.8, 0.9)[:int(SR*2.6)], 0.1, 1.0, 0.0)

# --- 2. הקשבה (1.9-4.5): פאד חם נפתח, נגיעת פסנתר ---
for f, tt, p in ((A3, 2.0, -0.3), (C4, 2.5, 0.25), (E4, 3.1, -0.2)):
    place(bell(f, 2.4, 0.20), tt, 1.0, p)
place(pad(A3, 3.0, 0.20)*env(1.9, 0.9, 1.2, 0.9)[:int(SR*3.0)], 1.9, 1.0, -0.1)
place(pad(E3, 3.0, 0.16)*env(2.1, 0.9, 1.2, 0.9)[:int(SR*3.0)], 2.1, 1.0, 0.2)

# --- 3. בהירות (4.1-6.5): המהלך עולה, F -> C ---
place(pad(F3, 2.6, 0.22)*env(4.1, 0.7, 1.0, 0.8)[:int(SR*2.6)], 4.1, 1.0, -0.15)
place(pad(C4, 2.6, 0.16)*env(4.3, 0.7, 1.0, 0.8)[:int(SR*2.6)], 4.3, 1.0, 0.15)
for f, tt in ((F4, 4.35), (G4, 4.95), (A4, 5.55)):
    place(bell(f, 1.8, 0.17), tt, 1.0, 0.1)

# --- 4. אמון (6.1-8.7): עלייה אל לחיצת היד, ואז חבטה ---
place(riser(1.05, 0.30), 5.60, 1.0, 0.0)
place(impact(2.8, 0.62), 6.62, 1.0, 0.0)
place(sub(A2, 2.4, 0.26)*np.exp(-1.5*np.arange(int(SR*2.4))/SR), 6.62, 1.0, 0.0)
for f, p in ((A3, -0.35), (E4, 0.0), (A4, 0.35)):
    place(bell(f, 2.6, 0.20), 6.66, 1.0, p)

# --- 5. מותג (8.3-10.5): פתרון חם ---
place(pad(A3, 2.4, 0.24)*env(8.3, 0.8, 0.7, 0.9)[:int(SR*2.4)], 8.3, 1.0, -0.2)
place(pad(C4, 2.4, 0.18)*env(8.4, 0.8, 0.7, 0.9)[:int(SR*2.4)], 8.4, 1.0, 0.2)
place(pad(E4, 2.2, 0.14)*env(8.5, 0.8, 0.6, 0.8)[:int(SR*2.2)], 8.5, 1.0, 0.0)
place(bell(A4, 2.2, 0.22), 8.35, 1.0, 0.0)
place(bell(E4, 2.0, 0.14), 8.75, 1.0, -0.25)

# --- מאסטרינג: דעיכה בקצוות, לימיטר רך, נורמליזציה ---
fade = np.ones(n)
fi, fo = int(SR*0.25), int(SR*1.1)
fade[:fi] = np.linspace(0, 1, fi)
fade[-fo:] = np.linspace(1, 0, fo)
mixL *= fade; mixR *= fade
peak = max(np.abs(mixL).max(), np.abs(mixR).max(), 1e-9)
mixL = np.tanh(mixL/peak*1.5)*0.86
mixR = np.tanh(mixR/peak*1.5)*0.86

out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "score.wav")
with wave.open(out, "w") as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
    inter = np.empty(n*2, dtype=np.int16)
    inter[0::2] = (mixL*32767).astype(np.int16)
    inter[1::2] = (mixR*32767).astype(np.int16)
    w.writeframes(inter.tobytes())
print("score.wav", round(DUR, 2), "s")
