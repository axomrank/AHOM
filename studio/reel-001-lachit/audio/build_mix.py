"""Build the reel's soundtrack as one pre-mixed master.

Every hit is placed on the same clock as index.html, so cuts and sound land together.
Music: Mixkit "Epical Drums 02" (Grigoriy Nuzhny), Mixkit Stock Music Free License.
SFX: Mixkit free SFX (via the ghost-editor library) plus synthesized sword, drone and ticks.

Run: python3 audio/build_mix.py   (writes assets/audio/master.wav)
"""
import subprocess
from pathlib import Path

import numpy as np
from scipy.signal import butter, sosfilt

SR = 48000
DUR = 24.0
ROOT = Path(__file__).resolve().parent.parent
SFX = Path.home() / ".claude/skills/ghost-editor/library/sfx"
MUSIC = ROOT / "assets/audio/epical-drums-02.mp3"
OUT = ROOT / "assets/audio/master.wav"

rng = np.random.default_rng(1671)


def load(path):
    raw = subprocess.run(
        ["ffmpeg", "-v", "error", "-i", str(path), "-ac", "2", "-ar", str(SR), "-f", "f32le", "-"],
        capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.float32).reshape(-1, 2).copy()


def db(x):
    return 10 ** (x / 20)


def stereo(m):
    return np.stack([m, m], 1)


def lp(x, f, order=4):
    return sosfilt(butter(order, f, "lp", fs=SR, output="sos"), x, axis=0)


def hp(x, f, order=4):
    return sosfilt(butter(order, f, "hp", fs=SR, output="sos"), x, axis=0)


mix = np.zeros((int(DUR * SR), 2), np.float32)


def place(sig, t, gain_db=0.0, fade_out=0.0, max_len=None):
    s = sig.copy()
    if max_len is not None:
        s = s[: int(max_len * SR)]
    if fade_out:
        n = min(len(s), int(fade_out * SR))
        s[-n:] *= np.linspace(1, 0, n)[:, None]
    i = int(t * SR)
    j = min(len(mix), i + len(s))
    mix[i:j] += s[: j - i] * db(gain_db)


# ---------- synthesized sounds ----------
def sword(length=1.6):
    t = np.arange(int(length * SR)) / SR
    ring = np.zeros_like(t)
    for f, a, d in [(2150, 1.0, 0.9), (3420, 0.7, 0.7), (5230, 0.5, 0.5), (7910, 0.35, 0.35), (9640, 0.25, 0.3)]:
        glide = f * (1 + 0.004 * np.exp(-t * 8))
        ring += a * np.sin(2 * np.pi * np.cumsum(glide) / SR) * np.exp(-t / d)
    scrape = hp(rng.standard_normal(len(t)), 3000) * np.exp(-t / 0.05)
    s = 0.5 * ring + 0.6 * scrape
    s *= np.minimum(1, t / 0.004)
    return stereo(s / np.abs(s).max() * 0.8)


def drone(length):
    t = np.arange(int(length * SR)) / SR
    s = np.zeros_like(t)
    for f, a in [(73.42, 1.0), (110.0, 0.55), (146.83, 0.35), (36.71, 0.6)]:
        for det in (-0.25, 0.25):
            ph = 2 * np.pi * (f + det) * t
            s += a * (np.sin(ph) + 0.3 * np.sin(2 * ph) + 0.15 * np.sin(3 * ph))
    s *= 0.75 + 0.25 * np.sin(2 * np.pi * 0.25 * t)
    s = lp(s, 900)
    env = np.minimum(1, t / 0.02) * np.minimum(1, (length - t) / 0.4)
    s = s * env
    return stereo(s / np.abs(s).max() * 0.7)


def tick():
    t = np.arange(int(0.08 * SR)) / SR
    s = np.sin(2 * np.pi * 1350 * t) * np.exp(-t / 0.012) + 0.5 * np.sin(2 * np.pi * 620 * t) * np.exp(-t / 0.02)
    return stereo(s / np.abs(s).max() * 0.7)


