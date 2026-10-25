"""End-to-end test of the release zip in a clean copy of the game.

python -I tools/test_release.py <zip> <rtp_installer.exe>
1. build/release_test = original/data + start.exe + Readme.txt (the game as bought, v1.20)
2. extract the zip into it, run Install.bat's script (RTP from the local installer copy, as if downloaded)
3. every data file must equal build/release_game (Player.exe there = data/RPG_RT.exe here), plus the RTP
   sounds (listed in rtp_files.tsv) byte-equal to the installer's files; nothing else added
4. run the installer again (must be a no-op), then uninstall: the folder must equal the original again
"""
import sys, os, shutil, subprocess, zipfile, hashlib, filecmp
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import textunits as tu

sys.stdout.reconfigure(encoding="utf-8")
root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
zpath, rtp_exe = os.path.abspath(sys.argv[1]), os.path.abspath(sys.argv[2])
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
    r = subprocess.run(["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File",
                        os.path.join(T, "LostMaria_English", "files", script), *args],
                       capture_output=True, text=True, encoding="utf-8", errors="replace")
    print(f"--- {script} exit {r.returncode}")
    print("\n".join(r.stdout.strip().splitlines()[-8:]))
    if r.stderr.strip():
        print("STDERR:", r.stderr.strip()[-1500:])
    return r.returncode


if os.path.exists(T):
    shutil.rmtree(T)
shutil.copytree(os.path.join(ORIG, "data"), os.path.join(T, "data"))
for f in ("start.exe", "Readme.txt"):
    shutil.copy2(os.path.join(ORIG, f), T)
before = tree(T)
zipfile.ZipFile(zpath).extractall(T)
pkg = {k for k in tree(T) if k.startswith("LostMaria_English")}
fails = []
if ps("install.ps1", "-RtpInstaller", rtp_exe):
    fails.append("install failed")

# 3. compare
after = {k: v for k, v in tree(T).items() if k not in pkg}
want = {}
for k, v in tree(GAME).items():
    if not k.startswith("data") or k == "data\\RPG_RT.exe":      # replaced by EasyRPG (Player.exe)
        continue
    want[k.replace("Player.exe", "RPG_RT.exe")] = v
want["data\\manual.htm"] = hashlib.sha256(open(os.path.join(root, "release", "manual_en.htm"), "rb").read()).hexdigest()
rtp = tu.read_tsv(os.path.join(root, "release", "rtp_files.tsv"))
x = os.path.join(root, "build", "rtp_x")
if os.path.exists(x):
    shutil.rmtree(x)
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
if ps("install.ps1", "-RtpInstaller", rtp_exe):
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
print("RESULT:", "PASS" if not fails else "FAIL " + "; ".join(fails))
sys.exit(1 if fails else 0)
