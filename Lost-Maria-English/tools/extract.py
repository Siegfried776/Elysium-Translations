"""Extract all translatable text to a TSV.

python -I tools/extract.py original/data extract/units.tsv
Columns: id, kind, event (event / common-event name, context only), jp, en
Message lines are joined with ␤. Tabs/newlines never occur in the source.
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import lcf, textunits as tu

sys.stdout.reconfigure(encoding="utf-8")
data, out = sys.argv[1], sys.argv[2]
rows, mismatched = [], []


def take(lid, ename, cmds):
    for i, c in enumerate(cmds):
        if c.code == tu.CHOICE and tu.rebuild_choice_header(cmds, i) != tu.dec(c.text):
            mismatched.append((f"{lid}:C{i:04d}", tu.dec(c.text), tu.rebuild_choice_header(cmds, i)))
    for uid, kind, text in tu.units_in_list(lid, cmds):
        rows.append([uid, kind, ename, text, ""])


for p in tu.map_paths(data):
    f = lcf.LcfFile.load(p, lcf.MAP)
    key = os.path.splitext(os.path.basename(p))[0]
    for lid, ename, rec, cid in tu.walk_map(f, key):
        take(lid, ename, lcf.get(rec, cid))
db = lcf.LcfFile.load(os.path.join(data, "RPG_RT.ldb"), lcf.LDB)
for lid, ename, rec, cid in tu.walk_ldb(db):
    take(lid, ename, lcf.get(rec, cid))
for uid, kind, text, _ in tu.db_units(db):
    rows.append([uid, kind, "", text, ""])

os.makedirs(os.path.dirname(os.path.abspath(out)), exist_ok=True)
tu.write_tsv(out, ["id", "kind", "event", "jp", "en"], rows)

from collections import Counter
print(len(rows), "units", dict(Counter(r[1] for r in rows)))
print("choice headers not equal to joined options:", len(mismatched))
for m in mismatched[:10]:
    print("  ", m)
