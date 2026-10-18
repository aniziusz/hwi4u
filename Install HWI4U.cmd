@echo off
setlocal
set "PYTHONUTF8=1"
cd /d "%~dp0"
py -3.14 install_desktop.py
if errorlevel 1 (
  echo Install Python 3.14 from python.org if the Python launcher is missing.
  pause
)
