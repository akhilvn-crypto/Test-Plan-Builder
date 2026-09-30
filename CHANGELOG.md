# Changelog

## 1.3.0
- Section 1.3 Scope of Testing is now two bulleted lists under `#### In Scope` and `#### Out of Scope` (one item per bullet, optional bold group labels) instead of comma-separated paragraphs.

## 1.2.0
- No intake questions. The project name is inferred from the reference documents; nobody running the command is named in the document.
- md properties follow the Emvigo Obsidian keys (title, document_type, project_id, document_id, version, approved_date, privacy, tags), left empty for the user to fill. The docx carries no properties.
- Document Version Control and Release History keep only the template's fields; author, reviewer and approver cells are left for the team.
- Release note preparation is always assigned to QA; Test Closure never carries `TBD`.
- Header logo is smaller and the rule under the header is gone. The Emvigo Technologies/date block is pinned to the cover page so it can no longer spill onto page 2.

## 1.1.0
- `render_docx.py` now builds the docx on Emvigo's master template (`assets/master-template.docx`): same cover, header/footer, heading numbering, table looks and section order.
- Section contract follows the template: Document Version Control and Release History tables in the template's columns, Kick off Document / Project Plan and report-location placeholders kept for QA, Assumptions/Dependencies/Risks as lists, Software/Hardware tables under Test Environment Needed.
- Layout fixes over the template: A and B no longer take heading numbers, aligned heading and list indents, tables fit the page width, no mid-word wraps in headers, small tables stay on one page, the cover stays on one page for long project names, and the contents page is built by Word when available.

## 1.0.0
- Initial release of `build-test-plan`: command, agent, template skill, and scripts (preflight, archive, run metadata, style lint, docx renderer).
