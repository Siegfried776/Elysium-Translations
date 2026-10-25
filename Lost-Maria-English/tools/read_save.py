"""Read an RPG Maker 2000 save (SaveNN.lsd): switches, variables, current map.

Library: load(path) -> {"switches": [bool...] (index 1-based via [i-1]), "variables": [int...], "map": id}
python -I tools/read_save.py <SaveNN.lsd> [switch ids...]   -> prints map and the given switches
Read-only. Format: "LcfSaveData" header, then chunks (id, length, data; BER-encoded);
chunk 0x65 = system data (0x1F/0x20 switch count/bytes, 0x21/0x22 variable count/int32 LE),
chunk 0x68 = party location (0x0B = map id).
"""
import sys, os, struct
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import lcf


def chunks(b, i=0, end=None):
    end = len(b) if end is None else end
    out = {}
    while i < end:
        cid, i = lcf.ber_read(b, i)
        if cid == 0:
            break
        n, i = lcf.ber_read(b, i)
        out[cid] = b[i:i + n]
        i += n
    return out


def load(path):
    b = open(path, "rb").read()
    hl, i = lcf.ber_read(b, 0)
    i += hl
    top = chunks(b, i)
    sysd = chunks(top[0x65])
    sw = [x != 0 for x in sysd.get(0x20, b"")]
    raw = sysd.get(0x22, b"")
    var = list(struct.unpack("<%di" % (len(raw) // 4), raw))
    loc = chunks(top.get(0x68, b""))
    m = loc.get(0x0B)
    map_id = lcf.ber_read(m, 0)[0] if m else None
    return {"switches": sw, "variables": var, "map": map_id}


def set_variables(src, dst, values):
    """Copy save src to dst with variables changed ({id: int}); everything else byte-identical.
    The variable array keeps its length, so the values are patched in place."""
    if os.path.abspath(src) == os.path.abspath(dst) or os.path.exists(dst):
        raise SystemExit(f"refusing to overwrite {dst}")
    b = bytearray(open(src, "rb").read())
    hl, i = lcf.ber_read(b, 0)
    i += hl
    while i < len(b):                                   # top-level chunks
        cid, i = lcf.ber_read(b, i)
        n, i = lcf.ber_read(b, i)
        if cid == 0x65:
            j, end = i, i + n
            while j < end:                              # system sub-chunks
                sid, j = lcf.ber_read(b, j)
                m, j = lcf.ber_read(b, j)
                if sid == 0x22:
                    for vid, val in values.items():
                        assert 1 <= vid <= m // 4, f"variable {vid} not in the save"
                        struct.pack_into("<i", b, j + 4 * (vid - 1), val)
                    open(dst, "wb").write(b)
                    return
                j += m
        i += n
    raise SystemExit("variables chunk not found")


def set_switches(src, dst, values):
    """Copy save src to dst with switches changed ({id: bool}); everything else byte-identical.
    The switch array (system sub-chunk 0x20, one byte per switch) keeps its length."""
    if os.path.abspath(src) == os.path.abspath(dst) or os.path.exists(dst):
        raise SystemExit(f"refusing to overwrite {dst}")
    b = bytearray(open(src, "rb").read())
    hl, i = lcf.ber_read(b, 0)
    i += hl
    while i < len(b):
        cid, i = lcf.ber_read(b, i)
        n, i = lcf.ber_read(b, i)
        if cid == 0x65:
            j, end = i, i + n
            while j < end:
                sid, j = lcf.ber_read(b, j)
                m, j = lcf.ber_read(b, j)
                if sid == 0x20:
                    for swid, val in values.items():
                        assert 1 <= swid <= m, f"switch {swid} not in the save"
                        b[j + swid - 1] = 1 if val else 0
                    open(dst, "wb").write(b)
                    return
                j += m
        i += n
    raise SystemExit("switches chunk not found")


def _records(b):
    """[(cid, bytes)] until the 0 terminator; returns (list, rest after terminator)."""
    out, i = [], 0
    while i < len(b):
        cid, i = lcf.ber_read(b, i)
        if cid == 0:
            return out, b[i:]
        n, i = lcf.ber_read(b, i)
        out.append((cid, b[i:i + n]))
        i += n
    return out, b""


def _join(recs, tail):
    return b"".join(lcf.ber_write(c) + lcf.ber_write(len(v)) + v for c, v in recs) + lcf.ber_write(0) + tail


def rename_actor(src, dst, old, new):
    """Copy save src to dst with any actor whose saved name is `old` renamed to `new` (chunk 0x6C =
    actors array: count, then per actor its index and a 0-terminated record; field 0x01 = name).
    Lengths are rebuilt; everything else stays byte-identical. Returns the number renamed."""
    if os.path.abspath(src) == os.path.abspath(dst) or os.path.exists(dst):
        raise SystemExit(f"refusing to overwrite {dst}")
    b = open(src, "rb").read()
    hl, i = lcf.ber_read(b, 0)
    head, i = b[:i + hl], i + hl
    top = []
    while i < len(b):
        cid, j = lcf.ber_read(b, i)
        if cid == 0:
            break
        n, j = lcf.ber_read(b, j)
        top.append([cid, b[j:j + n]])
        i = j + n
    tail = b[i:]
    renamed = 0
    for item in top:
        if item[0] == 0x64:
            # save title (what the load screen shows): 0x0B = leader's name
            recs, rest = _records(item[1])
            recs = [(c, (new.encode(lcf.ENC) if c == 0x0B and v == old.encode(lcf.ENC) else v)) for c, v in recs]
            renamed += sum(1 for c, v in recs if c == 0x0B and v == new.encode(lcf.ENC))
            item[1] = _join(recs, rest)
            continue
        if item[0] != 0x6C:
            continue
        data = item[1]
        cnt, k = lcf.ber_read(data, 0)
        out = lcf.ber_write(cnt)
        for _ in range(cnt):
            idx, k = lcf.ber_read(data, k)
            recs, rest = _records(data[k:])
            consumed = len(data[k:]) - len(rest)
            k += consumed
            recs = [(c, (new.encode(lcf.ENC) if c == 0x01 and v == old.encode(lcf.ENC) else v)) for c, v in recs]
            renamed += sum(1 for c, v in recs if c == 0x01 and v == new.encode(lcf.ENC))
            out += lcf.ber_write(idx) + _join(recs, b"")
        item[1] = out + data[k:]
    body = b"".join(lcf.ber_write(c) + lcf.ber_write(len(v)) + v for c, v in top)
    open(dst, "wb").write(head + body + tail)
    return renamed


if __name__ == "__main__":
    s = load(sys.argv[1])
    print("map", s["map"], "| switches", len(s["switches"]), "| variables", len(s["variables"]))
    for a in sys.argv[2:]:
        k = int(a)
        print(f"  S{k}:", s["switches"][k - 1] if k <= len(s["switches"]) else "(beyond saved range = OFF)")
