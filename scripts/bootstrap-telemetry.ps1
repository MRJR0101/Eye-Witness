<#
.SYNOPSIS
    Bootstrap OpenTelemetry auto-instrumentation packages for Eye-Witness.

.DESCRIPTION
    Follows the uv-OTel pattern from the New Relic guide:
      1. Install opentelemetry-distro + OTLP HTTP exporter
      2. Run opentelemetry-bootstrap to discover instrumentable libraries
      3. Output requirements to paste into pyproject.toml [telemetry] extra
      4. Sync with the telemetry extra

.USAGE
    cd C:\ThisIsAISandbox\Eye-Witness\observability
    .\scripts\bootstrap-telemetry.ps1
#>

$ErrorActionPreference = "Stop"
$projectRoot = Split-Path $PSScriptRoot -Parent

Write-Host ""
Write-Host "  Eye-Witness — OpenTelemetry Auto-Instrumentation Bootstrap" -ForegroundColor Cyan
Write-Host "  Following the uv-OTel + New Relic guide" -ForegroundColor Cyan
Write-Host ""

# Step 1: Install core OTel distro + OTLP HTTP exporter
Write-Host "  [1/4] Installing opentelemetry-distro + OTLP HTTP exporter..." -ForegroundColor Yellow
uv pip install opentelemetry-distro opentelemetry-exporter-otlp-proto-http
Write-Host "  Done." -ForegroundColor Green

# Step 2: Run bootstrap to discover instrumentable libraries
Write-Host ""
Write-Host "  [2/4] Running opentelemetry-bootstrap to discover instrumentations..." -ForegroundColor Yellow
$reqsFile = Join-Path $projectRoot "otel-reqs.txt"
uv run opentelemetry-bootstrap -a requirements | Out-File -FilePath $reqsFile -Encoding UTF8
Write-Host "  Wrote discovered packages to: $reqsFile" -ForegroundColor Green

# Step 3: Display discovered packages
Write-Host ""
Write-Host "  [3/4] Discovered instrumentation packages:" -ForegroundColor Yellow
$reqs = Get-Content $reqsFile
if ($reqs.Count -eq 0) {
    Write-Host "    (none discovered — your venv may not have instrumentable libraries yet)" -ForegroundColor DarkYellow
} else {
    foreach ($line in $reqs) {
        if ($line.Trim()) {
            Write-Host "    $($line.Trim())" -ForegroundColor White
        }
    }
}

# Step 4: Instructions
Write-Host ""
Write-Host "  [4/4] Next steps:" -ForegroundColor Yellow
Write-Host ""
Write-Host "  1. Copy the packages above into pyproject.toml under:" -ForegroundColor White
Write-Host "     [project.optional-dependencies]" -ForegroundColor DarkGray
Write-Host "     telemetry = [" -ForegroundColor DarkGray
Write-Host '         "opentelemetry-distro>=1.20.0",' -ForegroundColor DarkGray
Write-Host '         "opentelemetry-instrumentation>=1.20.0",' -ForegroundColor DarkGray
Write-Host '         # <paste discovered packages here>' -ForegroundColor DarkGray
Write-Host "     ]" -ForegroundColor DarkGray
Write-Host ""
Write-Host "  2. Sync with the telemetry extra:" -ForegroundColor White
Write-Host "     uv sync --extra telemetry" -ForegroundColor Cyan
Write-Host ""
Write-Host "  3. Run your app with auto-instrumentation:" -ForegroundColor White
Write-Host "     uv run --extra telemetry opentelemetry-instrument python -m your_app" -ForegroundColor Cyan
Write-Host ""
Write-Host "  4. Set up .env (copy .env.example and fill in NEW_RELIC_LICENSE_KEY):" -ForegroundColor White
Write-Host "     Copy-Item .env.example .env" -ForegroundColor Cyan
Write-Host ""
Write-Host "  Re-run this script after adding new dependencies to discover" -ForegroundColor DarkGray
Write-Host "  additional instrumentation packages." -ForegroundColor DarkGray
Write-Host ""
