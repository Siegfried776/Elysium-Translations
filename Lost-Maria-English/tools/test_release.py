"""End-to-end test of the release zip in a clean copy of the game.

python -I tools/test_release.py <zip> <rtp_installer.exe | -> [previous_release.zip]
1. build/release_test = original/data + its top-level files (the game as bought: v1.21 since 2026-11-05)
2. extract the zip into it, run Install.bat's script (RTP from the local installer copy, as if downloaded;
   "-" when the package fetches no RTP, as for v1.21, which bundles it)
3. every data file must equal build/release_game (Player.exe there = data/RPG_RT.exe here), plus the RTP
   sounds (listed in rtp_files.tsv) byte-equal to the installer's files; nothing else added
4. run the installer again (must be a no-op), then uninstall: the folder must equal the original again
5. with a previous release zip: install it, install this one over it (result = this version), uninstall
   (folder = original again)
"""
import sys, os, shutil, subprocess, zipfile, hashlib, filecmp
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import textunits as tu

sys.stdout.reconfigure(encoding="utf-8")
root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
zpath = os.path.abspath(sys.argv[1])
rtp_exe = os.path.abspath(sys.argv[2]) if sys.argv[2] != "-" else None
RTP_ARGS = ["-RtpInstaller", rtp_exe] if rtp_exe else []
T = os.path.join(root, "build", "release_test")
ORIG, GAME = os.path.join(root, "original"), os.path.join(root, "build", "release_game")


def tree(base):
    out = {}
    for dp, dn, fn in os.walk(base):
        for f in fn:
            p = os.path.join(dp, f)
            out[os.path.relpath(p, base)] = hashlib.sha256(open(p, "rb").read()).hexdigest()
    return out


def ps(script, *args):
    # a player's Install.bat starts Windows PowerShell with a clean environment: drop the module path
    # this session may carry (it made Get-FileHash unloadable in a test run, 2026-11-05)
    env = {k: v for k, v in os.environ.items() if k.upper() != "PSMODULEPATH"}
    r = subprocess.run(["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File",
                        os.path.join(T, "LostMaria_English", "files", script), *args],
                       capture_output=True, text=True, encoding="utf-8", errors="replace", env=env)
    print(f"--- {script} exit {r.returncode}")
    print("\n".join(r.stdout.strip().splitlines()[-8:]))
    if r.stderr.strip():
        print("STDERR:", r.stderr.strip()[-1500:])
    return r.returncode


if os.path.exists(T):
    shutil.rmtree(T)
shutil.copytree(os.path.join(ORIG, "data"), os.path.join(T, "data"))
for f in os.listdir(ORIG):                       # top-level files as bought (start.exe, Readme, manual.htm)
    if os.path.isfile(os.path.join(ORIG, f)) and f != "SHA256.txt":
        shutil.copy2(os.path.join(ORIG, f), T)
before = tree(T)
zipfile.ZipFile(zpath).extractall(T)
pkg = {k for k in tree(T) if k.startswith("LostMaria_English")}
fails = []
if ps("install.ps1", *RTP_ARGS):
    fails.append("install failed")

# 3. compare
after = {k: v for k, v in tree(T).items() if k not in pkg}
FILES = os.path.join(T, "LostMaria_English", "files")
swaps_exe = any(r["path"] == "data\\RPG_RT.exe" for r in tu.read_tsv(os.path.join(FILES, "manifest.tsv")))
want = {}
for k, v in tree(GAME).items():
    if not k.startswith("data"):
        continue
    if swaps_exe:                       # v1.0: EasyRPG (Player.exe in the build) installed as RPG_RT.exe
        if k == "data\\RPG_RT.exe":
            continue
        want[k.replace("Player.exe", "RPG_RT.exe")] = v
    elif k != "data\\Player.exe":       # v1.21 ships EasyRPG as its RPG_RT.exe; the build's extra copy isn't installed
        want[k] = v
man_rel = "manual.htm" if os.path.exists(os.path.join(ORIG, "manual.htm")) else "data\\manual.htm"
want.pop("data\\manual.htm", None)
want[man_rel] = hashlib.sha256(open(os.path.join(root, "release", "manual_en.htm"), "rb").read()).hexdigest()
rtp = tu.read_tsv(os.path.join(FILES, "rtp_files.tsv"))
x = os.path.join(root, "build", "rtp_x")
if os.path.exists(x):
    shutil.rmtree(x)
if rtp:
    subprocess.run([r"C:\Program Files\7-Zip\7z.exe", "x", rtp_exe, "-o" + x, "Sound\\*", "Music\\*", "-y"],
                   check=True, stdout=subprocess.DEVNULL)
for r in rtp:
    want[f"data\\{r['folder']}\\{r['jp']}.wav"] = hashlib.sha256(open(os.path.join(x, r["en"]), "rb").read()).hexdigest()
backup = {k for k in after if k.startswith("_original")}
extra = sorted(set(after) - set(want) - backup - {"ENGLISH_PATCH.txt", "start.exe", "Readme.txt"})
missing = sorted(set(want) - set(after))
diff = sorted(k for k in want if k in after and after[k] != want[k])
print(f"installed: {len(want)} expected files, {len(missing)} missing, {len(diff)} different, {len(extra)} unexpected; "
      f"backup holds {len(backup)} files")
for k in (missing + diff + extra)[:8]:
    print("  ", k)
if missing or diff or extra:
    fails.append("install result differs")
assert after["start.exe"] == before["start.exe"]

# 4. rerun = no-op, then uninstall
if ps("install.ps1", *RTP_ARGS):
    fails.append("second install failed")
if ps("uninstall.ps1"):
    fails.append("uninstall failed")
restored = {k: v for k, v in tree(T).items() if k not in pkg}
if restored != before:
    d = sorted(set(restored) ^ set(before)) + sorted(k for k in before if k in restored and restored[k] != before[k])
    print("after uninstall, differs from the original:", len(d), d[:8])
    fails.append("uninstall not clean")
else:
    print("uninstall: folder identical to the original game")
# 5. upgrade path (optional 3rd argument = the previous release zip): install it, then this one over it
if len(sys.argv) > 3:
    shutil.rmtree(T)
    shutil.copytree(os.path.join(ORIG, "data"), os.path.join(T, "data"))
    for f in os.listdir(ORIG):
        if os.path.isfile(os.path.join(ORIG, f)) and f != "SHA256.txt":
            shutil.copy2(os.path.join(ORIG, f), T)
    zipfile.ZipFile(os.path.abspath(sys.argv[3])).extractall(T)
    if ps("install.ps1", *RTP_ARGS):
        fails.append("previous version install failed")
    shutil.rmtree(os.path.join(T, "LostMaria_English"))
    zipfile.ZipFile(zpath).extractall(T)
    if ps("install.ps1", *RTP_ARGS):
        fails.append("upgrade install failed")
    up = {k: v for k, v in tree(T).items() if k not in pkg}
    bad = sorted(k for k in want if up.get(k) != want[k])
    print(f"upgrade: {len(bad)} files differ from this version", bad[:5])
    if bad:
        fails.append("upgrade result differs")
    if ps("uninstall.ps1"):
        fails.append("uninstall after upgrade failed")
    restored = {k: v for k, v in tree(T).items() if k not in pkg}
    if restored != before:
        print("after upgrade + uninstall, differs from the original:",
              sorted(set(restored) ^ set(before))[:8])
        fails.append("uninstall after upgrade not clean")
    else:
        print("upgrade + uninstall: folder identical to the original game")
print("RESULT:", "PASS" if not fails else "FAIL " + "; ".join(fails))
sys.exit(1 if fails else 0)
