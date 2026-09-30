---
description: Build a client-ready Emvigo Test Plan from reference documents (md or docx)
argument-hint: (--dir <folder> | --file <path>) --output-format <md|docx> [--out <folder>]
allowed-tools: Read, Write, Bash, PowerShell, Glob, Grep, Agent, AskUserQuestion
---

Build a test plan. Arguments: `$ARGUMENTS`

Usage: `/build-test-plan (--dir <folder> | --file <path>) --output-format <md|docx> [--out <folder>]`

`PLUGIN_ROOT` is `${CLAUDE_PLUGIN_ROOT}`. Follow these steps in order. Stop at the first failure and show the message.

1. **Preflight.** Run
   `python "${CLAUDE_PLUGIN_ROOT}/scripts/preflight.py" $ARGUMENTS`
   If it fails, print its `error` and the usage line, and stop. Nothing has been created yet. (If `python` is not found, say: "Python is required. Please install Python 3.x from python.org and re-run.")
   If the session is non-interactive (nobody can answer prompts), stop with a clear error.

2. **Assets folder.** Run the same command with `--init-assets`. Then tell the user:
   > I've created `<out>/assets/`. Please place your cover logo (PNG or JPG) in it, then reply **done**.

   Wait for the reply. Do not archive or generate anything yet.

3. **Detect the cover logo.** Run the preflight with `--detect-logo`.
   - One valid image: use it.
   - Several: ask which one.
   - None: say so and ask again; offer **skip** (cover keeps a marked placeholder, note it in the summary).
   - Invalid images listed in `logos_invalid`: report them and ask again.

4. **Intake.** Ask the user for the following (AskUserQuestion or plain questions). Re-ask required fields until answered. Optional fields left blank become `N/A`; never guess.
   - Your name (required), email, role
   - Project name (required unless the documents make it unambiguous), Project ID, Document ID
   - Version (default 1.0), Reviewed By, Approved By, Status (default draft)

   Save the answers as JSON in the scratchpad: `run_by, email, role, project, project_id, document_id, version, reviewed_by, approved_by, status, cover_logo` (cover_logo = filename or empty when skipped).

5. **Archive the previous run.** `python "${CLAUDE_PLUGIN_ROOT}/scripts/archive_previous.py" --out <out>`. Do this only after the sources are confirmed to exist (preflight already checked the path). `assets/` is never moved.

6. **Delegate.** Launch the `test-plan-builder` agent with: PLUGIN_ROOT, INPUT_MODE, INPUT_PATH, OUT, OUTPUT_FORMAT, the intake JSON path, and any extra notes the user gave. Relay its summary to the user.
