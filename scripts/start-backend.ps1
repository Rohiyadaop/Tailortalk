# Start backend with the recommended Python 3.10/3.11 virtual environment
param(
    [string]$VenvPath = ".venv310",
    [string]$EnvFile = ".env"
)

if (Test-Path $VenvPath) {
    Write-Host "Activating venv: $VenvPath"
    & "$VenvPath\Scripts\Activate.ps1"
} elseif (Test-Path ".venv") {
    Write-Host "Activating .venv"
    & ".venv\Scripts\Activate.ps1"
} else {
    Write-Host "No venv found at $VenvPath or .venv. Create one with: py -3.10 -m venv $VenvPath"
    exit 1
}

# load .env into session
if (Test-Path $EnvFile) {
    Get-Content $EnvFile | ForEach-Object {
        if ($_ -match '^[\s#]') { return }
        $parts = $_ -split '=',2
        if ($parts.Count -eq 2) { Set-Item -Path Env:$($parts[0].Trim()) -Value $parts[1].Trim() }
    }
}

uvicorn backend.app.main:app --reload --host $env:UVICORN_HOST --port $env:UVICORN_PORT
