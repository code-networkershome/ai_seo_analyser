@echo off
set "PATH=C:\Windows\System32;%PATH%"
echo ========================================
echo   Starting Frontend Development Server
echo ========================================
echo.
echo IMPORTANT: Run this in a NEW terminal as Administrator
echo.
cd frontend_web
call npm install
if %errorlevel% neq 0 (
    echo.
    echo ERROR: npm install failed!
    pause
    exit /b 1
)
echo.
echo Starting dev server...
call npm run dev
