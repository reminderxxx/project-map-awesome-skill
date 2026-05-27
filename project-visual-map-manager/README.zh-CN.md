# project-visual-map-manager 中文说明

`project-visual-map-manager` 是一个可复用的 Codex Skill，用于为任意软件项目生成可视化项目地图。它会同时输出适合 AI 和开发者快速阅读的 Markdown 项目结构说明，以及可以直接双击打开的单文件 HTML 可视化地图。

## 推荐集成方式

推荐把 `project-visual-map-manager/` 放进目标项目根目录。这样项目会自带地图生成能力，开发者和 AI 都能直接运行。

### 方法 1：让 AI 通过 GitHub 拉取并融入项目

把下面这段话发给 AI：

```text
请把 project-visual-map-manager 集成到当前项目。

来源仓库：
https://github.com/reminderxxx/project-map-awesome-skill.git

要求：
1. 当前工作目录是目标项目根目录。
2. 把来源仓库 clone 到临时目录，不要 clone 到当前项目里。
3. 只复制 project-visual-map-manager/ 目录到当前项目根目录。
4. 不要复制来源仓库的 .git 目录和外层生成文件。
5. 集成后运行：
   powershell -ExecutionPolicy Bypass -File project-visual-map-manager/run-project-map.ps1 -Root . -NoOpen
6. 生成后读取 PROJECT_STRUCTURE.md，后续新增、删除、移动、重命名文件后重新运行地图生成器。
```

更完整的 AI 指令见仓库根目录的 `AI-INTEGRATION.md`。

### 方法 2：PowerShell 一键集成

如果你已经拿到了本仓库根目录的 `install-project-map.ps1`，在目标项目根目录运行：

```powershell
powershell -ExecutionPolicy Bypass -File install-project-map.ps1 -RepoUrl https://github.com/reminderxxx/project-map-awesome-skill.git
```

只安装 Skill，不立即生成地图：

```powershell
powershell -ExecutionPolicy Bypass -File install-project-map.ps1 -NoRun
```

目标项目里已经存在 `project-visual-map-manager/`，需要覆盖更新：

```powershell
powershell -ExecutionPolicy Bypass -File install-project-map.ps1 -Force
```

常用参数：

- `-RepoUrl`：Skill 来源仓库，默认是 `https://github.com/reminderxxx/project-map-awesome-skill.git`。
- `-TargetRoot`：目标项目根目录，默认是当前目录。
- `-Force`：目标项目已有 `project-visual-map-manager/` 时覆盖。
- `-NoRun`：只复制 Skill，不生成地图。
- `-NoOpen`：生成地图但不自动打开 HTML。

### 方法 3：项目内日常运行

当目标项目已经包含 `project-visual-map-manager/` 后，直接双击：

```text
project-visual-map-manager/run-project-map.bat
```

或在 PowerShell 中运行：

```powershell
.\project-visual-map-manager\run-project-map.ps1
```

## 一键使用

普通 Windows 用户推荐使用一键脚本。

如果 `project-visual-map-manager` 目录就在目标项目中，直接双击：

```text
project-visual-map-manager/run-project-map.bat
```

脚本会自动完成三件事：

1. 扫描当前项目。
2. 生成或更新 `PROJECT_STRUCTURE.md`、`PROJECT_MAP.html`、`.project-map-cache.json`。
3. 用默认浏览器打开 `PROJECT_MAP.html`。

也可以在 PowerShell 中运行：

```powershell
.\project-visual-map-manager\run-project-map.ps1
```

PowerShell 入口支持参数：

```powershell
.\project-visual-map-manager\run-project-map.ps1 -Root . -Lang zh -MaxDepth 8
```

只生成文件、不自动打开浏览器：

```powershell
.\project-visual-map-manager\run-project-map.ps1 -Root . -NoOpen
```

## 作用

这个 Skill 适合在以下场景使用：

- 接手陌生项目时，快速理解目录结构和核心模块。
- AI 修改项目之前，先定位应该改哪些文件。
- 项目新增、删除、移动、重命名文件后，刷新项目结构说明。
- 为课程实验、前端、后端、全栈、Java、Python、Node.js、Vue、React、C/C++ 项目生成导航文档。

## 安装方式

把整个 `project-visual-map-manager` 目录复制到 Codex Skills 目录，例如：

```bash
~/.codex/skills/project-visual-map-manager
```

也可以不安装，直接在当前仓库中运行脚本：

