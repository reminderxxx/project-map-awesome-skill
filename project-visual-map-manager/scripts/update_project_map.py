#!/usr/bin/env python3
"""Generate PROJECT_STRUCTURE.md, PROJECT_MAP.html, and .project-map-cache.json.

The scanner is intentionally framework-neutral and uses only the Python
standard library so it can run in most software projects without setup.
"""

from __future__ import annotations

import argparse
import datetime as dt
import fnmatch
import hashlib
import html
import json
import os
import re
import webbrowser
from pathlib import Path
from typing import Any


DEFAULT_IGNORES = {
    ".git",
    "node_modules",
    "dist",
    "build",
    "coverage",
    ".next",
    ".nuxt",
    ".vite",
    "target",
    "out",
    "bin",
    "obj",
    "__pycache__",
    ".venv",
    "env",
    ".idea",
    ".vscode",
    ".DS_Store",
    "package-lock.json",
    "pnpm-lock.yaml",
    "yarn.lock",
    "PROJECT_MAP.html",
    "PROJECT_STRUCTURE.md",
    ".project-map-cache.json",
}

DEFAULT_IGNORE_PATTERNS = {"*.log"}

TEXT_EXTENSIONS = {
    ".c",
    ".cc",
    ".cfg",
    ".conf",
    ".cpp",
    ".cs",
    ".css",
    ".csv",
    ".env",
    ".go",
    ".h",
    ".hpp",
    ".html",
    ".ini",
    ".java",
    ".js",
    ".json",
    ".jsx",
    ".kt",
    ".less",
    ".md",
    ".mjs",
    ".bat",
    ".php",
    ".ps1",
    ".properties",
    ".py",
    ".rb",
    ".rs",
    ".sass",
    ".scss",
    ".sh",
    ".sql",
    ".swift",
    ".toml",
    ".ts",
    ".tsx",
    ".txt",
    ".vue",
    ".xml",
    ".yaml",
    ".yml",
}

EXTENSION_TYPES = {
    ".py": "Python",
    ".js": "JavaScript",
    ".mjs": "JavaScript",
    ".jsx": "React JSX",
    ".ts": "TypeScript",
    ".tsx": "React TSX",
    ".vue": "Vue component",
    ".java": "Java",
    ".c": "C",
    ".h": "C/C++ header",
    ".cpp": "C++",
    ".cc": "C++",
    ".hpp": "C++ header",
    ".cs": "C#",
    ".go": "Go",
    ".rs": "Rust",
    ".php": "PHP",
    ".rb": "Ruby",
    ".swift": "Swift",
    ".kt": "Kotlin",
    ".html": "HTML",
    ".css": "CSS",
    ".scss": "SCSS",
    ".sass": "Sass",
    ".less": "Less",
    ".json": "JSON config",
    ".yaml": "YAML config",
    ".yml": "YAML config",
    ".toml": "TOML config",
    ".ini": "INI config",
    ".xml": "XML config",
    ".sql": "SQL",
    ".md": "Markdown",
    ".bat": "Windows batch",
    ".ps1": "PowerShell",
    ".sh": "Shell",
}

SOURCE_EXTS = {
    ".py",
    ".js",
    ".mjs",
    ".jsx",
    ".ts",
    ".tsx",
    ".vue",
    ".java",
    ".c",
    ".h",
    ".cpp",
    ".cc",
    ".hpp",
    ".cs",
    ".go",
    ".rs",
    ".php",
    ".rb",
    ".swift",
    ".kt",
}

JS_IMPORT_PATTERNS = [
    re.compile(r"^\s*import\s+(?:[^'\"]+\s+from\s+)?['\"]([^'\"]+)['\"]", re.M),
    re.compile(r"require\(\s*['\"]([^'\"]+)['\"]\s*\)"),
]

PY_IMPORT_PATTERNS = [
    re.compile(r"^\s*import\s+([A-Za-z0-9_., ]+)\s*$", re.M),
    re.compile(r"^\s*from\s+([A-Za-z0-9_\.]+)\s+import\s+", re.M),
]

C_IMPORT_PATTERNS = [
    re.compile(r"^\s*#\s*include\s+[<\"]([^>\"]+)[>\"]", re.M),
]

CS_IMPORT_PATTERNS = [
    re.compile(r"^\s*using\s+([A-Za-z0-9_.]+)\s*;", re.M),
]

EXPORT_PATTERNS = [
    re.compile(r"^\s*export\s+(?:default\s+)?(?:class|function|const|let|var|interface|type)\s+([A-Za-z_$][\w$]*)", re.M),
    re.compile(r"^\s*export\s*\{([^}]+)\}", re.M),
    re.compile(r"^\s*module\.exports\s*=\s*([A-Za-z_$][\w$]*)", re.M),
    re.compile(r"^\s*exports\.([A-Za-z_$][\w$]*)\s*=", re.M),
    re.compile(r"^\s*public\s+(?:class|interface|enum)\s+([A-Za-z_$][\w$]*)", re.M),
]

