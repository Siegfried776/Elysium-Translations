#!/usr/bin/env python3
"""Build the English retranslation patch for 映夢 Dream (Steam).

Inserts translation/en.json into the English column of the game's
LocalizedText table (inside Dream_Data/resources.assets) and writes an
xdelta patch against your original, unmodified resources.assets.

Usage:
    python tools/build_patch.py "<path to original resources.assets>" [--out build]

Requires: Python 3.9+, UnityPy (pip install -r tools/requirements.txt),
and xdelta3 on PATH (or pass --xdelta path/to/xdelta3).
"""
import argparse
import json
import pathlib
import subprocess
import sys

import UnityPy

ROOT = pathlib.Path(__file__).resolve().parent.parent
EN_JSON = ROOT / "translation" / "en.json"
TEXT_ASSET = "LocalizedText"


def build(source: pathlib.Path, out_dir: pathlib.Path, xdelta: str) -> None:
    translation = json.loads(EN_JSON.read_text(encoding="utf-8"))
    env = UnityPy.load(str(source))

    found = False
    for obj in env.objects:
        if obj.type.name != "TextAsset":
            continue
        data = obj.read()
        if data.m_Name != TEXT_ASSET:
            continue
        table = json.loads(data.m_Script.lstrip("﻿"))
        missing = [k for k in translation if k not in table]
        if missing:
            sys.exit(f"IDs not found in the game's table (wrong game version?): {missing[:10]}")
        for key, text in translation.items():
            table[key]["English"] = text
        # The game ships this file with 4-space indentation and CRLF line endings.
        data.m_Script = json.dumps(table, ensure_ascii=False, indent=4).replace("\n", "\r\n")
        data.save()
        found = True
        break
    if not found:
        sys.exit(f"TextAsset '{TEXT_ASSET}' not found in {source}")

    out_dir.mkdir(parents=True, exist_ok=True)
    patched = out_dir / "resources.assets"
    patched.write_bytes(env.file.save())

    patch = out_dir / "Dream_patch.xdelta"
    subprocess.run([xdelta, "-e", "-9", "-S", "djw", "-f", "-s", str(source), str(patched), str(patch)], check=True)

    # Round trip: applying the patch to the original must reproduce the patched file exactly.
    check = out_dir / "roundtrip.assets"
    subprocess.run([xdelta, "-d", "-f", "-s", str(source), str(patch), str(check)], check=True)
    if check.read_bytes() != patched.read_bytes():
        sys.exit("Round-trip check failed: patch does not reproduce the patched file.")
    check.unlink()
    print(f"OK: {len(translation)} entries -> {patch}")


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("source", type=pathlib.Path, help="original, unmodified Dream_Data/resources.assets")
    p.add_argument("--out", type=pathlib.Path, default=ROOT / "build")
    p.add_argument("--xdelta", default="xdelta3")
    a = p.parse_args()
    build(a.source, a.out, a.xdelta)
