# setup-observability.ps1
# Creates the full observability project folder and file structure
# Run from wherever you want the project to live, e.g.:
#   cd C:\Dev
#   .\setup-observability.ps1

$root = "observability"

# ── Directories ──────────────────────────────────────────────────────────────
$dirs = @(
    "$root\logging"
    "$root\error_tracking"
    "$root\tracing"
)

foreach ($dir in $dirs) {
    New-Item -ItemType Directory -Path $dir -Force | Out-Null
}

# ── Files ────────────────────────────────────────────────────────────────────
$files = @(
    # Root
    "$root\requirements.txt"
    "$root\integration_demo.py"
    "$root\README.md"

    # Path 1 — Structlog (logging/)
    "$root\logging\__init__.py"
    "$root\logging\config.py"
    "$root\logging\processors.py"
    "$root\logging\demo.py"

    # Path 2 — Sentry SDK (error_tracking/)
    "$root\error_tracking\__init__.py"
    "$root\error_tracking\config.py"
    "$root\error_tracking\breadcrumbs.py"
    "$root\error_tracking\context.py"
    "$root\error_tracking\cli.py"
    "$root\error_tracking\demo.py"

    # Path 3 — OpenTelemetry (tracing/)
    "$root\tracing\__init__.py"
    "$root\tracing\provider.py"
    "$root\tracing\spans.py"
    "$root\tracing\propagation.py"
    "$root\tracing\sampling.py"
    "$root\tracing\log_correlation.py"
    "$root\tracing\cli.py"
    "$root\tracing\demo.py"
)

foreach ($file in $files) {
    if (-not (Test-Path $file)) {
        New-Item -ItemType File -Path $file -Force | Out-Null
    }
}

# ── Summary ──────────────────────────────────────────────────────────────────
Write-Host ""
Write-Host "  Observability project scaffolded:" -ForegroundColor Green
Write-Host ""
Get-ChildItem -Path $root -Recurse | ForEach-Object {
    $indent = "  " * ($_.FullName.Split([IO.Path]::DirectorySeparatorChar).Count - `
              (Resolve-Path $root).Path.Split([IO.Path]::DirectorySeparatorChar).Count)
    $icon = if ($_.PSIsContainer) { "[DIR] " } else { "      " }
    Write-Host ("  " + $indent + $icon + $_.Name)
}
Write-Host ""
Write-Host "  Done. All folders and placeholder files created." -ForegroundColor Green
Write-Host ""