DECLARATION_PATTERNS_BY_EXT = {
    ".py": [
        ("function", re.compile(r"^\s*def\s+([A-Za-z_]\w*)\s*\(", re.M)),
        ("function", re.compile(r"^\s*async\s+def\s+([A-Za-z_]\w*)\s*\(", re.M)),
        ("class", re.compile(r"^\s*class\s+([A-Za-z_]\w*)", re.M)),
    ],
    ".js": [
        ("function", re.compile(r"^\s*(?:export\s+)?(?:async\s+)?function\s+([A-Za-z_$][\w$]*)", re.M)),
        ("function", re.compile(r"^\s*(?:export\s+)?(?:const|let|var)\s+([A-Za-z_$][\w$]*)\s*=\s*(?:async\s*)?\([^)]*\)\s*=>", re.M)),
        ("class", re.compile(r"^\s*(?:export\s+)?class\s+([A-Za-z_$][\w$]*)", re.M)),
        ("component", re.compile(r"^\s*(?:export\s+default\s+)?(?:function|const)\s+([A-Z][A-Za-z0-9_]*)", re.M)),
        ("schema", re.compile(r"([A-Za-z_$][\w$]*)\s*Schema\s*=", re.M)),
    ],
    ".mjs": [],
    ".jsx": [],
    ".ts": [
        ("function", re.compile(r"^\s*(?:export\s+)?(?:async\s+)?function\s+([A-Za-z_$][\w$]*)", re.M)),
        ("function", re.compile(r"^\s*(?:export\s+)?(?:const|let|var)\s+([A-Za-z_$][\w$]*)\s*=\s*(?:async\s*)?\([^)]*\)\s*=>", re.M)),
        ("class", re.compile(r"^\s*(?:export\s+)?class\s+([A-Za-z_$][\w$]*)", re.M)),
        ("interface", re.compile(r"^\s*(?:export\s+)?interface\s+([A-Za-z_$][\w$]*)", re.M)),
        ("type", re.compile(r"^\s*(?:export\s+)?type\s+([A-Za-z_$][\w$]*)", re.M)),
        ("component", re.compile(r"^\s*(?:export\s+default\s+)?(?:function|const)\s+([A-Z][A-Za-z0-9_]*)", re.M)),
        ("schema", re.compile(r"([A-Za-z_$][\w$]*)\s*Schema\s*=", re.M)),
    ],
    ".tsx": [],
    ".vue": [
        ("function", re.compile(r"^\s*(?:function|const)\s+([A-Za-z_$][\w$]*)", re.M)),
        ("component", re.compile(r"\bname\s*:\s*['\"]([A-Z][A-Za-z0-9_]*)['\"]")),
        ("component", re.compile(r"defineComponent\s*\(\s*\{\s*name\s*:\s*['\"]([A-Z][A-Za-z0-9_]*)['\"]", re.S)),
    ],
    ".java": [
        ("class", re.compile(r"^\s*(?:public\s+)?(?:abstract\s+)?class\s+([A-Za-z_]\w*)", re.M)),
        ("interface", re.compile(r"^\s*(?:public\s+)?interface\s+([A-Za-z_]\w*)", re.M)),
        ("type", re.compile(r"^\s*(?:public\s+)?enum\s+([A-Za-z_]\w*)", re.M)),
        ("function", re.compile(r"^\s*(?:public|private|protected|static|\s)+[\w<>\[\], ?]+\s+([A-Za-z_]\w*)\s*\([^;]*\)\s*\{", re.M)),
    ],
    ".c": [
        ("function", re.compile(r"^\s*[A-Za-z_][\w\s\*]*\s+([A-Za-z_]\w*)\s*\([^;]*\)\s*\{", re.M)),
    ],
    ".cpp": [],
    ".cc": [],
    ".h": [
        ("function", re.compile(r"^\s*[A-Za-z_][\w\s\*]*\s+([A-Za-z_]\w*)\s*\([^;]*\)\s*;", re.M)),
        ("class", re.compile(r"^\s*class\s+([A-Za-z_]\w*)", re.M)),
        ("type", re.compile(r"^\s*(?:typedef\s+)?struct\s+([A-Za-z_]\w*)", re.M)),
    ],
    ".hpp": [],
    ".cs": [
        ("class", re.compile(r"^\s*(?:public|private|internal)?\s*(?:partial\s+)?class\s+([A-Za-z_]\w*)", re.M)),
        ("interface", re.compile(r"^\s*(?:public|private|internal)?\s*interface\s+([A-Za-z_]\w*)", re.M)),
        ("function", re.compile(r"^\s*(?:public|private|protected|internal|static|\s)+[\w<>\[\], ?]+\s+([A-Za-z_]\w*)\s*\([^;]*\)\s*\{", re.M)),
    ],
}

for alias, source in {
    ".mjs": ".js",
    ".jsx": ".js",
    ".tsx": ".ts",
    ".cpp": ".c",
    ".cc": ".c",
    ".hpp": ".h",
}.items():
    DECLARATION_PATTERNS_BY_EXT[alias] = DECLARATION_PATTERNS_BY_EXT[source]

ROUTE_PATTERNS = [
    re.compile(r"@\w*Mapping\s*\(\s*(?:value\s*=\s*)?['\"]([^'\"]+)['\"]"),
    re.compile(r"\b(?:app|router|server)\.(?:get|post|put|patch|delete|use)\s*\(\s*['\"]([^'\"]+)['\"]"),
    re.compile(r"\b(?:GET|POST|PUT|PATCH|DELETE)\s+(/[^\s'\"`]+)"),
    re.compile(r"\bpath\s*:\s*['\"]([^'\"]+)['\"]"),
    re.compile(r"\broute\s*[:=]\s*['\"]([^'\"]+)['\"]"),
    re.compile(r"@(?:app|router)\.(?:get|post|put|patch|delete)\s*\(\s*['\"]([^'\"]+)['\"]"),
]

COMMENT_PATTERNS = [
    re.compile(r"^\s*#\s?(.*)", re.M),
    re.compile(r"^\s*//\s?(.*)", re.M),
    re.compile(r"/\*\*?([\s\S]*?)\*/"),
    re.compile(r"<!--([\s\S]*?)-->"),
]


def now_iso() -> str:
    return dt.datetime.now(dt.timezone.utc).astimezone().isoformat(timespec="seconds")


def normalize_rel(path: Path, root: Path) -> str:
    return path.relative_to(root).as_posix()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def is_hidden(path: Path, root: Path) -> bool:
    try:
        parts = path.relative_to(root).parts
    except ValueError:
        parts = path.parts
    return any(part.startswith(".") and part not in {".", ".."} for part in parts)


def should_ignore(path: Path, root: Path, include_hidden: bool) -> bool:
    name = path.name
    rel = normalize_rel(path, root) if path != root else ""
    if name in DEFAULT_IGNORES or rel in DEFAULT_IGNORES:
        return True
    if any(fnmatch.fnmatch(name, pattern) or fnmatch.fnmatch(rel, pattern) for pattern in DEFAULT_IGNORE_PATTERNS):
        return True
    if not include_hidden and is_hidden(path, root):
        return True
    return False


