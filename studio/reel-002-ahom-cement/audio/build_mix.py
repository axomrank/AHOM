"""Soundtrack for reel 002 (v2): an earworm loop + kitchen foley.

Music is synthesized here (the reel owns it): a 4-bar pentatonic hook on a reedy
"pepa"-style lead, 808 bass, punchy kick/clap/hats with dhol slaps, offbeat chord stabs
with sidechain pump. 120 BPM, bar = 2 s, 11 bars = 22 s, and bar 10 ends with a fill
that lands back on bar 0, so the music loops as seamlessly as the picture.

Run: python3 audio/build_mix.py   (writes assets/audio/master.wav)
"""
import subprocess
import wave
from pathlib import Path

import numpy as np
from scipy.signal import butter, sosfilt, fftconvolve

SR = 48000
DUR = 22.0
BAR = 2.0
S16 = BAR / 16
ROOT = Path(__file__).resolve().parent.parent
SFX = ROOT / "assets/sfx"
LIB = Path.home() / ".claude/skills/ghost-editor/library/sfx"
OUT = ROOT / "assets/audio/master.wav"
rng = np.random.default_rng(7)

N = int(DUR * SR)
music = np.zeros((N, 2), np.float32)   # gets sidechain + reverb
drums = np.zeros((N, 2), np.float32)
foley = np.zeros((N, 2), np.float32)


def db(x):
    return 10 ** (x / 20)


def filt(x, kind, f, order=2):
    return sosfilt(butter(order, f, kind, fs=SR, output="sos"), x, axis=0)


def st(m, pan=0.0):
    return np.stack([m * (1 - max(pan, 0)), m * (1 + min(pan, 0))], 1).astype(np.float32)


def put(bus, sig, t, gain=0.0):
    i = int(round(t * SR)) % N  # wrap: anything spilling past 22 s lands at the start (loop-safe)
    s = sig * db(gain)
    j = min(N, i + len(s))
    bus[i:j] += s[: j - i]
    if i + len(s) > N:
        rest = s[N - i:]
        bus[: len(rest)] += rest[: N]


def mtof(m):
    return 440.0 * 2 ** ((m - 69) / 12)


# ---------------- instruments ----------------
def kick():
    t = np.arange(int(0.4 * SR)) / SR
    f = 48 + 110 * np.exp(-t * 38)
    s = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t / 0.18)
    s += filt(rng.standard_normal(len(t)), "hp", 2000) * np.exp(-t / 0.004) * 0.4
    return st(np.tanh(1.8 * s) / 0.95)


def clap():
    t = np.arange(int(0.35 * SR)) / SR
    n = filt(rng.standard_normal(len(t)), "bandpass", [900, 6000])
    env = np.zeros_like(t)
    for d in (0.0, 0.011, 0.022):
        env += np.where(t >= d, np.exp(-(t - d) / 0.008), 0)
    env += np.where(t >= 0.03, np.exp(-(t - 0.03) / 0.11), 0) * 0.7
    s = n * env
    return st(s / np.abs(s).max())


def hat(open_=False):
    t = np.arange(int((0.25 if open_ else 0.06) * SR)) / SR
    s = filt(rng.standard_normal(len(t)), "hp", 7500) * np.exp(-t / (0.08 if open_ else 0.015))
    return st(s / np.abs(s).max(), pan=-0.2)


def slap():
    t = np.arange(int(0.18 * SR)) / SR
    s = filt(rng.standard_normal(len(t)), "bandpass", [1200, 5000]) * np.exp(-t / 0.03)
    s += np.sin(2 * np.pi * 320 * t) * np.exp(-t / 0.05) * 0.8
    return st(s / np.abs(s).max(), pan=0.25)


def dhol_low():
    t = np.arange(int(0.4 * SR)) / SR
    f = 75 + 45 * np.exp(-t * 25)
    s = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t / 0.2)
    return st(np.tanh(2 * s), pan=0.1)


def lead(m, dur):
    """Reedy horn (pepa-like): scoop up into the note, nasal formants, vibrato after onset."""
    L = dur + 0.12
    t = np.arange(int(L * SR)) / SR
    f0 = mtof(m)
    scoop = 1 - 0.06 * np.exp(-t / 0.03)
    vib = 1 + 0.008 * np.sin(2 * np.pi * 5.5 * t) * np.clip((t - 0.12) / 0.15, 0, 1)
    ph = 2 * np.pi * np.cumsum(f0 * scoop * vib) / SR
    saw = 2 * ((ph / (2 * np.pi)) % 1) - 1
    sq = np.sign(np.sin(ph))
    s = 0.6 * saw + 0.4 * sq
    s = filt(s, "bandpass", [600, 3200], 2) + 0.5 * filt(s, "bandpass", [1100, 1600], 2)
    env = np.minimum(1, t / 0.012) * np.where(t < dur, 1.0, np.exp(-(t - dur) / 0.04))
    s *= env * (0.85 + 0.15 * np.exp(-t / 0.08))
    return st(s / (np.abs(s).max() + 1e-9) * 0.9, pan=0.08)


