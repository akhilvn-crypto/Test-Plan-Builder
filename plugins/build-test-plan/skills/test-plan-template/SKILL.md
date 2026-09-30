---
name: test-plan-template
description: Section contract, table columns and writing-style rules for Emvigo's Test Plan. Load before writing any test plan body.
---

# Emvigo Test Plan: section contract and writing rules

This skill is the source of truth for the plan's structure. Headings must match exactly; they are what makes the document look like Emvigo's own.

## Body format (markdown)

- Do NOT write frontmatter. `run_metadata.py finalize` adds the md property keys (title, document_type, project_id, document_id, version, approved_date, privacy, tags). Properties belong to the md only; the docx never shows them.
- First line: `# Test Plan - <project>` (the docx cover replaces it). The project name is inferred from the reference documents.
- Level 1 sections use `##`, sub-sections `###`, and the Software/Hardware and In Scope/Out of Scope sub-headings `####`. Numbers are written in the heading text.
- Tables are pipe tables with a header row. Use `N/A` for a cell that does not apply. A cell the sources do not answer and that QA fills by hand (names, IDs, dates of review or approval) is left empty. `TBD` is allowed only for open dates in 5. Test Schedule; never anywhere else, and never in 7. Test Closure.

## Sections, in order

This mirrors Emvigo's master template (`assets/master-template.docx`). Do not add, drop, rename or reorder sections, and do not add fields, rows or columns the template does not have (no author, prepared-by, status, revision or similar). Nobody running the command is named anywhere in the document.

```
## A. Document Version Control
## B. Document Release History
## 1. Introduction
### 1.1 Purpose
### 1.2 Project Overview
### 1.3 Scope of Testing
### 1.4 Reference Documents
## 2. Resource Requirement for Tests
### 2.1 Manpower Requirement
### 2.2 Responsibilities by Activity
### 2.3 Orientation/Training Plan
### 2.4 Inputs/Documents Needed from Project Team
### 2.5 Test Environment Needed
#### Software
#### Hardware
## 3. Assumptions, Dependencies & Risks
### 3.1 Assumptions
### 3.2 Dependencies
### 3.3 Risks
## 4. Test Strategy/Methods
### 4.1 Overall Test Strategy
### 4.2 Strategy for Integration of Product Modules
### 4.3 Sequence & Criteria for Integration Testing
## 5. Test Schedule
## 6. Test Deliverables
### 6.1 Test Plan
### 6.2 Test Cases & Test Logs
### 6.3 Acceptance/Exit Criteria
### 6.4 Bug Analysis
### 6.5 Release Notes
### 6.6 Non Functional Testing
## 7. Test Closure
```

(The cover and Table of Contents are added by the renderer. Do not write them. The renderer numbers the headings itself; the numbers in the md must match the list above.)

## Required content per section

