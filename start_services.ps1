# start_services.ps1
# News Intelligence Platform - Service Startup & Status Check

$ErrorActionPreference = "Continue"
$ProjectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path

Write-Host ""
Write-Host "=======================================================" -ForegroundColor Cyan
Write-Host "  NEWS INTELLIGENCE PLATFORM - SERVICE STARTUP" -ForegroundColor Cyan
Write-Host "=======================================================" -ForegroundColor Cyan
Write-Host ""

# ----------------------------------------------------------
# Step 1: Check Docker
# ----------------------------------------------------------
Write-Host "[1/4] Checking Docker..." -ForegroundColor Yellow
$dockerAvailable = $false
$dockerOut = & docker --version 2>&1
if ($LASTEXITCODE -eq 0) {
    Write-Host "  [OK] Docker: $dockerOut" -ForegroundColor Green
    $dockerAvailable = $true
} else {
    Write-Host "  [WARN] Docker not available. Skipping ES + Kafka." -ForegroundColor Yellow
}

# ----------------------------------------------------------
# Step 2: Start Elasticsearch + Kafka (if Docker available)
# ----------------------------------------------------------
if ($dockerAvailable) {
    Write-Host ""
    Write-Host "[2/4] Starting Elasticsearch + Kafka via docker-compose..." -ForegroundColor Yellow
    Push-Location "$ProjectRoot\docker"
    & docker-compose up -d
    Pop-Location

    Write-Host ""
    Write-Host "  Waiting for Elasticsearch health check..." -ForegroundColor Yellow
    $esReady = $false
    for ($i = 1; $i -le 20; $i++) {
        try {
            $r = Invoke-WebRequest -Uri "http://localhost:9200/_cluster/health" -UseBasicParsing -TimeoutSec 3 -ErrorAction SilentlyContinue
            if ($r.StatusCode -eq 200) {
                Write-Host "  [OK] Elasticsearch healthy (attempt $i)" -ForegroundColor Green
                $esReady = $true
                break
            }
        } catch {}
        Write-Host "  Still waiting... ($i/20)" -ForegroundColor Gray
        Start-Sleep -Seconds 3
    }
    if (-not $esReady) {
        Write-Host "  [WARN] ES not healthy after 60s. Continuing." -ForegroundColor Yellow
    }
} else {
    Write-Host "[2/4] Docker not found - skipping ES + Kafka startup." -ForegroundColor Yellow
}

# ----------------------------------------------------------
# Step 3: Start FastAPI
# ----------------------------------------------------------
Write-Host ""
Write-Host "[3/4] Starting FastAPI (port 8000)..." -ForegroundColor Yellow
$apiProcess = Start-Process python -ArgumentList "run_api.py" -WorkingDirectory $ProjectRoot -PassThru -WindowStyle Normal
Write-Host "  [OK] FastAPI started (PID: $($apiProcess.Id))" -ForegroundColor Green
Start-Sleep -Seconds 3

# ----------------------------------------------------------
# Step 4: Service Status Report
# Write Python scripts to temp files to avoid PS quoting issues
# ----------------------------------------------------------
Write-Host ""
Write-Host "[4/4] Checking all services..." -ForegroundColor Yellow

# Write mongo check script
$mongoTmp = "$env:TEMP\check_mongo_svc.py"
$mongoCode = "from pymongo import MongoClient`nc = MongoClient('mongodb://127.0.0.1:27017', serverSelectionTimeoutMS=2000)`nc.server_info()`nprint('OK')"
Set-Content -Path $mongoTmp -Value $mongoCode -Encoding UTF8

# Write kafka check script
$kafkaTmp = "$env:TEMP\check_kafka_svc.py"
$kafkaCode = "from kafka import KafkaProducer`np = KafkaProducer(bootstrap_servers='127.0.0.1:9092', request_timeout_ms=2000)`np.close()`nprint('OK')"
Set-Content -Path $kafkaTmp -Value $kafkaCode -Encoding UTF8

