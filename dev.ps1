# Run with Windows PowerShell. Start Docker Desktop before running this script.
$ErrorActionPreference = 'Stop'

$backend = Join-Path $PSScriptRoot 'backend'
$frontend = Join-Path $PSScriptRoot 'frontend'
$python = Join-Path $PSScriptRoot '.venv\Scripts\python.exe'
$compose = Join-Path $PSScriptRoot 'mailpit.compose.yml'

if (-not (Test-Path -LiteralPath $python -PathType Leaf)) {
    throw 'Create the Windows virtual environment from the repo root: py -m venv .venv'
}
if (-not (Get-Command npm.cmd -ErrorAction SilentlyContinue)) {
    throw 'Windows npm was not found. Make sure Node.js is on PATH.'
}
if (-not (Test-Path -LiteralPath (Join-Path $frontend 'node_modules\.bin\vite.cmd') -PathType Leaf)) {
    throw 'Install frontend dependencies in Windows PowerShell: npm.cmd --prefix frontend ci'
}
if (-not (Get-Command docker.exe -ErrorAction SilentlyContinue)) {
    throw 'Docker CLI was not found. Open a new terminal after installing Docker Desktop.'
}

& $python -c 'import uvicorn'
if ($LASTEXITCODE -ne 0) {
    throw 'Install backend dependencies: .\.venv\Scripts\python.exe -m pip install -r backend\requirements.txt'
}

& docker.exe compose -f $compose up -d
if ($LASTEXITCODE -ne 0) {
    throw 'Mailpit could not start. Check that Docker Desktop is running and review the Docker output above.'
}

$windowsPowerShell = Join-Path $PSHOME 'powershell.exe'
if (-not (Test-Path -LiteralPath $windowsPowerShell -PathType Leaf)) {
    $windowsPowerShell = (Get-Command powershell.exe).Source
}

Start-Process -FilePath $windowsPowerShell -WorkingDirectory $backend -ArgumentList @(
    '-NoProfile', '-NoExit', '-Command',
    '..\.venv\Scripts\python.exe -m uvicorn app.main:app --reload --port 8000'
)
Start-Process -FilePath $windowsPowerShell -WorkingDirectory $frontend -ArgumentList @(
    '-NoProfile', '-NoExit', '-Command', 'npm.cmd run dev'
)

Write-Host 'FastAPI and Vite are starting in separate windows. Press Ctrl+C in each window to stop it.'
Write-Host 'API docs: http://localhost:8000/docs'
Write-Host 'Mailpit:  http://localhost:8025'
Write-Host 'Frontend: use the Local URL printed by Vite.'
