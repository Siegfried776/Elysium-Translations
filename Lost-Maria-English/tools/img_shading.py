"""Frame shading our text erase wiped (found by the developer, v1.21 image fixes).

Panels have a 1 px shading line (the palette's shade colour) inside their dark-red border. Erasing the
Japanese text by segment box also erased that line wherever a box touched it. A pixel is damaged when
the original has the shade colour there, sits next to a border pixel, and our image has background.

python -I tools/img_shading.py [img_root]       report damaged images (default build/img)
Library: restore(orig_im, new_im) -> number of pixels put back (in place, palette images).
"""
import sys, os
from PIL import Image

SHADE, BG = (170, 170, 154), (191, 191, 175)
BORDER = {(119, 32, 28), (89, 22, 18)}


def damaged(orig, new):
    """[(x, y)] of wiped shading pixels (orig/new: RGB images of the same size)."""
    o, n = orig.load(), new.load()
    W, H = orig.size
    out = []
    for y in range(H):
        for x in range(W):
            if o[x, y] == SHADE and n[x, y] == BG and any(
                    0 <= x + dx < W and 0 <= y + dy < H and o[x + dx, y + dy] in BORDER
                    for dx, dy in ((0, -1), (-1, 0), (0, 1), (1, 0))):
                out.append((x, y))
    return out


def restore(orig_im, new_im):
    if orig_im.size != new_im.size:
        return 0
    pts = damaged(orig_im.convert("RGB"), new_im.convert("RGB"))
    if not pts:
        return 0
    pn = new_im.load()
    if new_im.mode == "P":
        pal = new_im.getpalette()
        shade = next(i for i in range(len(pal) // 3) if tuple(pal[3 * i:3 * i + 3]) == SHADE)
    else:
        shade = SHADE
    for x, y in pts:
        pn[x, y] = shade
    return len(pts)


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    base = os.path.abspath(sys.argv[1]) if len(sys.argv) > 1 else os.path.join(root, "build", "img")
    hit = total = 0
    for folder in sorted(os.listdir(base)):
        d = os.path.join(base, folder)
        if not os.path.isdir(d):
            continue
        for f in sorted(os.listdir(d)):
            o = os.path.join(root, "original", "data", folder, f)
            if not f.endswith(".png") or not os.path.exists(o):
                continue
            a, b = Image.open(o).convert("RGB"), Image.open(os.path.join(d, f)).convert("RGB")
            if a.size != b.size:
                continue
            n = len(damaged(a, b))
            total += 1
            if n:
                hit += 1
                print(f"{n:5}  {folder}/{f}")
    print(f"{hit} of {total} same-size images have wiped frame shading")
