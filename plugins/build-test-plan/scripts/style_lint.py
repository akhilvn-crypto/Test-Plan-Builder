"""Style lint for the generated test plan. Reports only; never rewrites.

Usage: style_lint.py <plan.md> [--banned banned-phrases.txt] [--json]
Exit code is always 0 when the lint ran; findings are in the output.
"""
import argparse
import json
import re
import sys
from collections import Counter
from pathlib import Path

MAX_SENTENCE_WORDS = 35


def load_banned(path):
    if not path or not Path(path).is_file():
        return []
    return [l.strip().lower() for l in Path(path).read_text(encoding="utf-8").splitlines() if l.strip() and not l.startswith("#")]


def split_md(text):
    """Return (prose_paragraphs, bullet_groups) ignoring frontmatter, code, tables and headings."""
    if text.startswith("---"):
        end = text.find("\n---", 3)
        if end != -1:
            text = text[end + 4:]
    paras, groups, cur_p, cur_b = [], [], [], []
    in_code = False

    def flush_p():
        nonlocal cur_p
        if cur_p:
            paras.append(" ".join(cur_p))
            cur_p = []

    def flush_b():
        nonlocal cur_b
        if cur_b:
            groups.append(cur_b)
            cur_b = []

    for line in text.splitlines():
        s = line.strip()
        if s.startswith("```"):
            in_code = not in_code
            continue
        if in_code or s.startswith("|") or s.startswith("#") or s.startswith("<") or s.startswith("---"):
            flush_p()
            flush_b()
            continue
        m = re.match(r"^([-*+]|\d+\.)\s+(.*)", s)
        if m:
            flush_p()
            cur_b.append(m.group(2))
            paras.append(m.group(2))
            continue
        if not s:
            flush_p()
            flush_b()
            continue
        flush_b()
        cur_p.append(s)
    flush_p()
    flush_b()
    return paras, groups


def sentences(par):
    return [s.strip() for s in re.split(r"(?<=[.!?])\s+", par) if s.strip()]


def strip_md(s):
    return re.sub(r"[*_`]", "", s)


def lint(text, banned):
    findings = []
    paras, groups = split_md(text)
    prose = "\n".join(paras)
    low = strip_md(prose).lower()

    for ph in banned:
        n = len(re.findall(r"(?<![\w-])" + re.escape(ph) + r"(?![\w-])", low))
        if n:
            findings.append({"type": "banned-phrase", "detail": f'"{ph}" x{n}'})

    all_sents = [strip_md(s) for p in paras for s in sentences(p)]
    openers = Counter(" ".join(s.lower().split()[:2]) for s in all_sents if len(s.split()) > 3)
    for op, n in openers.items():
        if n >= 4:
            findings.append({"type": "repeated-opener", "detail": f'{n} sentences start with "{op}"'})

    for s in all_sents:
        w = len(s.split())
        if w > MAX_SENTENCE_WORDS:
            findings.append({"type": "long-sentence", "detail": f"{w} words: {s[:90]}..."})

    words = max(len(low.split()), 1)
    dashes = prose.count("—")
    if dashes / words * 100 > 0.6:
        findings.append({"type": "em-dash-density", "detail": f"{dashes} em dashes in {words} words"})

    if re.search(r"\bnot (just|only|merely)\b[^.]{0,80}\bbut\b", low):
        findings.append({"type": "not-just-but", "detail": '"not just X, but Y" construction'})

    for g in groups:
        if len(g) >= 5:
            lens = [len(strip_md(b).split()) for b in g]
            if max(lens) - min(lens) <= 1:
                findings.append({"type": "uniform-bullets", "detail": f"{len(g)} bullets of ~{lens[0]} words: {g[0][:60]}..."})

    for m in re.finditer(r"(?im)^(#{2,4}\s+.*)\n+([^\n#|\-*].*)", text):
        head = re.sub(r"^#+\s+([\d.]+\s+|[A-Z]\.\s+)?", "", m.group(1)).strip().lower()
        first = strip_md(sentences(m.group(2))[0]).lower() if sentences(m.group(2)) else ""
        if head and len(head) > 4 and first.startswith(head):
            findings.append({"type": "restated-heading", "detail": f'first sentence repeats heading "{head}"'})
    return findings


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("plan")
    ap.add_argument("--banned")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()
    try:
        text = Path(a.plan).read_text(encoding="utf-8")
    except OSError as e:
        print(f"Cannot read {a.plan}: {e}", file=sys.stderr)
        sys.exit(2)
    banned = load_banned(a.banned)
    f = lint(text, banned)
    if a.json:
        print(json.dumps({"count": len(f), "findings": f}, indent=2))
    elif not f:
        print("Style lint: no findings.")
    else:
        print(f"Style lint: {len(f)} finding(s)")
        for x in f:
            print(f"- [{x['type']}] {x['detail']}")


if __name__ == "__main__":
    main()
