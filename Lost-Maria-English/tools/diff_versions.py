"""Compare two game versions file by file (e.g. original v1.20 vs the developer's v1.21).

python -I tools/diff_versions.py <old_game_dir> <new_game_dir> [report.tsv]
Prints counts of same / changed / added / removed files per top folder, the changed and removed files,
and for changed LCF files whether their extracted text (tools/extract.py units) changed.
"""
import sys, os, hashlib, collections, subprocess, tempfile
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import textunits as tu

sys.stdout.reconfigure(encoding="utf-8")
old, new = os.path.abspath(sys.argv[1]), os.path.abspath(sys.argv[2])


def tree(base):
    out = {}
    for dp, dn, fn in os.walk(base):
        for f in fn:
            p = os.path.join(dp, f)
            out[os.path.relpath(p, base).lower()] = (os.path.relpath(p, base), hashlib.sha256(open(p, "rb").read()).hexdigest())
    return out


a, b = tree(old), tree(new)
rows, stats = [], collections.Counter()
for k in sorted(set(a) | set(b)):
    name = (b.get(k) or a.get(k))[0]
    top = name.split(os.sep)[1] if name.lower().startswith("data" + os.sep) and name.count(os.sep) > 1 else name.split(os.sep)[0]
    st = "added" if k not in a else "removed" if k not in b else "same" if a[k][1] == b[k][1] else "changed"
    stats[(top, st)] += 1
    rows.append({"path": name, "status": st})
tops = sorted({t for t, _ in stats})
print(f"{'folder':<14} same changed added removed")
for t in tops:
    print(f"{t:<14} {stats[(t,'same')]:>4} {stats[(t,'changed')]:>7} {stats[(t,'added')]:>5} {stats[(t,'removed')]:>7}")
for r in rows:
    if r["status"] in ("changed", "removed"):
        print(f"  {r['status']:<8} {r['path']}")

# text-level comparison of the LCF files
tmp = tempfile.mkdtemp()
ex = os.path.join(os.path.dirname(os.path.abspath(__file__)), "extract.py")
units = {}
for tag, d in (("old", old), ("new", new)):
    out = os.path.join(tmp, tag + ".tsv")
    subprocess.run([sys.executable, "-I", ex, os.path.join(d, "data"), out], check=True, stdout=subprocess.DEVNULL)
    units[tag] = {r["id"]: r["jp"] for r in tu.read_tsv(out)}
o, n = units["old"], units["new"]
chg = [k for k in o if k in n and o[k] != n[k]]
print(f"text units: {len(o)} old, {len(n)} new; {len(chg)} changed, {len(set(n)-set(o))} added, {len(set(o)-set(n))} removed")
for k in chg[:30]:
    print(f"  ~ {k}\n      old: {o[k][:90]}\n      new: {n[k][:90]}")
for k in sorted(set(n) - set(o))[:15]:
    print(f"  + {k}: {n[k][:90]}")
for k in sorted(set(o) - set(n))[:15]:
    print(f"  - {k}: {o[k][:90]}")
if len(sys.argv) > 3:
    tu.write_tsv(sys.argv[3], ["path", "status"], rows)
