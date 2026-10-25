"""Minimal RPG Maker 2000 LCF reader/writer (LMU maps, LDB database, LMT map tree).

Everything the tools don't need stays as raw bytes, so an unmodified parse
re-serializes byte-identically. Event command lists are parsed into
Command objects; their byte-size companion chunk is recomputed on write.
"""
from dataclasses import dataclass, field

ENC = "cp932"


# ---------------------------------------------------------------- BER ints
def ber_read(b, i):
    v = 0
    while True:
        c = b[i]
        i += 1
        v = (v << 7) | (c & 0x7F)
        if not c & 0x80:
            return v, i


def ber_write(v):
    out = [v & 0x7F]
    v >>= 7
    while v:
        out.append(0x80 | (v & 0x7F))
        v >>= 7
    return bytes(reversed(out))


# ---------------------------------------------------------------- commands
@dataclass
class Command:
    code: int
    indent: int
    text: bytes
    params: list

    def to_bytes(self):
        out = bytearray(ber_write(self.code) + ber_write(self.indent))
        out += ber_write(len(self.text)) + self.text
        out += ber_write(len(self.params))
        for p in self.params:
            out += ber_write(p)
        return bytes(out)

    @property
    def s(self):
        return self.text.decode(ENC)


def parse_commands(b):
    cmds, i = [], 0
    while i < len(b):
        code, i = ber_read(b, i)
        indent, i = ber_read(b, i)
        n, i = ber_read(b, i)
        text = b[i:i + n]
        i += n
        pc, i = ber_read(b, i)
        params = []
        for _ in range(pc):
            p, i = ber_read(b, i)
            params.append(p)
        cmds.append(Command(code, indent, text, params))
    return cmds


def commands_bytes(cmds):
    return b"".join(c.to_bytes() for c in cmds)


# ---------------------------------------------------------------- chunk trees
# A "record" is an ordered list of [chunk_id, value]; value is bytes (raw),
# a list of Commands, or an Array. Arrays are lists of (index, record).

@dataclass
class Array:
    items: list = field(default_factory=list)   # [(index, record)]


def parse_record(b, i, end, schema, terminated):
    """Parse chunks from b[i:end]. Returns (record, new_i)."""
    rec = []
    while i < end:
        cid, i = ber_read(b, i)
        if cid == 0:
            if terminated:
                return rec, i
            # untermintated top-level: a 0 byte is still a terminator
            rec.append([0, None])
            continue
        size, i = ber_read(b, i)
        data = b[i:i + size]
        i += size
        sub = schema.get(cid) if schema else None
        if sub == "cmds":
            rec.append([cid, parse_commands(data)])
        elif isinstance(sub, dict):
            rec.append([cid, parse_array(data, sub)])
        else:
            rec.append([cid, data])
    if terminated:
        raise ValueError("record ran past end without terminator")
    return rec, i


def parse_array(b, schema):
    arr = Array()
    i = 0
    n, i = ber_read(b, i)
    for _ in range(n):
        idx, i = ber_read(b, i)
        rec, i = parse_record(b, i, len(b), schema, terminated=True)
        arr.items.append((idx, rec))
    if i != len(b):
        raise ValueError(f"array has {len(b) - i} trailing bytes")
    return arr


def record_bytes(rec, schema, terminated):
    out = bytearray()
    # recompute command byte-size companions: schema key ("size_of", cid)
    sizes = {}
    for cid, val in rec:
        if schema.get(cid) == "cmds":
            sizes[cid] = len(commands_bytes(val))
    for cid, val in rec:
        if cid == 0 and val is None:
            out += b"\x00"
            continue
        sub = schema.get(cid)
        if sub == "cmds":
            data = commands_bytes(val)
        elif isinstance(sub, dict):
            data = array_bytes(val, sub)
        elif isinstance(sub, tuple) and sub[0] == "size_of" and sub[1] in sizes:
            data = ber_write(sizes[sub[1]])
        else:
            data = val
        out += ber_write(cid) + ber_write(len(data)) + data
    if terminated:
        out += b"\x00"
    return bytes(out)


def array_bytes(arr, schema):
    out = bytearray(ber_write(len(arr.items)))
    for idx, rec in arr.items:
        out += ber_write(idx) + record_bytes(rec, schema, terminated=True)
    return bytes(out)


# ---------------------------------------------------------------- schemas
PAGE = {0x33: ("size_of", 0x34), 0x34: "cmds"}
MAP = {0x51: {0x05: PAGE}}                         # events -> pages
COMMON = {0x15: ("size_of", 0x16), 0x16: "cmds"}
TROOP_PAGE = {0x0C: ("size_of", 0x0D), 0x0D: "cmds"}
LDB = {
    0x0B: {},             # actors
    0x0C: {},             # skills
    0x0D: {},             # items
    0x0E: {},             # enemies
    0x0F: {0x0B: TROOP_PAGE},  # troops
    0x10: {},             # terrain
    0x11: {},             # attributes
    0x12: {},             # states
    0x13: {},             # animations
    0x14: {},             # chipsets
    0x19: COMMON,         # common events
}
LMT = {}


@dataclass
class LcfFile:
    header: bytes        # raw header string incl. length prefix
    body: list           # top-level record
    schema: dict
    tail: bytes = b""

    @classmethod
    def load(cls, path, schema):
        b = open(path, "rb").read()
        hl, i = ber_read(b, 0)
        i += hl
        header = b[:i]
        if schema is LMT:
            # LMT top level is not a chunk record (map info array first); keep raw
            return cls(header, b[i:], schema)
        body, j = parse_record(b, i, len(b), schema, terminated=False)
        return cls(header, body, schema, b[j:])

    def to_bytes(self):
        if self.schema is LMT:
            return self.header + self.body
        return self.header + record_bytes(self.body, self.schema, terminated=False) + self.tail

    def save(self, path):
        with open(path, "wb") as f:
            f.write(self.to_bytes())


def get(rec, cid, default=None):
    for c, v in rec:
        if c == cid:
            return v
    return default


def set_(rec, cid, val):
    for item in rec:
        if item[0] == cid:
            item[1] = val
            return
    rec.append([cid, val])


def schema_for(path):
    p = path.lower()
    if p.endswith(".lmu"):
        return MAP
    if p.endswith(".ldb"):
        return LDB
    return LMT
