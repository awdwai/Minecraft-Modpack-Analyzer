@echo off
setlocal EnableExtensions
cd /d "%~dp0"

set "ROOT=%~dp0"
rem Trailing backslash from %~dp0 is fine inside "..."

echo ========================================
echo  Minecraft Modpack Analyzer - start
echo ========================================
echo.

where python >nul 2>&1
if errorlevel 1 (
  echo ERROR: Python not found on PATH. Install Python 3.12+ and retry.
  pause
  exit /b 1
)

where npm >nul 2>&1
if errorlevel 1 (
  echo ERROR: npm not found on PATH. Install Node.js 20+ and retry.
  pause
  exit /b 1
)

rem --- Backend venv ---
if not exist "%ROOT%backend\.venv\Scripts\python.exe" (
  echo Creating backend virtualenv...
  pushd "%ROOT%backend"
  python -m venv .venv
  if errorlevel 1 (
    echo ERROR: Failed to create venv.
    popd
    pause
    exit /b 1
  )
  popd
  set "NEED_PIP=1"
) else (
  set "NEED_PIP="
)

if not exist "%ROOT%backend\.venv\Scripts\uvicorn.exe" set "NEED_PIP=1"

if defined NEED_PIP (
  echo Installing backend dependencies...
  "%ROOT%backend\.venv\Scripts\python.exe" -m pip install --upgrade pip
  "%ROOT%backend\.venv\Scripts\python.exe" -m pip install -r "%ROOT%requirements.txt"
  if errorlevel 1 (
    echo ERROR: pip install failed.
    pause
    exit /b 1
  )
) else (
  echo Backend venv and deps look ready.
)

rem --- Frontend deps ---
if not exist "%ROOT%frontend\node_modules\" (
  echo Installing frontend dependencies ^(npm install^)...
  pushd "%ROOT%frontend"
  call npm install
  if errorlevel 1 (
    echo ERROR: npm install failed.
    popd
    pause
    exit /b 1
  )
  popd
) else (
  echo Frontend node_modules found.
)

echo.
echo Starting backend on port 8000...
start "MPA Backend" /D "%ROOT%backend" cmd /k ".venv\Scripts\python.exe -m uvicorn app.main:app --reload --port 8000"

echo Starting frontend on port 5173...
start "MPA Frontend" /D "%ROOT%frontend" cmd /k "npm run dev"

echo Waiting a few seconds, then opening the browser...
timeout /t 3 /nobreak >nul
start "" "http://127.0.0.1:5173"

echo.
echo Backend:  http://127.0.0.1:8000
echo Frontend: http://127.0.0.1:5173
echo API docs: http://127.0.0.1:8000/docs
echo.
echo Close the Backend/Frontend console windows to stop, or run stop.bat.
echo.
endlocal
exit /b 0
