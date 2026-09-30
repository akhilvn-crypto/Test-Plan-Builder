"""Render the test-plan markdown to .docx using style-spec.json.

Usage: render_docx.py <plan.md> <plan.docx> [--spec style-spec.json] [--header-logo header-logo.png] [--assets <out>/assets]

The md is the source of truth. Prints a JSON result with any warnings. Exit 1 on failure.
"""
import argparse
import copy
import json
import re
import sys
from pathlib import Path

try:
    from docx import Document
    from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_BREAK
    from docx.oxml import OxmlElement
    from docx.oxml.ns import qn
    from docx.shared import Cm, Pt, RGBColor, Twips
except ImportError:
    print(json.dumps({"ok": False, "error": "Please run `pip install python-docx`."}))
    sys.exit(1)

DEFAULT_SPEC = {
    "page": {"width_twips": 11906, "height_twips": 16838, "margin_left_twips": 1440, "margin_right_twips": 1440, "margin_top_twips": 1440, "margin_bottom_twips": 1300},
    "fonts": {"body": "Calibri", "heading": "Calibri"},
    "sizes_pt": {"body": 11, "h1": 16, "h2": 13, "h3": 11.5, "cover_title": 32, "cover_project": 20, "cover_meta": 12, "table": 10, "header_footer": 9},
    "colors": {"heading": "1F3864", "body": "000000", "rule": "7F7F7F", "table_header_fill": "D9D9D9", "table_border": "808080", "placeholder": "C00000"},
    "section_indent_twips": {"1": 0, "2": 0, "3": 0},
    "tables": {"cell_margin_twips": 80, "min_col_weight": 8, "max_col_weight": 60, "narrow_headers": ["date", "version", "rev", "id", "no"], "narrow_max_weight": 12},
    "cover": {"logo_max_width_cm": 8.0, "logo_max_height_cm": 4.0, "company": "Emvigo Technologies", "placeholder_text": "[Cover logo not supplied]"},
    "header": {"logo_width_cm": 3.5, "rule_size_eighths_pt": 6},
    "toc": {"levels": "1-2", "title": "Table of Contents"},
    "footer": {"version_prefix": "Version "},
}


def merge(base, over):
    for k, v in over.items():
        if isinstance(v, dict) and isinstance(base.get(k), dict):
            merge(base[k], v)
        else:
            base[k] = v
    return base


def rgb(hexstr):
    return RGBColor.from_string(hexstr.upper())


def parse_frontmatter(text):
    fm = {}
    if text.startswith("---"):
        end = text.find("\n---", 3)
        if end != -1:
            for line in text[3:end].strip().splitlines():
                if ":" in line:
                    k, v = line.split(":", 1)
                    v = v.strip()
                    if v.startswith('"'):
                        try:
                            v = json.loads(v)
                        except ValueError:
                            pass
                    fm[k.strip()] = v
            text = text[end + 4:]
    return fm, text.lstrip("\n")


# ---------- low-level XML helpers ----------

def set_run_font(run, name, size=None, bold=None, italic=None, color=None):
    run.font.name = name
    rpr = run._element.get_or_add_rPr()
    rf = rpr.find(qn("w:rFonts"))
    if rf is None:
        rf = OxmlElement("w:rFonts")
        rpr.insert(0, rf)
    for att in ("w:ascii", "w:hAnsi", "w:cs", "w:eastAsia"):
        rf.set(qn(att), name)
    if size:
        run.font.size = Pt(size)
    if bold is not None:
        run.bold = bold
    if italic is not None:
        run.italic = italic
    if color:
        run.font.color.rgb = rgb(color)


def style_font(style, name, size, bold=None, color=None):
    style.font.name = name
    rpr = style.element.get_or_add_rPr()
    rf = rpr.find(qn("w:rFonts"))
    if rf is None:
        rf = OxmlElement("w:rFonts")
        rpr.insert(0, rf)
    for att in ("w:ascii", "w:hAnsi", "w:cs", "w:eastAsia"):
        rf.set(qn(att), name)
    for att in ("w:asciiTheme", "w:hAnsiTheme", "w:cstheme", "w:eastAsiaTheme"):
        if rf.get(qn(att)) is not None:
            del rf.attrib[qn(att)]
    style.font.size = Pt(size)
    if bold is not None:
        style.font.bold = bold
    if color:
        style.font.color.rgb = rgb(color)


