@echo off
setlocal enabledelayedexpansion

echo ==========================================
echo  P6BookingMe: Cloudflare Tunnel Launcher
echo ==========================================
echo.
echo [INFO] This will create a public URL for your local server.
echo.
echo [1] Launch Frontend Tunnel (Port 5173) - For Web UI
echo [2] Launch Backend Tunnel (Port 8000) - For API Access
echo [3] Custom Tunnel (If you have a configured Tunnel Name)
echo.

set /p choice="Choose an option (1-3): "

if "%choice%"=="1" (
    echo.
    echo [INFO] Starting Quick Tunnel for Frontend...
    echo [HINT] Look for the URL ending in .trycloudflare.com below!
    cloudflared tunnel --url http://localhost:5173
) else if "%choice%"=="2" (
    echo.
    echo [INFO] Starting Quick Tunnel for Backend...
    cloudflared tunnel --url http://localhost:8000
) else if "%choice%"=="3" (
    set /p name="Enter your Tunnel Name: "
    echo [INFO] Starting Tunnel !name!...
    cloudflared tunnel run !name!
) else (
    echo [ERROR] Invalid selection.
)

pause
