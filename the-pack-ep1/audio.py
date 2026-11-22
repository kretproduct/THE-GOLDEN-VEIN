"""Build the full soundtrack: voice-over + procedural music + procedural SFX."""
import os
import math
import subprocess
import numpy as np
from scipy import signal
from timeline import EDL, SCENE_START, TOTAL, LINES, line_abs_start, vo_path, find_word

SR = 48000
N = int((TOTAL + 1) * SR)
HERE = os.path.dirname(os.path.abspath(__file__))
rng = np.random.default_rng(7)


def A(scene, t):
    return SCENE_START[scene] + t


def lp(x, fc, order=2):
    b, a = signal.butter(order, min(fc / (SR / 2), 0.99), 'low')
    return signal.lfilter(b, a, x)


def hp(x, fc, order=2):
    b, a = signal.butter(order, fc / (SR / 2), 'high')
    return signal.lfilter(b, a, x)


def bp(x, f1, f2, order=2):
    b, a = signal.butter(order, [f1 / (SR / 2), min(f2 / (SR / 2), 0.99)], 'band')
    return signal.lfilter(b, a, x)


def env_adsr(n, a, r):
    e = np.ones(n)
    na = max(1, int(a * SR))
    nr = max(1, int(r * SR))
    e[:na] = np.linspace(0, 1, na)
    if nr < n:
        e[-nr:] *= np.linspace(1, 0, nr)
    return e


def add(buf, start_s, x, gain=1.0, pan=0.0):
    i = int(start_s * SR)
    if i >= N or i + len(x) <= 0:
        return
    if i < 0:
        x = x[-i:]
        i = 0
    x = x[:N - i]
    l = math.cos((pan + 1) * math.pi / 4)
    r = math.sin((pan + 1) * math.pi / 4)
    buf[0, i:i + len(x)] += x * gain * l * 1.414
    buf[1, i:i + len(x)] += x * gain * r * 1.414


def put(x, i, c, g=1.0):
    n = min(len(c), len(x) - i)
    if n > 0:
        x[i:i + n] += c[:n] * g


def noise(d):
    return rng.standard_normal(int(d * SR))


def brown(d):
    w = rng.standard_normal(int(d * SR))
    b = np.cumsum(w)
    b = hp(b, 20, 1)
    return b / (np.abs(b).max() + 1e-9)


def tvec(d):
    return np.arange(int(d * SR)) / SR


# ------------------------------------------------------------------ SFX

def s_heartbeat():
    t = tvec(0.5)
    def thump(f, amp):
        return amp * np.sin(2 * np.pi * f * t * (1 - 0.3 * t)) * np.exp(-t * 18)
    x = np.zeros(int(0.5 * SR))
    x += thump(55, 1.0)
    d = int(0.22 * SR)
    x[d:] += thump(48, 0.7)[:len(x) - d]
    return lp(x, 160)


def s_breath(d=0.7, bright=1500, amp=1.0):
    x = noise(d)
    x = bp(x, 300, bright)
    e = np.sin(np.linspace(0, np.pi, len(x))) ** 2
    return x * e * amp * 0.25


def s_wind(d, gust=0.3, bright=900):
    x = brown(d) * 0.6 + lp(noise(d), bright) * 0.15
    t = tvec(d)
    mod = 0.7 + gust * np.sin(2 * np.pi * 0.11 * t) + gust * 0.6 * np.sin(2 * np.pi * 0.23 * t + 1)
    return lp(x, bright) * mod


def s_crunch():
    x = noise(0.16)
    x = bp(x, 900, 5000) * np.exp(-tvec(0.16) * 30)
    x += lp(noise(0.16), 300) * np.exp(-tvec(0.16) * 40) * 0.8
    return x * 0.35


def s_whumpf():
    d = 2.2
    t = tvec(d)
    f = 70 * np.exp(-t * 0.8) + 25
    ph = 2 * np.pi * np.cumsum(f) / SR
    x = np.sin(ph) * np.exp(-t * 2.2)
    x += lp(noise(d), 200) * np.exp(-t * 3) * 0.8
    return x * 1.2


def s_crack(d=1.4):
    x = np.zeros(int(d * SR))
    for _ in range(40):
        i = int(rng.uniform(0, d * 0.85) * SR)
        c = hp(noise(0.03), 1500) * np.exp(-tvec(0.03) * 120)
        put(x, i, c, rng.uniform(0.3, 1.0))
    return x * 0.6


