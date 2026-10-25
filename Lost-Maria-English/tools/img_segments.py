"""Find text segments in flat UI panel images (LostMaria 12 px style).

python -I tools/img_segments.py <png> [--debug out.png]          -> prints JSON segments
Library use: segments(img) -> list of dicts {line, seg, x0, y0, x1, y1, color, align}

Rules (palette-index based, image stays in P mode):
- background = the panel grey (191,191,175); shadow = (170,170,154)
- text colours: dark (34,34,34), greys, and border-red pixels that are NOT part of a
  straight run >= RUN px (borders are long straight runs; glyph strokes are short)
- lines = rows of text pixels grouped into bands; a band splits into segments at
  horizontal gaps > GAP px
- align = right when the line's last segment ends flush (<= 16 px) against the panel's
  right inner edge (prices, "G", status words), else left
"""
import sys, json
from PIL import Image

BG = (191, 191, 175)
SHADOW = (170, 170, 154)
REDS = {(119, 32, 28), (89, 22, 18)}
RUN = 13
GAP = 7


def rgb(pal, i):
    return tuple(pal[i * 3:i * 3 + 3])


def text_mask(im):
    pal = im.getpalette()
    W, H = im.size
    px = im.load()
    colors = {}
    for y in range(H):
        for x in range(W):
            colors.setdefault(px[x, y], rgb(pal, px[x, y]))
    bg_idx = {i for i, c in colors.items() if c == BG}
    sh_idx = {i for i, c in colors.items() if c == SHADOW}
    red_idx = {i for i, c in colors.items() if c in REDS}
    textlike = {i for i, c in colors.items()
                if i not in bg_idx | sh_idx | red_idx and max(c) - min(c) < 40 and 20 <= c[0] <= 150}
    # structural reds: long straight runs
    struct = [[False] * W for _ in range(H)]
    for y in range(H):
        x = 0
        while x < W:
            if px[x, y] in red_idx:
                x2 = x
                while x2 < W and px[x2, y] in red_idx:
                    x2 += 1
                if x2 - x >= RUN:
                    for k in range(x, x2):
                        struct[y][k] = True
                x = x2
            else:
                x += 1
    for x in range(W):
        y = 0
        while y < H:
            if px[x, y] in red_idx:
                y2 = y
                while y2 < H and px[x, y2] in red_idx:
                    y2 += 1
                if y2 - y >= RUN:
                    for k in range(y, y2):
                        struct[k][x] = True
                y = y2
            else:
                y += 1
    # red pixels within 2 px of the image edge are frame (short strips have short borders)
    for y in range(H):
        for x in range(W):
            if px[x, y] in red_idx and (x <= 1 or x >= W - 2 or y <= 1 or y >= H - 2):
                struct[y][x] = True
    # red pixels adjacent to structural reds are border bevel, not text
    def near_struct(x, y):
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                xx, yy = x + dx, y + dy
                if 0 <= xx < W and 0 <= yy < H and struct[yy][xx]:
                    return True
        return False
    mask = [[False] * W for _ in range(H)]
    for y in range(H):
        for x in range(W):
            i = px[x, y]
            if i in textlike:
                # text must sit on panel background: at least one bg/shadow neighbour
                mask[y][x] = True
            elif i in red_idx and not struct[y][x] and not near_struct(x, y):
                mask[y][x] = True
    return mask, bg_idx, sh_idx


def segments(im):
    mask, bg_idx, sh_idx = text_mask(im)
    W, H = im.size
    px = im.load()
    rows = [any(mask[y]) for y in range(H)]
    bands, y = [], 0
    while y < H:
        if rows[y]:
            y2 = y
            while y2 < H and (rows[y2] or (y2 + 1 < H and rows[y2 + 1] and y2 - y < 12)):
                y2 += 1
            bands.append((y, y2 - 1))
            y = y2
        else:
            y += 1
    segs = []
    for li, (y0, y1) in enumerate(bands):
        cols = [any(mask[y][x] for y in range(y0, y1 + 1)) for x in range(W)]
        x, si = 0, 0
        while x < W:
            if cols[x]:
                x2, last = x, x
                while x2 < W and x2 - last <= GAP:
                    if cols[x2]:
                        last = x2
                    x2 += 1
                cnt = {}
                for yy in range(y0, y1 + 1):
                    for xx in range(x, last + 1):
                        if mask[yy][xx]:
                            cnt[px[xx, yy]] = cnt.get(px[xx, yy], 0) + 1
                color = max(cnt, key=cnt.get)
                segs.append({"line": li, "seg": si, "x0": x, "y0": y0, "x1": last, "y1": y1, "color": color})
                si += 1
                x = last + 1
            else:
                x += 1
    # drop slivers (gauge-bar end caps etc.): <= 2 px wide or < 5 px tall
    segs = [s for s in segs if s["x1"] - s["x0"] >= 2 and s["y1"] - s["y0"] >= 4]
    for li in sorted({s["line"] for s in segs}):
        for k, s in enumerate([t for t in segs if t["line"] == li]):
            s["seg"] = k
    # alignment: right if a later segment on a line ends near the inner right edge
    for s in segs:
        same = [t for t in segs if t["line"] == s["line"]]
        right = False
        if s is same[-1] and len(same) > 1:
            # ends flush against the panel's inner border -> right-aligned value column.
            # (A "starts past the middle" rule used to say right too; it misfired on two-pane
            # windows whose right pane shares a row with the left title: shutdown/change menus.)
            y = max(s["y0"], s["y1"] - 3)
            x = s["x1"] + 1
            bgset = bg_idx | sh_idx
            while x < W and px[x, y] in bgset:
                x += 1
            right = (x - s["x1"]) <= 16 and x < W
        s["align"] = "right" if right else "left"
    return segs


def debug_image(im, segs, scale=4):
    from PIL import ImageDraw
    rgbim = im.convert("RGB").resize((im.width * scale, im.height * scale), Image.NEAREST)
    d = ImageDraw.Draw(rgbim)
    for s in segs:
        d.rectangle([s["x0"] * scale, s["y0"] * scale, (s["x1"] + 1) * scale - 1, (s["y1"] + 1) * scale - 1],
                    outline=(0, 160, 255) if s["align"] == "left" else (255, 0, 200))
        d.text((s["x0"] * scale + 1, s["y0"] * scale - 9), f'{s["line"]}.{s["seg"]}', fill=(0, 90, 255))
    return rgbim


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    im = Image.open(sys.argv[1])
    segs = segments(im)
    print(json.dumps(segs, ensure_ascii=False))
    if "--debug" in sys.argv:
        debug_image(im, segs).save(sys.argv[sys.argv.index("--debug") + 1])
