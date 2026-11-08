"""Command-level diff of the event lists of two game versions (maps + common events + troops).

python -I tools/diff_events.py <old_data_dir> <new_data_dir> [file ...]
For every event page / common event whose command list differs, prints a compact opcode diff
(code, indent, params, text) so non-text changes (sound volumes, flashes, switches, moved commands)
are visible. Optional file names restrict the comparison (e.g. Map0086.lmu RPG_RT.ldb).
"""
import sys, os, difflib
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import lcf, textunits as tu

sys.stdout.reconfigure(encoding="utf-8")
old, new = sys.argv[1], sys.argv[2]
only = set(sys.argv[3:])


def lists(path, key):
    out = {}
    if key == "RPG_RT":
        for uid, _, rec, cid in tu.walk_ldb(lcf.LcfFile.load(path, lcf.LDB)):
            out[uid] = lcf.get(rec, cid) or []
    else:
        for uid, _, rec, cid in tu.walk_map(lcf.LcfFile.load(path, lcf.MAP), key):
            out[uid] = lcf.get(rec, cid) or []
    return out


def sig(c):
    t = c.text.decode(lcf.ENC, "replace") if c.text else ""
    return f"{c.code} i{c.indent} {list(c.params)} {t[:40]!r}"


files = sorted(f for f in os.listdir(new) if f.lower().endswith((".lmu", ".ldb")))
for f in files:
    if only and f not in only:
        continue
    po, pn = os.path.join(old, f), os.path.join(new, f)
    if not os.path.exists(po) or open(po, "rb").read() == open(pn, "rb").read():
        continue
    key = os.path.splitext(f)[0]
    a, b = lists(po, key), lists(pn, key)
    changed = [k for k in sorted(set(a) | set(b)) if [sig(c) for c in a.get(k, [])] != [sig(c) for c in b.get(k, [])]]
    print(f"== {f}: {len(changed)} command lists differ" + ("" if changed else " (non-event data only)"))
    for k in changed:
        sa, sb = [sig(c) for c in a.get(k, [])], [sig(c) for c in b.get(k, [])]
        print(f"  -- {k}: {len(sa)} -> {len(sb)} commands")
        for line in list(difflib.unified_diff(sa, sb, lineterm="", n=0))[2:40]:
            print("     " + line)
