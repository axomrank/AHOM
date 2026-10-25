"""Soundtrack for reel 006 (Joysagar): the reel-002 v1 sound —
a synthesized Bihu-style groove (dhol, taal, gogona) — plus foley on every picture cue.

120 BPM: beat 0.5 s, bar 2 s. Run: python3 audio/build_mix.py  (writes assets/audio/master.wav)
"""
import subprocess
import wave
from pathlib import Path

import numpy as np
from scipy.signal import butter, sosfilt

SR = 48000
DUR = 16.0
ROOT = Path(__file__).resolve().parent.parent
SFX = ROOT / "assets/sfx"
LIB = Path.home() / ".claude/skills/ghost-editor/library/sfx"
OUT = ROOT / "assets/audio/master.wav"
rng = np.random.default_rng(1697)
N = int(DUR * SR)
mix = np.zeros((N, 2), np.float32)


def db(x):
    return 10 ** (x / 20)


def bp(x, lo, hi, order=2):
    return sosfilt(butter(order, [lo, hi], "bp", fs=SR, output="sos"), x, axis=0)


def lp(x, f, order=2):
    return sosfilt(butter(order, f, "lp", fs=SR, output="sos"), x, axis=0)


def hp(x, f, order=2):
    return sosfilt(butter(order, f, "hp", fs=SR, output="sos"), x, axis=0)


def st(m, pan=0.0):
    return np.stack([m * (1 - max(pan, 0)), m * (1 + min(pan, 0))], 1).astype(np.float32)


def place(sig, t, gain=0.0):
    """Anything that runs past 22 s wraps to the start, so the loop point is seamless."""
    i = int(round(t * SR)) % N
    s = sig * db(gain)
    j = min(N, i + len(s))
    mix[i:j] += s[: j - i]
    if i + len(s) > N:
        rest = s[N - i:]
        mix[: len(rest)] += rest


def load(path, max_len=None, fade=0.05, rate=1.0, onset=True):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", str(path), "-ac", "2", "-ar", str(SR), "-f", "f32le", "-"],
                         capture_output=True, check=True).stdout
    s = np.frombuffer(raw, np.float32).reshape(-1, 2).copy()
    if rate != 1.0:
        idx = np.arange(0, len(s) - 1, rate)
        s = np.stack([np.interp(idx, np.arange(len(s)), s[:, c]) for c in (0, 1)], 1).astype(np.float32)
    if onset:
        env = np.abs(s).max(1)
        k = int(np.argmax(env > 0.08 * env.max()))
        s = s[max(0, k - int(0.005 * SR)):]
    if max_len:
        s = s[: int(max_len * SR)]
        n = int(fade * SR)
        s[-n:] *= np.linspace(1, 0, n)[:, None]
    return s / (np.abs(s).max() + 1e-9)


# ---------------- instruments (same voices as reel 002 v1) ----------------
def dhol_bass(pitch=1.0):
    t = np.arange(int(0.45 * SR)) / SR
    f = (62 + 40 * np.exp(-t * 30)) * pitch
    body = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t / 0.22)
    thump = lp(rng.standard_normal(len(t)), 300) * np.exp(-t / 0.015) * 0.6
    s = np.tanh(2.2 * (body + thump))
    return st(s / np.abs(s).max())


def dhol_slap(bright=1.0):
    t = np.arange(int(0.18 * SR)) / SR
    crack = bp(rng.standard_normal(len(t)), 1200, 5200) * np.exp(-t / (0.035 * bright))
    tone = np.sin(2 * np.pi * 330 * t) * np.exp(-t / 0.06) * 0.7
    s = crack + tone
    return st(s / np.abs(s).max(), pan=0.15)


def taal(open_=True):
    L = 0.6 if open_ else 0.12
    t = np.arange(int(L * SR)) / SR
    s = np.zeros_like(t)
    for f in (3150, 4270, 5590, 6830, 8110, 9420):
        s += np.sin(2 * np.pi * f * t + rng.uniform(0, 6)) * rng.uniform(0.5, 1)
    s = s * 0.25 + hp(rng.standard_normal(len(t)), 6000) * 0.5
    s *= np.exp(-t / (0.22 if open_ else 0.035))
    return st(s / np.abs(s).max(), pan=-0.25)