def is_probably_text(path: Path) -> bool:
    if path.suffix.lower() in TEXT_EXTENSIONS:
        return True
    return path.name in {"Dockerfile", "Makefile", "CMakeLists.txt", "README", "LICENSE"}


def read_text(path: Path, limit: int = 600_000) -> str:
    data = path.read_bytes()[:limit]
    for encoding in ("utf-8", "utf-8-sig", "gb18030", "latin-1"):
        try:
            return data.decode(encoding)
        except UnicodeDecodeError:
            continue
    return data.decode("utf-8", errors="replace")


def collect_files(root: Path, max_depth: int | None, include_hidden: bool) -> list[Path]:
    files: list[Path] = []
    for current, dirs, names in os.walk(root):
        current_path = Path(current)
        rel_depth = len(current_path.relative_to(root).parts) if current_path != root else 0
        dirs[:] = [
            d
            for d in dirs
            if not should_ignore(current_path / d, root, include_hidden)
            and (max_depth is None or rel_depth < max_depth)
        ]
        for name in names:
            path = current_path / name
            if should_ignore(path, root, include_hidden):
                continue
            if max_depth is not None and len(path.relative_to(root).parts) - 1 > max_depth:
                continue
            if is_probably_text(path):
                files.append(path)
    return sorted(files, key=lambda p: normalize_rel(p, root).lower())


def extract_comments(text: str) -> list[str]:
    comments: list[str] = []
    for pattern in COMMENT_PATTERNS:
        for match in pattern.findall(text):
            cleaned = re.sub(r"\s+", " ", str(match).replace("*", " ")).strip()
            if cleaned.startswith(("!", "eslint", "type:", "http://", "https://")):
                continue
            if "{" in cleaned or "}" in cleaned:
                continue
            if 8 <= len(cleaned) <= 180:
                comments.append(cleaned)
    return comments[:8]


def unique(items: list[str], limit: int = 40) -> list[str]:
    seen = set()
    result = []
    for item in items:
        cleaned = item.strip()
        if not cleaned or cleaned in seen:
            continue
        seen.add(cleaned)
        result.append(cleaned)
        if len(result) >= limit:
            break
    return result


def file_type(path: Path) -> str:
    if path.name.lower().startswith("readme"):
        return "README"
    if path.name.lower() in {"package.json", "pyproject.toml", "pom.xml", "build.gradle", "cmakelists.txt"}:
        return "Build/config"
    return EXTENSION_TYPES.get(path.suffix.lower(), path.suffix.lower().lstrip(".") or "Text")


def module_name(rel: str) -> str:
    parts = rel.split("/")
    if len(parts) == 1:
        return "root"
    if parts[0] in {"src", "app", "lib"} and len(parts) > 2:
        return f"{parts[0]}/{parts[1]}"
    return parts[0]


def classify_role(path: Path, text: str) -> list[str]:
    rel_lower = path.as_posix().lower()
    suffix = path.suffix.lower()
    type_lower = file_type(path).lower()
    signals = []
    if "test" in rel_lower or "spec" in rel_lower:
        signals.append("test")
    if suffix in {".md", ".txt"}:
        return unique(signals, 8)
    if "controller" in rel_lower or "controller" in text.lower():
        signals.append("controller")
    if "service" in rel_lower or "service" in text.lower():
        signals.append("service")
    if any(word in rel_lower for word in ("model", "entity", "schema")) or re.search(r"\b(schema|model|entity)\b", text, re.I):
        signals.append("model/schema")
    if re.search(r"\b(select|insert|update|delete|create table|alter table)\b", text, re.I) or type_lower == "sql":
        signals.append("SQL/data")
    if re.search(r"\b(main|if __name__ == ['\"]__main__['\"]|public static void main|createRoot|ReactDOM|new Vue)\b", text):
        signals.append("main/entry")
    if re.search(r"\b(route|router|@.*Mapping|app\.(get|post|put|patch|delete))\b", text):
        signals.append("route/api")
    if type_lower.endswith("config") or re.search(r"\b(config|settings|options|plugins|dependencies)\b", text, re.I):
        signals.append("config")
    return unique(signals, 8)


def extract_imports(text: str, path: Path) -> list[str]:
    imports = []
    suffix = path.suffix.lower()
    if suffix == ".py":
        patterns = PY_IMPORT_PATTERNS
    elif suffix in {".js", ".mjs", ".jsx", ".ts", ".tsx", ".vue"}:
        patterns = JS_IMPORT_PATTERNS
    elif suffix in {".c", ".h", ".cpp", ".cc", ".hpp"}:
        patterns = C_IMPORT_PATTERNS
    elif suffix == ".cs":
        patterns = CS_IMPORT_PATTERNS
    else:
        patterns = []
    for pattern in patterns:
        for match in pattern.findall(text):
            if isinstance(match, tuple):
                match = match[0]
            imports.extend(part.strip() for part in str(match).split(","))
    return unique(imports)


def extract_exports(text: str) -> list[str]:
    exports = []
    for pattern in EXPORT_PATTERNS:
        for match in pattern.findall(text):
            if "," in match:
                exports.extend(part.strip().split(" as ")[-1] for part in match.split(","))
            else:
                exports.append(str(match).strip())
    return unique(exports)


def extract_declarations(text: str, path: Path) -> list[dict[str, str]]:
    declarations = []
    patterns = DECLARATION_PATTERNS_BY_EXT.get(path.suffix.lower(), [])
    for kind, pattern in patterns:
        for name in pattern.findall(text):
            declarations.append({"kind": kind, "name": str(name)})
    seen = set()
    result = []
    for item in declarations:
        key = (item["kind"], item["name"])
        if key not in seen:
            seen.add(key)
            result.append(item)
        if len(result) >= 30:
            break
    return result


def extract_routes(text: str) -> list[str]:
    routes = []
    for pattern in ROUTE_PATTERNS:
        routes.extend(str(match).strip() for match in pattern.findall(text))
    return unique(routes, 30)