| Section | Form |
|---|---|
| A. Document Version Control | Table `Field, Value`, rows in this order: Title (`<Project> Test Plan`), Project ID, Document ID, Description (keep the template's sentence: "A test plan is a document detailing the objectives, resources, and processes for a specific test session for a software"), Approved date, Master Template ID (`ET/FQA01/A/05092023`), Privacy Classification (`Confidential. Shared with <client>` when the sources name the client; otherwise just `Confidential`). Project ID, Document ID and Approved date are left empty for the user. Nothing here is taken from the person running the command. |
| B. Document Release History | Table `Version, Date, Author, Reviewed By, Reviewed On, Approved By, Approved On, Reasons`. One row: `V1.0`, the run date as `DD-Mon-YYYY`, Author to Approved On left empty for the team to fill, Reasons `Initial draft`. |
| 1.1 Purpose | Short prose. Keep the template's meaning (a test plan documents the strategy used to verify the product meets its specification), in the project's terms. |
| 1.2 Project Overview | Short prose from the sources. |
| 1.3 Scope of Testing | Two `####` sub-headings, `#### In Scope` then `#### Out of Scope`, each holding `-` bullets, one scope item per bullet (no comma-separated paragraphs). Group long lists under a bold label line (`**Functional**`, `**Non-functional**`, `**Integrations**`, `**Environments**`) placed above that group's bullets; use only the groups the sources support, and skip the labels when a list has fewer than about 5 items. Cite the ID where one applies (e.g. `Login and password reset (REQ-01)`). An Out of Scope bullet may end with a short reason after a dash-free clause, e.g. `Load testing, as the client covers it in UAT`. |
| 1.4 Reference Documents | Table `Process Element, Reference` with rows `Kick off Document` and `Project Plan`. The Reference cell is `[Provide document link]` unless a source gives the link. QA fills these in; never change the wording of the placeholder or the row names. |
| 2.1 Manpower Requirement | Table `Resource Name, Designation/Role`. Names only when the sources name them; otherwise the name cell is empty and the role is filled. |
| 2.2 Responsibilities by Activity | Table `Element, Resource Name, Designation/Role`. Rows: Test Planning, Test Case Creation, Test Case Review, Defect logging, Retesting, Release Note (add rows only if the sources name more activities). Release note preparation is always done by QA: its Designation/Role is `QA`. Resource names come from the sources only, otherwise empty. |
| 2.3 Orientation/Training Plan | One lead-in line, then `-` bullets. |
| 2.4 Inputs/Documents Needed | Numbered list (`1.`). Template items: Requirement Document, User Stories or Tasks from Jira, Release Plan, Test Case, Release note, Defect Report, Bug Analysis Report, Bug Report. |
| 2.5 Test Environment Needed | `#### Software` and `#### Hardware`, each a table `S. No, Software` or `Hardware, Purpose`. |
| 3.1 to 3.3 | `-` bullets (the renderer numbers them i., ii., iii.). Put mitigation for a risk in the same bullet. |
| 4.1 to 4.2 | Short prose. |
| 4.3 | `-` bullets (numbered i., ii. by the renderer). |
| 5. Test Schedule | One line on the schedule basis, then table `Release, Sprint, Iteration, Start Date, End date`. `TBD` for dates the sources leave open (the only place `TBD` is allowed). |
| 6. Test Deliverables | One lead-in line. 6.1 prose. 6.2 to 6.6 each: short prose where the template has it, then a table `Document, Location`. |
| 6.2 | Rows `Test case`, `Test Reports`. Location `[Provide document link]`. |
| 6.3 | Prose on the criteria, then row `Project Plan`, `[Provide document link]`. |
| 6.4 | Rows `Bug Analysis Report`, `Bug Report` (`[Provide document link for all bugs exported from Jira]`). |
| 6.5 | Say release notes are prepared by QA and kept in a common folder. Row `Release Notes` (`[Provide folder link for release Notes]`). |
| 6.6 | Rows `Performance testing report`, `Security testing report` (`[Provide folder link for performance testing report]`, `[Provide folder link for security testing report]`). |
| 7. Test Closure | Lead-in sentence (the mail goes after the final UAT or production release, whichever the sources give; if they give neither, say "the final release"), then a numbered list (`1.`): test environment and credentials, test coverage percentage, pass percentage, known issues, deliverables attached, cc list. No `TBD`, no placeholders and no invented figures: these are the points the closing mail must cover, not values to fill in now. |

The `[Provide ...]` placeholders are what the QA team fills in after the run (kick off document, project plan, report locations). Keep them exactly as written unless a source supplies the real link. Structure stays the same every run.

## Rules for content

1. Every statement must be grounded in the source documents. Use the project's own terms, module names, environments and dates.
2. Give traceable IDs to extracted items (REQ-01, INT-01, NFR-01, RSK-01) and reference them where relevant, e.g. in scope and strategy. Assumptions, dependencies and risks are plain bullets, so cite an ID in the text when one applies.
3. Unknowns: if the sources do not say, write a labelled **Assumption** (add it to 3.1 as a bullet), leave a fill-in cell empty, or use `TBD` where the contract allows it. Never invent names, numbers, dates, tools or environments. If a value does not apply, write `N/A`.
4. Say what is unknown plainly: "Test data for the payment sandbox has not been shared yet."
5. Keep each section proportionate. A section with little to say gets a couple of sentences.
6. Write section 1.3 as two bulleted lists under `#### In Scope` and `#### Out of Scope`, one item per bullet, never as a comma-separated paragraph. Out of scope only from the sources or as a labelled assumption.

## Writing style: it must read like a person wrote it

The template's voice is short, practical and plain. Match it.

The template's own sentences (purpose, strategy, integration, bug analysis and so on) may be tightened: fix the grammar, drop the stiffness, use the project's terms. Keep the meaning and the length close to the original. Do not turn them into marketing copy, and do not pad.

**Do**
- Prefer concrete detail over general claims. "Regression on the checkout and refund flows before each release" beats "comprehensive regression coverage".
- Plain verbs, active voice, short paragraphs. Vary sentence length; a few short sentences are fine.
- Use bullets only where the template uses bullets (1.3 scope lists included). Do not turn prose sections into lists.
- Do not restate the heading in the first sentence of its section.

**Avoid**
- Filler and hype: comprehensive, robust, seamless, leverage, streamline, cutting-edge, holistic, "ensure" as a crutch, "in today's fast-paced", "it is important to note", delve. Full list in `banned-phrases.txt`.
- Formulaic structure: every paragraph opening the same way, everything in threes, every bullet the same length, closing sentences that summarise the paragraph just read.
- Em dashes in nearly every sentence, and "not just X, but Y" constructions.
- Invented specifics (see rule 3).

## Enforcement

`scripts/style_lint.py <plan.md> --banned skills/test-plan-template/banned-phrases.txt` reports banned phrases, repeated sentence openers, overlong sentences, em-dash density, "not just X but Y", uniform bullets and headings restated in the first sentence. After the lint, rewrite the flagged passages once, re-lint, and list whatever remains in the summary. Never hide findings.
