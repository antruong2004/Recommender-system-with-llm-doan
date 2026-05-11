[Console]::OutputEncoding = [System.Text.UTF8Encoding]::new()
$OutputEncoding = [Console]::OutputEncoding
$ScriptRoot = Split-Path -Parent $MyInvocation.MyCommand.Path

function Start-TechStore {
    param(
        [string]$ModeName,
        [string]$SkipVectors,
        [string]$SkipRecommender,
        [string]$Debug,
        [string]$Reloader
    )

    $env:SKIP_VECTORS = $SkipVectors
    $env:SKIP_RECOMMENDER = $SkipRecommender
    $env:FLASK_DEBUG = $Debug
    $env:FLASK_RELOADER = $Reloader

    Push-Location $ScriptRoot
    try {
        Write-Host "Dang chay $ModeName..." -ForegroundColor Green
        python app.py
    } finally {
        Pop-Location
    }
}

Write-Host "============================" -ForegroundColor Cyan
Write-Host "   MENU CHAY TECHSTORE" -ForegroundColor Cyan
Write-Host "============================" -ForegroundColor Cyan
Write-Host "1) Che do nhe        - nhanh nhat, khong tai vector/recommender"
Write-Host "2) Che do chat AI    - chat + tu van, nhe"
Write-Host "3) Che do semantic   - bat tim kiem vector"
Write-Host "4) Che do day du     - chay toan bo he thong"
Write-Host "5) Che do goi y      - chi recommender"
Write-Host ""
$choice = Read-Host "Chon che do (1-5)"

switch ($choice) {
    '1' { Start-TechStore -ModeName 'che do nhe' -SkipVectors '1' -SkipRecommender '1' -Debug '0' -Reloader '0' }
    '2' { Start-TechStore -ModeName 'che do chat AI' -SkipVectors '1' -SkipRecommender '1' -Debug '1' -Reloader '0' }
    '3' { Start-TechStore -ModeName 'che do semantic' -SkipVectors '0' -SkipRecommender '1' -Debug '0' -Reloader '0' }
    '4' { Start-TechStore -ModeName 'che do day du' -SkipVectors '0' -SkipRecommender '0' -Debug '1' -Reloader '1' }
    '5' { Start-TechStore -ModeName 'che do goi y' -SkipVectors '1' -SkipRecommender '0' -Debug '0' -Reloader '0' }
    Default { Write-Host "Lua chon khong hop le." -ForegroundColor Red }
}
