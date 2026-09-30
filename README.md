# Emvigo Plugins

Marketplace repo for Emvigo QA plugins. Currently: **build-test-plan**.

## Install

```
/plugin marketplace add <owner>/<repo>      # or a git URL / local path
/plugin install build-test-plan@emvigo-plugins
```

## Use

```
/build-test-plan (--dir <folder> | --file <path>) --output-format <md|docx> [--out <folder>]
```

- `--dir` (read recursively) or `--file`: exactly one.
- `--output-format`: required. `docx` also delivers the `md`, and the docx is rendered from it.
- `--out`: defaults to `./test-plan-output/`.

The command creates `<out>/assets/` and asks you to drop the cover logo in it, then asks for your name, project details and so on. Previous outputs move to `<out>/history/`.

## Requirements

- Python 3.x (python.org)
- `pip install python-docx` (for `docx` output)

## Notes

- The bundled `header-logo.png` is a placeholder wordmark. Replace `plugins/build-test-plan/skills/test-plan-template/assets/header-logo.png` with the real Emvigo logo.
- Set the real contact email in `.claude-plugin/marketplace.json` (`owner.email`).
- Bump the version in `plugin.json` and `marketplace.json` together and record it in `CHANGELOG.md`.
