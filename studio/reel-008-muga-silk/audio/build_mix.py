"""vlreel soundtrack builder: one pre-mixed master, every sound placed on the picture's clock.

Copy into <project>/audio/build_mix.py, then edit only the ARRANGEMENT section.
Run:  python3 audio/build_mix.py      -> assets/audio/master.wav  (loudness-normalised ~ -13 LUFS)

Clock: 120 BPM, beat = 0.5 s, bar = 2 s, sixteenth = 0.125 s.  Reel length DUR (default 16 s).
place() wraps anything that spills past DUR back to 0, so the loop seam is seamless.

SYNC RULE: a sound goes on the frame the thing *visibly lands*, not when its tween starts.
A 2-frame snap tween (0.0667 s) that starts at t lands at t + 0.0667 -> place the sound there.
"""
import subprocess
import wave
from pathlib import Path

import numpy as np
from scipy.signal import butter, sosfilt

SR = 48000
DUR = 16.0
S16 = 0.125
ROOT = Path(__file__).resolve().parent.parent
SFX = ROOT / "assets/sfx"
OUT = ROOT / "assets/audio/master.wav"
rng = np.random.default_rng(2007)  # change per reel; keep fixed for reproducible renders
N = int(DUR * SR)
mix = np.zeros((N, 2), np.float32)


# ---------------- plumbing ----------------
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
    i = int(round(t * SR)) % N
    s = sig * db(gain)
    j = min(N, i + len(s))
    mix[i:j] += s[: j - i]
    if i + len(s) > N:
        rest = s[N - i:]
        mix[: len(rest)] += rest


def load(name, max_len=None, fade=0.05, rate=1.0, onset=True):
    """Load assets/sfx/<name>; trims to its first transient so it lands exactly where placed."""
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", str(SFX / name), "-ac", "2", "-ar", str(SR), "-f", "f32le", "-"],
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


def mtof(m):
    return 440.0 * 2 ** ((m - 69) / 12)


# ---------------- instruments (all synthesized: the reel owns its music) ----------------
def dhol_bass(pitch=1.0):
    t = np.arange(int(0.45 * SR)) / SR
    f = (62 + 40 * np.exp(-t * 30)) * pitch
    body = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t / 0.22)
    thump = lp(rng.standard_normal(len(t)), 300) * np.exp(-t / 0.015) * 0.6
    s = np.tanh(2.2 * (body + thump))
    return st(s / np.abs(s).max())


def dhol_slap(bright=1.0):
    t = np.arange(int(0.18 * SR)) / SR
    s = bp(rng.standard_normal(len(t)), 1200, 5200) * np.exp(-t / (0.035 * bright)) + np.sin(2 * np.pi * 330 * t) * np.exp(-t / 0.06) * 0.7
    return st(s / np.abs(s).max(), pan=0.15)


def taal(open_=True):
    L = 0.6 if open_ else 0.12
    t = np.arange(int(L * SR)) / SR
    s = sum(np.sin(2 * np.pi * f * t + rng.uniform(0, 6)) * rng.uniform(0.5, 1) for f in (3150, 4270, 5590, 6830, 8110, 9420))
    s = s * 0.25 + hp(rng.standard_normal(len(t)), 6000) * 0.5
    s *= np.exp(-t / (0.22 if open_ else 0.035))
    return st(s / np.abs(s).max(), pan=-0.25)


def gogona(f0=98.0, length=0.32):
    """Bamboo jaw harp twang — the Bihu signature."""
    t = np.arange(int(length * SR)) / SR
    saw = 2 * ((f0 * t) % 1) - 1
    out = bp(saw, 300, 2400, order=1)
    sweep = np.sin(2 * np.pi * np.cumsum(450 + 1600 * np.clip(t / (length * 0.7), 0, 1)) / SR)
    s = out * (0.6 + 0.4 * sweep) * np.exp(-t / (length * 0.45)) * np.minimum(1, t / 0.003)
    return st(s / np.abs(s).max(), pan=0.3)


def banhi(m, dur=0.15, soft=1.0):
    """Bamboo flute lead: crisp breath chiff (audible onset), near-sine tone, short room tail."""
    L = dur + 0.5
    t = np.arange(int(L * SR)) / SR
    f0 = mtof(m) * (1 - 0.004 * np.exp(-t / 0.01)) * (1 + 0.007 * np.sin(2 * np.pi * 5.2 * t) * np.clip((t - 0.1) / 0.12, 0, 1))
    ph = 2 * np.pi * np.cumsum(f0) / SR
    tone = np.sin(ph) + 0.22 * np.sin(2 * ph) + 0.07 * np.sin(3 * ph)
    breath = bp(rng.standard_normal(len(t)), mtof(m) * 1.5, min(mtof(m) * 4, 15000)) * (0.08 + 0.6 * np.exp(-t / 0.012))
    env = np.clip(t / (0.008 * soft), 0, 1) * (0.8 + 0.2 * np.exp(-t / 0.05)) * np.where(t < dur, 1.0, np.exp(-(t - dur) / 0.06))
    dry = (tone + breath) * env
    ir_t = np.arange(int(0.45 * SR)) / SR
    wet = np.convolve(dry, lp(rng.standard_normal(len(ir_t)) * np.exp(-ir_t / 0.12), 4000))[: len(dry)]
    s = dry + 0.10 * wet / (np.abs(wet).max() + 1e-9) * np.abs(dry).max()
    return st(s / (np.abs(s).max() + 1e-9), pan=0.1)


