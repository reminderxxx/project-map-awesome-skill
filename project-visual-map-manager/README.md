# project-visual-map-manager

`project-visual-map-manager` is a reusable Codex Skill for generating visual project maps for software repositories. It creates a Markdown structure guide for humans and AI agents, plus a self-contained HTML map for browsing files, modules, dependencies, routes, exports, and modification hints.

## Installation

Copy the `project-visual-map-manager` directory into a Codex skills directory, for example:

```bash
~/.codex/skills/project-visual-map-manager
```

You can also keep it inside a repository and run the bundled script directly.

## Usage

From a target project root:

```bash
python path/to/project-visual-map-manager/scripts/update_project_map.py --root .
```

This creates or updates:

- `PROJECT_STRUCTURE.md`
- `PROJECT_MAP.html`
- `.project-map-cache.json`

## Command Parameters

```bash
python scripts/update_project_map.py \
  --root . \
  --lang auto \
  --output-html PROJECT_MAP.html \
  --output-md PROJECT_STRUCTURE.md \
  --max-depth 8
```

- `--root`: target project root. Defaults to current directory.
- `--lang zh/en/auto`: output language. Defaults to `auto`.
- `--output-html`: output path for the visual HTML map.
- `--output-md`: output path for the Markdown structure guide.
- `--max-depth`: maximum scan depth.
- `--include-hidden`: include hidden files and directories except default ignored paths.
- `--watch`: reserved for future watch mode. It currently runs one update.

## Output Files

`PROJECT_STRUCTURE.md` contains the project overview, update time, directory structure, core modules, important files, developer navigation advice, and AI modification-location rules.

`PROJECT_MAP.html` is a single-file HTML application. It includes an interactive directory tree, search, file-type filters, hover tooltips, a detail panel, and a dependency graph rendered with inline SVG.

`.project-map-cache.json` stores file hashes, summaries, types, declarations, imports, reverse references, and last analysis time so subsequent runs can reuse stable metadata.

## Reuse

The script uses only the Python standard library and is framework-neutral. It supports frontend, backend, full-stack, Java, Python, Node.js, Vue, React, C/C++, and coursework projects.

## Example Screenshot Description

The generated HTML page shows a compact developer dashboard: project metrics at the top, a searchable directory tree on the left, a details panel on the right, and a dependency graph below. Hovering over a file displays its purpose, declarations, type, and module.
