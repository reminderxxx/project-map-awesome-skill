[CmdletBinding()]
param(
    [string]$Root = (Get-Location).Path,
    [ValidateSet("zh", "en", "auto")]
    [string]$Lang = "auto",
    [int]$MaxDepth = 0,
    [switch]$NoOpen
)

$ErrorActionPreference = "Stop"

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$scriptPath = Join-Path $scriptDir "scripts\update_project_map.py"

if (-not (Get-Command python -ErrorAction SilentlyContinue)) {
    Write-Error "[project-map] Python was not found. Install Python or add it to PATH."
}

if (-not (Test-Path -LiteralPath $scriptPath)) {
    Write-Error "[project-map] Cannot find update_project_map.py at $scriptPath."
}

$argsList = @($scriptPath, "--root", $Root, "--lang", $Lang)
if ($MaxDepth -gt 0) {
    $argsList += @("--max-depth", [string]$MaxDepth)
}
if (-not $NoOpen) {
    $argsList += "--open"
}

Write-Host "[project-map] Target project: $Root"
python @argsList