def pluck(m, dur=0.22):
    t = np.arange(int(dur * SR)) / SR
    f0 = mtof(m)
    s = sum(np.sin(2 * np.pi * f0 * k * t) / k ** 1.3 for k in range(1, 7))
    s *= np.exp(-t / 0.09)
    return st(s / np.abs(s).max())


def stab(chord, dur=0.2):
    t = np.arange(int(dur * SR)) / SR
    s = np.zeros_like(t)
    for m in chord:
        for det in (-0.12, 0.12):
            ph = 2 * np.pi * mtof(m) * (1 + det / 100) * t
            s += 2 * ((ph / (2 * np.pi)) % 1) - 1
    s = filt(s, "lowpass", 2600) * np.exp(-t / 0.09) * np.minimum(1, t / 0.004)
    return st(s / np.abs(s).max())


def bass808(m, dur):
    t = np.arange(int((dur + 0.05) * SR)) / SR
    f = mtof(m) * (1 + 0.5 * np.exp(-t / 0.02))
    s = np.sin(2 * np.pi * np.cumsum(f) / SR)
    s = np.tanh(2.5 * s) * np.minimum(1, t / 0.005) * np.where(t < dur, 1, np.exp(-(t - dur) / 0.03)) * np.exp(-t / 1.2)
    return st(s / np.abs(s).max())


def riser(L):
    t = np.arange(int(L * SR)) / SR
    n = rng.standard_normal(len(t))
    out = np.zeros_like(t)
    seg = 2048
    for k in range(0, len(t), seg):
        fc = 400 + 9000 * (k / len(t)) ** 2
        out[k:k + seg] = filt(n[k:k + seg + 512], "bandpass", [fc * 0.7, min(fc * 1.3, 20000)], 1)[:len(out[k:k + seg])]
    out *= (t / L) ** 2
    return st(out / np.abs(out).max())


KICK, CLAP, HAT, OHAT, SLAP, DLOW = kick(), clap(), hat(), hat(True), slap(), dhol_low()

# ---------------- the hook (4 bars, D major pentatonic) ----------------
A = [(0, 81, 2), (2, 83, 1), (3, 81, 1), (4, 78, 2), (6, 74, 2), (8, 76, 1), (9, 78, 1), (10, 81, 3), (14, 78, 1), (15, 76, 1)]
B = [(0, 74, 2), (3, 74, 1), (4, 76, 2), (6, 78, 1), (7, 81, 3), (10, 83, 2), (12, 86, 3), (15, 83, 1)]
C = [(0, 81, 2), (2, 78, 2), (4, 76, 2), (6, 74, 5), (12, 69, 1), (13, 71, 1), (14, 74, 1), (15, 76, 1)]
HOOK = [A, B, A, C]
CHORDS = [[62, 66, 69], [59, 62, 66], [55, 59, 62], [57, 61, 64]]   # D  Bm  G  A
ROOTS = [38, 35, 31, 33]

LEAD_CACHE = {}


def play_lead(bar_t, notes, gain=-4, octave=0):
    for s, m, ln in notes:
        key = (m + octave, ln)
        if key not in LEAD_CACHE:
            LEAD_CACHE[key] = lead(m + octave, ln * S16 * 0.92)
        put(music, LEAD_CACHE[key], bar_t + s * S16, gain)


def play_beat(bar_t, full=True, hats16=False, kick_only=False):
    for b in range(4):
        put(drums, KICK, bar_t + b * 0.5, -1)
    if kick_only:
        return
    put(drums, CLAP, bar_t + 0.5, -5)
    put(drums, CLAP, bar_t + 1.5, -5)
    step = 1 if hats16 else 2
    for s in range(0, 16, step):
        put(drums, OHAT if s in (6, 14) else HAT, bar_t + s * S16, -15 if s % 4 else -12)
    if full:
        for s in (3, 7, 10, 11, 15):
            put(drums, SLAP, bar_t + s * S16, -9)
        put(drums, DLOW, bar_t + 11 * S16, -6)


def play_harmony(bar_t, idx, stabs=True):
    put(music, bass808(ROOTS[idx], 0.7), bar_t, -3)
    put(music, bass808(ROOTS[idx], 0.3), bar_t + 10 * S16, -5)
    put(music, bass808(ROOTS[idx] + 12 if idx != 2 else ROOTS[idx] + 7, 0.25), bar_t + 14 * S16, -7)
    if stabs:
        for s in (2, 6, 10, 14):
            put(music, stab(CHORDS[idx]), bar_t + s * S16, -13)


def fill(bar_t):
    """Last half-bar: dhol and slap roll that lands on bar 0 (the hook) when the reel loops."""
    for k, s in enumerate(range(8, 16)):
        put(drums, SLAP, bar_t + s * S16, -10 + k * 0.6)
    for s in (8, 11, 13, 14, 15):
        put(drums, DLOW, bar_t + s * S16, -6)


