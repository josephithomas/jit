"""
Create assets/icon.ico from the Titus logo PNG.
Run once before building the EXE:

    python make_icon.py
"""
from __future__ import annotations
import sys
from pathlib import Path

try:
    from PIL import Image
except ImportError:
    print("[ERROR] Pillow is required. Run:  pip install Pillow")
    sys.exit(1)

ASSETS = Path(__file__).resolve().parent / "assets"
SRC = ASSETS / "titus-logo-256.png"
if not SRC.exists():
    SRC = ASSETS / "titus-logo.png"
DST = ASSETS / "icon.ico"

if not SRC.exists():
    print(f"[ERROR] Logo not found. Expected one of:")
    print(f"  {ASSETS / 'titus-logo-256.png'}")
    print(f"  {ASSETS / 'titus-logo.png'}")
    sys.exit(1)

ASSETS.mkdir(parents=True, exist_ok=True)

img = Image.open(SRC)
if img.mode != "RGBA":
    img = img.convert("RGBA")

sizes = [(256, 256), (128, 128), (64, 64), (48, 48), (32, 32), (16, 16)]
img.save(DST, format="ICO", sizes=sizes)
print(f"[OK] Created {DST}")
print(f"     Source : {SRC.name}")
print(f"     Sizes  : {[s[0] for s in sizes]}")
