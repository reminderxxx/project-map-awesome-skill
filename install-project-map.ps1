[CmdletBinding()]
param(
    [string]$RepoUrl = "https://github.com/reminderxxx/project-map-awesome-skill.git",
    [string]$TargetRoot = (Get-Location).Path,
    [switch]$Force,
    [switch]$NoRun,
    [switch]$NoOpen
)

$ErrorActionPreference = "Stop"

function Write-Step {
    param([string]$Message)
    Write-Host "[project-map-install] $Message"
}

if (-not (Get-Command git -ErrorAction SilentlyContinue)) {
    Write-Error "[project-map-install] Git was not found. Install Git or add it to PATH."
}

if (-not (Test-Path -LiteralPath $TargetRoot)) {
    New-Item -ItemType Directory -Path $TargetRoot | Out-Null
}

$targetRootPath = (Resolve-Path -LiteralPath $TargetRoot).Path
$destination = Join-Path $targetRootPath "project-visual-map-manager"

if ((Test-Path -LiteralPath $destination) -and -not $Force) {
    Write-Error "[project-map-install] $destination already exists. Re-run with -Force to replace it."
}

$tempRoot = Join-Path ([System.IO.Path]::GetTempPath()) ("project-map-skill-" + [System.Guid]::NewGuid().ToString("N"))

try {
    Write-Step "Cloning $RepoUrl"
    git clone --depth 1 $RepoUrl $tempRoot | Out-Host

    $source = Join-Path $tempRoot "project-visual-map-manager"
    if (-not (Test-Path -LiteralPath $source)) {
        Write-Error "[project-map-install] The cloned repository does not contain project-visual-map-manager/."
    }

    if (Test-Path -LiteralPath $destination) {
        Write-Step "Replacing existing project-visual-map-manager directory"
        Remove-Item -LiteralPath $destination -Recurse -Force
    }

    Write-Step "Copying Skill into $targetRootPath"
    Copy-Item -LiteralPath $source -Destination $destination -Recurse

    if (-not $NoRun) {
        $runner = Join-Path $destination "run-project-map.ps1"
        Write-Step "Generating project map"
        if (Test-Path -LiteralPath $runner) {
            $runnerArgs = @("-Root", $targetRootPath, "-Lang", "auto")
            if ($NoOpen) {
                $runnerArgs += "-NoOpen"
            }
            & $runner @runnerArgs
        }
        else {
            $pythonScript = Join-Path $destination "scripts\update_project_map.py"
            if (-not (Test-Path -LiteralPath $pythonScript)) {
                Write-Error "[project-map-install] Cannot find scripts\update_project_map.py after installation."
            }
            if (-not (Get-Command python -ErrorAction SilentlyContinue)) {
                Write-Error "[project-map-install] Python was not found. Install Python or re-run with -NoRun."
            }
            python $pythonScript --root $targetRootPath --lang auto
        }
    }

    Write-Step "Done"
}
finally {
    if (Test-Path -LiteralPath $tempRoot) {
        Remove-Item -LiteralPath $tempRoot -Recurse -Force
    }
}
