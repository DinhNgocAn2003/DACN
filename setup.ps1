<#
setup.ps1 - Setup project development environment on Windows (PowerShell)

What it does:
- Checks for Python and Node/NPM on PATH and prints helpful hints if missing
- Creates a virtual environment at `./.venv` (project root)
- Upgrades pip/setuptools/wheel inside the venv
- Installs Python dependencies from `backend/requirements.txt` using the venv Python
- Runs `npm install` inside `frontend` to install frontend deps

Usage (PowerShell):
  .\setup.ps1

Note: If PowerShell's execution policy prevents running, you can run this file with:
  powershell -ExecutionPolicy Bypass -File .\setup.ps1
#>

Write-Host "Starting project setup..." -ForegroundColor Cyan

function Abort($msg) {
    Write-Host $msg -ForegroundColor Red
    exit 1
}

# Check Python
$pyCmd = Get-Command python -ErrorAction SilentlyContinue
if (-not $pyCmd) { Abort "Python not found on PATH. Please install Python 3.10+ from https://www.python.org/downloads/ and re-run the script." }

Write-Host "Python found:" -NoNewline; python --version

# Check pip
try { python -m pip --version | Out-Null } catch { Abort "pip not available for the discovered Python. Ensure pip is installed." }

# Check Node and npm
$nodeCmd = Get-Command node -ErrorAction SilentlyContinue
$npmCmd = Get-Command npm -ErrorAction SilentlyContinue
if (-not $nodeCmd -or -not $npmCmd) {
    Write-Host "Node.js or npm not found. Frontend `npm install` will be skipped. Install Node.js LTS from https://nodejs.org/ if you want frontend setup." -ForegroundColor Yellow
    $skipFrontend = $true
} else {
    Write-Host "Node and npm found:" -NoNewline; node --version; npm --version
    $skipFrontend = $false
}

# Create virtual environment
if (-not (Test-Path -Path .\.venv)) {
    Write-Host "Creating virtual environment at .\.venv" -ForegroundColor Cyan
    python -m venv .venv
} else {
    Write-Host "Virtual environment already exists at .\.venv" -ForegroundColor Green
}

$venvPython = Join-Path -Path (Resolve-Path .\.venv) -ChildPath "Scripts\python.exe"
if (-not (Test-Path $venvPython)) { Abort "venv python not found at $venvPython" }

Write-Host "Upgrading pip, setuptools, wheel in venv" -ForegroundColor Cyan
& $venvPython -m pip install --upgrade pip setuptools wheel

# Install backend requirements
$backendReq = "backend\requirements.txt"
if (-not (Test-Path $backendReq)) { Abort "Could not find $backendReq" }

Write-Host "Installing backend Python packages from $backendReq" -ForegroundColor Cyan
& $venvPython -m pip install -r $backendReq

# Install frontend dependencies if possible
if (-not $skipFrontend) {
    Push-Location frontend
    Write-Host "Running npm install in frontend" -ForegroundColor Cyan
    npm install
    Pop-Location
} else {
    Write-Host "Skipping frontend npm install (Node/npm missing)." -ForegroundColor Yellow
}

Write-Host "Setup complete. To activate the venv in PowerShell run:`n  .\.venv\Scripts\Activate.ps1`" -ForegroundColor Green
Write-Host "Or call venv python directly: .\.venv\Scripts\python.exe -m uvicorn main:app --reload" -ForegroundColor Green

exit 0
