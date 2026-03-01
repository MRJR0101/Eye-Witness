<#
.SYNOPSIS
    Deploy the Observability Stack to C:\ThisIsAISandbox\Eye-Witness\observability
.DESCRIPTION
    Extracts the observability-stack.zip into the Eye-Witness project folder.
    Run this from the same directory where observability-stack.zip was downloaded.
.USAGE
    cd <download-folder>
    .\deploy-to-eye-witness.ps1
#>

$ErrorActionPreference = "Stop"
$target = "C:\ThisIsAISandbox\Eye-Witness"
$zipFile = Join-Path $PSScriptRoot "observability-stack.zip"

# Verify zip exists
if (-not (Test-Path $zipFile)) {
    # Try current directory
    $zipFile = Join-Path (Get-Location) "observability-stack.zip"
    if (-not (Test-Path $zipFile)) {
        Write-Error "observability-stack.zip not found. Place this script next to the zip file."
        exit 1
    }
}

# Create target if needed
if (-not (Test-Path $target)) {
    New-Item -ItemType Directory -Path $target -Force | Out-Null
    Write-Host "  Created: $target" -ForegroundColor Green
}

# Extract
Write-Host "`n  Deploying Observability Stack..." -ForegroundColor Cyan
Write-Host "  From: $zipFile"
Write-Host "  To:   $target`n"

Expand-Archive -Path $zipFile -DestinationPath $target -Force

# Verify
$files = Get-ChildItem -Path "$target\observability" -Recurse -File
Write-Host "  Deployed $($files.Count) files to $target\observability" -ForegroundColor Green

# Show structure
Write-Host "`n  Project structure:" -ForegroundColor Cyan
$dirs = @(
    "observability\logging",
    "observability\error_tracking",
    "observability\tracing"
)
foreach ($d in $dirs) {
    $full = Join-Path $target $d
    if (Test-Path $full) {
        $count = (Get-ChildItem $full -File | Where-Object { $_.Extension -eq ".py" }).Count
        Write-Host "    $d\ ($count .py files)"
    }
}
Write-Host "    observability\integration_demo.py"
Write-Host "    observability\requirements.txt"
Write-Host "    observability\README.md"

# Install dependencies prompt
Write-Host "`n  Next steps:" -ForegroundColor Yellow
Write-Host "    cd $target\observability"
Write-Host "    pip install -r requirements.txt"
Write-Host ""
Write-Host "  Run demos:" -ForegroundColor Yellow
Write-Host "    python -m observability.logging.demo"
Write-Host "    python -m observability.error_tracking.demo"
Write-Host "    python -m observability.tracing.demo"
Write-Host "    python -m observability.integration_demo"
Write-Host ""