def bell(m, L=1.6):
    t = np.arange(int(L * SR)) / SR
    s = sum(a * np.sin(2 * np.pi * mtof(m) * r * t) * np.exp(-t / d) for r, a, d in [(1, 1, 0.9), (2.0, 0.4, 0.5), (3.01, 0.25, 0.3), (4.2, 0.12, 0.2)])
    return st(s * np.minimum(1, t / 0.004) / np.abs(s).max(), pan=-0.15)


def gong(L=3.0, base=98.0):
    t = np.arange(int(L * SR)) / SR
    s = sum(a * np.sin(2 * np.pi * base * r * t) * np.exp(-t / d) for r, a, d in [(1.0, 1.0, 2.4), (1.48, 0.7, 1.9), (2.11, 0.55, 1.5), (2.83, 0.4, 1.2), (3.9, 0.3, 0.9)])
    s = s * np.minimum(1, t / 0.006) + bp(rng.standard_normal(len(t)), 300, 3000) * np.exp(-t / 0.04) * 0.5
    return st(s / np.abs(s).max())


def ching(base=2600.0, L=0.9):
    """Silver / metal ring (coins, ornaments, bell-metal)."""
    t = np.arange(int(L * SR)) / SR
    s = sum(a * np.sin(2 * np.pi * base * r * t) * np.exp(-t / d) for r, a, d in [(1, 1, 0.5), (1.51, 0.6, 0.35), (2.17, 0.45, 0.25), (2.93, 0.3, 0.18)])
    s += hp(rng.standard_normal(len(t)), 5000) * np.exp(-t / 0.006) * 0.6
    return st(s / np.abs(s).max(), pan=0.15)


def anvil():
    t = np.arange(int(0.7 * SR)) / SR
    s = sum(a * np.sin(2 * np.pi * f * t) * np.exp(-t / d) for f, a, d in [(820, 1, 0.3), (1340, 0.7, 0.22), (2210, 0.5, 0.15), (3050, 0.3, 0.1)])
    s += lp(rng.standard_normal(len(t)), 400) * np.exp(-t / 0.02) * 1.2
    return st(np.tanh(1.5 * s))


def zap(up=True):
    """X-ray / scan sweep."""
    t = np.arange(int(0.16 * SR)) / SR
    f = (300 + 2100 * (t / 0.16)) if up else (2400 - 2100 * (t / 0.16))
    s = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t / 0.08) + hp(rng.standard_normal(len(t)), 4000) * np.exp(-t / 0.03) * 0.3
    return st(s / np.abs(s).max(), pan=-0.1)


def sword():
    t = np.arange(int(1.2 * SR)) / SR
    ring = sum(a * np.sin(2 * np.pi * f * t) * np.exp(-t / d) for f, a, d in [(2150, 1.0, 0.6), (3420, 0.7, 0.45), (5230, 0.5, 0.3), (7910, 0.35, 0.2)])
    s = 0.5 * ring + 0.6 * hp(rng.standard_normal(len(t)), 3000) * np.exp(-t / 0.04)
    return st(s / np.abs(s).max())


def tick(f=1800):
    t = np.arange(int(0.05 * SR)) / SR
    return st(np.sin(2 * np.pi * f * t) * np.exp(-t / 0.01))


BASS, BASS_LO, SLAP, SLAP_SOFT = dhol_bass(), dhol_bass(0.8), dhol_slap(), dhol_slap(0.6)
TAAL_O, TAAL_C = taal(True), taal(False)
PAT = {"bass": [0, 6, 8, 11, 14], "slap": [2, 4, 10, 12, 13, 15], "taal_o": [4, 12], "taal_c": [2, 6, 10, 14]}


def groove_bar(t0, level=0.0, light=False, double=False):
    """One 2-s bar of the Bihu groove (the user's favourite bed). light=True drops the bass."""
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
    """Dhol roll over the second half of the bar starting at t0 — lands on 0.0 when the reel loops."""
    for k, s in enumerate(range(8, 16)):
        place(SLAP, t0 + s * S16, -10 + k * 0.7)
    for s in (8, 12, 14, 15):
        place(BASS, t0 + s * S16, -4)


# shared foley (Mixkit free licence + ghost-editor library, copied into assets/sfx by new_reel.sh)
whoosh = load("whoosh-cine.wav", onset=False)
whoosh2 = load("whoosh-2.wav", onset=False)
hit = load("cinematic-cine-hit.wav", onset=False)
riser = load("cinematic-rumble-riser.wav", onset=False)
pop = load("pop-2.wav")
kanh = load("bowl-clang.mp3", 3.0, fade=1.2)        # bell-metal clang: the series' reveal sound
thud = load("dish-wood.mp3", 0.5)
stones = load("stones-fall.mp3", 0.3, fade=0.1)


