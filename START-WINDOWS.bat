@echo off
setlocal
cd /d "%~dp0"
where py >nul 2>nul
if errorlevel 1 (
  echo Python 3.11 or newer is required. Install Python with the Python Launcher enabled.
  pause
  exit /b 1
)
if not exist ".venv\Scripts\python.exe" (
  py -3 -m venv .venv
  if errorlevel 1 goto :failed
)
".venv\Scripts\python.exe" -m pip install -r backend\requirements.txt
if errorlevel 1 goto :failed
if not exist "frontend\dist\index.html" (
  where npm >nul 2>nul
  if errorlevel 1 (
    echo Install Node.js 22 LTS, then run this file again.
    goto :failed
  )
  pushd frontend
  call npm ci --no-audit --no-fund
  if errorlevel 1 (
    popd
    goto :failed
  )
  call npm run build
  if errorlevel 1 (
    popd
    goto :failed
  )
  popd
)
echo.
echo Open http://127.0.0.1:8000 in your browser.
echo First time? See START-HERE.md to create your admin account and add sample cars.
echo Keep this window open. Press Ctrl+C to stop the application.
".venv\Scripts\python.exe" -m uvicorn backend.app:create_app --factory --host 127.0.0.1 --port 8000
if errorlevel 1 goto :failed
exit /b 0
:failed
echo.
echo Setup or startup failed. Read the error above and the troubleshooting section in README.md.
pause
exit /b 1