def extract_config_keys(text: str, path: Path) -> list[str]:
    if path.suffix.lower() not in {".json", ".yaml", ".yml", ".toml", ".ini", ".properties", ".xml"}:
        return []
    keys = re.findall(r"^\s*['\"]?([A-Za-z0-9_.-]{2,})['\"]?\s*[:=]", text, re.M)
    return unique(keys, 20)


def summarize_file(rel: str, info: dict[str, Any], lang: str) -> str:
    roles = info["roles"]
    declarations = info["declarations"]
    routes = info["routes"]
    exports = info["exports"]
    comments = info["comments"]
    ftype = info["type"]

    if comments:
        first = comments[0].rstrip(".。")
        if len(first) > 12:
            return first[:160]

    names = ", ".join(item["name"] for item in declarations[:3])
    if lang == "en":
        if routes:
            return f"Defines route/API behavior for {', '.join(routes[:3])}."
        if "test" in roles:
            return f"Tests {names or 'project behavior'}."
        if "config" in roles:
            return f"Configures {', '.join(info['config_keys'][:4]) or ftype}."
        if declarations:
            return f"Implements {names} as {ftype} project code."
        if exports:
            return f"Exports {', '.join(exports[:4])} for other modules."
        return f"Provides {ftype} content used by the project."

    if routes:
        return f"定义 {', '.join(routes[:3])} 等路由或 API 行为。"
    if "test" in roles:
        return f"测试 {names or '项目核心行为'}。"
    if "config" in roles:
        return f"配置 {', '.join(info['config_keys'][:4]) or ftype}。"
    if declarations:
        return f"实现 {names} 等 {ftype} 代码。"
    if exports:
        return f"导出 {', '.join(exports[:4])} 供其他模块使用。"
    return f"提供项目使用的 {ftype} 内容。"


def resolve_dependency(import_value: str, source_rel: str, all_files: set[str]) -> str | None:
    if not import_value or import_value.startswith(("http://", "https://", "@")):
        return None
    source_dir = Path(source_rel).parent
    candidates: list[Path] = []
    raw = import_value
    if raw.startswith("."):
        base = (source_dir / raw).as_posix()
        candidates.append(Path(base))
    elif "/" in raw or raw.endswith((".h", ".hpp")):
        candidates.append(Path(raw))
        candidates.append(source_dir / raw)
    else:
        return None

    suffixes = ["", ".py", ".js", ".jsx", ".ts", ".tsx", ".vue", ".java", ".c", ".cpp", ".cc", ".h", ".hpp", ".json"]
    index_names = ["index.js", "index.ts", "index.tsx", "__init__.py"]
    for candidate in candidates:
        normalized = candidate.as_posix().lstrip("./")
        for suffix in suffixes:
            rel = f"{normalized}{suffix}"
            if rel in all_files:
                return rel
        for index in index_names:
            rel = f"{normalized}/{index}"
            if rel in all_files:
                return rel
    return None


def detect_language(root: Path, file_texts: dict[str, str], requested: str) -> str:
    if requested in {"zh", "en"}:
        return requested
    samples = []
    for name in ("README.md", "README", "readme.md"):
        path = root / name
        if path.exists() and path.is_file():
            samples.append(read_text(path, 80_000))
    for rel, text in list(file_texts.items())[:80]:
        samples.extend(extract_comments(text)[:3])
    sample = "\n".join(samples)
    zh_chars = len(re.findall(r"[\u4e00-\u9fff]", sample))
    en_words = len(re.findall(r"\b[A-Za-z]{3,}\b", sample))
    if zh_chars > 20 and zh_chars >= en_words * 0.25:
        return "zh"
    if en_words > 40 and zh_chars < en_words * 0.08:
        return "en"
    return "zh"


def analyze_project(root: Path, args: argparse.Namespace) -> dict[str, Any]:
    files = collect_files(root, args.max_depth, args.include_hidden)
    file_texts: dict[str, str] = {}
    hashes: dict[str, str] = {}
    for path in files:
        rel = normalize_rel(path, root)
        file_texts[rel] = read_text(path)
        hashes[rel] = sha256_file(path)

    lang = detect_language(root, file_texts, args.lang)
    all_rels = set(file_texts)
    analyzed: dict[str, Any] = {}

    for rel, text in file_texts.items():
        path = root / rel
        info: dict[str, Any] = {
            "path": rel,
            "hash": hashes[rel],
            "type": file_type(path),
            "module": module_name(rel),
            "imports": extract_imports(text, path),
            "exports": extract_exports(text),
            "declarations": extract_declarations(text, path),
            "routes": extract_routes(text),
            "comments": extract_comments(text),
            "config_keys": extract_config_keys(text, path),
            "line_count": text.count("\n") + 1,
            "last_analyzed": now_iso(),
        }
        info["roles"] = classify_role(path, text)
        info["dependencies"] = unique(
            [dep for dep in (resolve_dependency(value, rel, all_rels) for value in info["imports"]) if dep]
        )
        info["summary"] = summarize_file(rel, info, lang)
        info["ai_hint"] = make_ai_hint(info, lang)
        analyzed[rel] = info

    for info in analyzed.values():
        info["referenced_by"] = []
    for rel, info in analyzed.items():
        for dep in info["dependencies"]:
            if dep in analyzed:
                analyzed[dep]["referenced_by"].append(rel)
    for info in analyzed.values():
        info["referenced_by"] = unique(info["referenced_by"], 100)

    modules = build_modules(analyzed)
    return {
        "project_name": root.name,
        "root": str(root),
        "updated_at": now_iso(),
        "language": lang,
        "file_count": len(analyzed),
        "module_count": len(modules),
        "files": analyzed,
        "modules": modules,
        "tree": build_tree(list(analyzed)),
    }


