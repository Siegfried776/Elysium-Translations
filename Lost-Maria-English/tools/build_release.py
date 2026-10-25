"""Build the release package: an xdelta patch set + installer, no game files.

python -I tools/build_release.py <version>          e.g. 1.0
1. build_game.py -> build/release_game (fresh copy: merge, regressions, inject, images, font, verify)
2. diff build/release_game/data against original/data:
   changed game files -> xdelta3 patch against the original ("patch")
   new translation images (LM_*) -> xdelta3 against the card they are drawn from ("patch")
   our own files (font, EasyRPG as data/RPG_RT.exe, English manual.htm) -> shipped as they are ("copy")
3. stage release_build/LostMaria_English/ (Install.bat, Uninstall.bat, README.txt, files/...) and zip it
   to release_build/LostMaria_English_v<version>.zip
manifest.tsv columns: path (in the game folder), op, payload (in files/), base (original file the patch
applies to / that gets replaced), base_sha, dst_sha. The installer refuses to patch anything whose
base_sha doesn't match (game v1.20 from BOOTH only).
"""
import sys, os, shutil, subprocess, hashlib, zipfile, filecmp
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import textunits as tu

sys.stdout.reconfigure(encoding="utf-8")
root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
version = sys.argv[1]
py = [sys.executable, "-I"]
ORIG = os.path.join(root, "original")
GAME = os.path.join(root, "build", "release_game")
OUT = os.path.join(root, "release_build")
PKG = os.path.join(OUT, "LostMaria_English")
FILES = os.path.join(PKG, "files")
XD = os.path.join(root, "vendor", "xdelta3.exe")


def sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def rel(p, base):
    return os.path.relpath(p, base).replace("/", "\\")


# 1. fresh build (no saves in it)
if os.path.exists(GAME):
    shutil.rmtree(GAME)
subprocess.run(py + [os.path.join(root, "tools", "build_game.py"), GAME], check=True)

# the card the new food cards are drawn from (img_build.FOOD_BASE = an images.tsv id)
fb = next(r for r in tu.read_tsv(os.path.join(root, "work", "img", "images.tsv"))
          if r["id"] == open(os.path.join(root, "tools", "img_build.py"), encoding="utf-8").read()
          .split('FOOD_BASE = "')[1].split('"')[0])
FOOD_BASE = os.path.join("data", "Picture", fb["name"] + ".png")
assert os.path.exists(os.path.join(ORIG, FOOD_BASE)), FOOD_BASE

if os.path.exists(PKG):
    shutil.rmtree(PKG)
os.makedirs(os.path.join(FILES, "patches"))
os.makedirs(os.path.join(FILES, "new"))
os.makedirs(os.path.join(FILES, "bin"))
os.makedirs(os.path.join(FILES, "tmpbuild"))
TB = os.path.join(FILES, "tmpbuild")

rows, n = [], 0
skip = {"Player.exe"}                    # shipped as data\RPG_RT.exe below
for dp, dn, fn in os.walk(os.path.join(GAME, "data")):
    for f in sorted(fn):
        new = os.path.join(dp, f)
        r = rel(new, GAME)
        if f in skip or (f.startswith("Save") and f.endswith(".lsd")):
            continue
        old = os.path.join(ORIG, r)
        if os.path.exists(old) and filecmp.cmp(old, new, shallow=False):
            continue
        if r.lower().startswith("data\\font\\"):
            payload = "new\\" + f
            shutil.copy2(new, os.path.join(FILES, payload))
            rows.append({"path": r, "op": "copy", "payload": payload, "base": "", "base_sha": "", "dst_sha": sha(new)})
            continue
        base = r if os.path.exists(old) else FOOD_BASE
        assert os.path.exists(old) or f.startswith("LM_"), f"new file with no original: {r}"
        n += 1
        payload = f"patches\\{n:04d}.xd"
        # xdelta3 opens files through the ANSI API: work on ASCII temp names
        shutil.copy2(os.path.join(ORIG, base), os.path.join(TB, "s.bin"))
        shutil.copy2(new, os.path.join(TB, "t.bin"))
        subprocess.run([XD, "-e", "-9", "-f", "-s", "s.bin", "t.bin", "p.xd"], cwd=TB, check=True)
        shutil.move(os.path.join(TB, "p.xd"), os.path.join(FILES, payload))
        rows.append({"path": r, "op": "patch", "payload": payload, "base": base,
                     "base_sha": sha(os.path.join(ORIG, base)), "dst_sha": sha(new)})