def s_roar(d, rise=2.5):
    x = brown(d) * 1.0 + lp(noise(d), 600) * 0.3
    x = lp(x, 500)
    t = tvec(d)
    e = np.clip(t / rise, 0, 1) ** 1.5
    e *= 0.85 + 0.15 * np.sin(2 * np.pi * 7 * t)
    return x * e


def s_crow():
    d = 0.35
    t = tvec(d)
    f = 520 + 120 * np.sin(np.pi * t / d)
    ph = 2 * np.pi * np.cumsum(f) / SR
    x = signal.sawtooth(ph) * 0.6 + noise(d) * 0.25
    x = bp(x, 500, 2600) * np.sin(np.pi * t / d) ** 0.6
    return x * 0.5


def s_scrape(d=0.5):
    x = bp(noise(d), 600, 3500)
    t = tvec(d)
    e = np.sin(np.pi * t / d) * (0.6 + 0.4 * np.sin(2 * np.pi * 23 * t))
    return x * e * 0.35


def s_pop():
    d = 0.35
    t = tvec(d)
    x = bp(noise(d), 400, 2500) * np.sin(np.pi * t / d) ** 2 * 0.4
    x += np.sin(2 * np.pi * (600 + 600 * t) * t) * np.exp(-t * 14) * 0.25
    return x


def s_zip():
    d = 0.5
    x = np.zeros(int(d * SR))
    for k in range(30):
        i = int(k / 30 * d * 0.9 * SR)
        c = hp(noise(0.006), 2500) * np.exp(-tvec(0.006) * 400)
        put(x, i, c)
    return x * 0.5


def s_knock():
    d = 0.25
    t = tvec(d)
    x = np.sin(2 * np.pi * 180 * t) * np.exp(-t * 30) + lp(noise(d), 900) * np.exp(-t * 50) * 0.6
    return x * 0.9


def s_creak(d=0.6, f0=180):
    t = tvec(d)
    f = f0 + 60 * np.sin(np.pi * t / d)
    ph = 2 * np.pi * np.cumsum(f) / SR
    x = signal.sawtooth(ph) * (0.5 + 0.5 * np.sin(2 * np.pi * 30 * t))
    x = bp(x, 200, 1800) * np.sin(np.pi * t / d)
    return x * 0.18


def s_clank():
    d = 0.6
    t = tvec(d)
    x = sum(np.sin(2 * np.pi * f * t) * np.exp(-t * k) for f, k in ((420, 9), (1130, 12), (1870, 16)))
    return x * 0.25


def s_snap():
    d = 0.12
    x = hp(noise(d), 800) * np.exp(-tvec(d) * 60)
    return x * 0.8


def s_strike():
    d = 0.3
    x = hp(noise(d), 3000) * np.exp(-tvec(d) * 14)
    return x * 0.5


def s_whoosh(d=0.8, up=True):
    t = tvec(d)
    x = noise(d)
    out = np.zeros_like(x)
    seglen = SR // 50
    for k in range(0, len(x), seglen):
        fr = (k / len(x)) if up else 1 - k / len(x)
        fc = 300 + 3000 * fr
        out[k:k + seglen] = bp(x[k:k + seglen + 200], fc * 0.6, fc * 1.4)[:len(out[k:k + seglen])]
    return out * np.sin(np.pi * t / d) * 0.35


def s_crackle(d, density=12, amp=1.0):
    x = lp(noise(d), 2500) * 0.04
    for _ in range(int(d * density)):
        i = int(rng.uniform(0, d) * SR)
        c = hp(noise(0.012), 1500) * np.exp(-tvec(0.012) * 300)
        put(x, i, c, rng.uniform(0.2, 1.0))
    return x * amp * 0.5


def s_howl(d=4.0, base=420):
    t = tvec(d)
    f = base + 260 * np.sin(np.clip(t / (d * 0.5), 0, 1) * np.pi / 2) - 180 * np.clip((t - d * 0.6) / (d * 0.4), 0, 1)
    f = f + 6 * np.sin(2 * np.pi * 5.5 * t)
    ph = 2 * np.pi * np.cumsum(f) / SR
    x = np.sin(ph) + 0.3 * np.sin(2 * ph) + 0.1 * np.sin(3 * ph) + noise(d) * 0.02
    e = np.clip(t / 0.6, 0, 1) * np.clip((d - t) / 0.9, 0, 1)
    x = x * e
    # simple reverb: multi-tap echo
    out = np.zeros(len(x) + int(1.6 * SR))
    out[:len(x)] += x
    for k, (dl, g) in enumerate(((0.21, 0.45), (0.37, 0.35), (0.59, 0.25), (0.83, 0.18), (1.2, 0.12), (1.55, 0.08))):
        i = int(dl * SR)
        out[i:i + len(x)] += x * g
    return lp(out, 2500) * 0.35


