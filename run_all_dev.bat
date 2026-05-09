@echo off
TITLE P6BookingMe - Full Stack Dev
set CURRENT_DIR=%~dp0

echo ==========================================
echo   P6BookingMe - Startup Launcher (Dev)
echo ==========================================
echo.

:: Start Backend in a new window
echo Launching Backend...
start "P6-Backend" cmd /c "%CURRENT_DIR%run_backend.bat"

:: Small delay to let backend initialize
timeout /t 2 >nul

:: Start Frontend in a new window
echo Launching Frontend...
start "P6-Frontend" cmd /c "%CURRENT_DIR%run_frontend.bat"

echo.
echo ==========================================
echo  Servers are starting in separate windows.
echo  Press any key to close this launcher.
echo ==========================================
pause >nul
exit
