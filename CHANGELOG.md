# Changelog

## 1.1.0
- `render_docx.py` now builds the docx on Emvigo's master template (`assets/master-template.docx`): same cover, header/footer, heading numbering, table looks and section order.
- Section contract follows the template: Document Version Control and Release History tables in the template's columns, Kick off Document / Project Plan and report-location placeholders kept for QA, Assumptions/Dependencies/Risks as lists, Software/Hardware tables under Test Environment Needed.
- Layout fixes over the template: A and B no longer take heading numbers, aligned heading and list indents, tables fit the page width, no mid-word wraps in headers, small tables stay on one page, the cover stays on one page for long project names, and the contents page is built by Word when available.

## 1.0.0
- Initial release of `build-test-plan`: command, agent, template skill, and scripts (preflight, archive, run metadata, style lint, docx renderer).