def make_ai_hint(info: dict[str, Any], lang: str) -> str:
    rel = info["path"]
    related = info["dependencies"][:3] + info.get("referenced_by", [])[:3]
    if lang == "en":
        if info["routes"]:
            return f"Edit this file for route/API behavior; inspect related callers before changing {', '.join(info['routes'][:3])}."
        if "test" in info["roles"]:
            return "Update this file when behavior changes need test coverage or assertions."
        if "config" in info["roles"]:
            return "Edit carefully because configuration changes can affect startup, build, or deployment."
        if related:
            return f"Before editing, inspect related files: {', '.join(related)}."
        return f"Use this file when changes target {info['module']} behavior."
    if info["routes"]:
        return f"修改路由或 API 行为时优先查看本文件，并同步检查 {', '.join(info['routes'][:3])} 的调用方。"
    if "test" in info["roles"]:
        return "行为变化需要测试覆盖或断言调整时修改本文件。"
    if "config" in info["roles"]:
        return "配置改动可能影响启动、构建或部署，修改前确认引用位置。"
    if related:
        return f"修改前先检查相关文件：{', '.join(related)}。"
    return f"当变更目标属于 {info['module']} 模块时可从本文件定位。"


def build_modules(files: dict[str, Any]) -> dict[str, Any]:
    modules: dict[str, Any] = {}
    for rel, info in files.items():
        name = info["module"]
        module = modules.setdefault(name, {"name": name, "files": [], "depends_on": []})
        module["files"].append(rel)
        for dep in info["dependencies"]:
            dep_module = files.get(dep, {}).get("module")
            if dep_module and dep_module != name:
                module["depends_on"].append(dep_module)
    for module in modules.values():
        module["files"] = sorted(module["files"])
        module["depends_on"] = sorted(set(module["depends_on"]))
    return dict(sorted(modules.items()))


def build_tree(paths: list[str]) -> dict[str, Any]:
    root = {"name": "", "type": "dir", "children": {}}
    for rel in sorted(paths):
        node = root
        parts = rel.split("/")
        for part in parts[:-1]:
            node = node["children"].setdefault(part, {"name": part, "type": "dir", "children": {}})
        node["children"][parts[-1]] = {"name": parts[-1], "type": "file", "path": rel}

    def compact(node: dict[str, Any]) -> dict[str, Any]:
        if node["type"] == "file":
            return node
        children = [compact(child) for child in node["children"].values()]
        children.sort(key=lambda item: (item["type"] == "file", item["name"].lower()))
        return {"name": node["name"], "type": "dir", "children": children}

    return compact(root)


def directory_lines(paths: list[str]) -> list[str]:
    tree = build_tree(paths)
    lines: list[str] = []

    def walk(node: dict[str, Any], prefix: str = "") -> None:
        children = node.get("children", [])
        for index, child in enumerate(children):
            connector = "`-- " if index == len(children) - 1 else "|-- "
            lines.append(prefix + connector + child["name"])
            if child["type"] == "dir":
                extension = "    " if index == len(children) - 1 else "|   "
                walk(child, prefix + extension)

    walk(tree)
    return lines


def render_markdown(data: dict[str, Any]) -> str:
    zh = data["language"] == "zh"
    files = data["files"]
    modules = data["modules"]
    important = sorted(
        files.values(),
        key=lambda item: (
            -len(item["referenced_by"]),
            0 if any(role in item["roles"] for role in ("main/entry", "route/api", "config")) else 1,
            item["path"],
        ),
    )[:20]

    if zh:
        lines = [
            f"# {data['project_name']} 项目结构地图",
            "",
            "## 项目概览",
            "",
            f"- 更新时间：{data['updated_at']}",
            f"- 文件总数：{data['file_count']}",
            f"- 模块总数：{data['module_count']}",
            f"- 输出语言：中文",
            "",
            "## 目录结构",
            "",
            "```text",
            *directory_lines(list(files))[:600],
            "```",
            "",
            "## 核心模块说明",
            "",
        ]
        for module in modules.values():
            sample = ", ".join(module["files"][:5])
            deps = ", ".join(module["depends_on"]) or "无跨模块依赖"
            lines.append(f"- `{module['name']}`：包含 {len(module['files'])} 个文件；依赖模块：{deps}；代表文件：{sample}")
        lines.extend(["", "## 重要文件说明", ""])
        for item in important:
            decls = ", ".join(d["name"] for d in item["declarations"][:5]) or "未检测到主要声明"
            lines.append(f"- `{item['path']}`：{item['summary']} 类型：{item['type']}；模块：{item['module']}；主要声明：{decls}")
        lines.extend(
            [
                "",
                "## 开发者导航建议",
                "",
                "- 先从入口、路由、配置和被引用最多的文件理解运行路径。",
                "- 修改业务逻辑前查看右侧依赖与被引用关系，避免只改调用链的一端。",
                "- 测试文件通常与同名或同模块源码对应，行为变更后同步检查。",
                "",
                "## AI 修改定位规则",
                "",
                "- 修改前优先读取本文件和 `PROJECT_MAP.html` 中的文件详情。",
                "- 新增、删除、移动、重命名文件后必须重新运行 project-visual-map-manager。",
                "- 涉及 API、路由、配置、模型、schema、SQL 或入口文件时，必须检查依赖方和引用方。",
                "- 无法确认影响范围时，从模块说明、重要文件、依赖关系图三处交叉定位。",
            ]
        )
        return "\n".join(lines) + "\n"

    lines = [
        f"# {data['project_name']} Project Structure Map",
        "",
        "## Project Overview",
        "",
        f"- Updated: {data['updated_at']}",
        f"- Total files: {data['file_count']}",
        f"- Modules: {data['module_count']}",
        f"- Language: English",
        "",
        "## Directory Structure",
        "",
        "```text",
        *directory_lines(list(files))[:600],
        "```",
        "",
        "## Core Modules",
        "",
    ]
    for module in modules.values():
        sample = ", ".join(module["files"][:5])
        deps = ", ".join(module["depends_on"]) or "no cross-module dependencies"
        lines.append(f"- `{module['name']}`: {len(module['files'])} files; depends on: {deps}; examples: {sample}")
    lines.extend(["", "## Important Files", ""])
    for item in important:
        decls = ", ".join(d["name"] for d in item["declarations"][:5]) or "no major declarations detected"
        lines.append(f"- `{item['path']}`: {item['summary']} Type: {item['type']}; module: {item['module']}; declarations: {decls}")
    lines.extend(
        [
            "",
            "## Developer Navigation Advice",
            "",
            "- Start with entry, route, config, and highly referenced files to understand runtime flow.",
            "- Before changing business logic, inspect dependency and reverse-reference relationships.",
            "- Test files usually pair with same-name or same-module source files; check them after behavior changes.",
            "",
            "## AI Modification Location Rules",
            "",
            "- Read this file and `PROJECT_MAP.html` details before editing.",
            "- Rerun project-visual-map-manager after adding, deleting, moving, or renaming files.",
            "- For API, route, config, model, schema, SQL, or entry changes, inspect dependencies and callers.",
            "- If impact is unclear, cross-check modules, important files, and the dependency graph.",
        ]
    )
    return "\n".join(lines) + "\n"


