"""Fit message text to the bundled proportional font (Ark Pixel 12px, play-test 2026-10-24).

Used by merge.py as the last step (after every overlay), so it always works on current text:
  1. screams: a run of 8+ identical letters is shortened until its line fits
  2. a line wider than the box moves its last word to the next line of the same box; the last
     line of a unit may open a new line only if its 4-line box has room (pagination never changes)
  3. lines that were centred with spaces (padding within 1.5 cells of centred in the old 6 px grid)
     are re-centred by pixel width
python -I tools/fontfit.py      -> report: lines changed, lines still too wide
"""
import os, re

root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FONT = os.path.join(root, "vendor", "fonts", "ark-pixel-12px-proportional", "x", "ark-pixel-12px-proportional-latin.ttf")
SEP = "␤"
LIMIT = 300                       # 50 cells x 6 px (measured with the built-in font)
CELL = 6
NAME_PX = 48                      # \N[n]: widest name the game can put there
CODE = re.compile(r"\\[Nn]\[\d+\]|\\[Vv]\[\d+\]|\\[A-Za-z]\[\d+\]|\\[.|!><^$_]")
LEAD = re.compile(r"^((?:\\[<>^.|!_$])*)( *)((?:\\[<>^.|!_$])*)")
_f = None


def font():
    global _f
    if _f is None:
        from PIL import ImageFont
        _f = ImageFont.truetype(FONT, 12)
    return _f


def px(line):
    f, w, pos = font(), 0.0, 0
    for m in CODE.finditer(line):
        w += f.getlength(line[pos:m.start()])
        c = m.group(0)
        w += NAME_PX if c[1] in "Nn" else f.getlength("999999") if c[1] in "Vv" else 0
        pos = m.end()
    return w + f.getlength(line[pos:])


def cells(s):
    s = CODE.sub("", s)
    return sum(1 if ord(c) < 0x80 or 0xFF61 <= ord(c) <= 0xFF9F else 2 for c in s)


def split_lead(line):
    """(codes before the padding, padding, rest); rest keeps any codes right after the padding."""
    m = LEAD.match(line)
    return m.group(1), m.group(2), line[m.end(2):]


def insert_word(line, word):
    """Put word at the start of a line's text: after its padding and any leading codes."""
    m = LEAD.match(line)
    rest = line[m.end():]
    return line[:m.end()] + word + (" " + rest if rest else "")


def is_centred(line):
    codes, pad, body = split_lead(line)
    if len(pad) < 3 or not body:
        return False
    return abs(len(pad) - (50 - cells(body)) / 2) <= 1.5   # else a deliberate indent


def shorten_scream(line):
    runs = [m for m in re.finditer(r"([A-Za-z])\1{7,}", line)]
    if not runs:
        return None
    m = max(runs, key=lambda m: len(m.group(0)))
    return line[:m.start()] + line[m.start() + 1:]