```bash
python project-visual-map-manager/scripts/update_project_map.py --root . --open
```

## 基本使用

推荐方式是在目标项目根目录运行一键入口：

```powershell
.\project-visual-map-manager\run-project-map.ps1
```

如果需要直接调用 Python 脚本，运行：

```bash
python path/to/project-visual-map-manager/scripts/update_project_map.py --root .
```

如果 Skill 目录就在当前项目中，可以运行：

```bash
python project-visual-map-manager/scripts/update_project_map.py --root .
```

生成完成后自动打开 HTML：

```bash
python project-visual-map-manager/scripts/update_project_map.py --root . --open
```

运行后会在目标项目根目录生成或更新：

- `PROJECT_STRUCTURE.md`
- `PROJECT_MAP.html`
- `.project-map-cache.json`

## 常用命令

生成中文输出：

```bash
python project-visual-map-manager/scripts/update_project_map.py --root . --lang zh
```

生成英文输出：

```bash
python project-visual-map-manager/scripts/update_project_map.py --root . --lang en
```

自动判断输出语言：

```bash
python project-visual-map-manager/scripts/update_project_map.py --root . --lang auto
```

限制扫描深度：

```bash
python project-visual-map-manager/scripts/update_project_map.py --root . --max-depth 6
```

自定义输出路径：

```bash
python project-visual-map-manager/scripts/update_project_map.py \
  --root . \
  --output-md docs/PROJECT_STRUCTURE.md \
  --output-html docs/PROJECT_MAP.html
```

## 参数说明

- `--root`：目标项目根目录，默认是当前目录。
- `--lang zh/en/auto`：输出语言，默认是 `auto`。
- `--output-html`：指定 HTML 可视化地图输出路径，默认是 `<root>/PROJECT_MAP.html`。
- `--output-md`：指定 Markdown 项目结构说明输出路径，默认是 `<root>/PROJECT_STRUCTURE.md`。
- `--max-depth`：限制目录扫描深度。
- `--include-hidden`：包含隐藏文件和目录，但仍会忽略默认排除项。
- `--open`：生成完成后用系统默认浏览器打开 `PROJECT_MAP.html`。
- `--watch`：预留参数，目前只执行一次更新。

## 输出文件说明

`PROJECT_STRUCTURE.md` 面向开发者和 AI，包含：

- 项目概览
- 更新时间
- 目录结构
- 核心模块说明
- 重要文件说明
- 开发者导航建议
- AI 修改定位规则

`PROJECT_MAP.html` 面向开发者可视化阅读，包含：

- 项目名称、更新时间、文件总数、模块总数
- 搜索框
- 文件类型筛选
- 左侧目录树
- 鼠标悬停文件提示
- 点击文件后的详情面板
- 文件依赖关系和模块依赖关系图
- AI 修改定位建议

`.project-map-cache.json` 用于缓存扫描结果，包含：

- 文件路径
- 文件 hash
- 文件摘要
- 文件类型
- 主要函数、类、组件
- import / export 信息
- 依赖关系
- 被引用关系
- 上次分析时间

## AI 使用建议

AI 在修改项目之前，应优先读取：

```text
PROJECT_STRUCTURE.md
PROJECT_MAP.html
```

当 AI 新增、删除、移动、重命名文件，或修改了会影响依赖关系的文件后，必须重新运行：

```bash
python project-visual-map-manager/scripts/update_project_map.py --root .
```

如果不确定应该修改哪个文件，优先从以下信息定位：

- `PROJECT_STRUCTURE.md` 的核心模块说明
- `PROJECT_MAP.html` 的文件详情面板
- 文件的依赖和被引用关系
- AI 修改定位建议

## 默认忽略内容

默认会忽略常见构建产物、依赖目录和缓存文件，例如：

- `.git`
- `node_modules`
- `dist`
- `build`
- `coverage`
- `.next`
- `.nuxt`
- `.vite`
- `target`
- `__pycache__`
- `.venv`
- `.idea`
- `.vscode`
- `package-lock.json`
- `pnpm-lock.yaml`
- `yarn.lock`
- `*.log`

## 示例

生成后的 HTML 页面是一个紧凑的开发者地图：顶部显示项目统计信息，左侧是可搜索目录树，右侧显示文件详情，下方或侧边展示依赖关系图。开发者可以通过搜索、筛选、悬停和点击快速理解项目结构。
