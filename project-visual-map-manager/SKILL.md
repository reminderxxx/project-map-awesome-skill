---
name: project-visual-map-manager
description: Generate and update reusable visual project maps for software repositories. Use when Codex needs to document, inspect, or refresh PROJECT_STRUCTURE.md, PROJECT_MAP.html, and .project-map-cache.json so developers and AI agents can understand project structure, file purposes, modules, dependencies, routes, APIs, configuration, and safe modification locations across frontend, backend, full-stack, Java, Python, Node.js, Vue, React, C/C++, and coursework projects.
---

# Project Visual Map Manager

Use this skill when a project needs an AI-readable structure summary and a developer-friendly visual map.

## Project Integration

Prefer project-local integration when adding this skill to another repository:

1. Clone `https://github.com/reminderxxx/project-map-awesome-skill.git` into a temporary directory.
2. Copy only `project-visual-map-manager/` into the target project root.
3. Do not copy the source repository `.git` directory or outer generated files.
4. Generate the map from the target project root:

```powershell
powershell -ExecutionPolicy Bypass -File project-visual-map-manager/run-project-map.ps1 -Root . -NoOpen
```

If PowerShell is unavailable, run:

```bash
python project-visual-map-manager/scripts/update_project_map.py --root .
```

When working from this repository, see `AI-INTEGRATION.md` for a copy-paste prompt that another AI agent can use to pull the skill from GitHub and integrate it into a target project.

## Required Workflow

1. Before modifying a mapped project, read `PROJECT_STRUCTURE.md` first if it exists.
2. Use `PROJECT_MAP.html` data when file relationships, module ownership, or dependency direction matter.
3. After adding, deleting, moving, renaming, or materially changing files, rerun the map generator.
4. Prefer the bundled scripts over hand-written summaries:

```bash
python project-visual-map-manager/scripts/update_project_map.py --root .
```

For Windows project-local usage, prefer:

```powershell
.\project-visual-map-manager\run-project-map.ps1 -Root . -NoOpen
```

If the skill is installed outside the target repository, run the script from its installed path and pass the target repository with `--root`.

## Outputs

The script creates or updates these files in the target project root:

- `PROJECT_STRUCTURE.md`: concise project overview for developers and AI agents.
- `PROJECT_MAP.html`: self-contained visual map with directory tree, search, type filters, details, hover summaries, and dependency SVG.
- `.project-map-cache.json`: file hashes, summaries, declarations, dependency data, reverse references, and last analysis time.

## Updating PROJECT_STRUCTURE.md

Run:

```bash
python project-visual-map-manager/scripts/update_project_map.py --root . --output-md PROJECT_STRUCTURE.md
```

The Markdown output includes project overview, update time, directory structure, core modules, important files, developer navigation guidance, and AI modification-location rules.

## Updating PROJECT_MAP.html

Run:

```bash
python project-visual-map-manager/scripts/update_project_map.py --root . --output-html PROJECT_MAP.html
```

The HTML is a single file with embedded CSS, JavaScript, and project data. It can be opened directly from disk without installing frontend dependencies.

## Parameters

- `--root`: target project root. Defaults to current directory.
- `--lang zh/en/auto`: output language. Defaults to `auto`.
- `--output-html`: HTML output path. Defaults to `<root>/PROJECT_MAP.html`.
- `--output-md`: Markdown output path. Defaults to `<root>/PROJECT_STRUCTURE.md`.
- `--max-depth`: maximum directory traversal depth.
- `--include-hidden`: include hidden files and directories except default ignored paths.
- `--open`: open the generated HTML map with the system default browser.
- `--watch`: reserved flag for future watch mode; currently performs one update and exits.

## Language Selection

Use `--lang auto` unless the user requests a specific language.

Auto mode checks README files and representative source comments:

- If Chinese text dominates, output Chinese.
- If English text dominates, output English.
- If unclear, default to Chinese.

## Modification Rule For AI Agents

If you make any file-system change that affects project structure or dependency relationships, rerun this skill before finishing:

```bash
python project-visual-map-manager/scripts/update_project_map.py --root .
```

Use the regenerated `PROJECT_STRUCTURE.md` and `PROJECT_MAP.html` to explain where changes landed and how future agents should locate related files.
