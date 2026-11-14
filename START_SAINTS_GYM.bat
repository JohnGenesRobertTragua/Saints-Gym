@echo off
setlocal
cd /d "%~dp0"
if not exist ".env" (
    echo ERROR: .env is missing.
    echo Copy .env.example to .env and configure the required credentials first.
    pause
    exit /b 1
)
if not exist ".venv\Scripts\python.exe" (
    echo ERROR: Python environment is missing. Run INSTALL_DEPENDENCIES.bat first.
    pause
    exit /b 1
)
".venv\Scripts\python.exe" run_server.py
pause