CSS = r"""
:root { color-scheme: light; --bg:#f7f8fb; --panel:#ffffff; --ink:#172033; --muted:#667085; --line:#d9dee8; --accent:#1f7a8c; --accent2:#b23a48; --chip:#eef6f8; }
* { box-sizing: border-box; }
body { margin:0; font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; background:var(--bg); color:var(--ink); }
header { padding:18px 24px; border-bottom:1px solid var(--line); background:var(--panel); position:sticky; top:0; z-index:2; }
.top { display:flex; align-items:center; justify-content:space-between; gap:16px; flex-wrap:wrap; }
h1 { margin:0; font-size:22px; line-height:1.2; letter-spacing:0; }
.meta { display:flex; gap:10px; flex-wrap:wrap; color:var(--muted); font-size:13px; }
.pill { background:var(--chip); color:#14525e; border:1px solid #cfe6eb; padding:4px 8px; border-radius:8px; }
.controls { display:flex; gap:10px; margin-top:14px; flex-wrap:wrap; }
input, select { border:1px solid var(--line); border-radius:8px; padding:9px 10px; font-size:14px; background:#fff; color:var(--ink); }
#search { min-width:320px; flex:1; }
main { display:grid; grid-template-columns:minmax(280px, 34vw) 1fr; min-height:calc(100vh - 118px); }
aside { border-right:1px solid var(--line); background:#fbfcfe; overflow:auto; padding:14px; }
section { overflow:auto; padding:18px; }
.tree ul { list-style:none; padding-left:18px; margin:0; }
.tree > ul { padding-left:0; }
.dir { margin:7px 0; font-weight:650; color:#344054; }
.file { display:block; width:100%; text-align:left; border:0; background:transparent; color:var(--ink); padding:5px 7px; border-radius:6px; cursor:pointer; font-size:13px; overflow:hidden; text-overflow:ellipsis; white-space:nowrap; }
.file:hover, .file.active { background:#e8f3f5; color:#0f5361; }
.layout { display:grid; grid-template-columns:minmax(280px, 0.9fr) minmax(320px, 1.1fr); gap:16px; align-items:start; }
.panel { background:var(--panel); border:1px solid var(--line); border-radius:8px; padding:16px; }
.panel h2 { margin:0 0 10px; font-size:17px; }
.panel h3 { margin:16px 0 8px; font-size:14px; color:#344054; }
.summary { font-size:15px; line-height:1.5; }
.kv { display:grid; grid-template-columns:104px 1fr; gap:8px 12px; font-size:13px; margin-top:12px; }
.kv div:nth-child(odd) { color:var(--muted); }
.kv div, .summary, .list, .chip { overflow-wrap:anywhere; }
.chips { display:flex; flex-wrap:wrap; gap:6px; }
.chip { border:1px solid var(--line); background:#f9fafb; padding:3px 7px; border-radius:999px; font-size:12px; }
.list { margin:0; padding-left:18px; font-size:13px; line-height:1.55; }
#tooltip { position:fixed; display:none; max-width:360px; background:#172033; color:#fff; padding:10px 12px; border-radius:8px; box-shadow:0 10px 24px rgba(16,24,40,.22); pointer-events:none; z-index:5; font-size:12px; line-height:1.45; }
.graph-wrap { overflow:auto; }
svg { width:100%; height:360px; background:#fbfcfe; border:1px solid var(--line); border-radius:8px; }
.node { fill:#fff; stroke:#1f7a8c; stroke-width:1.4; }
.node.selected { stroke:#b23a48; stroke-width:2.2; }
.edge { stroke:#98a2b3; stroke-width:1.2; marker-end:url(#arrow); }
.node-label { font-size:13px; fill:#172033; }
.empty { color:var(--muted); font-size:13px; }
@media (max-width: 900px) {
  main, .layout { grid-template-columns:1fr; }
  aside { border-right:0; border-bottom:1px solid var(--line); max-height:42vh; }
  #search { min-width:100%; }
}
"""


