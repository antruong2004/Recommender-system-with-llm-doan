$ScriptRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
Push-Location $ScriptRoot
try {
    $env:SKIP_VECTORS='0'
    $env:SKIP_RECOMMENDER='0'
    $env:FLASK_DEBUG='1'
    $env:FLASK_RELOADER='1'
    python app.py
} finally {
    Pop-Location
}
