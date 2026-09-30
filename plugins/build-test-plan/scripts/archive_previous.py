"""Move the previous run set (test-plan_<timestamp>.*) from <out> into <out>/history/.

Copy, verify size, then delete the original, so a failure never loses the last good plan.
assets/ and history/ are never touched. Usage: archive_previous.py --out <folder>
"""
import argparse
import json
import re
import shutil
import sys
from pathlib import Path

PAT = re.compile(r"^(test-plan_\d{4}-\d{2}-\d{2}T\d{2}-\d{2}-\d{2}(?:-[a-z0-9]+)?)\.")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    out = Path(a.out)
    hist = out / "history"
    moved = []
    if out.is_dir():
        files = [p for p in out.iterdir() if p.is_file() and PAT.match(p.name)]
        if files:
            hist.mkdir(exist_ok=True)
        for p in files:
            dest = hist / p.name
            if dest.exists():  # same name already archived: keep both
                stem, suf = p.name.split(".", 1)
                n = 2
                while (hist / f"{stem}-dup{n}.{suf}").exists():
                    n += 1
                dest = hist / f"{stem}-dup{n}.{suf}"
            shutil.copy2(p, dest)
            if dest.stat().st_size != p.stat().st_size:
                print(json.dumps({"ok": False, "error": f"Copy verification failed for {p.name}; nothing removed."}))
                sys.exit(1)
            p.unlink()
            moved.append(p.name)
    print(json.dumps({"ok": True, "archived": moved}, indent=2))


if __name__ == "__main__":
    main()
