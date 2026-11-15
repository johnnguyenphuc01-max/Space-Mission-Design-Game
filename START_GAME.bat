@echo off
setlocal
cd /d "%~dp0"
if not exist ".venv\Scripts\python.exe" (
    py -3.12 -m venv .venv
    if errorlevel 1 goto error
    .venv\Scripts\python.exe -m pip install -r requirements.txt
    if errorlevel 1 goto error
)
.venv\Scripts\python.exe main.py
if errorlevel 1 goto error
exit /b 0
:error
echo.
echo Startup failed. Check the message above. Python 3.12 is required.
echo To repair dependencies: .venv\Scripts\python.exe -m pip install -r requirements.txt
pause
exit /b 1
