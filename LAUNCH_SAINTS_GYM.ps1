$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $MyInvocation.MyCommand.Path
$python = Join-Path $root ".venv\Scripts\python.exe"
$serverScript = Join-Path $root "run_server.py"
$loadingPage = Join-Path $root "SAINTS_GYM_STARTING.html"
$serverProcess = $null
$startedServer = $false
$chromeProcess = $null

function Test-SaintsGymServer {
    $client = New-Object System.Net.Sockets.TcpClient
    try {
        $async = $client.BeginConnect("127.0.0.1", 5000, $null, $null)
        if ($async.AsyncWaitHandle.WaitOne(300)) {
            $client.EndConnect($async)
            return $true
        }
        return $false
    } catch { return $false }
    finally { $client.Close() }
}

try {
    if (-not (Test-Path $python)) { throw "Python environment is missing: $python" }
    if (-not (Test-Path $serverScript)) { throw "run_server.py is missing." }
    if (-not (Test-Path $loadingPage)) { throw "SAINTS_GYM_STARTING.html is missing." }

    $chrome = (Get-Command chrome.exe -ErrorAction SilentlyContinue).Source
    if (-not $chrome) {
        $candidates = @(
            (Join-Path $env:ProgramFiles "Google\Chrome\Application\chrome.exe"),
            (Join-Path ${env:ProgramFiles(x86)} "Google\Chrome\Application\chrome.exe"),
            (Join-Path $env:LOCALAPPDATA "Google\Chrome\Application\chrome.exe")
        )
        foreach ($candidate in $candidates) {
            if ($candidate -and (Test-Path $candidate)) { $chrome = $candidate; break }
        }
    }
    if (-not $chrome) { throw "Google Chrome could not be found." }

    # Open the Chrome app window first, so the user sees it immediately.
    $profile = Join-Path $env:LOCALAPPDATA "SaintsGymChromeProfile"
    $loadingUri = ([System.Uri]$loadingPage).AbsoluteUri
    $chromeArgs = @("--app=$loadingUri", ('--user-data-dir="' + $profile + '"'), "--no-first-run", "--disable-background-mode")
    $chromeProcess = Start-Process -FilePath $chrome -ArgumentList $chromeArgs -PassThru

    # Start the server only if it is not already running.
    if (-not (Test-SaintsGymServer)) {
        $serverProcess = Start-Process -FilePath $python -ArgumentList ('"' + $serverScript + '"') -WorkingDirectory $root -WindowStyle Hidden -PassThru
        $startedServer = $true
    }

    # Keep this launcher alive while the dedicated Saints Gym Chrome app window is open.
    Wait-Process -Id $chromeProcess.Id
}
catch {
    Add-Type -AssemblyName PresentationFramework -ErrorAction SilentlyContinue
    [System.Windows.MessageBox]::Show($_.Exception.Message, "Saints Gym Launcher") | Out-Null
}
finally {
    # Only stop a server instance started by this launcher.
    if ($startedServer -and $serverProcess -and -not $serverProcess.HasExited) {
        Stop-Process -Id $serverProcess.Id -Force -ErrorAction SilentlyContinue
    }
}
