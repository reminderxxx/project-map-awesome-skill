# project-map-awesome-skill 项目结构地图

## 项目概览

- 更新时间：2026-05-27T14:58:32+08:00
- 文件总数：11
- 模块总数：2
- 输出语言：中文

## 目录结构

```text
|-- project-visual-map-manager
|   |-- scripts
|   |   |-- config.example.json
|   |   `-- update_project_map.py
|   |-- templates
|   |   |-- PROJECT_MAP.template.html
|   |   `-- PROJECT_STRUCTURE.template.md
|   |-- README.md
|   |-- README.zh-CN.md
|   |-- run-project-map.bat
|   |-- run-project-map.ps1
|   `-- SKILL.md
|-- AI-INTEGRATION.md
`-- install-project-map.ps1
```

## 核心模块说明

- `project-visual-map-manager`：包含 9 个文件；依赖模块：无跨模块依赖；代表文件：project-visual-map-manager/README.md, project-visual-map-manager/README.zh-CN.md, project-visual-map-manager/SKILL.md, project-visual-map-manager/run-project-map.bat, project-visual-map-manager/run-project-map.ps1
- `root`：包含 2 个文件；依赖模块：无跨模块依赖；代表文件：AI-INTEGRATION.md, install-project-map.ps1

## 重要文件说明

- `project-visual-map-manager/scripts/config.example.json`：配置 root, lang, output_html, output_md。 类型：JSON config；模块：project-visual-map-manager；主要声明：未检测到主要声明
- `project-visual-map-manager/scripts/update_project_map.py`：定义 Path, 文件路径 等路由或 API 行为。 类型：Python；模块：project-visual-map-manager；主要声明：now_iso, normalize_rel, sha256_file, is_hidden, should_ignore
- `AI-INTEGRATION.md`：AI Integration Guide 类型：Markdown；模块：root；主要声明：未检测到主要声明
- `install-project-map.ps1`：提供项目使用的 PowerShell 内容。 类型：PowerShell；模块：root；主要声明：未检测到主要声明
- `project-visual-map-manager/README.md`：project-visual-map-manager 类型：README；模块：project-visual-map-manager；主要声明：未检测到主要声明
- `project-visual-map-manager/README.zh-CN.md`：project-visual-map-manager 中文说明 类型：README；模块：project-visual-map-manager；主要声明：未检测到主要声明
- `project-visual-map-manager/SKILL.md`：Project Visual Map Manager 类型：Markdown；模块：project-visual-map-manager；主要声明：未检测到主要声明
- `project-visual-map-manager/run-project-map.bat`：提供项目使用的 Windows batch 内容。 类型：Windows batch；模块：project-visual-map-manager；主要声明：未检测到主要声明
- `project-visual-map-manager/run-project-map.ps1`：提供项目使用的 PowerShell 内容。 类型：PowerShell；模块：project-visual-map-manager；主要声明：未检测到主要声明
- `project-visual-map-manager/templates/PROJECT_MAP.template.html`：提供项目使用的 HTML 内容。 类型：HTML；模块：project-visual-map-manager；主要声明：未检测到主要声明
- `project-visual-map-manager/templates/PROJECT_STRUCTURE.template.md`：提供项目使用的 Markdown 内容。 类型：Markdown；模块：project-visual-map-manager；主要声明：未检测到主要声明

## 开发者导航建议

- 先从入口、路由、配置和被引用最多的文件理解运行路径。
- 修改业务逻辑前查看右侧依赖与被引用关系，避免只改调用链的一端。
- 测试文件通常与同名或同模块源码对应，行为变更后同步检查。

## AI 修改定位规则

- 修改前优先读取本文件和 `PROJECT_MAP.html` 中的文件详情。
- 新增、删除、移动、重命名文件后必须重新运行 project-visual-map-manager。
- 涉及 API、路由、配置、模型、schema、SQL 或入口文件时，必须检查依赖方和引用方。
- 无法确认影响范围时，从模块说明、重要文件、依赖关系图三处交叉定位。
