#!/usr/bin/env python3
"""Fix the "Load Game won't respond" bug in 映夢 Dream.

The bug: before writing a save, the game "pretty-prints" its JSON with
    json.Replace(",", ",\n\t\t")
On systems whose locale writes decimals with a comma (e.g. German, French),
float values like 0,5 get split in two, the save becomes invalid JSON, and
the Load menu can no longer read it.

This script does two things:

  dll   Patches Assembly-CSharp-firstpass.dll so the call becomes
        Replace(",", ",") - a harmless no-op. This is the same change
        SaveFix_firstpass.xdelta makes. A backup (.orig) is written first.

  save  Repairs save files already written by the unpatched game, by
        undoing the inserted ",\n\t\t". A backup (.bak) is written first.
        Saves live in %USERPROFILE%\\AppData\\LocalLow\\RisingWin\\Dream\\PlayerData\\

Usage:
    python tools/savefix.py dll  "<game>/Dream_Data/Managed/Assembly-CSharp-firstpass.dll"
    python tools/savefix.py save "<...>/PlayerData/PlayerData1.json" [more files...]
"""
import shutil
import struct
import sys
from pathlib import Path

# ldstr operand inside TypeSettingJson (Steam build, Unity 2019.2.17f1).
# 0x7000a29b is the user-string token for ",\n\t\t"; 0x7000a297 is the token for ",".
TOKEN_OFFSET = 187635
OLD_TOKEN = struct.pack("<I", 0x7000A29B)
NEW_TOKEN = struct.pack("<I", 0x7000A297)
LDSTR = 0x72


def patch_dll(path: Path) -> None:
    data = bytearray(path.read_bytes())
    current = bytes(data[TOKEN_OFFSET:TOKEN_OFFSET + 4])
    if current == NEW_TOKEN:
        print(f"{path.name}: already patched.")
        return
    if data[TOKEN_OFFSET - 1] != LDSTR or current != OLD_TOKEN:
        sys.exit(f"{path.name}: unexpected bytes at offset {TOKEN_OFFSET}; different game version? Nothing changed.")
    backup = path.with_suffix(path.suffix + ".orig")
    if not backup.exists():
        shutil.copy2(path, backup)
    data[TOKEN_OFFSET:TOKEN_OFFSET + 4] = NEW_TOKEN
    path.write_bytes(data)
    print(f"{path.name}: patched (backup: {backup.name}).")


def read_7bit(buf: bytes, pos: int) -> tuple[int, int]:
    value = shift = 0
    while True:
        b = buf[pos]
        pos += 1
        value |= (b & 0x7F) << shift
        if not b & 0x80:
            return value, pos
        shift += 7


def write_7bit(n: int) -> bytes:
    out = bytearray()
    while True:
        b = n & 0x7F
        n >>= 7
        out.append(b | (0x80 if n else 0))
        if not n:
            return bytes(out)


def repair_save(path: Path) -> None:
    # A save is a .NET BinaryFormatter stream holding a single string:
    # 17-byte header record, 0x06 BinaryObjectString (int32 id + 7-bit-length-prefixed UTF-8), 0x0B end.
    raw = path.read_bytes()
    if len(raw) < 23 or raw[0] != 0x00 or raw[17] != 0x06:
        sys.exit(f"{path.name}: not a Dream save file.")
    start = 22
    length, text_pos = read_7bit(raw, start)
    text = raw[text_pos:text_pos + length].decode("utf-8")
    tail = raw[text_pos + length:]
    fixed = text.replace(",\n\t\t", ",")
    if fixed == text:
        print(f"{path.name}: nothing to repair.")
        return
    body = fixed.encode("utf-8")
    backup = path.with_suffix(path.suffix + ".bak")
    if not backup.exists():
        shutil.copy2(path, backup)
    path.write_bytes(raw[:start] + write_7bit(len(body)) + body + tail)
    print(f"{path.name}: repaired (backup: {backup.name}).")


if __name__ == "__main__":
    if len(sys.argv) < 3 or sys.argv[1] not in ("dll", "save"):
        sys.exit(__doc__)
    for arg in sys.argv[2:]:
        (patch_dll if sys.argv[1] == "dll" else repair_save)(Path(arg))