def add_field(paragraph, instr, placeholder="", font=None, size=None, dirty=False):
    def r():
        run = paragraph.add_run()
        if font:
            set_run_font(run, font, size)
        return run

    a = r()
    b = OxmlElement("w:fldChar")
    b.set(qn("w:fldCharType"), "begin")
    if dirty:
        b.set(qn("w:dirty"), "true")
    a._element.append(b)
    i = r()
    t = OxmlElement("w:instrText")
    t.set(qn("xml:space"), "preserve")
    t.text = f" {instr} "
    i._element.append(t)
    s = r()
    sp = OxmlElement("w:fldChar")
    sp.set(qn("w:fldCharType"), "separate")
    s._element.append(sp)
    p = r()
    p.text = placeholder
    e = r()
    en = OxmlElement("w:fldChar")
    en.set(qn("w:fldCharType"), "end")
    e._element.append(en)


def para_border_bottom(paragraph, color, size):
    ppr = paragraph._p.get_or_add_pPr()
    bdr = OxmlElement("w:pBdr")
    b = OxmlElement("w:bottom")
    b.set(qn("w:val"), "single")
    b.set(qn("w:sz"), str(size))
    b.set(qn("w:space"), "4")
    b.set(qn("w:color"), color)
    bdr.append(b)
    ppr.append(bdr)


def shade(cell, fill):
    tcpr = cell._tc.get_or_add_tcPr()
    sh = OxmlElement("w:shd")
    sh.set(qn("w:val"), "clear")
    sh.set(qn("w:color"), "auto")
    sh.set(qn("w:fill"), fill)
    tcpr.append(sh)


# ---------- inline markdown ----------

INLINE = re.compile(r"\*\*(.+?)\*\*|(?<!\*)\*(?!\s)(.+?)(?<!\s)\*(?!\*)|`(.+?)`")


def add_inline(paragraph, text, font, size, color=None, bold=False):
    parts = re.split(r"<br\s*/?>", text)
    for pi, part in enumerate(parts):
        if pi:
            paragraph.add_run().add_break(WD_BREAK.LINE)
        pos = 0
        for m in INLINE.finditer(part):
            if m.start() > pos:
                set_run_font(paragraph.add_run(part[pos:m.start()]), font, size, bold=bold or None, color=color)
            if m.group(1) is not None:
                set_run_font(paragraph.add_run(m.group(1)), font, size, bold=True, color=color)
            elif m.group(2) is not None:
                set_run_font(paragraph.add_run(m.group(2)), font, size, italic=True, bold=bold or None, color=color)
            else:
                set_run_font(paragraph.add_run(m.group(3)), "Consolas", size - 1, color=color)
            pos = m.end()
        if pos < len(part):
            set_run_font(paragraph.add_run(part[pos:]), font, size, bold=bold or None, color=color)


# ---------- tables ----------

def split_row(line):
    line = line.strip()
    if line.startswith("|"):
        line = line[1:]
    if line.endswith("|"):
        line = line[:-1]
    return [c.strip().replace("\\|", "|") for c in re.split(r"(?<!\\)\|", line)]


def col_widths(rows, total, spec):
    t = spec["tables"]
    ncol = len(rows[0])
    header = [h.lower().strip() for h in rows[0]]
    weights = []
    for c in range(ncol):
        longest = max(len(re.sub(r"[*`]", "", r[c])) for r in rows)
        w = max(t["min_col_weight"], min(t["max_col_weight"], longest))
        if header[c] in t["narrow_headers"]:
            w = min(w, t["narrow_max_weight"])
        weights.append(w)
    s = sum(weights)
    widths = [int(total * w / s) for w in weights]
    widths[-1] += total - sum(widths)
    return widths


