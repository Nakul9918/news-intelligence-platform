# =====================================================
# News Intelligence Platform — Graceful Shutdown
# =====================================================

$ErrorActionPreference = "Continue"
$ProjectRoot = $PSScriptRoot
Set-Location $ProjectRoot

$RuntimeDir = Join-Path $ProjectRoot "runtime"

Write-Host "============================================================" -ForegroundColor Yellow
Write-Host "STOPPING NEWS INTELLIGENCE PLATFORM DEMO" -ForegroundColor Yellow
Write-Host "============================================================" -ForegroundColor Yellow

function Stop-ServiceProcess {
    param (
        [string]$Name,
        [string]$PidFileName
    )

    $PidFile = Join-Path $RuntimeDir $PidFileName

    if (Test-Path $PidFile) {
        $servicePid = Get-Content $PidFile -ErrorAction SilentlyContinue
        if ($servicePid) {
            $proc = Get-Process -Id $servicePid -ErrorAction SilentlyContinue
            if ($proc) {
                Write-Host "Stopping $Name (PID: $servicePid)..." -ForegroundColor Yellow
                Stop-Process -Id $servicePid -Force -ErrorAction SilentlyContinue
                Write-Host "  [-] $Name stopped successfully." -ForegroundColor Green
            } else {
                Write-Host "  [-] $Name (PID: $servicePid) was not running." -ForegroundColor Gray
            }
        }
        Remove-Item $PidFile -Force -ErrorAction SilentlyContinue
    } else {
        Write-Host "  [-] No PID file found for $Name." -ForegroundColor Gray
    }
}

Stop-ServiceProcess -Name "Streamlit Dashboard" -PidFileName "dashboard.pid"
Stop-ServiceProcess -Name "FastAPI Backend API" -PidFileName "api.pid"
Stop-ServiceProcess -Name "Pipeline Orchestrator" -PidFileName "orchestrator.pid"
Stop-ServiceProcess -Name "Realtime Kafka Consumer" -PidFileName "consumer.pid"
Stop-ServiceProcess -Name "Automatic Ingestion Service" -PidFileName "ingestion.pid"

# Force stop any stale processes bound to API port 8000 or Dashboard port 8501
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
