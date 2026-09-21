$ErrorActionPreference = "Stop"

$projectRoot = Split-Path -Parent $PSScriptRoot
$venvPath = Join-Path $projectRoot ".venv"
$pythonPath = Join-Path $venvPath "Scripts\python.exe"

if (-not (Test-Path -LiteralPath $pythonPath)) {
    Write-Host "Erzeuge virtuelle Umgebung mit Python 3.14 ..."
    & py -3.14 -m venv $venvPath
    if ($LASTEXITCODE -ne 0) {
        throw "Python 3.14 konnte nicht über den py-Launcher gestartet werden."
    }
}

Write-Host "Installiere Projektabhaengigkeiten ..."
& $pythonPath -m pip install --upgrade pip
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

& $pythonPath -m pip install -r (Join-Path $projectRoot "requirements-dev.txt")
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

Write-Host "Pruefe Umgebung ..."
& $pythonPath (Join-Path $projectRoot "scripts\doctor.py")
exit $LASTEXITCODE