def build_table(doc, rows, spec, indent, text_width):
    ncol = max(len(r) for r in rows)
    rows = [r + [""] * (ncol - len(r)) for r in rows]
    total = text_width - indent
    widths = col_widths(rows, total, spec)
    tbl = doc.add_table(rows=len(rows), cols=ncol)
    tblPr = tbl._tbl.tblPr
    for tag in ("w:tblW", "w:tblInd", "w:tblLayout", "w:tblBorders", "w:tblCellMar"):
        for e in tblPr.findall(qn(tag)):
            tblPr.remove(e)
    w = OxmlElement("w:tblW")
    w.set(qn("w:w"), str(total))
    w.set(qn("w:type"), "dxa")
    tblPr.append(w)
    ind = OxmlElement("w:tblInd")
    ind.set(qn("w:w"), str(indent))
    ind.set(qn("w:type"), "dxa")
    tblPr.append(ind)
    borders = OxmlElement("w:tblBorders")
    for side in ("top", "left", "bottom", "right", "insideH", "insideV"):
        b = OxmlElement(f"w:{side}")
        b.set(qn("w:val"), "single")
        b.set(qn("w:sz"), "4")
        b.set(qn("w:space"), "0")
        b.set(qn("w:color"), spec["colors"]["table_border"])
        borders.append(b)
    tblPr.append(borders)
    lay = OxmlElement("w:tblLayout")
    lay.set(qn("w:type"), "fixed")
    tblPr.append(lay)
    mar = OxmlElement("w:tblCellMar")
    for side in ("top", "left", "bottom", "right"):
        m = OxmlElement(f"w:{side}")
        m.set(qn("w:w"), str(spec["tables"]["cell_margin_twips"]))
        m.set(qn("w:type"), "dxa")
        mar.append(m)
    tblPr.append(mar)

    grid = tbl._tbl.tblGrid  # exactly one grid, widths sum to table width
    for gc in list(grid):
        grid.remove(gc)
    for wd in widths:
        gc = OxmlElement("w:gridCol")
        gc.set(qn("w:w"), str(wd))
        grid.append(gc)

    font, size = spec["fonts"]["body"], spec["sizes_pt"]["table"]
    for ri, row in enumerate(rows):
        tr = tbl.rows[ri]
        trpr = tr._tr.get_or_add_trPr()
        cs = OxmlElement("w:cantSplit")
        trpr.append(cs)
        if ri == 0:
            trpr.append(OxmlElement("w:tblHeader"))
        for ci, txt in enumerate(row):
            cell = tr.cells[ci]
            cell.width = Twips(widths[ci])
            p = cell.paragraphs[0]
            p.paragraph_format.space_after = Pt(0)
            p.paragraph_format.space_before = Pt(0)
            add_inline(p, txt, font, size, bold=(ri == 0))
            if ri == 0:
                shade(cell, spec["colors"]["table_header_fill"])
    spacer = doc.add_paragraph()
    spacer.paragraph_format.space_after = Pt(4)
    return tbl


# ---------- document ----------

def setup_styles(doc, spec):
    f, h, s = spec["fonts"], spec["fonts"]["heading"], spec["sizes_pt"]
    c = spec["colors"]
    style_font(doc.styles["Normal"], f["body"], s["body"], color=c["body"])
    doc.styles["Normal"].paragraph_format.space_after = Pt(6)
    for name, key in (("Heading 1", "h1"), ("Heading 2", "h2"), ("Heading 3", "h3")):
        st = doc.styles[name]
        style_font(st, h, s[key], bold=True, color=c["heading"])
        st.paragraph_format.space_before = Pt(14 if key == "h1" else 10)
        st.paragraph_format.space_after = Pt(6)
        st.paragraph_format.keep_with_next = True
        st.paragraph_format.left_indent = Twips(0)
    for name in ("List Bullet", "List Bullet 2", "List Number"):
        style_font(doc.styles[name], f["body"], s["body"], color=c["body"])
        doc.styles[name].paragraph_format.space_after = Pt(3)


def enable_update_fields(doc):
    settings = doc.settings.element
    u = OxmlElement("w:updateFields")
    u.set(qn("w:val"), "true")
    settings.append(u)


def scaled_picture(run, path, max_w_cm, max_h_cm):
    pic = run.add_picture(str(path), width=Cm(max_w_cm))
    if pic.height > Cm(max_h_cm):
        ratio = Cm(max_h_cm) / pic.height
        pic.width = int(pic.width * ratio)
        pic.height = Cm(max_h_cm)


