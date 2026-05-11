$ScriptRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
Push-Location $ScriptRoot
try {
    $env:SKIP_VECTORS='1'
    $env:SKIP_RECOMMENDER='1'
    $env:FLASK_DEBUG='1'
    $env:FLASK_RELOADER='0'
    python app.py
} finally {
    Pop-Location
}
