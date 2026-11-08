"""Rebase work/plan.tsv onto a new game version's extract (v1.20 -> v1.21, 2026-11-05).

python -I tools/rebase_plan.py <old_units.tsv> <old_plan.tsv> <new_units.tsv> <new_plan.tsv>
Every new unit keeps its finished English:
  same id, same JP          -> the old plan row as it was
  JP found elsewhere in old -> owner = that old unit's owner (role dup); covers commands the update moved
  JP new                    -> own, batch V121: translate it in work/overlays/lead_v121.json
Owners that only exist in the old extract stay valid: merge.py reads old units for them (kind, JP).
Prints every unit that isn't a plain carry-over.
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import textunits as tu

sys.stdout.reconfigure(encoding="utf-8")
old_u = {r["id"]: r for r in tu.read_tsv(sys.argv[1])}
old_p = {r["id"]: r for r in tu.read_tsv(sys.argv[2])}
new_u = tu.read_tsv(sys.argv[3])
by_jp = {}
for k, r in old_u.items():
    by_jp.setdefault(r["jp"], old_p[k]["owner"])
rows, moved, new = [], [], []
for r in new_u:
    k = r["id"]
    if k in old_u and old_u[k]["jp"] == r["jp"]:
        rows.append(old_p[k])
    elif r["jp"] in by_jp:
        o = by_jp[r["jp"]]
        rows.append({"id": k, "batch": old_p[o]["batch"], "owner": o, "role": "own" if o == k else "dup"})
        moved.append((k, o, r["jp"]))
    else:
        rows.append({"id": k, "batch": "V121", "owner": k, "role": "own"})
        new.append((k, r["jp"]))
tu.write_tsv(sys.argv[4], ["id", "batch", "owner", "role"], rows)
print(f"{len(rows)} units: {len(rows) - len(moved) - len(new)} carried over, {len(moved)} matched by JP, {len(new)} new")
for k, o, jp in moved:
    print(f"  = {k} <- {o}  {jp[:50]!r}")
for k, jp in new:
    print(f"  + {k}  {jp!r}")