# ---------------- arrangement (bar k starts at 2k s) ----------------
#  0      hook alone over kick — catchy from frame 0
#  1-4    full groove, hook A B A C
#  5      breakdown (mix): stabs + plucks, riser, bell, no kick
#  6-7    drop (bricks + reveal), hats 16ths, hook an octave up on bar 7
#  8-9    full, hook
#  10     stripped cadence + fill back to bar 0
for k in range(11):
    t = k * BAR
    h = HOOK[k % 4]
    idx = k % 4
    if k == 0:
        play_beat(t, kick_only=True)
        play_harmony(t, idx, stabs=False)
        play_lead(t, h, -3)
    elif 1 <= k <= 4:
        play_beat(t)
        play_harmony(t, idx)
        play_lead(t, h, -5)
    elif k == 5:
        for s in (2, 6, 10, 14):
            put(music, stab(CHORDS[idx]), t + s * S16, -11)
        for s, m, ln in HOOK[1]:
            put(music, pluck(m), t + s * S16, -9)
        put(music, riser(2.0), t, -10)
    elif k in (6, 7):
        play_beat(t, hats16=True)
        play_harmony(t, idx)
        play_lead(t, h, -5, octave=12 if k == 7 else 0)
    elif k in (8, 9):
        play_beat(t)
        play_harmony(t, idx)
        play_lead(t, h, -5)
    else:
        play_beat(t, full=False)
        play_harmony(t, idx, stabs=False)
        play_lead(t, C[:4], -5)
        fill(t)

# sidechain pump on the music bus, keyed from the kicks (beats where a kick plays)
pump = np.ones(N, np.float32)
kick_times = [k * BAR + b * 0.5 for k in range(11) if k != 5 for b in range(4)]
tt = np.arange(int(0.25 * SR)) / SR
curve = 1 - 0.55 * np.exp(-tt / 0.08)
for kt in kick_times:
    i = int(kt * SR)
    j = min(N, i + len(curve))
    pump[i:j] = np.minimum(pump[i:j], curve[: j - i])
music *= pump[:, None]

# short room reverb on the music bus
ir_t = np.arange(int(0.9 * SR)) / SR
ir = rng.standard_normal((len(ir_t), 2)) * np.exp(-ir_t / 0.22)[:, None]
ir = filt(ir, "lowpass", 5000)
wet = np.stack([fftconvolve(music[:, c], ir[:, c])[:N] for c in (0, 1)], 1)
music = music + 0.10 * wet / (np.abs(wet).max() + 1e-9) * np.abs(music).max()


# ---------------- foley (same cue points as the picture) ----------------
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


egg_place = load(SFX / "dish-wood.mp3", 0.5)
egg_break = load(SFX / "egg-break.mp3", 1.0)
egg_break2 = load(SFX / "egg-break-2.mp3", 0.9)
pour = load(SFX / "gravel-pour.mp3", 1.0)
fish = load(SFX / "fish-flap.mp3", 0.7)
splash = load(SFX / "water-splash.mp3", 0.9)
crumble = load(SFX / "stone-avalanche.mp3", 0.9)
syrup = load(SFX / "water-pour.mp3", 0.9, rate=0.7)
stir = load(SFX / "stirring.mp3", 1.6)
bell = load(SFX / "cook-bell.mp3", 1.1)
stones = load(SFX / "stones-fall.mp3", 0.35, fade=0.12)
kanh = load(SFX / "bowl-clang.mp3", 3.0, fade=1.2)
whoosh = load(LIB / "whoosh-cine.wav", onset=False)
hit = load(LIB / "cinematic-cine-hit.wav", onset=False)
pop = load(LIB / "pop-2.wav")

put(foley, egg_place, 0.0, -8)
put(foley, egg_break, 0.50, -2)
put(foley, whoosh, 1.42, -10)
for t, layers in [(3.0, [(pour, -5)]), (4.0, [(egg_break2, -3)]), (5.0, [(pour, -4)]),
                  (6.0, [(fish, -6), (splash, -5)]), (7.0, [(crumble, -5)]), (8.0, [(syrup, -4)])]:
    for sig, g in layers:
        put(foley, sig, t + 0.35, g)
    put(foley, pop, t + 0.42, -12)
put(foley, stir, 9.0, -4)
put(foley, bell, 10.75, -2)
for k in range(10):
    put(foley, stones, 12.0 + 0.25 * k, -9)
put(foley, stones, 14.5, -5)
put(foley, hit, 15.0, -4)
put(foley, kanh, 15.0, -5)
put(foley, pop, 17.95, -8)
put(foley, whoosh, 21.12, -10)
put(foley, egg_place, 21.5, -6)

# ---------------- master ----------------
mix = music * db(-1) + drums * db(-2) + foley * db(0)
mix /= np.abs(mix).max() + 1e-9
mix *= db(-1.0)
tmp = OUT.with_suffix(".raw.wav")
with wave.open(str(tmp), "wb") as w:
    w.setnchannels(2)
    w.setsampwidth(2)
    w.setframerate(SR)
    w.writeframes((np.clip(mix, -1, 1) * 32767).astype("<i2").tobytes())
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(tmp), "-af",
                "acompressor=threshold=-16dB:ratio=3:attack=4:release=90,loudnorm=I=-12:TP=-1.0:LRA=7",
                "-ar", str(SR), str(OUT)], check=True)
tmp.unlink()
print("wrote", OUT)
