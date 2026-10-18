@echo off
setlocal
set "PYTHONUTF8=1"
cd /d "%~dp0"
if not exist ".venv\Scripts\python.exe" (
  echo Run Install HWI4U.cmd first.
  pause
  exit /b 1
)
".venv\Scripts\python.exe" desktop_start.py 
if errorlevel 1 pause
