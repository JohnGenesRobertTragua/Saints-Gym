@echo off
setlocal
cd /d "%~dp0"

if not exist "%~dp0.env" (
    echo ERROR: .env is missing.
    echo Copy .env.example to .env and configure the required credentials first.
    pause
    exit /b 1
)

if not exist "%~dp0.venv\Scripts\python.exe" (
    echo ERROR: Python environment is missing.
    echo Run INSTALL_DEPENDENCIES.bat first.
    pause
    exit /b 1
)

REM If Saints Gym is already listening on port 5000, open it instead of starting another server.
powershell -NoProfile -ExecutionPolicy Bypass -Command "$c = New-Object System.Net.Sockets.TcpClient; try { $a = $c.BeginConnect('127.0.0.1',5000,$null,$null); if ($a.AsyncWaitHandle.WaitOne(500)) { $c.EndConnect($a); exit 0 } else { exit 1 } } catch { exit 1 } finally { $c.Close() }" >nul 2>&1
if not errorlevel 1 (
    start "" "http://127.0.0.1:5000"
    exit /b 0
)

REM Run the server in its own minimized console. Keep that window open while using Saints Gym.
start "Saints Gym Server - keep open" /min cmd /k "cd /d ""%~dp0"" && ""%~dp0.venv\Scripts\python.exe"" ""%~dp0run_server.py"""

echo Starting Saints Gym. Waiting for the server to respond...
powershell -NoProfile -ExecutionPolicy Bypass -Command "$deadline=(Get-Date).AddSeconds(30); do { try { $r=Invoke-WebRequest -UseBasicParsing 'http://127.0.0.1:5000/' -TimeoutSec 2; if ($r.StatusCode -ge 200) { exit 0 } } catch {}; Start-Sleep -Milliseconds 500 } while ((Get-Date) -lt $deadline); exit 1"
if errorlevel 1 (
    echo.
    echo ERROR: Saints Gym did not respond within 30 seconds.
    echo Check the minimized 'Saints Gym Server - keep open' window for errors.
    pause
    exit /b 1
)

start "" "http://127.0.0.1:5000"
exit /b 0
