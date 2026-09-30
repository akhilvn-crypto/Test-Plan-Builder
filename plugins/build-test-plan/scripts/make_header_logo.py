"""Regenerates the bundled placeholder header logo. Replace assets/header-logo.png with the real Emvigo logo when available."""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

out = Path(__file__).resolve().parent.parent / "skills" / "test-plan-template" / "assets" / "header-logo.png"
img = Image.new("RGBA", (420, 110), (255, 255, 255, 0))
d = ImageDraw.Draw(img)
try:
    font = ImageFont.truetype("arialbd.ttf", 56)
except OSError:
    font = ImageFont.load_default()
d.text((8, 22), "EMVIGO", fill=(31, 56, 100, 255), font=font)
img.save(out)
print(out)
