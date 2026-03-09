param(
    [switch]$SkipInstall,
    [Parameter(ValueFromRemainingArguments = $true)]
    [string[]]$OpenPcbArgs
)

$ErrorActionPreference = "Stop"

$repoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
Push-Location $repoRoot

try {
    $candidates = @()
    if ($env:OPENPCB_PYTHON) { $candidates += $env:OPENPCB_PYTHON }
    $candidates += @("python", "d:\\anaconda3\\python.exe", "py -3")

    $pythonCmd = $null
    foreach ($cand in $candidates) {
        try {
            & $cand -c "import typer" 2>$null
            if ($LASTEXITCODE -eq 0) {
                $pythonCmd = $cand
                break
            }
        }
        catch {
            # keep searching
        }
    }
    if (-not $pythonCmd) {
        throw "No usable Python interpreter found (requires typer). Set OPENPCB_PYTHON explicitly."
    }

    Write-Host "[openpcb-local] Repo root: $repoRoot"
    Write-Host "[openpcb-local] Python: $pythonCmd"

    if (-not $SkipInstall) {
        try {
            & $pythonCmd -m pip install -e . | Out-Host
        }
        catch {
            Write-Warning "[openpcb-local] pip install failed; continue with current environment."
        }
    }

    Write-Host "[openpcb-local] Runtime info:"
    & $pythonCmd -c "import openpcb,sys;print('python=',sys.executable);print('openpcb=',openpcb.__file__);print('version=',openpcb.__version__)" | Out-Host

    if ($OpenPcbArgs.Count -eq 0) {
        & $pythonCmd -m openpcb --help
    }
    else {
        & $pythonCmd -m openpcb @OpenPcbArgs
    }
}
finally {
    Pop-Location
}