def fit_lines(lines, centred):
    """Wrap/shorten lines wider than LIMIT; `centred` (list of bools) is kept in step with lines."""
    lines, centred = list(lines), list(centred)
    i = 0
    while i < len(lines):
        guard = 0
        while px(lines[i]) > LIMIT and guard < 200:
            guard += 1
            s = shorten_scream(lines[i])
            if s is not None:
                lines[i] = s
                continue
            codes, pad, body = split_lead(lines[i])
            if len(pad) >= 2:                         # drop centring padding first (a single
                lines[i] = codes + pad[:-1] + body    # space after a code is layout: keep it)
                continue
            if " " not in body.strip():
                break
            head, word = body.rsplit(" ", 1)
            lines[i] = codes + pad + head
            box_end = (i // 4 + 1) * 4
            if i + 1 < len(lines) and i + 1 < box_end:
                lines[i + 1] = insert_word(lines[i + 1], word)
            elif i + 1 == len(lines) and len(lines) < box_end:
                # continuation line: no code of its own (the source's style for document boxes:
                # instant text stays on until \<), keep the indent
                lines.append((pad or (" " if codes else "")) + word)
                centred.append(centred[i])
            else:
                lines[i] = codes + pad + head + " " + word   # nowhere to go: leave it, reported
                break
        i += 1
    return lines, centred


END = re.compile(r"""[.!?)"'\]]+(?:\\[.|!^$_<>])*\s*$""")


def balance_runs(lines, centred):
    """Re-break sentences that run across lines so the lines come out even (user, play-test: the
    script was wrapped for the old 50-cell monospaced font, which left orphans like
    "...what this / curse really is...!" in the narrower proportional font). A run is a line whose
    text goes on in the next line (no sentence-final punctuation; next line starts lowercase,
    same leading codes/padding, same 4-line box). The run keeps its number of lines; breaks are
    chosen to minimise the widest line, then the spread. Centred lines are left alone."""
    out, i = list(lines), 0
    while i < len(out):
        j = i
        while (j + 1 < len(out) and (j + 1) // 4 == i // 4 and not centred[j] and not centred[j + 1]
               and out[j].strip() and not END.search(out[j])
               and split_lead(out[j + 1])[:2] == split_lead(out[i])[:2]
               and (re.match(r"[a-z0-9(]", split_lead(out[j + 1])[2])
                    or re.search(r"[,;:—](?:\\[.|!^$_<>])*\s*$", out[j]))):
            j += 1
        if j > i:
            n = j - i + 1
            codes, pad, _ = split_lead(out[i])
            words = " ".join(split_lead(out[k])[2] for k in range(i, j + 1)).split(" ")
            pre = codes + pad
            best = _best_breaks(words, n, [pre if k == 0 else codes + pad for k in range(n)])
            if best:
                out[i:j + 1] = best
        i = j + 1
    return out


# break quality: after punctuation is good; after a function word, or before a particle, is poor
WEAK_END = {"a", "an", "the", "to", "of", "in", "on", "at", "for", "with", "from", "by", "and", "or",
            "but", "is", "are", "was", "my", "your", "his", "her", "its", "our", "their", "this",
            "that", "these", "those", "I", "I'm", "I'll", "you", "we", "they", "he", "she", "it's", "can't"}
WEAK_START = {"out", "up", "off", "down", "away", "back", "over", "on", "in", "it", "him", "her",
              "them", "me", "us"}


def _break_cost(left, right):
    l = CODE.sub("", left).rstrip()
    lw = l.split(" ")[-1] if l else ""
    rw = CODE.sub("", right).lstrip().split(" ")[0]
    if l.count("(") > l.count(")"):
        return 60                                    # inside brackets: "(your / share: ...)"
    if len(lw) > 1 and len(rw) > 1 and lw.isupper() and rw.isupper() and not l.isupper():
        return 60                                    # a caps term in normal text: "BAD / END"
    if re.search(r"[,;:.!?)…—-]$", l):
        return -15
    return (25 if lw in WEAK_END else 0) + (25 if rw.strip(".,!?") in WEAK_START else 0)


def _best_breaks(words, n, prefixes):
    """Split words into exactly n lines (prefix per line): even widths (the widest line, then the
    spread) plus the quality of each break point (_break_cost, in px)."""
    from functools import lru_cache
    W = len(words)

    @lru_cache(None)
    def go(start, k):
        # returns ((max width, sum of squares, break cost), lines)
        if k == n - 1:
            line = prefixes[k] + " ".join(words[start:])
            w = px(line)
            return None if w > LIMIT else ((w, w * w, 0), [line])
        best = None
        for end in range(start + 1, W - (n - 1 - k) + 1):
            line = prefixes[k] + " ".join(words[start:end])
            w = px(line)
            if w > LIMIT:
                break
            rest = go(end, k + 1)
            if rest is None:
                continue
            (mw, sq, bc), rl = rest
            cand = (max(w, mw), w * w + sq, bc + _break_cost(" ".join(words[start:end]), " ".join(words[end:])))
            score = cand[0] + cand[2] + cand[1] / 20000
            if best is None or score < best[0]:
                best = (score, cand, [line] + rl)
        return best and (best[1], best[2])

    r = go(0, 0)
    return r[1] if r else None


DLG = re.compile(r'^(?:\\N\[\d+\]|[^\s\\][^:␤]{0,20}): ["(]')     # speaker as text or as \N[n]


def reflow_dialogue(lines, centred):
    """Speech boxes (one box, 'Name: "...' or 'Name: (...'): fill each line, sentences running on
    (user, play-test: two sentences running across three full lines read better than one sentence
    per line). No single-word last line. Returns
    None for anything else: centred or indented text, blank lines, multi-box units (moving text
    between boxes would shift their breaks)."""
    if not 2 <= len(lines) <= 4 or any(centred) or not DLG.match(lines[0]):
        return None
    if any(not l.strip() for l in lines) or any(split_lead(l)[0] or split_lead(l)[1] for l in lines[1:]):
        return None
    words = " ".join(l.strip() for l in lines).split()
    out, cur = [], ""                                # greedy fill: the fewest lines possible
    for w in words:
        t = cur + " " + w if cur else w
        if px(t) <= LIMIT or not cur:
            cur = t
        else:
            out.append(cur)
            cur = w
    out.append(cur)
    if len(out) > len(lines) or any(px(l) > LIMIT for l in out):
        return None
    # a click ending its line may take the box up to its 4 lines (one box: nothing shifts)
    return fill_segments(words, 4) or _fill_breaks(words, len(out)) or out


SENT_END = re.compile(r"""[.!?]["')]?(?:\\[.|!^$_<>])*\s*$""")


def reflow_indented(lines, centred):
    """Indented notes in one box (every line the same leading codes/padding, e.g. '\\> '): lines that
    form running prose are re-filled like speech (user, play-test: a three-line note took four
    lines for three lines of text). Line i joins i+1 only when the sentence runs on (no final
    punctuation, next line lowercase) or a sentence ends and the next begins (final . ! ?, next line
    capitalised); headings and list items (no final punctuation, next line capitalised) stay apart."""
    if not 2 <= len(lines) <= 4 or any(centred) or any(not l.strip() for l in lines):
        return None
    codes, pad, _ = split_lead(lines[0])
    if not (codes or pad) or any(split_lead(l)[:2] != (codes, pad) for l in lines):
        return None
    pre = codes + pad
    body = [split_lead(l)[2] for l in lines]
    groups, cur = [], [body[0]]
    for a, b in zip(body, body[1:]):
        # runs on: no final punctuation and the next line lowercase, or the line ends in , ; : —
        # whatever follows ("If he should ever err again, / I'll execute him", user play-test)
        runs_on = ((not END.search(a) and re.match(r"[a-z0-9(]", b))
                   or re.search(r"[,;:—](?:\\[.|!^$_<>])*\s*$", a))
        next_sentence = SENT_END.search(a) and re.match(r"""[A-Z"'(]""", b)
        if runs_on or next_sentence:
            cur.append(b)
        else:
            groups.append(cur)
            cur = [b]
    groups.append(cur)
    out = []
    for g in groups:
        if len(g) == 1:
            out.append(pre + g[0])
            continue
        words = " ".join(g).split()
        seg = fill_segments(words, len(g) + 4 - len(lines), pre)     # spare box lines may be used
        if seg:
            out += seg
            continue
        n = 1
        while n <= len(g):
            fill = _fill_breaks(words, n, pre)
            if fill:
                out += fill
                break
            n += 1
        else:
            out += [pre + x for x in g]
    return out if len(out) <= 4 and all(px(l) <= LIMIT for l in out) else None


KW_ENDS = None          # per unit: for each \! in order, True if the JP ends its line there (set by apply)


def jp_keywait_ends(jp):
    """For each \\! in the JP, in order: does the line end right after it (only codes/spaces left)?"""
    out = []
    for line in jp.split(SEP):
        for m in re.finditer(r"\\!", line):
            out.append(not re.sub(r"\\[A-Za-z]\[\d+\]|\\.|[\s\u3000]", "", line[m.end():]))
    return out


def fill_segments(words, max_lines, pre=""):
    """Fill words into the fewest lines, but start a new line after every key-wait (a word ending in
    \\!): the text after a click must not appear halfway along a line (user, play-test: a box showed
    half a line, then the rest of the line after the click).
    None if that needs more than max_lines; callers then fall back to plain filling."""
    # only where the JP itself ends the line at that click; a JP mid-line click stays
    # mid-line (user, play-test: three short questions had become one per line)
    n_en = sum(w.count("\\!") for w in words)
    ends = KW_ENDS if KW_ENDS is not None and len(KW_ENDS) == n_en else None
    if ends is None:
        return None
    segs, cur, idx = [], [], 0
    for w in words:
        cur.append(w)
        hit = False
        for _ in range(w.count("\\!")):
            hit = ends[idx] if w.endswith("\\!") else False
            idx += 1
        if hit:
            segs.append(cur)
            cur = []
    if cur:
        segs.append(cur)
    if len(segs) < 2:
        return None
    out = []
    for seg in segs:
        n, line = 1, ""
        for w in seg:                                   # greedy count for this segment
            t = (line + " " + w) if line else pre + w
            if px(t) <= LIMIT or not line:
                line = t
            else:
                n += 1
                line = pre + w
        out += _fill_breaks(seg, n, pre) or [pre + " ".join(seg)]
    return out if len(out) <= max_lines and all(px(l) <= LIMIT for l in out) else None


def _fill_breaks(words, n, pre=""):
    """Exactly n lines, full lines preferred (slack of non-last lines, squared) plus the quality of
    each break (_break_cost); a one-word last line is penalised."""
    from functools import lru_cache
    W = len(words)

    @lru_cache(None)
    def go(start, k):
        if k == n - 1:
            line = pre + " ".join(words[start:])
            if px(line) > LIMIT:
                return None
            return (80 if W - start == 1 and W > 1 else 0), [line]
        best = None
        for end in range(start + 1, W - (n - 1 - k) + 1):
            line = pre + " ".join(words[start:end])
            w = px(line)
            if w > LIMIT:
                break
            rest = go(end, k + 1)
            if rest is None:
                continue
            cost = ((LIMIT - w) / 15) ** 2 + _break_cost(line, " ".join(words[end:])) + rest[0]
            if best is None or cost < best[0]:
                best = (cost, [line] + rest[1])
        return best

    r = go(0, 0)
    return r[1] if r else None


AREA = 304          # message text area: x 8..312 (measured in game); its centre is x 160 - 8 = 152


def recenter_block(lines, centred):
    """Re-centre the centred lines of one message together. Padding is whole 6 px spaces, so each
    line's centre lands up to 3 px off; choose the shared centre (within 3 px of the true one) that
    keeps the lines' centres closest to each other (play-test: long + short line looked uneven)."""
    idx = [i for i, c in enumerate(centred) if c and split_lead(lines[i])[2]]
    if not idx:
        return lines
    widths = {i: px(split_lead(lines[i])[2]) for i in idx}
    best = None
    for k in range(-6, 7):                       # candidate centre: 152 +/- 3 px in 0.5 px steps
        c = AREA / 2 + k / 2
        pads = {i: max(0, round((c - widths[i] / 2) / CELL)) for i in idx}
        centres = [CELL * pads[i] + widths[i] / 2 for i in idx]
        score = (max(centres) - min(centres), abs(sum(centres) / len(centres) - AREA / 2))
        if best is None or score < best[0]:
            best = (score, pads)
    out = list(lines)
    for i in idx:
        codes, _, body = split_lead(lines[i])
        out[i] = codes + " " * best[1][i] + body
    return out


SPACER = re.compile(r"\\>\s*")


def caption_layout(lines):
    """Cutscene captions (one box: blank '\\>' spacer lines first, then speakerless text), left-aligned
    and re-filled like speech (user, play-test: centred captions looked awkward). Spacers are added
    at the top for every line saved, so the text stays at the bottom of the box. The lines' own
    leading codes (\\> instant on, \\< off) move inline with their first word."""
    if not 2 <= len(lines) <= 4 or not SPACER.fullmatch(lines[0]):
        return None
    k = 0
    while k < len(lines) and SPACER.fullmatch(lines[k]):
        k += 1
    body = lines[k:]
    if not body or any(not CODE.sub("", l).strip() for l in body):
        return None
    words = []
    for l in body:
        codes, _, rest = split_lead(l)
        words += (codes + rest.strip()).split()
    out, cur = [], ""
    for w in words:
        t = cur + " " + w if cur else w
        if px(t) <= LIMIT or not cur:
            cur = t
        else:
            out.append(cur)
            cur = w
    out.append(cur)
    if len(out) > len(body) or any(px(l) > LIMIT for l in out):
        return None
    out = fill_segments(words, 4 - min(k, 1)) or _fill_breaks(words, len(out)) or out
    return ["\\>"] * max(len(lines) - len(out), min(k, 1)) + out     # at least one spacer stays


def left_align(lines, centred):
    """Centred lines lose their centring padding (user, play-test: no centred text)."""
    return [split_lead(l)[0] + split_lead(l)[2] if c else l for l, c in zip(lines, centred)]


# system notices that keep one notice per line (no refilling): the battle-end results in CE0248
# ("Harvested food from the corpse." / "Found 116G." / the gold split; user, play-test 2026-10-25)
KEEP_LINES = ("CE0248:",)


def apply(text, kind, uid="", jp=""):
    global KW_ENDS
    if kind != "msg" or not text:
        return text
    KW_ENDS = jp_keywait_ends(jp) if jp else None
    lines = text.split(SEP)
    centred = [is_centred(l) for l in lines]
    keep = uid.startswith(KEEP_LINES)
    flowed = None if keep else (reflow_dialogue(lines, centred) or reflow_indented(lines, centred)
                                or caption_layout(lines))
    if flowed:
        return SEP.join(flowed)
    lines, centred = fit_lines(lines, centred)
    if not keep:
        lines = balance_runs(lines, centred)
    lines = left_align(lines, centred)
    return SEP.join(lines)


if __name__ == "__main__":
    import sys
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    import textunits as tu
    sys.stdout.reconfigure(encoding="utf-8")
    rows = tu.read_tsv(os.path.join(root, "build", "units_en.tsv"))
    changed = still = 0
    for r in rows:
        if r["kind"] != "msg" or not r["en"]:
            continue
        out = apply(r["en"], "msg")
        bad = [l for l in out.split(SEP) if px(l) > LIMIT]
        still += bool(bad)
        if out != r["en"]:
            changed += 1
        for l in bad:
            print("STILL WIDE", r["id"], round(px(l)), l)
    print(f"units changed by font fit: {changed}; units still too wide: {still}")
