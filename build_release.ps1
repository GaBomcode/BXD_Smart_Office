param(
    [switch]$SkipOneFile,
    [switch]$SkipVerify
)

$ErrorActionPreference = "Stop"
$AppName = "BXD-Smart-Office"
$Python = if (Test-Path ".venv\Scripts\python.exe") { ".venv\Scripts\python.exe" } else { "python" }

PowerShell -NoProfile -ExecutionPolicy Bypass -File ".\clean_build.ps1"

& $Python -m PyInstaller --version | Out-Null

$CommonArgs = @(
    "--clean",
    "--noconfirm",
    "--name", $AppName,
    "--paths", ".",
    "--collect-all", "streamlit",
    "--add-data", "app;app",
    "--add-data", "core;core",
    "--add-data", "database;database",
    "--add-data", "models;models",
    "--add-data", "modules;modules",
    "--add-data", "repositories;repositories",
    "--add-data", "services;services",
    "--add-data", "templates;templates",
    "--add-data", "static;static",
    "release_launcher.py"
)

& $Python -m PyInstaller @CommonArgs --onedir

if (-not $SkipOneFile) {
    & $Python -m PyInstaller @CommonArgs --onefile
}

if (-not $SkipVerify) {
    & $Python ".\verify_release.py"
}

Write-Host "Release build completed."
