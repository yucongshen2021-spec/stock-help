@echo off
setlocal
set "PROJECT_DIR=%~dp0"
set "LOG_DIR=%PROJECT_DIR%runtime"
if not exist "%LOG_DIR%" mkdir "%LOG_DIR%"

echo Starting backend and frontend in background...
cmd /c start "" /b cmd /c "cd /d ""%PROJECT_DIR%backend"" && py run.py > ""%LOG_DIR%\\backend.log"" 2>&1"
cmd /c start "" /b cmd /c "cd /d ""%PROJECT_DIR%frontend"" && npm run dev > ""%LOG_DIR%\\frontend.log"" 2>&1"

timeout /t 5 /nobreak >nul
start "" http://localhost:3000

echo.
echo App started.
echo Frontend: http://localhost:3000
echo Backend : http://localhost:3001
echo Logs    : runtime\\backend.log, runtime\\frontend.log
echo.
echo Keep this window open while using the app.
pause
endlocal