JS = r"""
const data = JSON.parse(document.getElementById('project-data').textContent);
const files = data.files;
let selectedPath = Object.keys(files)[0] || null;

const labels = data.language === 'en' ? {
  search:'Search files, modules, routes, declarations',
  allTypes:'All file types',
  details:'File Details',
  path:'Path',
  type:'Type',
  purpose:'Purpose',
  module:'Module',
  declarations:'Functions / Classes / Components',
  exports:'Exports',
  dependencies:'Depends on',
  referencedBy:'Referenced by',
  routes:'Interfaces / Routes / Config',
  aiHint:'AI Location Advice',
  graph:'Dependency Graph',
  none:'None detected'
} : {
  search:'搜索文件、模块、路由、声明',
  allTypes:'全部文件类型',
  details:'文件详情',
  path:'文件路径',
  type:'文件类型',
  purpose:'文件作用',
  module:'所属模块',
  declarations:'主要函数 / 类 / 组件',
  exports:'主要导出内容',
  dependencies:'依赖了哪些文件',
  referencedBy:'被哪些文件引用',
  routes:'相关接口 / 路由 / 配置',
  aiHint:'AI 修改定位建议',
  graph:'依赖关系图',
  none:'未检测到'
};

function el(tag, attrs={}, children=[]) {
  const node = document.createElement(tag);
  Object.entries(attrs).forEach(([key, value]) => {
    if (key === 'class') node.className = value;
    else if (key === 'text') node.textContent = value;
    else node.setAttribute(key, value);
  });
  children.forEach(child => node.appendChild(child));
  return node;
}

function matches(info, query, type) {
  if (type && info.type !== type) return false;
  if (!query) return true;
  const haystack = [
    info.path, info.type, info.module, info.summary,
    ...(info.routes || []), ...(info.exports || []),
    ...(info.declarations || []).map(d => d.name)
  ].join(' ').toLowerCase();
  return haystack.includes(query.toLowerCase());
}

function visiblePaths() {
  const query = document.getElementById('search').value.trim();
  const type = document.getElementById('typeFilter').value;
  return new Set(Object.values(files).filter(info => matches(info, query, type)).map(info => info.path));
}

function renderTreeNode(node, visible) {
  if (node.type === 'file') {
    if (!visible.has(node.path)) return null;
    const info = files[node.path];
    const button = el('button', {class:'file', text:node.name, 'data-path':node.path});
    if (node.path === selectedPath) button.classList.add('active');
    button.addEventListener('click', () => { selectedPath = node.path; renderAll(); });
    button.addEventListener('mousemove', evt => showTip(evt, info));
    button.addEventListener('mouseleave', hideTip);
    return el('li', {}, [button]);
  }
  const children = (node.children || []).map(child => renderTreeNode(child, visible)).filter(Boolean);
  if (!children.length && node.name) return null;
  const list = el('ul', {}, children);
  if (!node.name) return list;
  return el('li', {}, [el('div', {class:'dir', text:node.name}), list]);
}

function showTip(evt, info) {
  const tip = document.getElementById('tooltip');
  const decls = (info.declarations || []).slice(0,5).map(d => d.name).join(', ') || labels.none;
  tip.innerHTML = `<strong>${escapeHtml(info.path)}</strong><br>${escapeHtml(info.summary)}<br>${labels.declarations}: ${escapeHtml(decls)}<br>${labels.type}: ${escapeHtml(info.type)}<br>${labels.module}: ${escapeHtml(info.module)}`;
  tip.style.display = 'block';
  tip.style.left = Math.min(evt.clientX + 14, window.innerWidth - 380) + 'px';
  tip.style.top = Math.min(evt.clientY + 14, window.innerHeight - 160) + 'px';
}
function hideTip(){ document.getElementById('tooltip').style.display = 'none'; }
function escapeHtml(value){ return String(value).replace(/[&<>"']/g, ch => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[ch])); }

function chips(values) {
  const list = values && values.length ? values : [labels.none];
  return el('div', {class:'chips'}, list.map(value => el('span', {class:'chip', text:value})));
}

function list(values) {
  const items = values && values.length ? values : [labels.none];
  return el('ul', {class:'list'}, items.map(value => el('li', {text:value})));
}

function renderDetails() {
  const info = files[selectedPath];
  const details = document.getElementById('details');
  details.innerHTML = '';
  if (!info) {
    details.appendChild(el('p', {class:'empty', text:labels.none}));
    return;
  }
  details.appendChild(el('h2', {text:labels.details}));
  details.appendChild(el('p', {class:'summary', text:info.summary}));
  const kv = el('div', {class:'kv'}, [
    el('div', {text:labels.path}), el('div', {text:info.path}),
    el('div', {text:labels.type}), el('div', {text:info.type}),
    el('div', {text:labels.module}), el('div', {text:info.module}),
    el('div', {text:'Lines'}), el('div', {text:String(info.line_count)})
  ]);
  details.appendChild(kv);
  details.appendChild(el('h3', {text:labels.declarations}));
  details.appendChild(chips((info.declarations || []).map(d => `${d.kind}: ${d.name}`)));
  details.appendChild(el('h3', {text:labels.exports}));
  details.appendChild(chips(info.exports || []));
  details.appendChild(el('h3', {text:labels.dependencies}));
  details.appendChild(list(info.dependencies || []));
  details.appendChild(el('h3', {text:labels.referencedBy}));
  details.appendChild(list(info.referenced_by || []));
  details.appendChild(el('h3', {text:labels.routes}));
  details.appendChild(chips([...(info.routes || []), ...(info.config_keys || [])]));
  details.appendChild(el('h3', {text:labels.aiHint}));
  details.appendChild(el('p', {class:'summary', text:info.ai_hint}));
}

function renderGraph() {
  const info = files[selectedPath];
  const svg = document.getElementById('graph');
  svg.innerHTML = '<defs><marker id="arrow" markerWidth="8" markerHeight="8" refX="7" refY="3" orient="auto"><path d="M0,0 L0,6 L7,3 z" fill="#98a2b3"/></marker></defs>';
  if (!info) return;
  const related = Array.from(new Set([...(info.dependencies || []), info.path, ...(info.referenced_by || [])])).slice(0, 18);
  const width = 640, height = 330, cx = width / 2, cy = height / 2;
  const positions = {};
  positions[info.path] = {x:cx, y:cy};
  const others = related.filter(path => path !== info.path);
  others.forEach((path, index) => {
    const angle = (Math.PI * 2 * index / Math.max(others.length, 1)) - Math.PI / 2;
    positions[path] = {x:cx + Math.cos(angle) * 220, y:cy + Math.sin(angle) * 105};
  });
  svg.setAttribute('viewBox', `0 0 ${width} ${height}`);
  related.forEach(path => {
    const source = files[path];
    if (!source) return;
    (source.dependencies || []).forEach(dep => {
      if (!positions[dep]) return;
      const a = positions[path], b = positions[dep];
      const line = document.createElementNS('http://www.w3.org/2000/svg', 'line');
      line.setAttribute('x1', a.x); line.setAttribute('y1', a.y);
      line.setAttribute('x2', b.x); line.setAttribute('y2', b.y);
      line.setAttribute('class', 'edge');
      svg.appendChild(line);
    });
  });
  related.forEach(path => {
    const p = positions[path];
    const circle = document.createElementNS('http://www.w3.org/2000/svg', 'circle');
    circle.setAttribute('cx', p.x); circle.setAttribute('cy', p.y); circle.setAttribute('r', path === info.path ? 34 : 28);
    circle.setAttribute('class', path === info.path ? 'node selected' : 'node');
    circle.addEventListener('click', () => { selectedPath = path; renderAll(); });
    svg.appendChild(circle);
    const text = document.createElementNS('http://www.w3.org/2000/svg', 'text');
    text.setAttribute('x', p.x); text.setAttribute('y', p.y + 48);
    text.setAttribute('text-anchor', 'middle'); text.setAttribute('class', 'node-label');
    text.textContent = shortLabel(path);
    svg.appendChild(text);
  });
}

function shortLabel(path) {
  const parts = path.split('/');
  const label = parts[parts.length - 1] || path;
  return label.length > 24 ? '...' + label.slice(-21) : label;
}

function renderAll() {
  const visible = visiblePaths();
  if (!visible.has(selectedPath)) selectedPath = Array.from(visible)[0] || Object.keys(files)[0] || null;
  const tree = document.getElementById('tree');
  tree.innerHTML = '';
  tree.appendChild(renderTreeNode(data.tree, visible) || el('p', {class:'empty', text:labels.none}));
  renderDetails();
  renderGraph();
}

function initControls() {
  document.getElementById('search').setAttribute('placeholder', labels.search);
  const select = document.getElementById('typeFilter');
  select.appendChild(el('option', {value:'', text:labels.allTypes}));
  Array.from(new Set(Object.values(files).map(info => info.type))).sort().forEach(type => {
    select.appendChild(el('option', {value:type, text:type}));
  });
  document.getElementById('search').addEventListener('input', renderAll);
  select.addEventListener('change', renderAll);
}

initControls();
renderAll();
"""