def gogona(f0=98.0, length=0.32):
    t = np.arange(int(length * SR)) / SR
    ph = 2 * np.pi * f0 * t
    saw = 2 * ((ph / (2 * np.pi)) % 1) - 1
    out = bp(saw, 300, 2400, order=1)
    sweep = np.sin(2 * np.pi * np.cumsum(450 + 1600 * np.clip(t / (length * 0.7), 0, 1)) / SR)
    s = out * (0.6 + 0.4 * sweep) * np.exp(-t / (length * 0.45)) * np.minimum(1, t / 0.003)
    return st(s / np.abs(s).max(), pan=0.3)


def sword():
    t = np.arange(int(1.2 * SR)) / SR
    ring = sum(a * np.sin(2 * np.pi * f * t) * np.exp(-t / d)
               for f, a, d in [(2150, 1.0, 0.6), (3420, 0.7, 0.45), (5230, 0.5, 0.3), (7910, 0.35, 0.2)])
    scrape = hp(rng.standard_normal(len(t)), 3000) * np.exp(-t / 0.04)
    s = 0.5 * ring + 0.6 * scrape
    return st(s / np.abs(s).max())


def tick(f=1800):
    t = np.arange(int(0.05 * SR)) / SR
    return st(np.sin(2 * np.pi * f * t) * np.exp(-t / 0.01))


def zap(up=True):
    t = np.arange(int(0.16 * SR)) / SR
    f = (300 + 2100 * (t / 0.16)) if up else (2400 - 2100 * (t / 0.16))
    s = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t / 0.08) + hp(rng.standard_normal(len(t)), 4000) * np.exp(-t / 0.03) * 0.3
    return st(s / np.abs(s).max(), pan=-0.1)


BASS, BASS_LO, SLAP, SLAP_SOFT = dhol_bass(), dhol_bass(0.8), dhol_slap(), dhol_slap(0.6)
TAAL_O, TAAL_C = taal(True), taal(False)
S16 = 0.125
PAT = {"bass": [0, 6, 8, 11, 14], "slap": [2, 4, 10, 12, 13, 15], "taal_o": [4, 12], "taal_c": [2, 6, 10, 14]}


def groove_bar(t0, level=0.0, light=False, double=False):
    if not light:
        for s in PAT["bass"] + ([3, 9] if double else []):
            place(BASS, t0 + s * S16, level - 2)
    for s in PAT["slap"]:
        place(SLAP if not light else SLAP_SOFT, t0 + s * S16, level - (9 if light else 7))
    for s in PAT["taal_o"]:
        place(TAAL_O, t0 + s * S16, level - 13)
    for s in PAT["taal_c"]:
        place(TAAL_C, t0 + s * S16, level - 15)


def gogona_riff(t0, level=-9):
    for s, f in [(0, 98), (3, 98), (6, 110), (8, 98), (11, 131), (14, 110)]:
        place(gogona(f), t0 + s * S16, level)


def fill(t0):
    """Half-bar dhol roll that lands on the hook's first hit when the reel loops."""
    for k, s in enumerate(range(8, 16)):
        place(SLAP, t0 + s * S16, -10 + k * 0.7)
    for s in (8, 12, 14, 15):
        place(BASS, t0 + s * S16, -4)


# ---------------- foley ----------------
whoosh = load(LIB / "whoosh-cine.wav", onset=False)
whoosh2 = load(LIB / "whoosh-2.wav", onset=False)
hit = load(LIB / "cinematic-cine-hit.wav", onset=False)
riser = load(LIB / "cinematic-rumble-riser.wav", onset=False)
pop = load(LIB / "pop-2.wav")
kanh = load(SFX / "bowl-clang.mp3", 3.0, fade=1.2)
thud = load(SFX / "dish-wood.mp3", 0.5)
stones = load(SFX / "stones-fall.mp3", 0.3, fade=0.1)
pour = load(SFX / "gravel-pour.mp3", 0.45, fade=0.1)
sparkle = load(SFX / "sparkle.mp3", 1.0)
water = load(SFX / "water-pour.mp3", 1.2, fade=0.3)
splash = load(SFX / "water-splash.mp3", 1.0)
drain = water[::-1].copy()
ZUP, ZDN = zap(True), zap(False)
SWORD = sword()

