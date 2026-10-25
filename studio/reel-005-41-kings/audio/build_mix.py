"""Soundtrack for reel 005 (41 reigns): the reel-002 v1 sound —
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
rng = np.random.default_rng(2024)
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


def mtof(m):
    return 440.0 * 2 ** ((m - 69) / 12)


def kali(m, dur=0.2, bright=1.0):
    """Long brass court trumpet: two detuned saws, filter opens on attack, scoop up, vibrato."""
    L = dur + 0.15
    t = np.arange(int(L * SR)) / SR
    f0 = mtof(m) * (1 - 0.03 * np.exp(-t / 0.025)) * (1 + 0.006 * np.sin(2 * np.pi * 5.8 * t) * np.clip((t - 0.08) / 0.1, 0, 1))
    out = np.zeros_like(t)
    for det in (-0.004, 0.004):
        ph = 2 * np.pi * np.cumsum(f0 * (1 + det)) / SR
        out += 2 * ((ph / (2 * np.pi)) % 1) - 1
    # time-varying lowpass approximated in blocks
    y = np.zeros_like(out)
    blk = 480
    for k in range(0, len(out), blk):
        tt = k / SR
        fc = (600 + 3400 * bright * (1 - np.exp(-tt / 0.03))) * (0.75 + 0.25 * np.exp(-tt / 0.3))
        seg = out[max(0, k - 2048): k + blk]
        y[k:k + blk] = lp(seg, min(fc, 16000), 2)[-len(y[k:k + blk]):]
    env = np.minimum(1, t / 0.015) * np.where(t < dur, 1.0, np.exp(-(t - dur) / 0.05))
    s = np.tanh(1.6 * y * env)
    return st(s / (np.abs(s).max() + 1e-9), pan=0.12)


def banhi(m, dur=0.22, soft=1.0):
    """Bamboo flute: near-sine tone, breath chiff on attack, vibrato after onset, short room tail."""
    L = dur + 0.5
    t = np.arange(int(L * SR)) / SR
    f0 = mtof(m) * (1 - 0.004 * np.exp(-t / 0.01)) * (1 + 0.007 * np.sin(2 * np.pi * 5.2 * t) * np.clip((t - 0.1) / 0.12, 0, 1))
    ph = 2 * np.pi * np.cumsum(f0) / SR
    tone = np.sin(ph) + 0.22 * np.sin(2 * ph) + 0.07 * np.sin(3 * ph)
    breath = bp(rng.standard_normal(len(t)), mtof(m) * 1.5, min(mtof(m) * 4, 15000)) * (0.08 + 0.6 * np.exp(-t / 0.012))
    env = np.clip(t / (0.008 * soft), 0, 1) * (0.8 + 0.2 * np.exp(-t / 0.05)) * np.where(t < dur, 1.0, np.exp(-(t - dur) / 0.06))
    dry = (tone + breath) * env
    ir_t = np.arange(int(0.45 * SR)) / SR
    ir = rng.standard_normal(len(ir_t)) * np.exp(-ir_t / 0.12)
    wet = np.convolve(dry, lp(ir, 4000))[: len(dry)]
    s = dry + 0.10 * wet / (np.abs(wet).max() + 1e-9) * np.abs(dry).max()
    return st(s / (np.abs(s).max() + 1e-9), pan=0.1)


def bell(m, L=1.6):
    t = np.arange(int(L * SR)) / SR
    f = mtof(m)
    s = sum(a * np.sin(2 * np.pi * f * r * t) * np.exp(-t / d) for r, a, d in [(1, 1, 0.9), (2.0, 0.4, 0.5), (3.01, 0.25, 0.3), (4.2, 0.12, 0.2)])
    s *= np.minimum(1, t / 0.004)
    return st(s / np.abs(s).max(), pan=-0.15)


def nagara(pitch=1.0, L=0.7):
    t = np.arange(int(L * SR)) / SR
    f = (82 + 60 * np.exp(-t * 18)) * pitch
    body = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t / 0.32)
    skin = bp(rng.standard_normal(len(t)), 150, 1800) * np.exp(-t / 0.025) * 0.7
    s = np.tanh(1.8 * (body + skin))
    return st(s / np.abs(s).max(), pan=-0.08)


def gong(L=3.0, base=98.0):
    t = np.arange(int(L * SR)) / SR
    s = np.zeros_like(t)
    for r, a, d in [(1.0, 1.0, 2.4), (1.48, 0.7, 1.9), (2.11, 0.55, 1.5), (2.83, 0.4, 1.2), (3.9, 0.3, 0.9), (5.2, 0.2, 0.6)]:
        s += a * np.sin(2 * np.pi * base * r * t * (1 + 0.002 * np.sin(2 * np.pi * 0.7 * t))) * np.exp(-t / d)
    s *= np.minimum(1, t / 0.006)
    s += bp(rng.standard_normal(len(t)), 300, 3000) * np.exp(-t / 0.04) * 0.5
    return st(s / np.abs(s).max())


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
ZUP, ZDN = zap(True), zap(False)
SWORD = sword()

# ---------------- arrangement (16 s) ----------------
REIGNS = [(0, None)] * 5 + [(1, None), (1, None)] + [(0, None)] * 4 + [(1, None), (0, None), (1, None), (0, None),
          (0, "long"), (0, None), (1, None), (1, None), (0, None), (0, None), (1, None), (1, None), (0, None),
          (1, "short"), (0, None), (1, None), (1, None)] + [(0, None)] * 10 + [(0, "again1"), (0, None), (0, "again2")]
assert len(REIGNS) == 41, len(REIGNS)
t = 1.0
times = []
for i, (k, sp) in enumerate(REIGNS):
    times.append(t)
    t += (0.5 if i < 2 else 0.25) + (0.5 if sp else 0)
assert abs(t - 13.75) < 1e-6, t

# royal fanfare: each king plays the next arpeggio note; chords D G A Bm, one chord per 4 kings,
# and the whole line climbs an octave in the second half of the dynasty
CH = [[62, 66, 69, 74], [55, 59, 62, 67], [57, 61, 64, 69], [59, 62, 66, 71]]
GONG, GONG_HI = gong(3.0, 98.0), gong(2.2, 147.0)
NAG, NAG_LO = nagara(0.9, 0.6), nagara(0.7, 0.9)
KCACHE = {}


def horn(m, dur=0.18, g=-6, bright=1.0):
    """Lead voice (was the kali trumpet): now the banhi flute, legato."""
    key = (m, round(dur, 3), bright)
    if key not in KCACHE:
        KCACHE[key] = banhi(m, dur, 1.6 if bright < 1 else 1.0)
    return KCACHE[key]


# hook: gong, then the deck fans out on a quick horn flourish and snaps shut on the nagara
place(GONG, 0.0, -11)
place(NAG_LO, 0.0, -3)
for k, m in enumerate([62, 66, 69, 74, 78, 81]):
    place(horn(m, 0.06), 0.40 + k * 0.03, -9)
place(NAG, 0.72, -3)
place(horn(74, 0.25), 0.78, -6)

for i, ((kill, sp), ti) in enumerate(zip(REIGNS, times)):
    ch = CH[(i // 4) % 4]
    up = 12 if i >= 20 else 0
    note = ch[i % 4] + up
    LAND = ti + 0.0667  # the frame the card settles
    if kill:
        # dark hit: low nagara + a low horn growl a minor second below the chord root
        place(NAG_LO, ti + 0.1667, -2)  # with the stamp
        place(horn(ch[0] - 13, 0.18, bright=0.5), LAND, -7)
    else:
        place(horn(note, 0.15), LAND, -5)
    if sp:
        # surprise: a full chord blast and a gong
        for k, m in enumerate(ch[:3]):
            place(bell(m + 12), ti + 0.24 + k * 0.03, -9)
        place(GONG_HI if sp != "short" else GONG, ti + 0.24, -12)
        place(NAG_LO, ti + 0.24, -1)


# end: the ask lands on a held D-major fanfare and a gong; then the deck riffles back to Sukaphaa
place(GONG, 13.75, -11)
place(horn(74, 1.0), 13.75, -6)
for k, m in enumerate((62, 66, 69)):
    place(bell(m + 12, 2.0), 13.75 + k * 0.04, -10)
place(NAG_LO, 13.75, -1)
groove_bar(13.0, level=-4, light=True)
place(whoosh2, 15.0, -9)
for k, m in enumerate([74, 69, 66]):
    place(horn(m, 0.08), 15.0 + k * 0.06, -10)
place(NAG, 15.2, -3)
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