def s_scribble(d):
    x = bp(noise(d), 1500, 6000)
    t = tvec(d)
    e = (0.5 + 0.5 * np.sign(np.sin(2 * np.pi * 3.3 * t))) * (0.6 + 0.4 * np.sin(2 * np.pi * 11 * t))
    return x * e * 0.08


def s_thud():
    d = 0.6
    t = tvec(d)
    return (np.sin(2 * np.pi * 60 * t) * np.exp(-t * 8) + lp(noise(d), 300) * np.exp(-t * 12)) * 0.8


# ------------------------------------------------------------------ music

def midi(n):
    return 440 * 2 ** ((n - 69) / 12)


def pad(notes, d, amp=0.1, bright=1200, a=2.0, r=2.5, detune=0.004):
    t = tvec(d)
    x = np.zeros(len(t))
    for n in notes:
        f = midi(n)
        for dt in (-detune, 0, detune):
            x += signal.sawtooth(2 * np.pi * f * (1 + dt) * t + rng.uniform(0, 6)) * 0.33
        x += np.sin(2 * np.pi * f / 2 * t) * 0.5
    x = lp(x, bright, 2)
    x *= env_adsr(len(x), a, r)
    return x * amp / max(1, len(notes))


def cello(n, d, amp=0.25):
    t = tvec(d)
    f = midi(n) * (1 + 0.004 * np.sin(2 * np.pi * 5 * t))
    ph = 2 * np.pi * np.cumsum(f) / SR
    x = signal.sawtooth(ph)
    x = lp(x, 700, 2) * env_adsr(len(t), 1.5, 3.0)
    return x * amp


def pulse_track(d, bpm=76, amp=0.3, note=38):
    x = np.zeros(int(d * SR))
    beat = 60 / bpm
    k = 0
    while k * beat < d:
        i = int(k * beat * SR)
        t = tvec(0.5)
        kick = np.sin(2 * np.pi * (60 * np.exp(-t * 8) + 35) * t) * np.exp(-t * 7)
        x[i:i + len(kick)] += kick[:len(x) - i] * (1.0 if k % 2 == 0 else 0.6)
        k += 1
    bass = lp(signal.sawtooth(2 * np.pi * midi(note) * tvec(d)), 180) * 0.25
    bass *= 0.5 + 0.5 * (np.sin(2 * np.pi * tvec(d) / (beat * 2)) > 0)
    return (x + bass) * amp * env_adsr(len(x), 1.0, 1.5)


def drone(n, d, amp=0.12, bright=400):
    t = tvec(d)
    x = np.sin(2 * np.pi * midi(n) * t) + 0.5 * np.sin(2 * np.pi * midi(n + 1) * t * 1.001) + 0.3 * lp(noise(d), bright)
    x *= 0.8 + 0.2 * np.sin(2 * np.pi * 0.07 * t)
    return x * amp * env_adsr(len(t), 3.0, 3.0)


Dm, Bb, F, C, Gm, Am = [50, 53, 57], [46, 50, 53], [53, 57, 60], [48, 52, 55], [43, 46, 50], [45, 48, 52]


def progression(chords, d, amp=0.1, bright=1200, up=0):
    seglen = d / len(chords)
    out = np.zeros(int(d * SR) + int(3 * SR))
    for k, ch in enumerate(chords):
        p = pad([n + up for n in ch], seglen + 2.5, amp, bright, a=1.5, r=2.5)
        i = int(k * seglen * SR)
        out[i:i + len(p)] += p
    return out[:int(d * SR)]


