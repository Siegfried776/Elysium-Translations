"""Typeset English into LostMaria UI panel images.

Library: typeset(im, segs, texts, font) -> new P image
  segs  from img_segments.segments(); texts: list parallel to segs, each None (keep) or a string
        (a string may contain "\\n" to spill onto following lines at the panel's line pitch).
CLI test:  python -I tools/img_typeset.py <png> <out.png> "<text for seg 0>" "<seg 1>" ...  ("-" = keep)

Erase: the segment box (+1 px for the shadow) is filled with the panel background, but only
pixels that are background / shadow / text colours (borders are never touched).
Draw: MS Gothic 12 px bitmap glyphs (no anti-aliasing), shadow at +1,+1 in the shadow colour,
text in the segment's own colour. Left segments start at the original x; right segments end
at the original right edge.
"""
import sys, os
from PIL import Image, ImageDraw, ImageFont
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import img_segments as S

FONT_PATH = r"C:\Windows\Fonts\msgothic.ttc"


def load_font(index=0, size=12):
    return ImageFont.truetype(FONT_PATH, size, index=index)


def palette_index(im, rgb):
    pal = im.getpalette()
    used = set(im.getdata()) if hasattr(im, "getdata") else set()
    for i in range(len(pal) // 3):
        if tuple(pal[i * 3:i * 3 + 3]) == rgb and (i in used or True):
            return i
    return None


def text_width(font, s):
    return int(round(font.getlength(s)))


def render_mask(font, s):
    """1-bit glyph mask for string s; returns (mask Image 'L', top offset of ink)."""
    w = max(1, text_width(font, s)) + 2
    m = Image.new("L", (w, 20), 0)
    d = ImageDraw.Draw(m)
    d.fontmode = "1"
    # MS PGothic's 12 px bitmap 'g' is a cramped two-storey glyph that reads like an '8'
    # (play-test 2026-10-24). Draw a single-storey g instead: the 'q' (same 6 px advance)
    # with its descender turned into a hook.
    d.text((0, 0), s.replace("g", "q"), font=font, fill=255)
    px = m.load()
    for i, ch in enumerate(s):
        if ch != "g":
            continue
        x0 = text_width(font, s[:i])
        ink = [(x, y) for x in range(x0, min(w, x0 + 6)) for y in range(20) if px[x, y]]
        if not ink:
            continue
        b = max(y for _, y in ink)
        r = max(x for x, y in ink if y == b)
        px[r, b] = 0
        for x in range(r - 3, r):
            px[x, b] = 255
    return m


_CAP = {}
OVERFLOW = []   # (segment, line, width, available) for reporting
ERASE = "∅"     # translation value meaning: erase this segment, draw nothing
PAD = "␠"       # hard 4 px space inside a translation (not stripped by wrap)


def available_width(im, s, bg, sh, mask):
    """Pixels from the segment's x0 to the first border pixel on its right (minus a 2 px margin)."""
    px = im.load()
    W = im.width
    y = max(s["y0"], min(s["y1"] - 3, im.height - 1))
    x = s["x1"] + 1
    # stop at the next text (any row of the band) or at a border pixel
    while x < W and px[x, y] in (bg, sh) and not any(mask[yy][x] for yy in range(s["y0"], s["y1"] + 1)):
        x += 1
    if s["align"] == "right":
        # right-aligned: room extends leftwards to the previous text or border
        x2 = s["x0"] - 1
        while x2 > 0 and (px[x2, y] in (bg, sh)) and not mask[y][x2]:
            x2 -= 1
        return s["x1"] - x2 - 2
    return x - s["x0"] - 2


def clear_boxes(mask, segs):
    """Copy of a text mask with the given segments' boxes cleared (they will be erased)."""
    m = [row[:] for row in mask]
    for s in segs:
        for y in range(s["y0"], s["y1"] + 1):
            for x in range(s["x0"], s["x1"] + 1):
                m[y][x] = False
    return m


def wrap(font, text, width):
    words, lines, cur = text.split(" "), [], ""
    for w in words:
        cand = (cur + " " + w).strip()
        if cur and text_width(font, cand) > width:
            lines.append(cur)
            cur = w
        else:
            cur = cand
    if cur:
        lines.append(cur)
    return lines


def cap_bottom(font):
    key = id(font)
    if key not in _CAP:
        _CAP[key] = render_mask(font, "H").getbbox()[3] - 1
    return _CAP[key]


def widen(im, new_w):
    """Widen a banner/panel symmetrically by repeating its middle column (keeps borders)."""
    W, H = im.size
    if new_w <= W:
        return im
    mid = W // 2
    out = Image.new("P", (new_w, H))
    out.putpalette(im.getpalette())
    if "transparency" in im.info:
        out.info["transparency"] = im.info["transparency"]
    out.paste(im.crop((0, 0, mid, H)), (0, 0))
    col = im.crop((mid, 0, mid + 1, H))
    for x in range(mid, mid + (new_w - W)):
        out.paste(col, (x, 0))
    out.paste(im.crop((mid, 0, W, H)), (mid + new_w - W, 0))
    return out


def typeset(im, segs, texts, font, line_pitch=None, y_adjust=0):
    im = im.copy()
    px = im.load()
    W, H = im.size
    pal = im.getpalette()
    colors = {px[x, y] for y in range(H) for x in range(W)}
    bg = next((i for i in colors if tuple(pal[i * 3:i * 3 + 3]) == S.BG), None)
    sh = next((i for i in colors if tuple(pal[i * 3:i * 3 + 3]) == S.SHADOW), None)
    mask, _, _ = S.text_mask(im)
    if bg is None and segs:
        # non-standard panel (e.g. a CG): background = commonest colour around the text,
        # shadow = commonest colour diagonally below text pixels
        from collections import Counter
        s0 = segs[0]
        around = Counter(px[x, y] for y in range(max(0, s0["y0"] - 2), min(H, s0["y1"] + 3))
                         for x in range(max(0, s0["x0"] - 2), min(W, s0["x1"] + 3)) if not mask[y][x])
        bg = around.most_common(1)[0][0]
        diag = Counter(px[x + 1, y + 1] for y in range(s0["y0"], min(H - 1, s0["y1"] + 1))
                       for x in range(s0["x0"], min(W - 1, s0["x1"] + 1)) if mask[y][x] and not mask[y + 1][x + 1])
        cand = [c for c, _ in diag.most_common() if c != bg]
        sh = cand[0] if cand else None
    if line_pitch is None:
        ys = sorted({s["y0"] for s in segs})
        diffs = [b - a for a, b in zip(ys, ys[1:]) if b - a > 6]
        line_pitch = min(diffs) if diffs else 16
    texts = ["" if t == ERASE else t for t in texts]
    # pass 1: erase every segment that gets replaced (so later erases can't clip earlier text)
    for s, t in zip(segs, texts):
        if t is None:
            continue
        for y in range(max(0, s["y0"] - 1), min(H, s["y1"] + 3)):
            for x in range(max(0, s["x0"] - 1), min(W, s["x1"] + 3)):
                i = px[x, y]
                if mask[y][x] or i == sh or i == bg:
                    px[x, y] = bg
    # text that stays (segments not being replaced) is what limits the available width
    mask = clear_boxes(mask, [s for s, t in zip(segs, texts) if t is not None])
    # pass 2: draw
    for s, t in zip(segs, texts):
        if not t:
            continue
        avail = available_width(im, s, bg, sh, mask)
        lines = []
        for para in t.split("\n"):
            lines += wrap(font, para, avail) if para else [""]
        for k, line in enumerate(lines):
            if not line:
                continue
            # "␠" = hard 4 px space (survives wrapping), e.g. to keep a right-aligned label clear
            # of a number the game draws at runtime: shop stock "x␠␠␠␠" + digit
            pad = 4 * line.count(PAD)
            line = line.replace(PAD, "")
            if text_width(font, line) + pad > avail:
                OVERFLOW.append((s, line, text_width(font, line) + pad, avail))
            m = render_mask(font, line)
            bbox = m.getbbox() or (0, 0, 1, 1)
            w = text_width(font, line) + pad
            # left-aligned: line up the first inked column, not the glyph box ('A', 'm' carry a blank
            # left column in this font, so lines starting with them looked indented; play-test)
            x = s["x0"] - bbox[0] if s["align"] == "left" else s["x1"] + 1 - w
            # baseline: capital bottom 2 px above the JP band bottom (room for descenders),
            # but never let descenders leave the image
            y = s["y1"] - 2 - cap_bottom(font) + y_adjust + k * line_pitch
            y = min(y, H - 1 - (bbox[3] - 1))
            mp = m.load()
            for yy in range(m.height):
                for xx in range(m.width):
                    if mp[xx, yy]:
                        X, Y = x + xx, y + yy
                        if sh is not None and 0 <= X + 1 < W and 0 <= Y + 1 < H and px[X + 1, Y + 1] == bg:
                            px[X + 1, Y + 1] = sh
            for yy in range(m.height):
                for xx in range(m.width):
                    if mp[xx, yy]:
                        X, Y = x + xx, y + yy
                        if 0 <= X < W and 0 <= Y < H:
                            px[X, Y] = s["color"]
    return im


def typeset_block(im, text, font, keep=(), line_pitch=None):
    """Card text: erase every segment except indexes in `keep`, then flow `text` (\\n = forced
    break) as one wrapped block starting at the first erased segment, at the JP line pitch."""
    segs = S.segments(im)
    body = [s for i, s in enumerate(segs) if i not in keep]
    if not body:
        return im
    texts = [None if i in keep else "" for i in range(len(segs))]
    out = typeset(im, segs, texts, font)
    if line_pitch is None:
        ys = sorted({s["y1"] for s in body})
        diffs = [b - a for a, b in zip(ys, ys[1:]) if b - a > 6]
        line_pitch = min(diffs) if diffs else 15
    first = dict(body[0])
    first["align"] = "left"
    # one pseudo-segment; typeset() wraps it at the card's right border
    return typeset(out, [first], [text], font, line_pitch=line_pitch)


def plan_block(segs, t):
    """Split a block card into label slots and the flowing block.
    Lines that contain a kept segment (numbers) keep those segments; the other segments on such
    lines become label slots (their JP = that line's text minus digits, '/', spaces).
    Returns (label_slots [(seg_index, jp_label)], block_jp, first_block_seg_index or None)."""
    import re as _re
    keep = set(t.get("keep", []))
    lines = sorted({s["line"] for s in segs})
    jp_lines = [l for l in t.get("block", "").split("\n")]
    seg_lines = [l for l in lines if any(i not in keep for i, s in enumerate(segs) if s["line"] == l)]
    keep_lines = {segs[i]["line"] for i in keep if i < len(segs)}
    labels, block_lines, first = [], [], None
    for k, l in enumerate(seg_lines):
        jl = jp_lines[k] if k < len(jp_lines) else ""
        if l in keep_lines:
            idx = next(i for i, s in enumerate(segs) if s["line"] == l and i not in keep)
            lab = _re.sub(r"[0-9０-９/／\s　]+", "", jl)
            if lab:
                labels.append((idx, lab))
        else:
            if first is None:
                first = next(i for i, s in enumerate(segs) if s["line"] == l and i not in keep)
            block_lines.append(jl)
    # any JP lines beyond the segment lines belong to the block
    block_lines += jp_lines[len(seg_lines):]
    return labels, "\n".join(x for x in block_lines if x), first


def block_line_cap(segs, t, first):
    """Lines available to the flowing block before the first stat row (a line with a kept
    value box) that lies below the block's first line; large if there is none."""
    keep = set(t.get("keep", []))
    keep_lines = sorted({segs[i]["line"] for i in keep if i < len(segs)})
    start = segs[first]["line"]
    below = [l for l in keep_lines if l > start]
    if not below:
        return 99
    body = [s for i, s in enumerate(segs) if i not in keep]
    ys = sorted({s["y1"] for s in body})
    diffs = [b - a for a, b in zip(ys, ys[1:]) if b - a > 6]
    pitch = min(diffs) if diffs else 15
    y_stat = min(s["y0"] for s in segs if s["line"] == below[0])
    return max(1, (y_stat - segs[first]["y0"]) // pitch)


# Item-card stat numbers drawn exactly like the game draws Bloodrune's live number (CE0046 +
# work/event_patches.json): the game's own digit pictures (Picture/全角　N, 10x20), first digit in
# the leftmost slot, 7 px apart. Slot 1 is centred at screen x 228, y 53; the card's top-left is
# (159, 33) -> picture top-left in card coords (64, 10). (Play-test: "13" and "10" looked different.)
STAT_X, STAT_Y, STAT_PITCH = 228 - 5 - 159, 53 - 10 - 33, 7    # 7: the glyphs are 7 px with shadow


def typeset_equip(im, type_en, desc_en, stat_en, num, font, pitch=16):
    """Weapon/shield card in the gun-card layout (user, play-test): type line, description,
    then the stat line with the number in the game's digit pictures (num None = drawn live by
    the game, e.g. Bloodrune). Returns (image, index of the stat line)."""
    segs = S.segments(im)
    out = typeset(im, segs, [""] * len(segs), font)
    px = out.load()
    pal = out.getpalette()
    cols = {px[x, y] for y in range(out.height) for x in range(out.width)}
    bg = next(i for i in cols if tuple(pal[i * 3:i * 3 + 3]) == S.BG)
    sh = next((i for i in cols if tuple(pal[i * 3:i * 3 + 3]) == S.SHADOW), None)
    first = dict(min(segs, key=lambda s: (s["line"], s["x0"])), align="left")
    first["x0"] = min(s["x0"] for s in segs)
    mask, _, _ = S.text_mask(out)
    avail = available_width(out, first, bg, sh, mask)
    desc = []
    for para in desc_en.split("\n"):
        desc += wrap(font, para, avail)
    lines = [type_en] + desc + [stat_en]
    out = typeset(out, [first], ["\n".join(lines)], font, line_pitch=pitch)
    k = len(lines) - 1
    if num:
        paste_game_digits(out, num, STAT_X, first["y0"] + pitch * k)
    return out, k


def paste_game_digits(im, num, x0, y0):
    """Paste the game's digit pictures (dark + shadow pixels, transparent background) into a
    P-mode card, mapping their colours onto the card's palette."""
    import os
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    px, pal = im.load(), im.getpalette()
    idx = {}
    for k, ch in enumerate(num):
        d = Image.open(os.path.join(root, "original", "data", "Picture", f"全角　{ch}.png"))
        dp, dpal = d.load(), d.getpalette()
        for y in range(d.height):
            for x in range(d.width):
                i = dp[x, y]
                if i == 0:                                  # the picture's transparent colour
                    continue
                rgb = tuple(dpal[i * 3:i * 3 + 3])
                if rgb not in idx:
                    idx[rgb] = palette_index(im, rgb)
                X, Y = x0 + STAT_PITCH * k + x, y0 + y
                if idx[rgb] is not None and 0 <= X < im.width and 0 <= Y < im.height:
                    px[X, Y] = idx[rgb]


def typeset_card(im, t, labels_en, block_en, font, stat=None):
    """Block card with optional label slots (see plan_block).
    stat: {JP label: EN label}; a label line whose kept boxes are drawn full-width digits is re-set
    like the status screen: EN label left, the number in the font's half-width digits right-aligned
    at STAT_RIGHT (e.g. 盾：１０ -> 'Defense      10')."""
    segs = S.segments(im)
    keep = set(t.get("keep", []))
    labels, _, first = plan_block(segs, t)
    texts = [None if i in keep else "" for i in range(len(segs))]
    numbers = []
    for (idx, lab), e in zip(labels, labels_en):
        texts[idx] = e
        if stat and lab in stat:
            kept = sorted((i for i in keep if i < len(segs) and segs[i]["line"] == segs[idx]["line"]),
                          key=lambda i: segs[i]["x0"])
            nums = [read_digits(im, segs[i]) for i in kept]
            if kept and all(n is not None for n in nums):
                texts[idx] = stat[lab]
                for i in kept:
                    texts[i] = ""
                numbers.append((segs[idx], "".join(nums)))
    out = typeset(im, segs, texts, font)
    for s, num in numbers:
        paste_game_digits(out, num, STAT_X, s["y0"])      # on that label's own line
    if first is not None and block_en:
        body = [s for i, s in enumerate(segs) if i not in keep and s["line"] >= segs[first]["line"]]
        ys = sorted({s["y1"] for s in body})
        diffs = [b - a for a, b in zip(ys, ys[1:]) if b - a > 6]
        pitch = min(diffs) if diffs else 15
        anchors = anchored_lines(body)
        en_lines = block_en.split("\n")
        if anchors and len(anchors) == len(en_lines):
            # positional card (the mixing screens): the game draws item names and the cursor into
            # the gaps, so each English line goes exactly where its Japanese line was.
            # A description whose EN was rewrapped (line counts differ) flows as usual.
            for a, line in zip(anchors, en_lines):
                out = typeset(out, [a], [line], font, line_pitch=pitch)
            return out
        f = dict(segs[first]); f["align"] = "left"
        out = typeset(out, [f], [block_en], font, line_pitch=pitch)
    return out


_DIGITS = {}


def _digit_templates():
    """Dark-pixel masks of the game's own digit pictures, full-width (Picture/全角　N.png) and
    half-width (半角　N.png): {(set, digit): mask}."""
    if not _DIGITS:
        import os
        root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        for kind in ("全角", "半角"):
            for d in range(10):
                im = Image.open(os.path.join(root, "original", "data", "Picture", f"{kind}　{d}.png"))
                pal, px = im.getpalette(), im.load()
                pts = {(x, y) for y in range(im.height) for x in range(im.width)
                       if tuple(pal[px[x, y] * 3:px[x, y] * 3 + 3]) == (34, 34, 34)}
                x0, y0 = min(x for x, _ in pts), min(y for _, y in pts)
                _DIGITS[(kind, d)] = {(x - x0, y - y0) for x, y in pts}
    return _DIGITS


def read_digits(im, seg):
    """Read the full-width digits drawn in a segment (exact match against the game's digit
    pictures); returns the number as a string, or None if any glyph isn't a digit."""
    tpl = _digit_templates()
    pal, px = im.getpalette(), im.load()
    dark = lambda x, y: tuple(pal[px[x, y] * 3:px[x, y] * 3 + 3]) == (34, 34, 34)
    cols = [x for x in range(seg["x0"], seg["x1"] + 1) if any(dark(x, y) for y in range(seg["y0"], seg["y1"] + 1))]
    if not cols:
        return None
    groups, cur = [], [cols[0]]
    for x in cols[1:]:
        if x - cur[-1] > 2:
            groups.append(cur); cur = [x]
        else:
            cur.append(x)
    groups.append(cur)
    out = ""
    for g in groups:
        pts = {(x, y) for x in range(g[0], g[-1] + 1) for y in range(seg["y0"], seg["y1"] + 1) if dark(x, y)}
        x0, y0 = min(x for x, _ in pts), min(y for _, y in pts)
        norm = {(x - x0, y - y0) for x, y in pts}
        hit = {d for (_, d), m in tpl.items() if m == norm}
        if len(hit) != 1:
            return None
        out += str(hit.pop())
    return out


def anchored_lines(body):
    """For a block whose JP lines are spaced irregularly (gaps > 1.5x the line pitch), one
    pseudo-segment per JP line (left x of the line, its band); else None (free-flowing text)."""
    by_line = {}
    for s in body:
        by_line.setdefault(s["line"], []).append(s)
    rows = []
    for l in sorted(by_line):
        ss = by_line[l]
        rows.append({"line": l, "seg": 0, "x0": min(s["x0"] for s in ss), "x1": max(s["x1"] for s in ss),
                     "y0": min(s["y0"] for s in ss), "y1": max(s["y1"] for s in ss), "color": ss[0]["color"],
                     "align": "left"})
    if len(rows) < 2:
        return None
    gaps = [b["y1"] - a["y1"] for a, b in zip(rows, rows[1:])]
    if max(gaps) <= 1.5 * min(gaps):
        return None
    return rows


def tail_sprite(im, seg):
    """Cut the small trailing glyph cluster of a segment (e.g. the 'E' equipped mark):
    returns (sprite pixels {(dx,dy): idx}, width) taken from the last gap-separated cluster."""
    mask, _, _ = S.text_mask(im)
    px = im.load()
    cols = [x for x in range(seg["x0"], seg["x1"] + 1) if any(mask[y][x] for y in range(seg["y0"], seg["y1"] + 1))]
    if not cols:
        return {}, 0
    x = cols[-1]
    start = x
    while start - 1 >= seg["x0"] and (start - 1) in cols:
        start -= 1
    sprite = {}
    for yy in range(max(0, seg["y0"] - 1), min(im.height, seg["y1"] + 3)):
        for xx in range(start, min(im.width, x + 2)):
            if mask[yy][xx] or tuple(im.getpalette()[px[xx, yy] * 3:px[xx, yy] * 3 + 3]) == S.SHADOW:
                sprite[(xx - start, yy)] = px[xx, yy]
    return sprite, x - start + 1


def paste_sprite(im, sprite, x0):
    px = im.load()
    for (dx, y), i in sprite.items():
        if 0 <= x0 + dx < im.width:
            px[x0 + dx, y] = i
    return im


def typeset_status(im, text, font, bar=3, gap=2):
    """DATA-screen status word (状態　*.png, 38x12). The last `bar` columns are a slice of the
    panel's red border; the word sits left of it in dark (normal) or dark red (ailments) with a
    grey shadow. The game centres the picture on the border-side panel, so: keep the border slice
    at the right, right-align the English against it, and widen symmetrically (transparent index
    0 on both sides) so the game's centre still lands the slice on the border."""
    W, H = im.size
    px = im.load()
    pal = im.getpalette()
    from collections import Counter
    cnt = Counter(px[x, y] for y in range(H) for x in range(W - bar) if px[x, y] != 0)
    shadow = next(i for i in cnt if tuple(pal[i * 3:i * 3 + 3]) == S.SHADOW)
    color = next(i for i, _ in cnt.most_common() if i != shadow)
    m = render_mask(font, text)
    bx0, _, bx1, _ = m.getbbox()
    # end where the Japanese word ended (its shadow included): that column lines up with the
    # DATA screen's number column and the Likes value (user, play-test: "Normal" stuck out)
    right = max(x for x in range(W - bar) for y in range(H) if px[x, y] != 0)
    left_needed = 1
    ink_w = bx1 - bx0 + 1                          # incl. 1 px shadow
    e = max(0, left_needed - (right - ink_w + 1))
    out = Image.new("P", (W + 2 * e, H), 0)
    out.putpalette(pal)
    op = out.load()
    for x in range(W - bar, W):                    # the border slice, same screen position
        for y in range(H):
            op[x + e, y] = px[x, y]
    x0 = right + e - ink_w + 1 - bx0
    mp = m.load()
    for dy in (1, 0):                              # shadow pass then glyph pass
        for yy in range(m.height):
            for xx in range(m.width):
                if mp[xx, yy]:
                    X, Y = x0 + xx + dy, yy - 1 + dy  # 1 px up: descenders fit in the 12 px picture
                    if 0 <= X < out.width and 0 <= Y < H:
                        if dy == 0 or op[X, Y] == 0:
                            op[X, Y] = shadow if dy else color
    return out


def typeset_banner(im, text, font, min_margin=None, anchor_right=False):
    """Single-line call-out: erase all text, widen if needed, draw the English centred.
    anchor_right: the text ends where the JP ended and the picture grows only to the left
    (symmetric widening keeps the game's centre; the right-hand padding is transparent).
    For status words on the DATA screen, whose right edge touches the panel border."""
    segs = S.segments(im)
    if not segs:
        return im
    erased = typeset(im, segs, [""] * len(segs), font)
    color, y1 = segs[0]["color"], max(s["y1"] for s in segs)
    margin = min_margin if min_margin is not None else max(4, min(s["x0"] for s in segs))
    w = text_width(font, text)
    if anchor_right:
        right = max(s["x1"] for s in segs)
        e = max(0, margin - (right - w + 1))
        out = widen(erased, im.width + 2 * e)
        px = out.load()
        for y in range(out.height):              # widen() repeats the middle column; make the
            for x in range(im.width + e, out.width):   # new right-hand strip transparent
                px[x, y] = 0
        x0 = right + e - w + 1
        fake = [{"line": 0, "seg": 0, "x0": x0, "y0": y1 - 11, "x1": x0 + w - 1, "y1": y1, "color": color, "align": "left"}]
        return typeset(out, fake, [text], font)
    new_w = max(im.width, w + 2 * margin)
    if new_w % 2 != im.width % 2:
        new_w += 1          # keep the centre where it was
    out = widen(erased, new_w)
    x0 = (new_w - w) // 2
    fake = [{"line": 0, "seg": 0, "x0": x0, "y0": y1 - 11, "x1": x0 + w - 1, "y1": y1, "color": color, "align": "left"}]
    return typeset(out, fake, [text], font)


if __name__ == "__main__":
    src, out = sys.argv[1], sys.argv[2]
    texts = [None if a == "-" else a.replace("\\n", "\n") for a in sys.argv[3:]]
    im = Image.open(src)
    segs = S.segments(im)
    texts += [None] * (len(segs) - len(texts))
    font = load_font(int(os.environ.get("FONT_INDEX", "2")))
    res = typeset(im, segs, texts, font, y_adjust=int(os.environ.get("Y_ADJ", "0")))
    res.save(out)
    if os.environ.get("ZOOM"):
        z = int(os.environ["ZOOM"])
        res.convert("RGB").resize((res.width * z, res.height * z), Image.NEAREST).save(out.replace(".png", f"_x{z}.png"))
