"""One ellipsis on short murmured phrases (user, play-test 2026-10-24): "...Goodbye..." -> "Goodbye...".

Used by merge.py. A line (after leading codes/padding, or inside a speaker's quote) that starts
"...<phrase>..." where the phrase has at most MAX_WORDS words, no dots of its own, and starts with
a capital letter, loses the leading ellipsis, whether the line ends there or goes on
("...But... where in that mansion" -> "But... where in that mansion"; user, play-test).
Lowercase starts are left alone (they usually continue a sentence, so the opening pause carries
meaning), as are longer phrases.
python -I tools/ellipsis_rule.py      -> preview of what it would change in build/units_en.tsv
"""
import re

MAX_WORDS = 4
# group 1: everything before the leading ellipsis (codes, padding, 'Name: "'), group 2: the phrase
RULE = re.compile(r'^((?:\\[<>^.|!_$]|\s)*(?:[^"\n]{1,24}: ")?(?:\\[<>^.|!_$]|\s)*)\.\.\.'
                  r'(?=([A-Z][^.\n"]*?)\.\.\.(?:[\s\\"?!]|$))')


def apply(text, sep="␤"):
    out = []
    for line in text.split(sep):
        m = RULE.match(line)
        if m and len(m.group(2).split()) <= MAX_WORDS:
            line = m.group(1) + line[m.end():]
        out.append(line)
    return sep.join(out)


if __name__ == "__main__":
    import sys, os
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    sys.stdout.reconfigure(encoding="utf-8")
    import textunits as tu
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    n = 0
    for r in tu.read_tsv(os.path.join(root, "build", "units_en.tsv")):
        if r["kind"] != "msg" or not r["en"]:
            continue
        new = apply(r["en"])
        if new != r["en"]:
            n += 1
            for a, b in zip(r["en"].split(tu.SEP), new.split(tu.SEP)):
                if a != b:
                    print(f"{r['id']}: {a.strip()}  ->  {b.strip()}")
    print(n, "units changed")