def build():
    mus = np.zeros((2, N))
    sfx = np.zeros((2, N))
    vo = np.zeros((2, N))
    # ---------------- voice-over
    for i, (sc, sp, text) in enumerate(LINES):
        raw = subprocess.check_output(['ffmpeg', '-v', 'error', '-i', vo_path(i), '-ac', '1', '-ar', str(SR),
                                       '-f', 'f32le', '-'])
        x = np.frombuffer(raw, dtype=np.float32).astype(np.float64)
        x = x / (np.abs(x).max() + 1e-9) * 0.82
        if sp == 'R' and i == 34:  # notebook voice-over: a little softer, warmer
            x = lp(x, 6000) * 0.95
        if sp == 'R' and i in (12,):  # under the snow: muffled
            x = lp(x, 2500)
        add(vo, line_abs_start(i), x, 1.0, 0.0 if sp == 'N' else 0.05)

    # ---------------- music beds (per scene)
    def m(s, t0, x, g=1.0):
        add(mus, A(s, t0), x, g)
    m(1, 0, drone(38, 26, 0.10, 250))
    m(2, 0.2, cello(36, 12, 0.35))
    m(2, 2.0, pad(Dm, 10, 0.10, 900, a=4))
    m(3, 0, progression([Dm, Bb, F, C], 34, 0.09, 1100))
    m(3, 0, pulse_track(34, 76, 0.22))
    m(4, 0, progression([Dm, Bb, Gm, Am], 30, 0.09, 1100))
    m(4, 0, pulse_track(30, 76, 0.2))
    m(5, 0, progression([Dm, Bb], 6.5, 0.09, 1100) * env_adsr(int(6.5 * SR), 0.5, 0.05))
    m(5, 0, pulse_track(6.5, 76, 0.2) * env_adsr(int(6.5 * SR), 0.5, 0.05))
    m(5, 12, drone(38, 36, 0.09, 300))
    m(7, 0.5, drone(41, 37.5, 0.08, 300))
    m(7, 0.5, pad([62, 65, 69], 37, 0.05, 2500, a=3, r=1))
    m(9, 0, drone(36, 40, 0.10, 250))
    m(10, 0, drone(36, 36, 0.09, 250))
    m(10, 4, pad([60, 63, 67], 30, 0.04, 1500, a=4))
    m(11, 2, progression([Dm, F, C, Bb, C], 34, 0.11, 1500))
    m(12, 1, pad(Am, 24, 0.07, 900, a=4))
    m(13, 0, progression([Am, F, Dm, Am], 34, 0.08, 900))
    m(14, 0, progression([Dm, Bb, Gm, C], 40, 0.08, 1000))
    m(15, 0, progression([F, C, Dm, Bb], 20, 0.09, 1400, up=12))
    m(16, 0, pad(Dm, 20, 0.07, 800, a=3))
    m(17, 0, progression([Dm, Gm, Bb, Am], 34, 0.07, 900))
    m(18, 0, drone(38, 46, 0.06, 300))
    m(18, 2, progression([Dm, Bb, Gm, Am, Dm], 44, 0.05, 800))
    m(19, 4, progression([F, C, Dm, Bb], 16, 0.08, 1300, up=12))
    m(20, 0, progression([F, Am, Bb, C], 21, 0.09, 1300, up=12))
    m(21, 0, progression([F, C, Dm, Bb, F, C, Bb, F], 50, 0.10, 1500, up=12))
    m(22, 3, drone(37, 16.5, 0.12, 300))
    m(22, 19.5, cello(38, 6.5, 0.3))
    m(22, 19.5, pad(Dm, 6.5, 0.1, 1000, a=0.3, r=3))

    # ---------------- SFX
    def x(s, t0, snd, g=1.0, pan=0.0):
        add(sfx, A(s, t0), snd, g, pan)
    # S1: heartbeat + shallow breaths, muffled
    hb = s_heartbeat()
    k = 0.0
    while k < 26:
        x(1, k, hb, 0.6)
        k += 1.05
    for k in np.arange(1.0, 26, 2.3):
        x(1, k, lp(s_breath(0.6, 900), 900), 0.6)
    # S2 wind rising
    x(2, 0, s_wind(12, 0.3, 700) * np.linspace(0.2, 1, int(12 * SR)), 0.35)
    # S3/4 wind + steps + map flap
    x(3, 0, s_wind(34, 0.35, 900), 0.3)
    for k in np.arange(0.2, 12, 0.6):
        x(3, k, s_crunch(), 0.8, -0.1)
    x(3, 21.5, s_scrape(12.5) * 0.4, 0.5)
    x(4, 0, s_wind(30, 0.2, 700), 0.2)
    for w in ('Food', 'Fuel', 'Radio', 'Map'):
        x(4, find_word(4, w) - 0.2, s_pop(), 0.7, 0.4)
    x(4, find_word(4, 'Map') + 0.6, s_zip(), 0.8)
    x(4, 24.5, s_zip(), 0.5)
    # S5 slope
    x(5, 0, s_wind(48, 0.3, 800), 0.25)
    for k in np.arange(0.2, 6, 0.63):
        x(5, k, s_crunch(), 0.8)
    x(5, 6.5, s_whumpf(), 1.0)
    x(5, 6.7, s_crack(1.6), 0.7, 0.3)
    for k in np.arange(33.5, 42, 1.05):
        x(5, k, s_crunch(), 0.5)
    # S6 avalanche
    x(6, 2.0, s_crack(0.8), 1.0)
    x(6, 2.2, s_roar(14.8, 2.5), 1.2)
    x(6, 4.8, s_thud(), 0.8)
    # S7 freeze
    x(7, 0.0, s_whoosh(0.9, False), 0.8)
    x(7, find_word(10, 'push'), s_whoosh(0.6, True), 0.4)
    x(7, 38.0, s_roar(5.0, 0.4), 1.0)
    x(7, 43.0, s_thud(), 0.9)
    # S8 silence + crow
    x(8, 0, s_wind(12, 0.1, 400), 0.08)
    x(8, 2.5, s_crow(), 0.5, -0.5)
    x(8, 2.95, s_crow(), 0.4, -0.5)
    x(8, 9.6, s_crow(), 0.35, 0.3)
    # S9/10 under snow: breathing + heartbeat
    for s, d, calm_at in ((9, 40, find_word(14, 'Slow') + 1.0), (10, 36, 999)):
        k = 0.2
        while k < d:
            rate = 0.55 if k < calm_at else 1.9
            if s == 10:
                rate = 1.2
            x(s, k, lp(s_breath(0.45 if rate < 1 else 1.1, 1100), 1300), 0.55)
            k += rate
        k = 0.0
        while k < d:
            x(s, k, hb, 0.5)
            k += 0.75 if (s == 9 and k < calm_at) else 1.0
    # S11 digging out
    x(11, 0.3, s_crack(1.0), 0.5)
    for k in np.arange(0.6, 30, 0.7):
        x(11, k + rng.uniform(-0.1, 0.1), s_scrape(0.4), 0.7, rng.uniform(-0.3, 0.3))
    for k in np.arange(1.0, 30, 1.6):
        x(11, k, s_breath(0.5, 1800), 0.5)
    x(11, 0, s_wind(36, 0.2, 600), 0.15)
    # S12 gasping + wind
    for k in np.arange(0.2, 6.5, 0.75):
        x(12, k, s_breath(0.6, 2000), 0.7)
    x(12, 0, s_wind(25, 0.2, 600), 0.18)
    # S13
    x(13, 0, s_wind(34, 0.3, 700), 0.2)
    for k in np.arange(3.0, 6.5, 0.45):
        x(13, k, s_scrape(0.35), 0.6, 0.2)
    for w in ('Knife', 'Fire', 'Emergency', 'Notebook', 'energy', 'Water'):
        x(13, find_word(20, w) - 0.3, s_pop(), 0.4, -0.4)
    # S14 strong wind
    x(14, 0, s_wind(40, 0.5, 1200), 0.45)
    # S15 footsteps, softer wind
    x(15, 0, s_wind(20, 0.2, 600) * np.linspace(1, 0.4, int(20 * SR)), 0.25)
    for k in np.arange(0.2, 12, 0.7):
        x(15, k, s_crunch(), 0.6)
    # S16 deep snow steps + creaks
    x(16, 0, s_wind(20, 0.15, 500) * np.linspace(0.6, 0.2, int(20 * SR)), 0.2)
    for k in np.arange(0.3, 11, 0.92):
        x(16, k, lp(s_crunch(), 1500), 1.0)
    for k in (2.0, 6.5, 13.0):
        x(16, k, s_creak(0.9, 140), 0.6, 0.5)
    # S17
    x(17, 0, s_wind(34, 0.15, 500), 0.15)
    for k in np.arange(0.6, 12, 0.78):
        x(17, k, s_crunch(), 0.6)
    tl = find_word(28, 'Look', 1)
    for k in (0.2, 0.55, 0.9, 1.6, 1.95):
        x(17, tl + k, s_knock(), 0.8, 0.3)
    x(17, 24.0, s_scrape(4.0), 0.4)
    # S18 interior
    x(18, 0.0, s_creak(1.4, 110), 0.9, -0.5)
    x(18, 0.0, s_scrape(1.4), 0.5, -0.5)
    k = 1.5
    while k < 14:
        x(18, k, s_creak(0.5, rng.uniform(160, 260)), 0.7, rng.uniform(-0.2, 0.2))
        k += math.pi / 2.2
    x(18, 15.0, s_clank(), 0.7, 0.4)
    x(18, 16.2, s_scrape(0.6), 0.4, 0.4)
    x(18, 21.0, s_thud() * 0.3, 0.5)
    # S19 fire
    x(19, 0.5, s_snap(), 0.9)
    x(19, 1.0, s_snap(), 0.9)
    for st in (1.8, 2.7, 3.6, 4.2):
        x(19, st, s_strike(), 0.9, 0.3)
    x(19, 4.3, s_whoosh(1.0, True), 0.5)
    cr = s_crackle(15.7, 10)
    cr *= np.linspace(0.3, 1.0, len(cr))
    x(19, 4.3, cr, 0.9, 0.3)
    x(19, 0, s_wind(20, 0.2, 400), 0.12)
    # S20 crackle + pencil
    x(20, 0, s_crackle(21, 10), 0.8, 0.3)
    x(20, 2.0, s_scribble(7.0), 1.0, -0.1)
    # S21 exterior night
    x(21, 0, s_wind(50, 0.15, 400), 0.15)
    x(21, 0, s_crackle(50, 5) * 0.3, 0.5)
    # S22 howls
    x(22, 0, s_crackle(19.5, 6) * np.linspace(1, 0.3, int(19.5 * SR)), 0.7, 0.3)
    x(22, 3.5, lp(s_howl(4.2, 400), 1500), 0.55, -0.6)
    x(22, 7.0, s_howl(4.0, 450), 0.85, 0.4)
    x(22, 10.5, s_howl(4.5, 380), 1.0, -0.2)
    x(22, 11.2, s_howl(3.5, 470), 0.7, 0.6)

    # ---------------- mix with ducking
    vo_env = np.abs(vo[0]) + np.abs(vo[1])
    win = int(0.25 * SR)
    act = (vo_env > 0.02).astype(np.float64)
    cs = np.concatenate([[0.0], np.cumsum(act)])
    lo = np.clip(np.arange(N) - win // 2, 0, N)
    hi = np.clip(np.arange(N) + win // 2, 0, N)
    duck = (cs[hi] - cs[lo]) / win
    duck = lp(duck, 4)
    gain_m = 1.0 - 0.55 * np.clip(duck * 1.5, 0, 1)
    gain_s = 1.0 - 0.35 * np.clip(duck * 1.5, 0, 1)
    mix = vo * 1.0 + mus * gain_m * 0.9 + sfx * gain_s * 0.8
    sp = act > 0
    def db(v):
        return 20 * np.log10(np.sqrt(np.mean(v ** 2)) + 1e-12)
    print('during speech: vo %.1f  music %.1f  sfx %.1f dB' % (db(vo[0][sp]), db((mus[0] * gain_m * 0.9)[sp]),
                                                              db((sfx[0] * gain_s * 0.8)[sp])))
    print('no speech:     music %.1f  sfx %.1f dB' % (db((mus[0] * gain_m * 0.9)[~sp]), db((sfx[0] * gain_s * 0.8)[~sp])))
    # global fade-out at the very end
    fo = int(1.2 * SR)
    end = int(TOTAL * SR)
    mix[:, end - fo:end] *= np.linspace(1, 0, fo)
    mix[:, end:] = 0
    peak = np.abs(mix).max()
    mix = np.tanh(mix / peak * 1.2) * 0.89 if peak > 0 else mix
    mix = mix[:, :end]
    out = os.path.join(HERE, 'build', 'mix.wav')
    os.makedirs(os.path.dirname(out), exist_ok=True)
    pcm = (mix.T * 32767).astype(np.int16)
    import wave
    with wave.open(out, 'wb') as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(pcm.tobytes())
    print('wrote', out, mix.shape[1] / SR)


if __name__ == '__main__':
    build()
