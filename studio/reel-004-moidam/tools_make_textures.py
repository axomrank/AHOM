"""Gamosa cloth texture (handloom off-white with visible weave) and a grain tile.

Run: python3 tools_make_textures.py   (writes assets/tex/)
"""
from pathlib import Path

import numpy as np
from PIL import Image
from scipy.ndimage import gaussian_filter

OUT = Path(__file__).resolve().parent / "assets/tex"
OUT.mkdir(parents=True, exist_ok=True)
rng = np.random.default_rng(2026)
W, H = 1080, 1920

yy, xx = np.mgrid[0:H, 0:W]
# warp and weft threads, slightly irregular
warp = 0.5 + 0.5 * np.sin(2 * np.pi * (xx + 1.5 * gaussian_filter(rng.standard_normal(W), 30)[None, :] * 8) / 5.0)
weft = 0.5 + 0.5 * np.sin(2 * np.pi * (yy + 1.5 * gaussian_filter(rng.standard_normal(H), 30)[:, None] * 8) / 5.0)
weave = 0.5 * warp + 0.5 * weft
slub = gaussian_filter(rng.standard_normal((H, W)), (0.6, 25))  # thick-thin yarn streaks
blot = gaussian_filter(rng.standard_normal((H, W)), 60)
lum = 0.955 + 0.022 * (weave - 0.5) + 0.03 * slub + 0.25 * blot
base = np.array([0.965, 0.945, 0.905])  # unbleached cotton
rgb = base[None, None, :] * np.clip(lum, 0, 1.05)[..., None]
Image.fromarray((np.clip(rgb, 0, 1) * 255).astype(np.uint8)).save(OUT / "cloth.jpg", quality=92)

g = gaussian_filter(rng.standard_normal((512, 512)), 0.6)
g = (g - g.min()) / (g.max() - g.min())
tile = np.zeros((512, 512, 4), np.uint8)
tile[..., :3] = np.where(g[..., None] > 0.5, 255, 20)
tile[..., 3] = np.clip((np.abs(g - 0.5) * 2) ** 2 * 110, 0, 255).astype(np.uint8)
Image.fromarray(tile, "RGBA").save(OUT / "grain.png")
print("textures ->", OUT)
