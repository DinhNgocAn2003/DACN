<#
setup.ps1 - Thiết lập môi trường phát triển trên Windows (PowerShell)

Nội dung:
- Kiểm tra Python và Node/NPM trên PATH, in hướng dẫn nếu thiếu
- Tạo virtual environment tại `./.venv`
- Nâng cấp pip/setuptools/wheel trong venv
- Cài phụ thuộc Python từ `backend/requirements.txt`
- Chạy `npm install` trong `frontend` nếu có Node/npm

Cách dùng (PowerShell):
    .\setup.ps1

Nếu chính sách PowerShell chặn chạy file, chạy:
    powershell -ExecutionPolicy Bypass -File .\setup.ps1
#>

Write-Host "Bắt đầu thiết lập dự án..." -ForegroundColor Cyan

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

# Tạo virtual environment
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
    Write-Host "Bỏ qua npm install cho frontend (thiếu Node/npm)." -ForegroundColor Yellow
}

Write-Host "Thiết lập hoàn tất. Kích hoạt venv bằng:`n  .\.venv\Scripts\Activate.ps1`" -ForegroundColor Green
Write-Host "Hoặc dùng python trong venv: .\.venv\Scripts\python.exe -m uvicorn main:app --reload" -ForegroundColor Green

exit 0
