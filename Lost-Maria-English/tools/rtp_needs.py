"""List the assets the game references but does not ship (= taken from the RPG Maker 2000 RTP).

python -I tools/rtp_needs.py [data_dir]      (default original/data)
Scans every event command list (maps + common events + troop pages) for asset commands and checks
the named file against the game's own folders (any extension). Prints folder, name, use count.
Move-route SEs (inside 11330 parameters) are not decoded; see the raw scan at the end.
"""
import sys, os, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import lcf, textunits as tu

sys.stdout.reconfigure(encoding="utf-8")
root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
data = os.path.abspath(sys.argv[1] if len(sys.argv) > 1 else os.path.join(root, "original", "data"))
# command code -> asset folder
CODES = {11550: "Sound", 11510: "Music", 11110: "Picture", 10630: "FaceSet", 10640: "CharSet",
         11720: "Panorama", 10650: "Music", 10660: "Sound"}
have = {}
for folder in set(CODES.values()) | {"Battle", "System", "Title", "GameOver", "ChipSet"}:
    d = os.path.join(data, folder)
    have[folder] = {os.path.splitext(f)[0] for f in os.listdir(d)} if os.path.isdir(d) else set()

used = collections.Counter()


def scan(cmds):
    for c in cmds or []:
        f = CODES.get(c.code)
        if f and c.text:
            n = c.text.decode(lcf.ENC)
            if n and n != "(OFF)":
                used[(f, n)] += 1


for uid, _, rec, cid in tu.walk_ldb(lcf.LcfFile.load(os.path.join(data, "RPG_RT.ldb"), lcf.LDB)):
    scan(lcf.get(rec, cid))
for fn in sorted(os.listdir(data)):
    if fn.lower().endswith(".lmu"):
        key = os.path.splitext(fn)[0]
        for uid, _, rec, cid in tu.walk_map(lcf.LcfFile.load(os.path.join(data, fn), lcf.MAP), key):
            scan(lcf.get(rec, cid))

missing = sorted((k, n) for k, n in used.items() if k[1] not in have[k[0]])
for (folder, name), n in missing:
    print(f"{folder}\t{name}\t{n}")
print(f"-- {len(missing)} referenced files not in the game ({len(used)} referenced in all)")
