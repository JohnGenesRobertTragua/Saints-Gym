@echo off
setlocal
cd /d "%~dp0"
echo Creating the Saints Gym Python environment if needed...
if not exist ".venv\Scripts\python.exe" (
    py -3 -m venv .venv
    if errorlevel 1 goto failed
)
echo Installing required packages...
".venv\Scripts\python.exe" -m pip install --upgrade pip
if errorlevel 1 goto failed
".venv\Scripts\python.exe" -m pip install -r requirements.txt
if errorlevel 1 goto failed
echo.
echo Dependencies installed. Next, configure .env using .env.example.
pause
exit /b 0
:failed
echo.
echo Setup failed. Confirm Python 3 is installed and internet access is available.
pause
exit /b 1