def render_html(data: dict[str, Any]) -> str:
    zh = data["language"] == "zh"
    body = f"""
<header>
  <div class="top">
    <div>
      <h1>{html.escape(data['project_name'])} {'项目地图' if zh else 'Project Map'}</h1>
      <div class="meta">
        <span class="pill">{'更新时间' if zh else 'Updated'}: {html.escape(data['updated_at'])}</span>
        <span class="pill">{'文件总数' if zh else 'Files'}: {data['file_count']}</span>
        <span class="pill">{'模块总数' if zh else 'Modules'}: {data['module_count']}</span>
      </div>
    </div>
  </div>
  <div class="controls">
    <input id="search" type="search">
    <select id="typeFilter"></select>
  </div>
</header>
<main>
  <aside class="tree" id="tree"></aside>
  <section>
    <div class="layout">
      <div class="panel" id="details"></div>
      <div class="panel">
        <h2>{'依赖关系图' if zh else 'Dependency Graph'}</h2>
        <div class="graph-wrap"><svg id="graph" role="img"></svg></div>
      </div>
    </div>
  </section>
</main>
<div id="tooltip"></div>
"""
    payload = json.dumps(data, ensure_ascii=False).replace("</", "<\\/")
    return (
        "<!doctype html>\n"
        f"<html lang=\"{data['language']}\">\n<head>\n<meta charset=\"utf-8\">\n"
        "<meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">\n"
        f"<title>{html.escape(data['project_name'])} Project Map</title>\n"
        f"<style>{CSS}</style>\n</head>\n<body>\n"
        f"<script id=\"project-data\" type=\"application/json\">{payload}</script>\n"
        f"{body}\n<script>{JS}</script>\n</body>\n</html>\n"
    )


def write_outputs(root: Path, data: dict[str, Any], output_md: Path, output_html: Path) -> None:
    output_md.write_text(render_markdown(data), encoding="utf-8")
    output_html.write_text(render_html(data), encoding="utf-8")
    cache = {
        "project_name": data["project_name"],
        "updated_at": data["updated_at"],
        "language": data["language"],
        "files": {
            rel: {
                "path": rel,
                "hash": info["hash"],
                "summary": info["summary"],
                "type": info["type"],
                "module": info["module"],
                "imports": info["imports"],
                "declarations": info["declarations"],
                "exports": info["exports"],
                "dependencies": info["dependencies"],
                "referenced_by": info["referenced_by"],
                "routes": info["routes"],
                "config_keys": info["config_keys"],
                "last_analyzed": info["last_analyzed"],
            }
            for rel, info in data["files"].items()
        },
    }
    (root / ".project-map-cache.json").write_text(json.dumps(cache, ensure_ascii=False, indent=2), encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate a visual project map and AI-readable structure summary.")
    parser.add_argument("--root", default=".", help="Target project root.")
    parser.add_argument("--lang", choices=["zh", "en", "auto"], default="auto", help="Output language.")
    parser.add_argument("--output-html", default=None, help="HTML output path. Defaults to <root>/PROJECT_MAP.html.")
    parser.add_argument("--output-md", default=None, help="Markdown output path. Defaults to <root>/PROJECT_STRUCTURE.md.")
    parser.add_argument("--max-depth", type=int, default=None, help="Maximum directory traversal depth.")
    parser.add_argument("--include-hidden", action="store_true", help="Include hidden files except default ignored paths.")
    parser.add_argument("--watch", action="store_true", help="Reserved for future watch mode; currently runs once.")
    parser.add_argument("--open", action="store_true", help="Open the generated HTML map with the system default browser.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    root = Path(args.root).resolve()
    if not root.exists() or not root.is_dir():
        raise SystemExit(f"Root directory does not exist: {root}")
    output_html = Path(args.output_html).resolve() if args.output_html else root / "PROJECT_MAP.html"
    output_md = Path(args.output_md).resolve() if args.output_md else root / "PROJECT_STRUCTURE.md"
    data = analyze_project(root, args)
    write_outputs(root, data, output_md, output_html)
    print(f"Updated {output_md}")
    print(f"Updated {output_html}")
    print(f"Updated {root / '.project-map-cache.json'}")
    if args.open:
        webbrowser.open(output_html.as_uri())
        print(f"Opened {output_html}")
    if args.watch:
        print("--watch is reserved for future use; completed one update.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
