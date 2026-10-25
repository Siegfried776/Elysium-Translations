"""Side-effect check after the punctuation pass (counts + unit ids only; no line text).

python -I tools/punct_lint.py [--ids]
Runs on build/units_en.tsv (own message units, control codes removed).
"""
import sys, os, re, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import textunits as tu

sys.stdout.reconfigure(encoding="utf-8")
root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
plan = {p["id"]: p for p in tu.read_tsv(os.path.join(root, "work", "plan.tsv"))}
C = re.compile(r"\\[A-Za-z]\[\d+\]|\\[.|!<>^$_]")
CHECKS = {
    "space before punctuation": r"\w \s*[,.!?;:](?!\.\.)",
    "double space mid-line": r"\S  +\S",
    "doubled mark": r"(?<!\.)[,;:]{2}|[!?]{3,}|,\.|\.,(?!\.)|!\.(?!\.)|\?\.(?!\.)",
    "4+ dots / spaced dots": r"\.{4,}|\. \. \.",
    "lowercase after full stop": r"(?<!\.)(?<![A-Z])\. +[a-z]",
    "spaced em dash": r" — | —|— ",
    "!? order": r"!\?",
    "empty quotes": r'""|\(\)',
    "comma after opening But/And/So": r'(?:^|[."(] )(?:But|And|So), ',
    # a box with no letters or digits must be a silence form ("...", "...?", "...!?", or a bare "?"/"!"
    # reaction), never a lone dash ("—?!")
    "letterless box, not a silence": r'^(?=[^A-Za-z0-9]*$)(?![\s|>"(]*(?:[^:]*: ["(])?\s*(?:\.\.\.)?[?!]*["\)]?[\s|]*$).*\S',
}
hits = collections.defaultdict(list)
snips = collections.defaultdict(collections.Counter)
for r in tu.read_tsv(os.path.join(root, "build", "units_en.tsv")):
    if r["kind"] != "msg" or plan.get(r["id"], {}).get("role") != "own":
        continue
    # line breaks become " | " so a break is not mistaken for a double space
    t = C.sub("", r["en"]).replace("␤", " | ")
    for name, pat in CHECKS.items():
        ms = list(re.finditer(pat, t))
        if ms:
            hits[name].append(r["id"])
            for m in ms:
                snips[name][t[max(0, m.start() - 2):m.end() + 2]] += 1
for name in CHECKS:
    ids = hits.get(name, [])
    print(f"{len(ids):4}  {name}" + (f"  {ids[:12]}" if "--ids" in sys.argv and ids else ""))
    if "--snippets" in sys.argv and ids:      # a few characters around each match, most common first
        print("        ", snips[name].most_common(8))