shutil.rmtree(TB)

# EasyRPG Player replaces RPG_RT.exe, so the game's own start.exe launches it
player = os.path.join(root, "vendor", "easyrpg-0.8.1.1", "x", "Player.exe")
shutil.copy2(player, os.path.join(FILES, "new", "RPG_RT.exe"))
rows.append({"path": "data\\RPG_RT.exe", "op": "copy", "payload": "new\\RPG_RT.exe", "base": "data\\RPG_RT.exe",
             "base_sha": sha(os.path.join(ORIG, "data", "RPG_RT.exe")), "dst_sha": sha(player)})
# English manual (the original links its pictures from data\manual\, unchanged)
man = os.path.join(root, "release", "manual_en.htm")
shutil.copy2(man, os.path.join(FILES, "new", "manual.htm"))
rows.append({"path": "data\\manual.htm", "op": "copy", "payload": "new\\manual.htm", "base": "data\\manual.htm",
             "base_sha": sha(os.path.join(ORIG, "data", "manual.htm")), "dst_sha": sha(man)})

cols = ["path", "op", "payload", "base", "base_sha", "dst_sha"]
tu.write_tsv(os.path.join(FILES, "manifest.tsv"), cols, rows)
shutil.copy2(os.path.join(root, "release", "rtp_files.tsv"), os.path.join(FILES, "rtp_files.tsv"))

# installer, tools, licences
I = os.path.join(root, "release", "installer")
for f in ("install.ps1", "uninstall.ps1"):
    t = open(os.path.join(I, f), encoding="utf-8").read()
    assert t.isascii(), f"{f} must be ASCII (PowerShell 5.1 reads it as ANSI)"
    open(os.path.join(FILES, f), "w", encoding="ascii", newline="\r\n").write(t)
for f in ("Install.bat", "Uninstall.bat"):
    t = open(os.path.join(I, f), encoding="utf-8").read()
    open(os.path.join(PKG, f), "w", encoding="ascii", newline="\r\n").write(t)
for f in ("7z.exe", "7z.dll"):
    shutil.copy2(os.path.join(root, "vendor", "7zip", f), os.path.join(FILES, "bin", f))
shutil.copy2(XD, os.path.join(FILES, "bin", "xdelta3.exe"))
L = os.path.join(PKG, "licenses")
os.makedirs(L)
shutil.copy2(os.path.join(root, "vendor", "licenses", "GPL-3.0.txt"), os.path.join(L, "EasyRPG-Player_GPL-3.0.txt"))
shutil.copy2(os.path.join(root, "vendor", "licenses", "Apache-2.0.txt"), os.path.join(L, "xdelta3_Apache-2.0.txt"))
shutil.copy2(os.path.join(root, "vendor", "7zip", "License.txt"), os.path.join(L, "7-Zip_License.txt"))
shutil.copy2(os.path.join(root, "vendor", "fonts", "ark-pixel-12px-proportional", "x", "OFL.txt"),
             os.path.join(L, "Ark-Pixel-Font_OFL-1.1.txt"))
shutil.copy2(os.path.join(root, "release", "THIRD_PARTY.txt"), os.path.join(L, "THIRD_PARTY.txt"))
readme = open(os.path.join(root, "release", "README.txt"), encoding="utf-8").read().replace("{version}", version)
open(os.path.join(PKG, "README.txt"), "w", encoding="utf-8-sig", newline="\r\n").write(readme)

# zip
z = os.path.join(OUT, f"LostMaria_English_v{version}.zip")
if os.path.exists(z):
    os.remove(z)
with zipfile.ZipFile(z, "w", zipfile.ZIP_DEFLATED, compresslevel=9) as zf:
    for dp, dn, fn in os.walk(PKG):
        for f in sorted(fn):
            p = os.path.join(dp, f)
            zf.write(p, os.path.relpath(p, OUT))
n_patch = sum(r["op"] == "patch" for r in rows)
print(f"manifest: {len(rows)} files ({n_patch} patches, {len(rows) - n_patch} copies)")
print(f"zip: {z} ({os.path.getsize(z) / 1e6:.1f} MB)")
