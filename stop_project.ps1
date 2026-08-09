# =====================================================
# News Intelligence Platform — Graceful Shutdown
# =====================================================

$ErrorActionPreference = "Continue"
$ProjectRoot = $PSScriptRoot
Set-Location $ProjectRoot

$VenvPython = Join-Path $ProjectRoot ".venv\Scripts\python.exe"
if (-not (Test-Path $VenvPython)) {
    $VenvPython = "C:\Users\Asus\AppData\Local\Programs\Python\Python312\python.exe"
}
if (-not (Test-Path $VenvPython)) {
    $VenvPython = (Get-Command python).Source
}

Write-Host "============================================================" -ForegroundColor Yellow
Write-Host "STOPPING NEWS INTELLIGENCE PLATFORM DEMO" -ForegroundColor Yellow
Write-Host "============================================================" -ForegroundColor Yellow

& "$VenvPython" stop_daemons.py

# Force stop any leftover processes bound to API port 8000 or Dashboard port 8501
$port8000Proc = Get-NetTCPConnection -LocalPort 8000 -ErrorAction SilentlyContinue | Select-Object -ExpandProperty OwningProcess -Unique
foreach ($p in $port8000Proc) {
    if ($p -and $p -gt 0) {
        Stop-Process -Id $p -Force -ErrorAction SilentlyContinue
    }
}
$port8501Proc = Get-NetTCPConnection -LocalPort 8501 -ErrorAction SilentlyContinue | Select-Object -ExpandProperty OwningProcess -Unique
foreach ($p in $port8501Proc) {
    if ($p -and $p -gt 0) {
        Stop-Process -Id $p -Force -ErrorAction SilentlyContinue
    }
}

Write-Host "`n============================================================" -ForegroundColor Yellow
Write-Host "ALL PLATFORM SERVICES STOPPED CLEANLY" -ForegroundColor Yellow
Write-Host "============================================================" -ForegroundColor Yellow
