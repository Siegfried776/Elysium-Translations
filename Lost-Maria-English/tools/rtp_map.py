"""Map the RTP files the game needs (tools/rtp_needs.py) to the official English RTP's filenames.

python -I tools/rtp_map.py <rtp_table.cpp> [rtp_listing.txt]   -> release/rtp_files.tsv
rtp_table.cpp = EasyRPG Player 0.8.1.1 src/rtp_table.cpp (columns: folder, Official Japanese,
Official English, ...). rtp_listing.txt (optional) = `7z l` of KADOKAWA's rpg2000_rtp_installer.exe;
every mapped English file must be in it. Output columns: folder (game data folder), jp (name the game
uses), en (path inside the installer).
"""
import sys, os, re, subprocess
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import textunits as tu

sys.stdout.reconfigure(encoding="utf-8")
root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
src = open(sys.argv[1], encoding="utf-8").read()
block = src[src.index("rtp_table_2k"):src.index("rtp_table_2k3")]
table = {}
for folder, jp, en in re.findall(r'\{"(\w+)", "([^"]*)", (?:"([^"]*)"|nullptr)', block):
    if en:
        table[(folder.lower(), jp)] = en

out = subprocess.run([sys.executable, "-I", os.path.join(root, "tools", "rtp_needs.py")],
                     capture_output=True, text=True, encoding="utf-8", check=True).stdout
needs = [l.split("\t")[:2] for l in out.splitlines() if l.startswith(("Sound\t", "Music\t"))]
listing = ""
if len(sys.argv) > 2:
    listing = open(sys.argv[2], encoding="utf-8", errors="replace").read().lower()
rows, bad = [], []
for folder, jp in needs:
    en = table.get((folder.lower(), jp))
    if not en:
        bad.append(f"no English name: {folder}/{jp}")
        continue
    path = f"{folder}\\{en}.wav"
    if listing and path.lower() not in listing:
        bad.append(f"not in the installer: {path} (for {folder}/{jp})")
    rows.append({"folder": folder, "jp": jp, "en": path})
os.makedirs(os.path.join(root, "release"), exist_ok=True)
tu.write_tsv(os.path.join(root, "release", "rtp_files.tsv"), ["folder", "jp", "en"], rows)
print(f"{len(rows)} of {len(needs)} mapped -> release/rtp_files.tsv")
for b in bad:
    print("  !", b)
sys.exit(1 if bad else 0)
