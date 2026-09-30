"""Preflight for /build-test-plan.

Usage:
  preflight.py (--dir D | --file F) --output-format md|docx [--out O]          validate only, creates nothing
  preflight.py ... --init-assets                                               also create <out>/assets/
  preflight.py ... --detect-logo                                               list valid/invalid images in <out>/assets/

Prints one JSON object on stdout. Exit code 0 = ok, 1 = failed (message in "error").
"""
import argparse
import json
import sys
from pathlib import Path

USAGE = "/build-test-plan (--dir <folder> | --file <path>) --output-format <md|docx> [--out <folder>]"
IMAGE_EXT = {".png", ".jpg", ".jpeg"}


def fail(msg):
    print(json.dumps({"ok": False, "error": msg, "usage": USAGE}, indent=2))
    sys.exit(1)


def image_kind(path):
    """Return 'png'/'jpg' if the file really is that image, else None."""
    try:
        with open(path, "rb") as f:
            head = f.read(16)
    except OSError:
        return None
    if head.startswith(b"\x89PNG\r\n\x1a\n"):
        return "png"
    if head.startswith(b"\xff\xd8\xff"):
        return "jpg"
    return None


def detect_logo(assets):
    valid, invalid = [], []
    if assets.is_dir():
        for p in sorted(assets.iterdir()):
            if p.is_file() and p.suffix.lower() in IMAGE_EXT:
                if p.stat().st_size > 0 and image_kind(p):
                    valid.append(p.name)
                else:
                    invalid.append(p.name)
    return valid, invalid


def main():
    ap = argparse.ArgumentParser(add_help=False)
    ap.add_argument("--dir")
    ap.add_argument("--file")
    ap.add_argument("--output-format")
    ap.add_argument("--out", default="./test-plan-output")
    ap.add_argument("--init-assets", action="store_true")
    ap.add_argument("--detect-logo", action="store_true")
    try:
        a, extra = ap.parse_known_args()
    except SystemExit:
        fail("Could not read the arguments.")
    if extra:
        fail(f"Unknown argument(s): {' '.join(extra)}")

    if sys.version_info < (3, 8):
        fail("Python is required. Please install Python 3.x from python.org and re-run.")

    if bool(a.dir) == bool(a.file):
        fail("Give exactly one of --dir or --file.")
    if a.output_format not in ("md", "docx"):
        fail("--output-format is required and must be md or docx.")

    src = Path(a.dir or a.file)
    if a.dir and not src.is_dir():
        fail(f"--dir path is not a folder: {src}")
    if a.file and not src.is_file():
        fail(f"--file path is not a file: {src}")

    if a.output_format == "docx":
        try:
            import docx  # noqa: F401
        except ImportError:
            fail("Please run `pip install python-docx`.")

    out = Path(a.out)
    if out.exists() and not out.is_dir():
        fail(f"--out exists and is not a folder: {out}")
    try:
        if src.resolve() == out.resolve() or (a.dir and out.resolve().is_relative_to(src.resolve())):
            fail("--out must not be the input folder or inside it.")
    except OSError:
        pass

    result = {
        "ok": True,
        "input_mode": "dir" if a.dir else "file",
        "input_path": str(src),
        "output_format": a.output_format,
        "out": str(out),
        "assets": str(out / "assets"),
    }
    assets = out / "assets"
    if a.init_assets:
        assets.mkdir(parents=True, exist_ok=True)
        result["assets_created"] = True
    if a.detect_logo:
        valid, invalid = detect_logo(assets)
        result["logos_valid"] = valid
        result["logos_invalid"] = invalid
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
