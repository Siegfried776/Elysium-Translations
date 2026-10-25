"""Dump the raw commands of one event page / common event / troop page.

python -I tools/dump_event.py <list id> [from] [to] [--build]
  list id: Map0011:E0034:P01 | CE0005 | T0003:P02      (--build reads build/game_en instead of original)
Prints: index, indent, code, params, text.
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import lcf, textunits as tu

sys.stdout.reconfigure(encoding="utf-8")
root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
args = [a for a in sys.argv[1:] if not a.startswith("--")]
data = os.path.join(root, "build", "game_en", "data") if "--build" in sys.argv else os.path.join(root, "original", "data")
lid = args[0]
lo = int(args[1]) if len(args) > 1 else 0
hi = int(args[2]) if len(args) > 2 else 10 ** 9
if lid.startswith("Map"):
    key = lid.split(":")[0]
    f = lcf.LcfFile.load(os.path.join(data, key + ".lmu"), lcf.MAP)
    walk = tu.walk_map(f, key)
else:
    f = lcf.LcfFile.load(os.path.join(data, "RPG_RT.ldb"), lcf.LDB)
    walk = tu.walk_ldb(f)
for uid, name, rec, cid in walk:
    if uid != lid:
        continue
    cmds = lcf.get(rec, cid)
    if isinstance(cmds, (bytes, bytearray)):
        cmds = lcf.parse_commands(cmds)
    print(uid, name)
    for i, c in enumerate(cmds):
        if lo <= i <= hi:
            t = c.text.decode(lcf.ENC, "replace")
            print(f"{i:4d} {'  ' * c.indent}{c.code} {c.params} {t}")