def build_cover(doc, fm, spec, assets_dir, warnings):
    cv, sz, c = spec["cover"], spec["sizes_pt"], spec["colors"]
    font = spec["fonts"]["heading"]
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(60)
    logo = fm.get("cover_logo", "N/A")
    logo_path = Path(assets_dir) / logo if assets_dir and logo not in ("N/A", "") else None
    if logo_path and logo_path.is_file():
        try:
            scaled_picture(p.add_run(), logo_path, cv["logo_max_width_cm"], cv["logo_max_height_cm"])
        except Exception as e:  # unreadable image
            warnings.append(f"Cover logo could not be placed ({e}); placeholder used.")
            set_run_font(p.add_run(cv["placeholder_text"]), font, sz["cover_meta"], color=c["placeholder"])
    else:
        if logo not in ("N/A", ""):
            warnings.append(f"Cover logo file not found: {logo}")
        set_run_font(p.add_run(cv["placeholder_text"]), font, sz["cover_meta"], color=c["placeholder"])

    def line(text, size, bold=False, before=0, color=None):
        q = doc.add_paragraph()
        q.alignment = WD_ALIGN_PARAGRAPH.CENTER
        q.paragraph_format.space_before = Pt(before)
        q.paragraph_format.space_after = Pt(6)
        set_run_font(q.add_run(text), font, size, bold=bold, color=color)

    line("Test Plan", sz["cover_title"], True, 60, c["heading"])
    line(fm.get("project", ""), sz["cover_project"], True, 12)
    if fm.get("project_id", "N/A") != "N/A":
        line(f"Project ID: {fm['project_id']}", sz["cover_meta"], before=12)
    line(cv["company"], sz["cover_meta"], True, 36)
    date = fm.get("run_at", "")[:10]
    try:
        from datetime import datetime
        date = datetime.fromisoformat(fm["run_at"]).strftime("%d %B %Y")
    except (KeyError, ValueError):
        pass
    line(date, sz["cover_meta"])
    doc.add_paragraph().add_run().add_break(WD_BREAK.PAGE)


def build_toc(doc, spec):
    t = spec["toc"]
    p = doc.add_paragraph()
    set_run_font(p.add_run(t["title"]), spec["fonts"]["heading"], spec["sizes_pt"]["h1"], bold=True, color=spec["colors"]["heading"])
    tp = doc.add_paragraph()
    add_field(tp, f'TOC \\o "{t["levels"]}" \\h \\z \\u', "Right-click and choose Update Field to build the table of contents.", dirty=True)
    doc.add_paragraph().add_run().add_break(WD_BREAK.PAGE)


