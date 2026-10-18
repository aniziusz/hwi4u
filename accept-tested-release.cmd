@echo off
cd /d "%~dp0"
py -3 run_desktop.py promote-test --gui %*
