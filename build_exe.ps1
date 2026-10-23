# Builds dist\DownLSort.exe (single-file, no console window).
# Usage: powershell -ExecutionPolicy Bypass -File build_exe.ps1

Set-Location -Path $PSScriptRoot

# ---------------------------------------------------------------------------
# Locate PyInstaller: PATH first, then common user-install locations,
# then fall back to `python -m PyInstaller`.
# ---------------------------------------------------------------------------
$pyi = $null
$cmd = Get-Command pyinstaller -ErrorAction SilentlyContinue
if ($cmd -and $cmd.CommandType -eq "Application") { $pyi = $cmd.Source }

if (-not $pyi) {
    $candidates = @(
        (Join-Path $env:APPDATA "Python\Python314\Scripts\pyinstaller.exe"),
        (Join-Path $env:LOCALAPPDATA "Programs\Python\Python314\Scripts\pyinstaller.exe"),
        (Join-Path $env:LOCALAPPDATA "Programs\Python\Python312\Scripts\pyinstaller.exe")
    )
    foreach ($c in $candidates) { if (Test-Path $c) { $pyi = $c; break } }
}

# ---------------------------------------------------------------------------
# A running copy locks the output file; stale EXE blocks the rebuild.
# ---------------------------------------------------------------------------
Stop-Process -Name DownLSort -ErrorAction SilentlyContinue
Start-Sleep -Milliseconds 300

$exe = Join-Path $PSScriptRoot "dist\DownLSort.exe"
if (Test-Path $exe) {
    try { Remove-Item $exe -Force } catch {
        Write-Host "Could not delete the old EXE - close it and re-run."
        exit 1
    }
}

# ---------------------------------------------------------------------------
# Build. PyInstaller logs to stderr, so do not use $ErrorActionPreference="Stop".
# ---------------------------------------------------------------------------
$args = @(
    "--name", "DownLSort",
    "--windowed",
    "--onefile",
    "--icon", "src\downlsort\assets\downlsort-logo.ico",
    "--collect-all", "customtkinter",
    "--add-data", "src\downlsort\assets;downlsort\assets",
    "-p", "src",
    "src\downlsort\main.py"
)

if ($pyi) {
    & $pyi @args
} else {
    python -m PyInstaller @args
}

if ($LASTEXITCODE -ne 0 -or -not (Test-Path $exe)) {
    Write-Host "Build failed (exit $LASTEXITCODE)."
    exit 1
}

$size = [math]::Round((Get-Item $exe).Length / 1MB, 1)
Write-Host ""
Write-Host "Built: $exe ($size MB)"
