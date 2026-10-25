"""Make a TTF render at its design size in EasyRPG.

python -I tools/patch_font_metrics.py <in.ttf> <out.ttf>
EasyRPG (0.8.1.1, font.cpp FTFont::SetSize) sizes a bundled font as
    pixel size = 12 * unitsPerEm / (OS/2 usWinAscent + usWinDescent)
Ark Pixel 12px declares 1300 + 300 for a 1200 em, so it was drawn at 9 px (blurry, broken).
This rewrites only usWinAscent/usWinDescent so they sum to unitsPerEm (same ascent:descent
ratio); every glyph and every other table is untouched. FreeType doesn't verify table checksums,
but the OS/2 checksum is recomputed anyway.
"""
import sys, struct

src, dst = sys.argv[1], sys.argv[2]
b = bytearray(open(src, "rb").read())
n = struct.unpack(">H", b[4:6])[0]
tabs = {}
for i in range(n):
    rec = 12 + 16 * i
    tag, cs, off, ln = struct.unpack(">4sIII", b[rec:rec + 16])
    tabs[tag.decode()] = (rec, off, ln)
_, ho, _ = tabs["head"]
upem = struct.unpack(">H", b[ho + 18:ho + 20])[0]
rec, o, ln = tabs["OS/2"]
wasc, wdesc = struct.unpack(">HH", b[o + 74:o + 78])
# Baseline: EasyRPG puts it at face->ascender (hhea, or OS/2 typo when USE_TYPO_METRICS), scaled.
# The glyphs must fit the 12-row text line: ascent = ASC_PX rows above the baseline.
# Ark Pixel 12px reaches 10 rows up (brackets) and 2 down (g, p, y): ascent 10, descent 2.
ASC_PX = int(sys.argv[3]) if len(sys.argv) > 3 else 10
new_asc = round(upem * ASC_PX / 12)
new_desc = upem - new_asc
b[o + 74:o + 78] = struct.pack(">HH", new_asc, new_desc)               # usWinAscent/Descent
b[o + 68:o + 74] = struct.pack(">hhh", new_asc, -new_desc, 0)          # sTypoAscender/Descender/LineGap
_, hh, hl = tabs["hhea"]
old_hhea = struct.unpack(">hh", b[hh + 4:hh + 8])
b[hh + 4:hh + 10] = struct.pack(">hhh", new_asc, -new_desc, 0)         # hhea ascender/descender/lineGap


def fix_checksum(tag):
    rec, off, ln = tabs[tag]
    data = bytes(b[off:off + ln]) + b"\0" * ((4 - ln % 4) % 4)
    cs = sum(struct.unpack(">%dI" % (len(data) // 4), data)) & 0xFFFFFFFF
    b[rec + 4:rec + 8] = struct.pack(">I", cs)


fix_checksum("OS/2")
fix_checksum("hhea")
open(dst, "wb").write(b)
print(f"unitsPerEm {upem}; win {wasc}/{wdesc}, hhea {old_hhea[0]}/{old_hhea[1]} -> ascent {new_asc}, "
      f"descent {new_desc} (all three tables); EasyRPG size {12 * upem / (wasc + wdesc):.1f} -> "
      f"{12 * upem / (new_asc + new_desc):.1f} px, baseline at row {ASC_PX}")
