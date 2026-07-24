param(
    [switch]$SkipAndroid,
    [switch]$SkipWeb
)

$ErrorActionPreference = "Stop"
$repo = Split-Path -Parent $PSScriptRoot
Set-Location $repo

python -m compileall -q api ml graph
python scripts\generate_endpoint_inventory.py
python -m pytest -q
python scripts\measure_performance.py

if (-not $SkipWeb) {
    Push-Location web
    try {
        npm run build
    } finally {
        Pop-Location
    }
}

if (-not $SkipAndroid) {
    if (-not $env:ANDROID_HOME) {
        $env:ANDROID_HOME = Join-Path $env:LOCALAPPDATA "Android\Sdk"
    }
    Push-Location fusion-reference-bank
    try {
        .\gradlew.bat testDebugUnitTest assembleDebug assembleRelease bundleRelease `
            --no-daemon --console=plain --max-workers=2 `
            '-Dkotlin.compiler.execution.strategy=in-process'
    } finally {
        Pop-Location
    }
}

Write-Output "PRODUCTION_VALIDATION_COMPLETED"
