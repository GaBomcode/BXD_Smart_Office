$ErrorActionPreference = "Stop"

$paths = @("build", "dist", "__pycache__")
foreach ($path in $paths) {
    if (Test-Path $path) {
        Remove-Item -LiteralPath $path -Recurse -Force
    }
}

Get-ChildItem -Recurse -Directory -Filter "__pycache__" |
    Where-Object { $_.FullName -notmatch "\\.venv\\|\\.codex_test_deps\\" } |
    ForEach-Object { Remove-Item -LiteralPath $_.FullName -Recurse -Force }

Write-Host "Build artifacts cleaned."
