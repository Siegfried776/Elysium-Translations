"""Apply non-text event patches (command parameters) to a built game copy.

python -I tools/patch_events.py <data_dir>
Reads work/event_patches.json: a list of
  {"list": "CE0046", "code": 11110, "match": [5, 0, 216], "set": {"2": 229}, "count": 9, "why": "..."}
Every command in that list whose code matches and whose params start with `match` gets the
params in `set` (index -> value); an optional "match_text" also requires that file name/text. `count` must equal the number of commands changed, so a
patch that no longer matches the data fails loudly instead of silently doing nothing.
"""
import sys, os, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import lcf, textunits as tu

sys.stdout.reconfigure(encoding="utf-8")
root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
data = sys.argv[1]
patches = json.load(open(os.path.join(root, "work", "event_patches.json"), encoding="utf-8-sig"))
# Database system sounds the engine plays itself: 0x2B cancel, 0x2C buzzer. Both are the RTP buzz
# しびれ2, heard on every choice cancel (item pick-ups, the elevator) once the RTP was installed;
# muted like the event uses (user, play-test 2026-10-24; tools/mute_ui_se.py).
SYSTEM_MUTE = {0x2B: "しびれ2", 0x2C: "しびれ2"}


def _pairs(b):
    out, i = [], 0
    while i < len(b):
        cid, i = lcf.ber_read(b, i)
        if cid == 0:
            return out, b[i - 1:]
        n, i = lcf.ber_read(b, i)
        out.append([cid, b[i:i + n]])
        i += n
    return out, b""


def _join(pairs, tail):
    return b"".join(lcf.ber_write(c) + lcf.ber_write(len(v)) + v for c, v in pairs) + tail


def mute_system_se(f):
    sysrec, sys_tail = _pairs(bytes(lcf.get(f.body, 0x16)))
    n = 0
    for item in sysrec:
        if item[0] in SYSTEM_MUTE:
            snd, tail = _pairs(item[1])
            name = lcf.get(snd, 0x01, b"").decode(lcf.ENC)
            assert name == SYSTEM_MUTE[item[0]], f"system SE {item[0]:#x} is {name}, expected {SYSTEM_MUTE[item[0]]}"
            lcf.set_(snd, 0x03, lcf.ber_write(0))                     # volume 0
            snd.sort(key=lambda p: p[0])
            item[1] = _join(snd, tail)
            n += 1
    assert n == len(SYSTEM_MUTE), "system SE chunk not as expected"
    lcf.set_(f.body, 0x16, _join(sysrec, sys_tail))
    return n


by_file = {}
for p in patches:
    f = p["list"].split(":")[0] + ".lmu" if p["list"].startswith("Map") else "RPG_RT.ldb"
    by_file.setdefault(f, []).append(p)
total, added = 0, []
for fname, ps in by_file.items():
    path = os.path.join(data, fname)
    schema = lcf.MAP if fname.endswith(".lmu") else lcf.LDB
    f = lcf.LcfFile.load(path, schema)
    walk = tu.walk_map(f, fname[:-4]) if schema is lcf.MAP else tu.walk_ldb(f)
    lists = {}
    for uid, _, rec, cid in walk:
        lists[uid] = (rec, cid)
    for p in ps:
        rec, cid = lists[p["list"]]
        cmds = lcf.get(rec, cid)
        n = 0
        if "rename_by_cond" in p:
            # Show Picture commands with this file name, each right after a condition
            # "variable == item id": the picture file becomes the one mapped to that id
            names = p["rename_by_cond"]
            for i, c in enumerate(cmds):
                prev = cmds[i - 1] if i else None
                if (c.code == 11110 and c.text.decode(lcf.ENC) == p["match_text"] and prev is not None
                        and prev.code == 12010 and prev.params[0] == 1 and str(prev.params[3]) in names):
                    c.text = names[str(prev.params[3])].encode(lcf.ENC)
                    n += 1
        elif "at" in p and "set" in p:
            # one command at a known index; it must still be exactly the expected command
            c = cmds[p["at"]]
            assert c.code == p["code"] and c.params == p["expect"], \
                f"{p['list']} C{p['at']}: found {c.code} {c.params}, expected {p['code']} {p['expect']}"
            for k, v in p["set"].items():
                c.params[int(k)] = v
            n = 1
        elif "insert_at" in p:
            # new commands (an added line with its conditions) before a known command; the
            # message texts are recorded so the build's verify step can account for them
            i = p["insert_at"]
            c = cmds[i]
            assert [c.code, c.indent] == p["expect_at"], f"{p['list']} C{i}: found {c.code}/{c.indent}"
            new = [lcf.Command(code, ind, text.encode(lcf.ENC), list(params)) for code, ind, text, params in p["commands"]]
            cmds[i:i] = new
            msg = []
            for x in new:
                if x.code == 10110:
                    msg.append([x.text.decode(lcf.ENC)])
                elif x.code == 20110:
                    msg[-1].append(x.text.decode(lcf.ENC))
            added += [tu.SEP.join(m) for m in msg]
            n = 1
        elif "replace_with_branches" in p:
            # one Show Picture for a whole range of items -> one branch per item, each showing its
            # own picture (same picture id, position and settings as the original command)
            i = p["at"]
            c = cmds[i]
            assert c.code == 11110 and c.text.decode(lcf.ENC) == p["match_text"], f"{p['list']} C{i} not as expected"
            var, names, ind = p["var"], p["replace_with_branches"], c.indent
            block = []
            for item, pic in names.items():
                block += [lcf.Command(12010, ind, b"", [1, var, 0, int(item), 0, 0]),
                          lcf.Command(11110, ind + 1, pic.encode(lcf.ENC), list(c.params)),
                          lcf.Command(10, ind + 1, b"", []),
                          lcf.Command(22011, ind, b"", [])]
            cmds[i:i + 1] = block
            n = len(names)
        else:
            for c in cmds:
                if (c.code == p["code"] and c.params[:len(p["match"])] == p["match"]
                        and ("match_text" not in p or c.text.decode(lcf.ENC) == p["match_text"])):
                    for k, v in p["set"].items():
                        c.params[int(k)] = v
                    n += 1
        assert n == p["count"], f"{p['list']} {p.get('match') or p.get('match_text')}: changed {n}, expected {p['count']}"
        total += n
    if fname == "RPG_RT.ldb":
        total += mute_system_se(f)
    f.save(path)
tu.write_tsv(os.path.join(data, "..", "patch_added.tsv"), ["text"], [{"text": t} for t in added])
print(f"event patches: {len(patches)} rules, {total} commands changed, {len(added)} messages added")
