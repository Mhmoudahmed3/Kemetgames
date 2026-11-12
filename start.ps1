$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $Root

$VenvPython = Join-Path $Root ".venv\Scripts\python.exe"
if (-not (Test-Path $VenvPython)) {
    Write-Host "[BLACKOUT ARCADE] Creating virtual environment..." -ForegroundColor Yellow
    $Created = $false
    foreach ($PyVer in @("-3.14", "-3.13", "-3.15")) {
        try {
            & py $PyVer -m venv ".venv" 2>$null
            if ($LASTEXITCODE -eq 0 -and (Test-Path $VenvPython)) {
                $Created = $true
                break
            }
        } catch {}
    }
    if (-not $Created) {
        python -m venv ".venv"
    }
    & $VenvPython -m pip install --upgrade pip
    & $VenvPython -m pip install -r "requirements.txt"
}

$Port = if ($env:PORT) { $env:PORT } else { "8000" }
$HostAddr = if ($env:HOST) { $env:HOST } else { "0.0.0.0" }
Write-Host "[BLACKOUT ARCADE] Launching server at http://localhost:$Port" -ForegroundColor Green
& $VenvPython -m uvicorn backend.main:app --host $HostAddr --port $Port

