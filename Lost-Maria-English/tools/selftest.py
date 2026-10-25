"""Stress test for inject.py: fill every unit with dummy English of varying line
counts (1-7 lines, so some messages spill into a second box), inject, re-extract,
and check that the texts come back in order.

python -I tools/selftest.py original/data <scratch_dir>
"""
import sys, os, subprocess
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import textunits as tu
sys.stdout.reconfigure(encoding="utf-8")
data, tmp = sys.argv[1], sys.argv[2]
here = os.path.dirname(os.path.abspath(__file__))
SEP = "␤"
os.makedirs(tmp, exist_ok=True)
src = os.path.join(tmp, "units.tsv")
subprocess.run([sys.executable, "-I", os.path.join(here, "extract.py"), data, src], check=True, stdout=subprocess.DEVNULL)
rows = tu.read_tsv(src)
for n, r in enumerate(rows):
    if not r["jp"]:
        r["en"] = ""; continue
    if r["kind"] == "msg":
        k = n % 7 + 1
        r["en"] = SEP.join(f"Line {i + 1} of unit {n}: \"quote\" ... it's fine." for i in range(k))
    else:
        r["en"] = f"Opt {n}"
dummy = os.path.join(tmp, "dummy.tsv")
tu.write_tsv(dummy, list(rows[0]), rows)
out = os.path.join(tmp, "data")
subprocess.run([sys.executable, "-I", os.path.join(here, "inject.py"), data, dummy, out], check=True)
back = os.path.join(tmp, "back.tsv")
subprocess.run([sys.executable, "-I", os.path.join(here, "extract.py"), out, back], check=True)
got = tu.read_tsv(back)

# expected sequence: messages longer than 4 lines become several boxes
exp = []
for r in rows:
    if r["kind"] == "msg" and r["en"]:
        ls = r["en"].split(SEP)
        exp += [SEP.join(ls[i:i + 4]) for i in range(0, len(ls), 4)]
    else:
        exp.append(r["en"] or r["jp"])
gotv = [g["jp"] for g in got]
bad = [i for i, (x, y) in enumerate(zip(exp, gotv)) if x != y]
print(f"expected {len(exp)} units, got {len(gotv)}, mismatches {len(bad)}")
for i in bad[:5]:
    print("  ", i, repr(exp[i][:60]), "|", repr(gotv[i][:60]))
sys.exit(0 if len(exp) == len(gotv) and not bad else 1)
