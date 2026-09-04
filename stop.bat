@echo off
setlocal EnableExtensions
cd /d "%~dp0"

echo Stopping processes listening on ports 8000 and 5173...

set "KILLED=0"
for %%P in (8000 5173) do (
  for /f "tokens=5" %%A in ('netstat -ano ^| findstr /C:":%%P " ^| findstr /I "LISTENING"') do (
    echo Killing PID %%A ^(port %%P^)...
    taskkill /F /PID %%A >nul 2>&1
    if not errorlevel 1 set "KILLED=1"
  )
)

if "%KILLED%"=="0" (
  echo No listening processes found on 8000 or 5173.
) else (
  echo Done.
)

echo.
pause
endlocal
exit /b 0
