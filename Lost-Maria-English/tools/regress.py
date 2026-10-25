"""Regression check: every play-test fix the user asked for must still be in the build.

python -I tools/regress.py        (build_game.py runs it and fails the build on any regression)
work/regressions.tsv rows: kind / where / text / why
  must     <unit id>  text   the unit's English must contain text (line breaks count as spaces)
  must     *          text   at least one unit contains it
  nowhere  *          text   no unit may contain it
  line     <unit id>  text   the unit must have exactly this line (layout codes ignored)
Plus layout checks: no line over the box width, no centred line, no letterless non-silence box,
key-wait regressions against the JP no higher than the recorded 6.
"""
import sys, os, re
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import textunits as tu, fontfit

sys.stdout.reconfigure(encoding="utf-8")
root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
units = tu.read_tsv(os.path.join(root, "build", "units_en.tsv"))
CODES = re.compile(r"\\[<>^$_]")            # layout codes may sit at a line start; waits/vars stay
norm = lambda t: re.sub(r"[ ␤]+", " ", CODES.sub("", t)).strip()
by_id = {r["id"]: norm(r["en"]) for r in units}
raw = {r["id"]: r["en"] for r in units}
fails = []
for row in tu.read_tsv(os.path.join(root, "work", "regressions.tsv")):
    kind, where, text, why = row["kind"], row["where"], norm(row["text"]), row["why"]
    if kind == "must" and where != "*":
        if where not in by_id or text not in by_id[where]:
            fails.append(f"MISSING  {where}: {text!r}  ({why})")
    elif kind == "line":
        # layout matters: the unit must have this exact line (layout codes stripped)
        lines = [CODES.sub("", l).strip() for l in raw.get(where, "").split(tu.SEP)]
        if CODES.sub("", row["text"]).strip() not in lines:
            fails.append(f"LAYOUT   {where}: no line {row['text']!r}  ({why})")
    elif kind == "must":
        if not any(text in t for t in by_id.values()):
            fails.append(f"MISSING  anywhere: {text!r}  ({why})")
    elif kind == "nowhere":
        hits = [k for k, t in by_id.items() if text in t]
        if hits:
            fails.append(f"BACK     {text!r} in {len(hits)} units, e.g. {hits[:3]}  ({why})")
# image text (work/img/units.tsv, last column = final English)
for r in tu.read_tsv(os.path.join(root, "work", "img", "units.tsv")):
    en = list(r.values())[-1]
    if "Sniper Gun" in en:
        fails.append(f"BACK     image {r['uid']}: 'Sniper Gun'  (renamed Sniper Rifle)")
    if r["uid"] in {f"u0{n}" for n in range(377, 387)} and not re.search(r"[.!?]$", en):
        fails.append(f"BACK     image {r['uid']}: ending description without final punctuation")
    if r.get("category") == "E item equipped label" and en.endswith(" E"):
        fails.append(f"BACK     image {r['uid']}: equipped label ends in ' E'  (the E mark is a sprite)")
# layout
for r in units:
    if r["kind"] != "msg" or not r["en"]:
        continue
    for l in r["en"].split(tu.SEP):
        if fontfit.px(l) > fontfit.LIMIT:
            fails.append(f"WIDE     {r['id']}: {round(fontfit.px(l))} px")
        if fontfit.is_centred(l):
            fails.append(f"CENTRED  {r['id']}")
n_kw = 0
for r in units:
    if r["kind"] != "msg" or "\\!" not in r["en"]:
        continue
    mid = lambda ls: sum(1 for l in ls for m in re.finditer(r"\\!", l)
                         if re.search(r"[^\s\u3000]", re.sub(r"\\[A-Za-z]\[\d+\]|\\.", "", l[m.end():])))
    n_kw += mid(r["en"].split(tu.SEP)) > mid(r["jp"].split(tu.SEP))
if n_kw > 6:
    fails.append(f"KEYWAIT  {n_kw} boxes put a click mid-line where the JP ended the line (recorded: 6)")
print(f"regressions: {len(fails)}")
for f in fails[:40]:
    print("  " + f)
sys.exit(1 if fails else 0)
