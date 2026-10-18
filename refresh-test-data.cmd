@echo off
setlocal
set "PYTHONUTF8=1"
cd /d "%~dp0"
if exist ".venv\Scripts\python.exe" (
  ".venv\Scripts\python.exe" run_desktop.py refresh-test --gui %*
) else (
  py -3.14 run_desktop.py refresh-test --gui %*
)
