# PowerShell CI runner: installs dev deps, runs pytest, regenerates grading artifacts
Set-StrictMode -Version Latest
$root = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location (Join-Path $root '..')

if (Test-Path requirements-dev.txt) {
    py -3 -m pip install -r requirements-dev.txt
}

py -3 -m pytest -q

py -3 scripts/prepare_grading.py
py -3 scripts/compile_results.py

Write-Host "CI checks passed."
