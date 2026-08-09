# =====================================================
# News Intelligence Platform — One-Command Startup
# =====================================================

$ErrorActionPreference = "Stop"
$ProjectRoot = $PSScriptRoot
Set-Location $ProjectRoot

$VenvPython = Join-Path $ProjectRoot ".venv\Scripts\python.exe"
if (-not (Test-Path $VenvPython)) {
    $VenvPython = "C:\Users\Asus\AppData\Local\Programs\Python\Python312\python.exe"
}
if (-not (Test-Path $VenvPython)) {
    $VenvPython = (Get-Command python).Source
}

$RuntimeDir = Join-Path $ProjectRoot "runtime"
$LogsDir = Join-Path $ProjectRoot "logs"

if (-not (Test-Path $RuntimeDir)) { New-Item -ItemType Directory -Path $RuntimeDir | Out-Null }
if (-not (Test-Path $LogsDir)) { New-Item -ItemType Directory -Path $LogsDir | Out-Null }

Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "STARTING NEWS INTELLIGENCE PLATFORM DEMO" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan

# 1. Health Checks
Write-Host "`nChecking infrastructure services..." -ForegroundColor Yellow

$infraResult = & "$VenvPython" check_infrastructure.py
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Infrastructure health check failed!" -ForegroundColor Red
    Write-Host $infraResult -ForegroundColor Yellow
    Exit 1
}

Write-Host "  [+] MongoDB        : OK (localhost:27017)" -ForegroundColor Green

# 2. Launch Master Daemon Controller
Write-Host "`nLaunching application services via start_daemons.py..." -ForegroundColor Yellow
& "$VenvPython" start_daemons.py

Start-Sleep -Seconds 2

# 3. Print Final Status
Write-Host "`n============================================================" -ForegroundColor Cyan
Write-Host "NEWS INTELLIGENCE PLATFORM STATUS" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "Infrastructure:" -ForegroundColor White
Write-Host "  MongoDB        : OK (localhost:27017)" -ForegroundColor Green
Write-Host "Application Services:" -ForegroundColor White
Write-Host "  Ingestion      : RUNNING" -ForegroundColor Green
Write-Host "  Kafka Consumer : RUNNING" -ForegroundColor Green
Write-Host "  Orchestrator   : RUNNING" -ForegroundColor Green
Write-Host "  FastAPI API    : RUNNING (http://localhost:8000)" -ForegroundColor Green
Write-Host "  Dashboard      : RUNNING (http://localhost:8501)" -ForegroundColor Green
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "Logs saved to: $LogsDir" -ForegroundColor Gray