Write-Host ""
Write-Host "=======================================================" -ForegroundColor Cyan
Write-Host "  SERVICE STATUS REPORT" -ForegroundColor Cyan
Write-Host "=======================================================" -ForegroundColor Cyan

# MongoDB check
try {
    $mongoOut = & python $mongoTmp 2>&1
    if ("$mongoOut" -match "OK") {
        Write-Host "  MongoDB (27017)      : [OK] ONLINE" -ForegroundColor Green
    } else {
        Write-Host "  MongoDB (27017)      : [FAIL] OFFLINE" -ForegroundColor Red
    }
} catch {
    Write-Host "  MongoDB (27017)      : [FAIL] OFFLINE" -ForegroundColor Red
}

# Elasticsearch check
try {
    $esOut = Invoke-WebRequest -Uri "http://localhost:9200" -UseBasicParsing -TimeoutSec 2 -ErrorAction Stop
    if ($esOut.StatusCode -eq 200) {
        Write-Host "  Elasticsearch (9200) : [OK] ONLINE" -ForegroundColor Green
    } else {
        Write-Host "  Elasticsearch (9200) : [WARN] OFFLINE (Mongo fallback)" -ForegroundColor Yellow
    }
} catch {
    Write-Host "  Elasticsearch (9200) : [WARN] OFFLINE (Mongo fallback)" -ForegroundColor Yellow
}

# Kafka check
try {
    $kafkaOut = & python $kafkaTmp 2>&1
    if ("$kafkaOut" -match "OK") {
        Write-Host "  Kafka (9092)         : [OK] ONLINE" -ForegroundColor Green
    } else {
        Write-Host "  Kafka (9092)         : [WARN] OFFLINE (Mongo mode)" -ForegroundColor Yellow
    }
} catch {
    Write-Host "  Kafka (9092)         : [WARN] OFFLINE (Mongo mode)" -ForegroundColor Yellow
}

# Cleanup temp files
Remove-Item $mongoTmp -ErrorAction SilentlyContinue
Remove-Item $kafkaTmp -ErrorAction SilentlyContinue

# FastAPI check
Start-Sleep -Seconds 2
try {
    $apiOut = Invoke-WebRequest -Uri "http://localhost:8000/health" -UseBasicParsing -TimeoutSec 3 -ErrorAction Stop
    if ($apiOut.StatusCode -eq 200) {
        Write-Host "  FastAPI (8000)       : [OK] ONLINE" -ForegroundColor Green
    } else {
        Write-Host "  FastAPI (8000)       : [WARN] Starting..." -ForegroundColor Yellow
    }
} catch {
    Write-Host "  FastAPI (8000)       : [WARN] Starting..." -ForegroundColor Yellow
}

# Dashboard check
try {
    $dashOut = Invoke-WebRequest -Uri "http://localhost:8501" -UseBasicParsing -TimeoutSec 2 -ErrorAction Stop
    if ($dashOut.StatusCode -eq 200) {
        Write-Host "  Streamlit (8501)     : [OK] ONLINE" -ForegroundColor Green
    } else {
        Write-Host "  Streamlit (8501)     : [WARN] Not running" -ForegroundColor Yellow
    }
} catch {
    Write-Host "  Streamlit (8501)     : [WARN] Not running - run: python run_dashboard.py" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "=======================================================" -ForegroundColor Cyan
Write-Host "  Dashboard : http://localhost:8501" -ForegroundColor White
Write-Host "  API Docs  : http://localhost:8000/docs" -ForegroundColor White
Write-Host "  Health    : http://localhost:8000/health" -ForegroundColor White
Write-Host ""
Write-Host "  Pilot     : python historical/pilot_runner.py --limit 100" -ForegroundColor Cyan
Write-Host "  Tests     : python run_all_tests.py" -ForegroundColor Cyan
Write-Host "=======================================================" -ForegroundColor Cyan
Write-Host ""
