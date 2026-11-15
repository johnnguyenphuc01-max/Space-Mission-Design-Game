@echo off
cd /d "%~dp0"
if not exist ".venv\Scripts\python.exe" (
  echo Run START_GAME.bat first to install the game.
  pause
  exit /b 1
)
.venv\Scripts\python.exe tools\build_windows.py
pause
