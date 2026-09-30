"""Run metadata: md properties and sources.json. The LLM never writes these values.

  run_metadata.py start --out O --input-mode dir|file --input-path P --output-format md|docx \
                        --plugin-root R [--cover-logo FILE]
      Writes <out>/.run.json and prints it (stem, run_id, run_at, date, plugin_version, template_version).

  run_metadata.py finalize --out O --body body.md --project "<name>" [--tags a,b] \
                           [--unreadable path ...] [--source-file path ...]
      Prepends the md properties to the body, writes <stem>.md and <stem>.sources.json, removes .run.json and the body file.
      --source-file lists every source that was actually read (paths, repeatable, or @listfile with one path per line).

The md properties are the Emvigo Obsidian property keys (title, document_type, project_id, document_id, version,
approved_date, privacy, tags). Only title, document_type, privacy and tags are filled; the rest are left empty for the
user to fill in Obsidian. The docx carries no properties.
"""
import argparse
import hashlib
import json
import sys
import uuid
from datetime import datetime
from pathlib import Path

NA = "N/A"


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def yq(v):
    """Quote a YAML scalar only when needed."""
    s = str(v)
    if s and (any(c in s for c in ':#{}[],&*!|>\'"%@`') or s != s.strip() or s.lower() in ("yes", "no", "true", "false", "null")):
        return json.dumps(s, ensure_ascii=False)
    return s


def die(msg):
    print(json.dumps({"ok": False, "error": msg}))
    sys.exit(1)


def cmd_start(a):
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)

    plugin_root = Path(a.plugin_root)
    try:
        plugin_version = json.loads((plugin_root / ".claude-plugin" / "plugin.json").read_text(encoding="utf-8"))["version"]
    except (OSError, ValueError, KeyError):
        plugin_version = NA
    try:
        template_version = json.loads((plugin_root / "skills" / "test-plan-template" / "style-spec.json").read_text(encoding="utf-8"))["template_version"]
    except (OSError, ValueError, KeyError):
        template_version = NA

    now = datetime.now().astimezone()
    stem = "test-plan_" + now.strftime("%Y-%m-%dT%H-%M-%S")
    n = 0
    base = stem
    while any(out.glob(stem + ".*")) or any((out / "history").glob(stem + ".*")):
        n += 1
        stem = f"{base}-{n}"

    run = {
        "ok": True,
        "stem": stem,
        "run_id": str(uuid.uuid4()),
        "run_at": now.isoformat(timespec="seconds"),
        "date": now.strftime("%d-%b-%Y"),
        "cover_logo": (a.cover_logo or "").strip() or NA,
        "input_mode": a.input_mode,
        "input_path": a.input_path,
        "output_format": a.output_format,
        "plugin_version": plugin_version,
        "template_version": template_version,
    }
    (out / ".run.json").write_text(json.dumps(run, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps(run, indent=2, ensure_ascii=False))


def read_list(items):
    paths = []
    for it in items or []:
        if it.startswith("@"):
            paths += [l.strip() for l in Path(it[1:]).read_text(encoding="utf-8").splitlines() if l.strip()]
        else:
            paths.append(it)
    return paths


def cmd_finalize(a):
    out = Path(a.out)
    rp = out / ".run.json"
    if not rp.is_file():
        die("No .run.json found. Run 'start' first.")
    run = json.loads(rp.read_text(encoding="utf-8"))
    project = a.project.strip()
    if not project:
        die("--project is required (infer it from the reference documents).")
    body_path = Path(a.body)
    body = body_path.read_text(encoding="utf-8").lstrip("﻿")
    if body.lstrip().startswith("---"):
        die("Body must not contain frontmatter; the script adds it.")

    sources = []
    for p in read_list(a.source_file):
        pp = Path(p)
        if pp.is_file():
            sources.append({"path": str(pp), "sha256": sha256(pp)})
    unreadable = read_list(a.unreadable)

    logo_rec = None
    if run["cover_logo"] != NA:
        lp = out / "assets" / run["cover_logo"]
        if lp.is_file():
            logo_rec = {"file": run["cover_logo"], "sha256": sha256(lp)}

    tags = [t.strip() for t in a.tags.split(",") if t.strip()]
    props = [
        ("title", f"{project} Test Plan"),
        ("document_type", "Test Plan"),
        ("project_id", ""),
        ("document_id", ""),
        ("version", ""),
        ("approved_date", ""),
        ("privacy", "Confidential"),
    ]
    head = "".join(f"{k}: {yq(v)}\n" if v else f"{k}:\n" for k, v in props)
    head += "tags:\n" + "".join(f"  - {t}\n" for t in tags)
    text = "---\n" + head + "---\n\n" + body.lstrip("\n")
    md_path = out / f"{run['stem']}.md"
    md_path.write_text(text, encoding="utf-8", newline="\n")

    src_json = dict(run)
    src_json.update({"project": project, "sources": sources, "unreadable": unreadable, "cover_logo_record": logo_rec})
    (out / f"{run['stem']}.sources.json").write_text(json.dumps(src_json, indent=2, ensure_ascii=False), encoding="utf-8")

    rp.unlink()
    try:
        body_path.unlink()
    except OSError:
        pass
    print(json.dumps({"ok": True, "md": str(md_path), "stem": run["stem"], "sources_count": len(sources)}, indent=2))


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("start")
    s.add_argument("--out", required=True)
    s.add_argument("--input-mode", required=True, choices=["dir", "file"])
    s.add_argument("--input-path", required=True)
    s.add_argument("--output-format", required=True, choices=["md", "docx"])
    s.add_argument("--plugin-root", required=True)
    s.add_argument("--cover-logo", default="")
    f = sub.add_parser("finalize")
    f.add_argument("--out", required=True)
    f.add_argument("--body", required=True)
    f.add_argument("--project", required=True)
    f.add_argument("--tags", default="test-plan,qa")
    f.add_argument("--unreadable", nargs="*")
    f.add_argument("--source-file", nargs="*")
    a = ap.parse_args()
    (cmd_start if a.cmd == "start" else cmd_finalize)(a)


if __name__ == "__main__":
    main()
