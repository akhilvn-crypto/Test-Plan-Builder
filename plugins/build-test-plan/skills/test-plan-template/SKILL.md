---
name: test-plan-template
description: Section contract, table columns and writing-style rules for Emvigo's Test Plan. Load before writing any test plan body.
---

# Emvigo Test Plan: section contract and writing rules

This skill is the source of truth for the plan's structure. Headings must match exactly; they are what makes the document look like Emvigo's own.

## Body format (markdown)

- Do NOT write frontmatter. `run_metadata.py finalize` adds it.
- First line: `# Test Plan - <project>` (the docx cover replaces it).
- Level 1 sections use `##`, sub-sections `###`. Numbers are written in the heading text.
- Tables are pipe tables with a header row. Use `N/A` for a known-empty cell, `TBD` only when the sources leave it open.

## Sections, in order

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
### 2.5 Test Environment Needed (Software, Hardware)
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
### 6.6 Non-Functional Testing
## 7. Test Closure
```

(The cover and Table of Contents are added by the renderer. Do not write them.)

## Required tables

| Section | Columns |
|---|---|
| A. Document Version Control | Field, Value. Rows: Document Title, Project Name, Project ID, Document ID, Version, Status, Prepared By, Date. Values come from the run info (`.run.json` output of `start`). |
| B. Document Release History | Version, Date, Author, Reviewed By, Approved By, Reasons for Change. First row: this run's version, date, run_by, reviewed_by, approved_by, "Initial draft" (or a real reason). |
| 2.1 Manpower Requirement | Role, Name, Responsibility, Allocation. Only people or roles named in the sources; the person running the tool appears with their role if given. |
| 2.2 Responsibilities by Activity | Activity, Responsible, Support/Review |
| 2.3 Orientation/Training Plan | Topic, Audience, Timing |
| 2.5 Test Environment Needed | Type (Software/Hardware), Item, Details |
| 3.1 to 3.3 | Assumptions: ID (A-01...), Assumption. Dependencies: ID (D-01...), Dependency, Owner. Risks: ID (R-01...), Risk, Impact, Mitigation |
| 5. Test Schedule | Activity, Start, End, Owner |
| 6.3 Acceptance/Exit Criteria | Criterion, Threshold |

Other sections are short prose or template-style bullets. Keep a section's structure the same every run.

## Rules for content

1. Every statement must be grounded in the source documents. Use the project's own terms, module names, environments and dates.
2. Give traceable IDs to extracted items (REQ-01, INT-01, NFR-01, RSK-01) and reference them where relevant, e.g. in scope and strategy.
3. Unknowns: if the sources do not say, write a labelled **Assumption** (add it to 3.1) or `TBD`. Never invent names, numbers, dates, tools or environments. If a value does not apply, write `N/A`.
4. Say what is unknown plainly: "Test data for the payment sandbox has not been shared yet."
5. Keep each section proportionate. A section with little to say gets a couple of sentences.
6. Write section 1.3 as: in scope, out of scope. Out of scope only from the sources or as a labelled assumption.

## Writing style: it must read like a person wrote it

The template's voice is short, practical and plain. Match it.

**Do**
- Prefer concrete detail over general claims. "Regression on the checkout and refund flows before each release" beats "comprehensive regression coverage".
- Plain verbs, active voice, short paragraphs. Vary sentence length; a few short sentences are fine.
- Use bullets only where the template uses bullets. Do not turn prose sections into lists.
- Do not restate the heading in the first sentence of its section.

**Avoid**
- Filler and hype: comprehensive, robust, seamless, leverage, streamline, cutting-edge, holistic, "ensure" as a crutch, "in today's fast-paced", "it is important to note", delve. Full list in `banned-phrases.txt`.
- Formulaic structure: every paragraph opening the same way, everything in threes, every bullet the same length, closing sentences that summarise the paragraph just read.
- Em dashes in nearly every sentence, and "not just X, but Y" constructions.
- Invented specifics (see rule 3).

## Enforcement

`scripts/style_lint.py <plan.md> --banned skills/test-plan-template/banned-phrases.txt` reports banned phrases, repeated sentence openers, overlong sentences, em-dash density, "not just X but Y", uniform bullets and headings restated in the first sentence. After the lint, rewrite the flagged passages once, re-lint, and list whatever remains in the summary. Never hide findings.
