"""Generate the Buranji page textures: sanchipat bark paper, grain tile, torn ink-edge masks.

Run: python3 tools_make_textures.py   (writes into assets/tex/)
"""
from pathlib import Path

import numpy as np
from PIL import Image
from scipy.ndimage import gaussian_filter, zoom

OUT = Path(__file__).resolve().parent / "assets/tex"
OUT.mkdir(parents=True, exist_ok=True)
rng = np.random.default_rng(1671)
W, H = 1080, 1920


def noise(h, w, sy, sx):
    return gaussian_filter(rng.standard_normal((h, w)), (sy, sx))


def norm(a):
    a = a - a.min()
    return a / a.max()


# ---- bark paper: horizontal fibres, blotches, darker burnt edges ----
fib = norm(noise(H, W, 0.8, 40) + 0.6 * noise(H, W, 2, 120) + 0.25 * noise(H, W, 0.5, 8))
blot = norm(noise(H // 8, W // 8, 6, 6))
blot = zoom(blot, 8, order=1)[:H, :W]
yy, xx = np.mgrid[0:H, 0:W]
ex = np.clip(np.minimum(xx, W - 1 - xx) / 220, 0, 1)
ey = np.clip(np.minimum(yy, H - 1 - yy) / 300, 0, 1)
edge = (ex * ey) ** 0.5
lum = 0.95 + 0.07 * (fib - 0.5) + 0.06 * (blot - 0.5)
lum *= 0.62 + 0.38 * edge
paper = np.array([0.957, 0.890, 0.745])  # warm sanchipat
ink = np.array([0.110, 0.071, 0.047])    # #1c120c
rgb = ink + (paper - ink) * np.clip(lum, 0, 1)[..., None] ** 0.9
# faint hengul stain
stain = norm(noise(H // 4, W // 4, 20, 20))
stain = zoom(stain, 4, order=1)[:H, :W]
rgb += np.array([0.05, -0.01, -0.03]) * np.clip(stain - 0.6, 0, 1)[..., None] * 2
Image.fromarray((np.clip(rgb, 0, 1) * 255).astype(np.uint8)).save(OUT / "bark.jpg", quality=92)

# ---- dark page (ink side) for the quote ----
dl = 0.10 + 0.05 * (fib - 0.5) + 0.04 * (blot - 0.5)
dl *= 0.6 + 0.4 * edge
drgb = np.array([0.43, 0.26, 0.17]) * np.clip(dl, 0, 1)[..., None] * 2.2
Image.fromarray((np.clip(drgb, 0, 1) * 255).astype(np.uint8)).save(OUT / "bark-dark.jpg", quality=92)

# ---- grain tile (alpha noise) ----
g = rng.standard_normal((512, 512))
g = norm(gaussian_filter(g, 0.6))
a = (np.abs(g - 0.5) * 2) ** 2 * 120
tile = np.zeros((512, 512, 4), np.uint8)
tile[..., :3] = np.where(g[..., None] > 0.5, 255, 20)
tile[..., 3] = np.clip(a, 0, 255).astype(np.uint8)
Image.fromarray(tile, "RGBA").save(OUT / "grain.png")


# ---- torn ink-edge masks (white = visible) ----
def torn(w, h, seed, inset=34, rough=26):
    r = np.random.default_rng(seed)
    m = np.zeros((h, w))
    def edge_profile(n):
        p = gaussian_filter(r.standard_normal(n), 18) * rough * 3 + gaussian_filter(r.standard_normal(n), 3) * rough * 0.6
        return inset + p
    top, bot = edge_profile(w), edge_profile(w)
    lef, rig = edge_profile(h), edge_profile(h)
    Y, X = np.mgrid[0:h, 0:w]
    inside = (Y > top[None, :]) & (Y < h - bot[None, :]) & (X > lef[:, None]) & (X < w - rig[:, None])
    m[inside] = 1
    # ink bleed: soften plus speckle near the edge
    soft = gaussian_filter(m, 3)
    speck = gaussian_filter(r.standard_normal((h, w)), 1.2)
    m = np.clip(soft * 1.4 - 0.2 + (speck * 0.35) * (soft * (1 - soft)) * 4, 0, 1)
    img = np.zeros((h, w, 4), np.uint8)
    img[..., :3] = 255
    img[..., 3] = (m * 255).astype(np.uint8)
    return Image.fromarray(img, "RGBA")


torn(1000, 860, 11).save(OUT / "torn-a.png")
torn(1000, 1240, 12).save(OUT / "torn-b.png")
torn(1080, 1300, 13, inset=10, rough=30).save(OUT / "torn-c.png")
print("textures ->", OUT)
