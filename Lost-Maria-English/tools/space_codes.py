"""Global pass: add the display space after invisible pause codes.

python -I tools/space_codes.py            -> writes work/overlays/lead_zspacing.json, lists review cases
The codes \\. \\| \\! print nothing, so "Wait,\\.you" shows as "Wait,you".
Rule: after a pause code (or a run of them), insert one space when
  - the character before the code(s) is punctuation (.,!?;:)"') and
  - the next character is a letter, digit or an opening quote/paren.
Not touched: stutters ("I-\\.If"), code at line start, a code already followed by a space.
Letter-code-letter cases ("BUT\\.THIS") are listed for review and spaced only if listed in
work/overlays/zspacing_letters_ok.txt (one id per line).
Runs on the merged final text (work/master.tsv), owner units only; the overlay sorts last
(lead_z...) so it applies after every other overlay.
"""
import sys, os, re, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import textunits as tu

sys.stdout.reconfigure(encoding="utf-8")
root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
W = os.path.join(root, "work")
out_p = os.path.join(W, "overlays", "lead_zspacing.json")
if os.path.exists(out_p):
    os.remove(out_p)          # recompute from the text without this overlay
    import subprocess
    subprocess.run([sys.executable, "-I", os.path.join(root, "tools", "merge.py")], check=True, stdout=subprocess.DEVNULL)
rows = [r for r in tu.read_tsv(os.path.join(W, "master.tsv")) if r["role"] == "own" and r["final"]]
ok_p = os.path.join(W, "overlays", "zspacing_letters_ok.txt")
letters_ok = set(open(ok_p, encoding="utf-8").read().split()) if os.path.exists(ok_p) else set()

PUNCT = re.compile(r"(?<=[.,!?;:)\"'])((?:\\[.|!])+)(?=[A-Za-z0-9\"(])")
LETTER = re.compile(r"(?<=[A-Za-z])((?:\\[.|!])+)(?=[A-Za-z])")
ov, review, overflow = {}, [], []
for r in rows:
    s = r["final"]
    t = PUNCT.sub(lambda m: m.group(1) + " ", s)
    for m in LETTER.finditer(t):
        review.append((r["id"], t[max(0, m.start() - 12):m.end() + 12]))
    if r["id"] in letters_ok:
        t = LETTER.sub(lambda m: m.group(1) + " ", t)
    if t != s:
        too_wide = r["kind"] == "msg" and any(
            tu.width(l) + 8 * len(re.findall(r"\\N\[\d+\]", l)) > tu.LINE_MAX for l in t.split(tu.SEP))
        if too_wide:
            overflow.append(r["id"])
        else:
            ov[r["id"]] = t
json.dump(ov, open(out_p, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(f"lead_zspacing.json: {len(ov)} units spaced")
if overflow:
    print(f"NOT spaced because a line would exceed {tu.LINE_MAX} cells (fix by hand in lead_zz_manual.json): {overflow}")
print(f"letter-code-letter cases for review ({len(review)}):")
for k, ctx in review:
    print(" ", "OK " if k in letters_ok else "   ", k, repr(ctx))