def build_header_footer(doc, fm, spec, header_logo, warnings):
    sec = doc.sections[0]
    pg = spec["page"]
    text_width = pg["width_twips"] - pg["margin_left_twips"] - pg["margin_right_twips"]
    hp = sec.header.paragraphs[0]
    hp.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    hp.paragraph_format.space_after = Pt(0)
    if header_logo and Path(header_logo).is_file():
        try:
            hp.add_run().add_picture(str(header_logo), width=Cm(spec["header"]["logo_width_cm"]))
        except Exception as e:
            warnings.append(f"Header logo could not be placed: {e}")
    else:
        warnings.append("Header logo missing; header left without a logo.")
    para_border_bottom(hp, spec["colors"]["rule"], spec["header"]["rule_size_eighths_pt"])

    fp = sec.footer.paragraphs[0]
    fp.paragraph_format.tab_stops.add_tab_stop(Twips(text_width), alignment=2)  # right
    hf = spec["sizes_pt"]["header_footer"]
    font = spec["fonts"]["body"]
    ver = fm.get("version", "N/A")
    set_run_font(fp.add_run(f"{spec['footer']['version_prefix']}{ver}"), font, hf)
    set_run_font(fp.add_run("\tPage "), font, hf)
    add_field(fp, "PAGE", "1", font, hf)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("md")
    ap.add_argument("docx")
    ap.add_argument("--spec")
    ap.add_argument("--header-logo")
    ap.add_argument("--assets")
    a = ap.parse_args()
    warnings = []

    spec = copy.deepcopy(DEFAULT_SPEC)
    if a.spec and Path(a.spec).is_file():
        try:
            merge(spec, json.loads(Path(a.spec).read_text(encoding="utf-8")))
        except ValueError:
            warnings.append("style-spec.json is not valid JSON; defaults used.")
    else:
        warnings.append("style-spec.json not found; defaults used.")

    try:
        text = Path(a.md).read_text(encoding="utf-8")
    except OSError as e:
        print(json.dumps({"ok": False, "error": f"Cannot read markdown: {e}"}))
        sys.exit(1)
    fm, body = parse_frontmatter(text)

    pg = spec["page"]
    text_width = pg["width_twips"] - pg["margin_left_twips"] - pg["margin_right_twips"]

    doc = Document()
    sec = doc.sections[0]
    sec.page_width, sec.page_height = Twips(pg["width_twips"]), Twips(pg["height_twips"])
    sec.left_margin, sec.right_margin = Twips(pg["margin_left_twips"]), Twips(pg["margin_right_twips"])
    sec.top_margin, sec.bottom_margin = Twips(pg["margin_top_twips"]), Twips(pg["margin_bottom_twips"])
    setup_styles(doc, spec)
    enable_update_fields(doc)
    cp = doc.core_properties
    cp.author = fm.get("run_by", "")
    cp.title = fm.get("title", "Test Plan")
    cp.subject = fm.get("project", "")
    cp.comments = ""
    cp.last_modified_by = fm.get("run_by", "")

    build_header_footer(doc, fm, spec, a.header_logo, warnings)
    build_cover(doc, fm, spec, a.assets, warnings)
    build_toc(doc, spec)

    font, size = spec["fonts"]["body"], spec["sizes_pt"]["body"]
    lines = body.splitlines()
    i, para, cur_level = 0, [], 1
    skipped_title = False

    def flush():
        nonlocal para
        if para:
            p = doc.add_paragraph()
            add_inline(p, " ".join(para), font, size)
            para = []

    while i < len(lines):
        raw = lines[i]
        s = raw.strip()
        if not s:
            flush()
            i += 1
            continue
        m = re.match(r"^(#{1,4})\s+(.*)$", s)
        if m:
            flush()
            n, title = len(m.group(1)), m.group(2).strip()
            if n == 1:
                if not skipped_title:  # the cover carries the title
                    skipped_title = True
                    i += 1
                    continue
                n = 2
            level = min(n - 1, 3)
            cur_level = level
            h = doc.add_heading(level=level)
            h.paragraph_format.left_indent = Twips(spec["section_indent_twips"].get(str(level), 0))
            add_inline(h, title, spec["fonts"]["heading"], spec["sizes_pt"][f"h{level}"], color=spec["colors"]["heading"], bold=True)
            i += 1
            continue
        if s.startswith("|"):
            flush()
            block = []
            while i < len(lines) and lines[i].strip().startswith("|"):
                block.append(lines[i])
                i += 1
            rows = [split_row(l) for l in block if not re.match(r"^\s*\|?\s*:?-{2,}:?\s*(\|\s*:?-{2,}:?\s*)*\|?\s*$", l)]
            if rows:
                indent = spec["section_indent_twips"].get(str(cur_level), 0)
                build_table(doc, rows, spec, indent, text_width)
            continue
        bm = re.match(r"^(\s*)([-*+])\s+(.*)$", raw)
        nm = re.match(r"^(\s*)(\d+)[.)]\s+(.*)$", raw)
        if bm or nm:
            flush()
            mm = bm or nm
            depth = 1 if len(mm.group(1).replace("\t", "    ")) >= 2 else 0
            style = ("List Bullet 2" if depth else "List Bullet") if bm else "List Number"
            p = doc.add_paragraph(style=style)
            add_inline(p, mm.group(3), font, size)
            i += 1
            continue
        if re.match(r"^-{3,}$", s):
            flush()
            i += 1
            continue
        para.append(s)
        i += 1
    flush()

    try:
        doc.save(a.docx)
    except OSError as e:
        print(json.dumps({"ok": False, "error": f"Cannot write docx: {e}"}))
        sys.exit(1)
    print(json.dumps({"ok": True, "docx": a.docx, "warnings": warnings}, indent=2))


if __name__ == "__main__":
    main()
