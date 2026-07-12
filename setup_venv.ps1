# Python virtual environment setup (Windows PowerShell)
# Usage: .\setup_venv.ps1

python --version
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt

Write-Host ""
Write-Host "Done. Activate in future sessions with: .\.venv\Scripts\Activate.ps1"
