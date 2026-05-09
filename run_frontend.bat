@echo off
TITLE P6BookingMe - Frontend Dev Server
set CURRENT_DIR=%~dp0
cd /d "%CURRENT_DIR%frontend"

echo Starting Frontend in Dev Mode...
:: Check if node_modules exists
if not exist node_modules (
    echo node_modules not found. Installing dependencies...
    call npm install
)

:: Run vite dev server
npm run dev
pause
