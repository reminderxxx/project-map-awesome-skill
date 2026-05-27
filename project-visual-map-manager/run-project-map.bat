@echo off
setlocal

set "SCRIPT_DIR=%~dp0"
set "PROJECT_ROOT=%CD%"
set "SCRIPT_PATH=%SCRIPT_DIR%scripts\update_project_map.py"

where python >nul 2>nul
if errorlevel 1 (
  echo [project-map] Python was not found.
  echo Install Python or add it to PATH, then run this file again.
  pause
  exit /b 1
)

if not exist "%SCRIPT_PATH%" (
  echo [project-map] Cannot find update_project_map.py:
  echo %SCRIPT_PATH%
  echo Make sure this file is inside the project-visual-map-manager folder.
  pause
  exit /b 1
)

echo [project-map] Target project: %PROJECT_ROOT%
python "%SCRIPT_PATH%" --root "%PROJECT_ROOT%" --lang auto --open
if errorlevel 1 (
  echo [project-map] Failed to generate project map.
  pause
  exit /b 1
)

echo [project-map] Done.
pause
