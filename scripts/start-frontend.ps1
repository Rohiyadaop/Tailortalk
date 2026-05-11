# Start Streamlit frontend (assumes a venv with streamlit installed)
param(
    [string]$VenvPath = ".venv-frontend",
    [string]$EnvFile = ".env"
)

if (Test-Path $VenvPath) {
    Write-Host "Activating venv: $VenvPath"
    & "$VenvPath\Scripts\Activate.ps1"
} elseif (Test-Path ".venv") {
    Write-Host "Activating .venv"
    & ".venv\Scripts\Activate.ps1"
} else {
    Write-Host "No frontend venv found. Create one with: py -3.10 -m venv $VenvPath"
    exit 1
}

# load .env
if (Test-Path $EnvFile) {
    Get-Content $EnvFile | ForEach-Object {
        if ($_ -match '^[\s#]') { return }
        $parts = $_ -split '=',2
        if ($parts.Count -eq 2) { Set-Item -Path Env:$($parts[0].Trim()) -Value $parts[1].Trim() }
    }
}

streamlit run frontend/streamlit_app.py
