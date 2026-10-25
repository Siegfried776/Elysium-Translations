"""Parse and re-serialize every LCF file; report any byte difference.

python -I tools/roundtrip.py original/data
"""
import sys, glob, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import lcf

sys.stdout.reconfigure(encoding="utf-8")
d = sys.argv[1]
paths = sorted(glob.glob(os.path.join(d, "*.lmu"))) + [os.path.join(d, "RPG_RT.ldb"), os.path.join(d, "RPG_RT.lmt")]
bad = 0
for p in paths:
    raw = open(p, "rb").read()
    try:
        f = lcf.LcfFile.load(p, lcf.schema_for(p))
        out = f.to_bytes()
    except Exception as ex:
        print("PARSE FAIL", os.path.basename(p), repr(ex)); bad += 1; continue
    if out != raw:
        k = next((i for i in range(min(len(out), len(raw))) if out[i] != raw[i]), min(len(out), len(raw)))
        print("DIFF", os.path.basename(p), "len", len(raw), len(out), "first diff at", k); bad += 1
print(f"{len(paths) - bad}/{len(paths)} files round-trip byte-identical")
sys.exit(1 if bad else 0)
