"""Text units shared by extract.py and inject.py.

Unit IDs (stable, from the pristine files):
  Map0056:E0012:P01:C0034   map event 12, page 1, command index 34
  CE0005:C0010              common event 5
  T0003:P02:C0007           troop 3, battle page 2
  DB:actor:0001:name        database strings
Kinds: msg (10110 + following 20110 lines, joined with SEP), choice (one 20140
option; the 10140 header is rebuilt from its options), name (10610), dbtext.
"""
import os, glob, re
import lcf

SEP = "␤"   # line separator inside a message unit
MSG, MSG_CONT, CHOICE, CHOICE_OPT, CHOICE_END, NAME = 10110, 20110, 10140, 20140, 20141, 10610


def dec(b):
    return b.decode(lcf.ENC)


def enc(s):
    return s.encode(lcf.ENC)


_CODES = re.compile(r"\\[A-Za-z]\[\d+\]|\\[.|!><^$_]")
LINE_MAX = 50     # half-width cells per message line (EasyRPG test, 2026-10-20)
CHOICE_MAX = 46   # choice option, cursor takes ~2 cells


def width(s):
    """Display width in half-width cells; control codes take no space."""
    s = _CODES.sub("", s)
    return sum(1 if ord(c) < 0x80 or 0xFF61 <= ord(c) <= 0xFF9F else 2 for c in s)


def read_tsv(path):
    """Plain tab-split TSV (no quoting) -> list of dicts."""
    with open(path, encoding="utf-8") as fh:
        lines = fh.read().split("\n")
    head = lines[0].split("\t")
    return [dict(zip(head, l.split("\t"))) for l in lines[1:] if l]


def write_tsv(path, head, rows):
    """rows: list of dicts or lists. Refuses tabs/newlines inside fields."""
    with open(path, "w", encoding="utf-8", newline="") as fh:
        fh.write("\t".join(head) + "\n")
        for r in rows:
            vals = [r.get(h, "") for h in head] if isinstance(r, dict) else r
            for v in vals:
                if "\t" in v or "\n" in v:
                    raise ValueError(f"tab/newline in field: {v!r}")
            fh.write("\t".join(vals) + "\n")


def map_paths(data_dir):
    return sorted(glob.glob(os.path.join(data_dir, "Map*.lmu")))


def walk_map(f, key):
    ev = lcf.get(f.body, 0x51)
    for eid, erec in ev.items:
        ename = lcf.get(erec, 0x01, b"")
        for pid, prec in lcf.get(erec, 0x05).items:
            cmds = lcf.get(prec, 0x34)
            if cmds:
                yield f"{key}:E{eid:04d}:P{pid:02d}", dec(ename), prec, 0x34


def walk_ldb(f):
    for cid, rec in lcf.get(f.body, 0x19).items:
        cmds = lcf.get(rec, 0x16)
        if cmds:
            yield f"CE{cid:04d}", dec(lcf.get(rec, 0x01, b"")), rec, 0x16
    for tid, rec in lcf.get(f.body, 0x0F).items:
        for pid, prec in lcf.get(rec, 0x0B).items:
            cmds = lcf.get(prec, 0x0D)
            if cmds:
                yield f"T{tid:04d}:P{pid:02d}", dec(lcf.get(rec, 0x01, b"")), prec, 0x0D


def choice_options(cmds, i):
    """Indices of the 20140 options belonging to the 10140 at i."""
    ind = cmds[i].indent
    out = []
    for j in range(i + 1, len(cmds)):
        c = cmds[j]
        if c.indent == ind and c.code == CHOICE_OPT:
            out.append(j)
        elif c.indent == ind and c.code == CHOICE_END:
            return out
    raise ValueError("unterminated choice")


def rebuild_choice_header(cmds, i):
    return "/".join(dec(cmds[j].text) for j in choice_options(cmds, i) if cmds[j].text)


def units_in_list(lid, cmds):
    """Yield (unit_id, kind, text) for one command list."""
    i = 0
    while i < len(cmds):
        c = cmds[i]
        if c.code == MSG:
            lines = [dec(c.text)]
            j = i + 1
            while j < len(cmds) and cmds[j].code == MSG_CONT:
                lines.append(dec(cmds[j].text)); j += 1
            yield f"{lid}:C{i:04d}", "msg", SEP.join(lines)
            i = j
            continue
        if c.code == CHOICE:
            for j in choice_options(cmds, i):
                if cmds[j].text:
                    yield f"{lid}:C{j:04d}", "choice", dec(cmds[j].text)
        elif c.code == NAME and c.text:
            yield f"{lid}:C{i:04d}", "name", dec(c.text)
        i += 1


# database string fields worth translating: (array chunk, label, {field: label})
DB_FIELDS = [
    (0x0B, "actor", {0x01: "name", 0x02: "title"}),
    (0x0C, "skill", {0x01: "name", 0x02: "desc", 0x03: "msg1", 0x04: "msg2", 0x07: "fail"}),
    (0x0D, "item", {0x01: "name", 0x02: "desc"}),
    (0x0E, "enemy", {0x01: "name"}),
    (0x11, "attribute", {0x01: "name"}),
    (0x12, "state", {0x01: "name", 0x33: "ally", 0x34: "enemy", 0x35: "already", 0x36: "affected", 0x37: "recovery"}),
]


def db_units(f):
    """Yield (unit_id, kind, text, setter) for database strings."""
    for top, label, fields in DB_FIELDS:
        for idx, rec in lcf.get(f.body, top).items:
            for fid, fl in fields.items():
                v = lcf.get(rec, fid)
                if v:
                    def setter(s, rec=rec, fid=fid):
                        lcf.set_(rec, fid, enc(s))
                    yield f"DB:{label}:{idx:04d}:{fl}", "dbtext", dec(v), setter
    raw = lcf.get(f.body, 0x15)
    terms, _ = lcf.parse_record(raw, 0, len(raw), {}, terminated=False)
    for item in terms:
        cid, v = item
        if v:
            try:
                s = dec(v)
            except UnicodeDecodeError:
                continue
            def setter(s, item=item, terms=terms, f=f):
                item[1] = enc(s)
                lcf.set_(f.body, 0x15, lcf.record_bytes(terms, {}, terminated=False))
            yield f"DB:term:{cid:02x}", "dbtext", s, setter