def pop_at(rate):
    return load("pop-2.wav", rate=rate)


# ======================= ARRANGEMENT (reel-008 muga) =======================
L = 0.0667  # snap landing offset


def crunch():
    t = np.arange(int(0.09 * SR)) / SR
    x = bp(rng.standard_normal(len(t)), 1800, 7000) * np.exp(-t / 0.02) * (0.6 + 0.4 * np.sign(np.sin(2 * np.pi * 90 * t)))
    return st(x / np.abs(x).max())


def clack():
    t = np.arange(int(0.08 * SR)) / SR
    x = np.sin(2 * np.pi * 900 * t) * np.exp(-t / 0.012) + lp(rng.standard_normal(len(t)), 1500) * np.exp(-t / 0.006)
    return st(x / np.abs(x).max(), pan=0.2)


CR, CL = crunch(), clack()
water = load("water-pour.mp3", 0.9, fade=0.3)
splash = load("water-splash.mp3", 0.8)
sparkle = load("sparkle.mp3", 1.0)

# hook: golden shimmer, worm pops out
place(BASS_LO, 0.0, -3)
place(ching(2600, 0.6), 0.0, -14)
place(pop_at(1.1), 0.42 + L, -4)
place(gogona(110, 0.3), 0.42 + L, -8)
place(gogona(98, 0.4), 0.78, -6)
# card
place(whoosh2, 0.95, -10)
for k, t in enumerate([1.25, 1.45, 1.65, 1.85]):
    place(pop_at(1.0 + 0.1 * k), t, -11)
groove_bar(1.0, light=True)
# 1 · leaves sprout
for k in range(6):
    place(pop_at(1.0 + 0.12 * k), 2.5 + k * 0.083 + L, -9)
# 2 · worm crawls in, three bites, grows
place(whoosh, 3.0, -12)
for k, t in enumerate([3.25, 3.5, 3.75]):
    place(CR, t, -5)
    place(pop_at(0.9 + 0.1 * k), t + L, -12)
# 3 · cocoon closes, silk wraps on sixteenths
place(pop_at(0.8), 4.2 + L, -6)
place(ching(2200, 0.5), 4.2 + L, -12)
for k in range(8):
    place(tick(1400 + 90 * k), 4.25 + k * 0.0625 + L, -12)
# 4 · reeling whirr while the spool fills
place(whoosh, 4.72, -12)
for k in range(16):
    place(tick(1100 + 25 * k), 4.85 + k * 0.0625, -17)
# 5 · loom: one clack per woven row, then the muga border
for k in range(22):
    place(CL, 5.8 + k * 0.0625 + L, -9 if k % 2 else -7)
place(whoosh2, 7.15, -11)
place(thud, 7.35, -5)
# "সোণালী মুগা!"
place(BASS_LO, 7.5, -1)
for k, m in enumerate((74, 78, 81)):
    place(bell(m + 12, 1.4), 7.5 + 0.12 + k * 0.03, -10)
place(sparkle, 7.55, -10)
groove_bar(3.0, light=True)
groove_bar(5.0, light=True)
groove_bar(7.0)
# reveal: four real photos on the beat
place(kanh, 8.0, -3); place(hit, 8.0, -5); place(BASS_LO, 8.0, 0)
for t in (9.0, 10.0, 11.0):
    place(thud, t, -4); place(BASS, t, -3)
for t in (8.0, 9.0, 10.0, 11.0):
    place(pop_at(1.0), t + 0.32, -9)
tt = 11.75
for k in range(14):
    place(tick(1500 + 45 * k), tt, -17)
    tt += 0.6 / 14
place(pop, 12.35, -6); place(thud, 12.37, -4)
groove_bar(9.0)
gogona_riff(9.0, -10)
groove_bar(11.0)
# end: wash, sparkle on three beats, unravel into the golden ball
place(splash, 13.0, -6); place(water, 13.05, -9)
for i in range(6):
    place(pop_at(1.2 + 0.1 * i), 13.15 + i * 0.07, -14)
for k, t in enumerate([13.75, 14.0, 14.25]):
    place(ching(2400 * 2 ** (k * 4 / 12), 0.7), t + L, -7)
place(sparkle, 14.25, -11)
place(whoosh2, 14.5, -9)
for k in range(12):
    place(tick(2400 - 80 * k), 14.5 + k * 0.04, -15)
place(pop_at(0.9), 15.0 + L, -5); place(BASS, 15.0 + L, -4)
place(ching(2600, 0.6), 15.3, -13)
groove_bar(13.0, light=True)
groove_bar(15.0, light=True)
fill(14.0)

# ======================= MASTER =======================
mix /= np.abs(mix).max() + 1e-9
mix *= db(-1.0)
tmp = OUT.with_suffix(".raw.wav")
OUT.parent.mkdir(parents=True, exist_ok=True)
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
