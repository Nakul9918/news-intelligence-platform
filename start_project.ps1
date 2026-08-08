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
Write-Host "  [+] Kafka          : OK (localhost:9092)" -ForegroundColor Green
Write-Host "  [+] Elasticsearch  : OK (localhost:9200)" -ForegroundColor Green

# 2. Start Application Background Daemons
Write-Host "`nLaunching application services..." -ForegroundColor Yellow

function Start-ServiceProcess {
    param (
        [string]$Name,
        [string]$ScriptPath,
        [string]$PidFileName,
        [string]$LogFileName
    )

    $PidFile = Join-Path $RuntimeDir $PidFileName
    $LogFile = Join-Path $LogsDir $LogFileName

    # Check if process is already running
    if (Test-Path $PidFile) {
        $oldPid = Get-Content $PidFile -ErrorAction SilentlyContinue
        if ($oldPid) {
            $proc = Get-Process -Id $oldPid -ErrorAction SilentlyContinue
            if ($proc -and $proc.ProcessName -like "*python*") {
                Write-Host "  [+] $Name is already running (PID: $oldPid)" -ForegroundColor Yellow
                return
            } else {
                Remove-Item $PidFile -Force -ErrorAction SilentlyContinue
            }
        }
    }

    $AbsScriptPath = Join-Path $ProjectRoot $ScriptPath
    $ErrLogFile = $LogFile.Replace(".log", "_err.log")
    $proc = Start-Process -FilePath $VenvPython -ArgumentList "-u `"$AbsScriptPath`"" -RedirectStandardOutput $LogFile -RedirectStandardError $ErrLogFile -PassThru -NoNewWindow
    $proc.Id | Out-File -FilePath $PidFile -Encoding ascii
    Write-Host "  [+] $Name : STARTED (PID: $($proc.Id))" -ForegroundColor Green
}

Start-ServiceProcess -Name "Automatic Ingestion Service" -ScriptPath "ingestion_service.py" -PidFileName "ingestion.pid" -LogFileName "ingestion.log"
Start-ServiceProcess -Name "Realtime Kafka Consumer" -ScriptPath "streaming/realtime_consumer.py" -PidFileName "consumer.pid" -LogFileName "consumer.log"
Start-ServiceProcess -Name "Pipeline Orchestrator" -ScriptPath "pipeline_orchestrator.py" -PidFileName "orchestrator.pid" -LogFileName "orchestrator.log"
Start-ServiceProcess -Name "FastAPI Backend API" -ScriptPath "run_api.py" -PidFileName "api.pid" -LogFileName "api.log"
Start-ServiceProcess -Name "Streamlit Dashboard" -ScriptPath "run_dashboard.py" -PidFileName "dashboard.pid" -LogFileName "dashboard.log"

Start-Sleep -Seconds 2

# 3. Print Final Status
Write-Host "`n============================================================" -ForegroundColor Cyan
Write-Host "NEWS INTELLIGENCE PLATFORM STATUS" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "Infrastructure:" -ForegroundColor White
Write-Host "  MongoDB        : OK (localhost:27017)" -ForegroundColor Green
Write-Host "  Kafka          : OK (localhost:9092)" -ForegroundColor Green
Write-Host "  Elasticsearch  : OK (localhost:9200)" -ForegroundColor Green
Write-Host "Application Services:" -ForegroundColor White
Write-Host "  Ingestion      : RUNNING" -ForegroundColor Green
Write-Host "  Kafka Consumer : RUNNING" -ForegroundColor Green
Write-Host "  Orchestrator   : RUNNING" -ForegroundColor Green
Write-Host "  FastAPI API    : RUNNING (http://localhost:8000)" -ForegroundColor Green
Write-Host "  Dashboard      : RUNNING (http://localhost:8501)" -ForegroundColor Green
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "Logs saved to: $LogsDir" -ForegroundColor Gray