cine_hit = load(SFX / "cinematic-cine-hit.wav")
deep_boom = load(SFX / "cinematic-deep-boom.wav")
heartbeat = load(SFX / "cinematic-heartbeat.wav")
rumble_riser = load(SFX / "cinematic-rumble-riser.wav")
drone_swell = load(SFX / "cinematic-drone-swell.wav")
whoosh = load(SFX / "whoosh-cine.wav")
whoosh_big = load(SFX / "whoosh-2.wav")
riser = load(SFX / "riser-1.wav")
impact = load(SFX / "impact-2.wav")
flash = load(SFX / "cinematic-film-flash.wav")

# ---------- music: two windows of the same track ----------
music = load(MUSIC)


def music_window(reel_start, reel_end, track_at_reel_start, gain_db, fade_in=0.0, fade_out=0.0):
    a = int(track_at_reel_start * SR)
    seg = music[a: a + int((reel_end - reel_start) * SR)].copy()
    if fade_in:
        n = int(fade_in * SR)
        seg[:n] *= np.linspace(0, 1, n)[:, None]
    if fade_out:
        n = int(fade_out * SR)
        seg[-n:] *= np.linspace(1, 0, n)[:, None]
    place(seg, reel_start, gain_db)


# Drums enter on the 1671 seal (reel 3.50 = track 2.12, its first hit) and stop dead at the cut to black.
music_window(3.50, 12.00, 2.12, -3.0, fade_out=0.06)
# Second window: the track's own breath at 57 s, its drop at 58.05 lands on the victory slam (reel 17.00).
music_window(16.00, 24.00, 57.05, -2.0)

# ---------- S1 hook 0.0-2.0 ----------
place(cine_hit, 0.00, -1.0)
place(drone(3.6), 0.00, -12.0)
place(whoosh, 0.86, -4.0)
place(sword(), 1.00, -6.0)
place(flash, 1.00, -10.0)
# ---------- S2 "why?" 2.0-3.5 ----------
place(heartbeat, 2.05, 0.0)
place(heartbeat, 2.55, -2.0)
place(rumble_riser, 0.50, -9.0, max_len=3.0)
# ---------- S3 1671 / Mughals 3.5-6.0 ----------
place(deep_boom, 3.50, -2.0)
place(whoosh_big, 3.98, -12.0)
# ---------- S4 one night 6.0-8.5: wood-block clock ----------
for k in range(5):
    place(tick(), 6.0 + k * 0.5, -10.0)
place(whoosh, 7.18, -8.0)
# ---------- S5 the uncle 8.5-10.5 ----------
place(impact, 8.50, -8.0)
place(heartbeat, 9.50, -1.0)
place(heartbeat, 10.00, -1.0)
# ---------- S6 Lachit sees 10.5-12.5 ----------
place(whoosh, 10.45, -6.0)
place(sword(), 11.95, -3.0)
place(deep_boom, 12.00, 0.0)
# ---------- S7 the line 12.5-16.5 ----------
place(drone(4.2), 12.45, -10.0)
place(drone_swell, 12.50, -8.0)
place(riser, 15.30, -8.0)
# ---------- S8 dawn + Saraighat 16.5-20.5 ----------
place(cine_hit, 17.00, -2.0)
place(whoosh_big, 16.80, -10.0)
place(deep_boom, 18.50, -6.0)
# ---------- S9 name seal + loop 20.5-24.0 ----------
place(deep_boom, 20.50, -3.0)
place(whoosh, 23.40, -6.0)

# ---------- master ----------
peak = np.abs(mix).max()
mix = mix / peak * db(-1.0)
tmp = OUT.with_suffix(".raw.wav")
import wave
with wave.open(str(tmp), "wb") as w:
    w.setnchannels(2)
    w.setsampwidth(2)
    w.setframerate(SR)
    w.writeframes((np.clip(mix, -1, 1) * 32767).astype("<i2").tobytes())
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(tmp),
                "-af", "loudnorm=I=-12:TP=-1.0:LRA=9", "-ar", str(SR), str(OUT)], check=True)
tmp.unlink()
print("wrote", OUT)
