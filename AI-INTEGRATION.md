# AI Integration Guide

This repository contains the reusable `project-visual-map-manager` Codex Skill. Use this guide when you want an AI agent to pull the Skill from GitHub and integrate it into another project.

## Copy-Paste Prompt For AI

```text
Please integrate project-visual-map-manager into this project.

Source repository:
https://github.com/reminderxxx/project-map-awesome-skill.git

Required behavior:
1. Treat the current working directory as the target project root.
2. Clone the source repository into a temporary directory, not inside this project.
3. Copy only the project-visual-map-manager/ directory into the target project root.
4. Do not copy the source repository .git directory or unrelated generated files.
5. Generate the project map by running:
   powershell -ExecutionPolicy Bypass -File project-visual-map-manager/run-project-map.ps1 -Root . -NoOpen
   If PowerShell is unavailable, run:
   python project-visual-map-manager/scripts/update_project_map.py --root .
6. Read PROJECT_STRUCTURE.md before making project edits.
7. After adding, deleting, moving, renaming, or materially changing files, rerun the project map generator.
```

## Recommended AI Workflow

1. Confirm the target project root.
2. Create a temporary clone directory.
3. Run:

```bash
git clone --depth 1 https://github.com/reminderxxx/project-map-awesome-skill.git <temp-dir>
```

4. Copy only:

```text
<temp-dir>/project-visual-map-manager/
```

into:

```text
<target-project>/project-visual-map-manager/
```

5. Generate or refresh:

```powershell
powershell -ExecutionPolicy Bypass -File project-visual-map-manager/run-project-map.ps1 -Root . -NoOpen
```

6. Use `PROJECT_STRUCTURE.md` and `PROJECT_MAP.html` as the project navigation source.

## Why Use A Temporary Clone

Cloning into a temporary directory prevents the target project from accidentally receiving:

- this repository's `.git` metadata
- outer repository generated files
- unrelated local test artifacts

The target project should normally receive only `project-visual-map-manager/` plus the generated map files.
