"""Inject translations from a TSV into a copy of the data folder.

python -I tools/inject.py original/data <units.tsv> <out_dir> [--col en] [--jp-as-en]
Only LCF files (maps, RPG_RT.ldb) are written to out_dir; copy the rest yourself.
Units with an empty value in --col keep the original text.
Message units: lines split on ␤; every 4 lines start a new message box (10110).
--jp-as-en  re-inject the jp column (round-trip check: output must equal input).
"""
import sys, os, argparse
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import lcf, textunits as tu

sys.stdout.reconfigure(encoding="utf-8")
ap = argparse.ArgumentParser()
ap.add_argument("data"); ap.add_argument("tsv"); ap.add_argument("out")
ap.add_argument("--col", default="en"); ap.add_argument("--jp-as-en", action="store_true")
ap.add_argument("--lines-per-box", type=int, default=4)
a = ap.parse_args()

tr = {}
for r in tu.read_tsv(a.tsv):
    v = r["jp"] if a.jp_as_en else (r.get(a.col) or "")
    if v:
        tr[r["id"]] = v
used, errors = set(), []


# EasyRPG test (2026-10-20): curly quotes render full-width; ASCII quotes are drawn
# slanted already. cp932 has no U+2014; its em dash slot is U+2015 (2 cells, looks right).
TYPO = str.maketrans({"“": '"', "”": '"', "‘": "'", "’": "'", "—": "―"})


def enc(uid, s):
    if not a.jp_as_en:
        s = s.translate(TYPO)
    try:
        return tu.enc(s)
    except UnicodeEncodeError as ex:
        errors.append(f"{uid}: cannot encode {s[ex.start:ex.end]!r}")
        return s.encode(lcf.ENC, "replace")


def apply_list(lid, cmds):
    """Return a new command list with translations applied."""
    out, i = [], 0
    while i < len(cmds):
        c = cmds[i]
        uid = f"{lid}:C{i:04d}"
        if c.code == tu.MSG:
            j = i + 1
            while j < len(cmds) and cmds[j].code == tu.MSG_CONT:
                j += 1
            if uid in tr:
                used.add(uid)
                lines = tr[uid].split(tu.SEP)
                for k, line in enumerate(lines):
                    code = tu.MSG if k % a.lines_per_box == 0 else tu.MSG_CONT
                    params = c.params if code == tu.MSG else cmds[i + 1].params if j > i + 1 else []
                    out.append(lcf.Command(code, c.indent, enc(uid, line), list(params)))
            else:
                out.extend(cmds[i:j])
            i = j
            continue
        if c.code in (tu.CHOICE_OPT, tu.NAME) and uid in tr:
            used.add(uid)
            c = lcf.Command(c.code, c.indent, enc(uid, tr[uid]), list(c.params))
        out.append(c)
        i += 1
    # rebuild choice headers from (possibly translated) options
    for k, c in enumerate(out):
        if c.code == tu.CHOICE:
            hdr = tu.rebuild_choice_header(out, k)
            if hdr != tu.dec(c.text):
                out[k] = lcf.Command(c.code, c.indent, tu.enc(hdr), list(c.params))
    return out


os.makedirs(a.out, exist_ok=True)
changed = 0
for p in tu.map_paths(a.data):
    raw = open(p, "rb").read()
    f = lcf.LcfFile.load(p, lcf.MAP)
    key = os.path.splitext(os.path.basename(p))[0]
    for lid, _, rec, cid in tu.walk_map(f, key):
        lcf.set_(rec, cid, apply_list(lid, lcf.get(rec, cid)))
    b = f.to_bytes()
    changed += b != raw
    open(os.path.join(a.out, os.path.basename(p)), "wb").write(b)

p = os.path.join(a.data, "RPG_RT.ldb")
raw = open(p, "rb").read()
db = lcf.LcfFile.load(p, lcf.LDB)
for lid, _, rec, cid in tu.walk_ldb(db):
    lcf.set_(rec, cid, apply_list(lid, lcf.get(rec, cid)))
for uid, _, text, setter in list(tu.db_units(db)):
    if uid in tr:
        used.add(uid)
        if tr[uid] != text:
            setter(tr[uid])
b = db.to_bytes()
changed += b != raw
open(os.path.join(a.out, "RPG_RT.ldb"), "wb").write(b)

unused = sorted(set(tr) - used)
print(f"applied {len(used)} units; {changed} files changed; {len(unused)} unknown ids; {len(errors)} encode errors")
for u in unused[:10]:
    print("  unknown id", u)
for e in errors[:20]:
    print("  ", e)
sys.exit(1 if unused or errors else 0)
