"""Show the save screen's level label "†" in EasyRPG.

python -I tools/font_remap.py <font.ttf>        (edits in place; run after patch_font_metrics.py)
EasyRPG pads/trims the level label (terms.lvl_short) to 2 *bytes* of UTF-8, which cuts the 3-byte
"†" and draws nothing (the original engine works in Shift-JIS, 2 bytes). So the label becomes the
one-byte backtick (DB:term:80, tools/lead_playtest.py) and this maps "`" to the font's own "†"
glyph. The backtick is used nowhere else in the game. Needs fontTools (vendor/pylib).
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "vendor", "pylib"))
from fontTools.ttLib import TTFont

path = sys.argv[1]
font = TTFont(path)
n = 0
for table in font["cmap"].tables:
    if table.isUnicode() and 0x2020 in table.cmap:
        table.cmap[0x60] = table.cmap[0x2020]
        n += 1
assert n, "no Unicode cmap with U+2020"
font.save(path)
print(f"'`' -> glyph of U+2020 in {n} cmap subtable(s): {os.path.basename(path)}")
