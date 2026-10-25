"""Pixel-width check of every English line against the box, for a bundled EasyRPG font.

python -I tools/fit_font.py [font.ttf]     (default: the Ark Pixel font in vendor/fonts)
EasyRPG loads a bundled Font/Font.ttf at 12 px. Limits = the cell limits measured with the built-in
6 px font: message line 50 cells = 300 px, choice 46 cells = 276 px. Control codes take no space;
\\N[n] counts as the widest actor name, \\V[n] as "999999". Text is checked as injected (TYPO map).
Also lists characters the font lacks (EasyRPG would fall back to its built-in font for those).
"""
import sys, os, re
from PIL import ImageFont
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import textunits as tu

sys.stdout.reconfigure(encoding="utf-8")
root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FONT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(
    root, "vendor", "fonts", "ark-pixel-12px-proportional", "x", "ark-pixel-12px-proportional-latin.ttf")
TYPO = str.maketrans({"“": '"', "”": '"', "‘": "'", "’": "'", "—": "―"})
MSG_PX, CHOICE_PX = tu.LINE_MAX * 6, tu.CHOICE_MAX * 6
f = ImageFont.truetype(FONT, 12)
_NOTDEF = bytes(f.getmask(""))      # a private-use char: renders as the font's placeholder box
_has = {}


def has(ch):
    """True if the font has a real glyph for ch (not the placeholder box)."""
    if ch not in _has:
        _has[ch] = ch.isspace() or bytes(f.getmask(ch)) != _NOTDEF
    return _has[ch]
rows = tu.read_tsv(os.path.join(root, "build", "units_en.tsv"))
names = [r["en"] for r in rows if r["id"].startswith("DB:actor:") and r["id"].endswith(":name") and r["en"]]
name_px = max((f.getlength(n) for n in names), default=48)
CODE = re.compile(r"\\[Nn]\[\d+\]|\\[Vv]\[\d+\]|\\[A-Za-z]\[\d+\]|\\[.|!><^$_]")


def px(line):
    w = 0.0
    pos = 0
    for m in CODE.finditer(line):
        w += f.getlength(line[pos:m.start()])
        c = m.group(0)
        if c[1] in "Nn":
            w += name_px
        elif c[1] in "Vv":
            w += f.getlength("999999")
        pos = m.end()
    return w + f.getlength(line[pos:])


over, missing = [], {}
for r in rows:
    if not r["en"] or r["kind"] not in ("msg", "choice"):
        continue
    text = r["en"].translate(TYPO)
    limit = MSG_PX if r["kind"] == "msg" else CHOICE_PX
    for line in text.split(tu.SEP):
        w = px(line)
        if w > limit:
            over.append((r["id"], round(w), limit, line))
        for ch in CODE.sub("", line):
            if not has(ch):
                missing.setdefault(ch, r["id"])
print(f"font: {os.path.basename(FONT)}; widest actor name {name_px:.0f} px")
print(f"lines over the limit: {len(over)}")
for o in over[:30]:
    print("  ", o)
print(f"characters missing from the font: {len(missing)}", {k: v for k, v in missing.items()})