# ---------------- arrangement (16 s) ----------------
# hook: two shovel strikes into dry earth (blade lands at t + 0.11)
place(BASS_LO, 0.0, -2)
for t in (0.31, 0.66):
    place(stones, t, -5)
    place(thud, t, -6)
    place(BASS, t, -4)
place(gogona(98, 0.4), 0.78, -6)
# card
place(whoosh2, 0.95, -10)
for k, t in enumerate([1.25, 1.45, 1.65, 1.85]):
    place(load(LIB / "pop-2.wav", rate=1.0 + 0.1 * k), t, -11)
groove_bar(1.0, light=True)
# dig 2.5–8.0: a day jump every beat, diggers arrive in waves, shovels chop on the eighths
for k, t in enumerate([2.5, 3.0, 3.5, 4.0, 4.5, 5.0, 5.5, 6.0, 6.5, 7.0, 7.5]):
    place(tick(1500 + 60 * k), t, -9)
    place(BASS, t, -5)
for w, t in enumerate([2.5, 3.0, 3.5, 4.0, 4.5]):
    for i in range(3 + w):
        place(load(LIB / "pop-2.wav", rate=1.0 + 0.15 * i), t + 0.03 * i, -13)
for k in range(21):
    place(stones, 2.625 + 0.25 * k, -15 if k % 2 else -13)
place(BASS_LO, 7.5, 0)
place(gogona(131, 0.4), 7.55, -6)
groove_bar(3.0)
groove_bar(5.0, double=True)
groove_bar(7.0)
# flood 8.0
place(water, 8.0, -3)
place(splash, 8.05, -5)
place(BASS_LO, 8.0, -1)
place(thud, 8.62, -4); place(TAAL_O, 8.62, -6)
for i, t in enumerate([9.0, 9.25, 9.5, 9.75]):
    place(load(LIB / "pop-2.wav", rate=0.9 + 0.12 * i), t + 0.1, -8)
groove_bar(9.0)
# size 10.0: acre count + fields filling row by row
tt = 10.0
for k in range(14):
    place(tick(1500 + 45 * k), tt, -17)
    tt += 0.6 / 14
for r in range(10):
    place(tick(2200 + 80 * r), 10.1 + r * 0.07, -14)
place(pop, 10.6, -6)
place(thud, 10.85, -4); place(BASS, 10.85, -2)
# reveal 11.5
place(kanh, 11.5, -3)
place(hit, 11.5, -5)
place(BASS_LO, 11.5, 0)
place(thud, 12.87, -2); place(BASS, 12.87, -1)
groove_bar(11.0)
gogona_riff(11.5, -9)
groove_bar(13.0)
# end 14.0: the sea drains back into dry land, the shovel drops in
for i in range(4):
    place(load(LIB / "pop-2.wav", rate=1.4 - 0.1 * i), 14.0 + 0.03 * i, -12)
place(drain, 14.15, -5)
place(whoosh2, 14.3, -9)
place(whoosh, 15.0, -10)
place(thud, 15.25, -3); place(stones, 15.25, -8)
groove_bar(15.0, light=True)
fill(14.0)

# ---------------- master ----------------
mix /= np.abs(mix).max() + 1e-9
mix *= db(-1.0)
tmp = OUT.with_suffix(".raw.wav")
with wave.open(str(tmp), "wb") as w:
    w.setnchannels(2)
    w.setsampwidth(2)
    w.setframerate(SR)
    w.writeframes((np.clip(mix, -1, 1) * 32767).astype("<i2").tobytes())
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(tmp), "-af",
                "acompressor=threshold=-18dB:ratio=3:attack=5:release=80,loudnorm=I=-13:TP=-1.0:LRA=8",
                "-ar", str(SR), str(OUT)], check=True)
tmp.unlink()
print("wrote", OUT)
