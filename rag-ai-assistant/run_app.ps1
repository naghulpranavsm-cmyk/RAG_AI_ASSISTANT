param(
    [string]$PythonCommand = "py -3.11"
)

$ErrorActionPreference = "Stop"

if (-not (Test-Path ".venv")) {
    Write-Host "Creating virtual environment with $PythonCommand..."
    Invoke-Expression "$PythonCommand -m venv .venv"
}

Write-Host "Activating virtual environment..."
& ".\.venv\Scripts\Activate.ps1"

Write-Host "Installing dependencies..."
python -m pip install --upgrade pip
python -m pip install -r requirements.txt

Write-Host "Starting Streamlit..."
python -m streamlit run streamlit_app.py
