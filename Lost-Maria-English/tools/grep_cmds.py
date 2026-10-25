"""Find event commands by code and leading params across all maps and the database.

python -I tools/grep_cmds.py <code> [p0 p1 ...] [--ctx N]
e.g. grep_cmds.py 12010 0 201   -> conditions on switch 201
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import lcf, textunits as tu

sys.stdout.reconfigure(encoding="utf-8")
root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
data = os.path.join(root, "original", "data")
args = [a for a in sys.argv[1:] if not a.startswith("--")]
ctx = int(sys.argv[sys.argv.index("--ctx") + 1]) if "--ctx" in sys.argv else 0
if ctx:
    args = args[:-1]
code, want = int(args[0]), [int(a) for a in args[1:]]


def lists():
    f = lcf.LcfFile.load(os.path.join(data, "RPG_RT.ldb"), lcf.LDB)
    yield from tu.walk_ldb(f)
    for p in tu.map_paths(data):
        key = os.path.basename(p)[:-4]
        yield from tu.walk_map(lcf.LcfFile.load(p, lcf.MAP), key)


for uid, name, rec, cid in lists():
    cmds = lcf.get(rec, cid)
    if isinstance(cmds, (bytes, bytearray)):
        cmds = lcf.parse_commands(cmds)
    for i, c in enumerate(cmds):
        if c.code == code and c.params[:len(want)] == want:
            print(f"{uid} [{name}] C{i}")
            for j in range(max(0, i - ctx), min(len(cmds), i + ctx + 1)):
                d = cmds[j]
                print(f"   {j:4d} {'  ' * d.indent}{d.code} {d.params} {d.text.decode(lcf.ENC, 'replace')}")
