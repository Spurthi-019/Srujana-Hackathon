@echo off
echo 🔧 ClassTrack Auto-Commit Tool
echo =============================
echo.

REM Check if PowerShell is available
where powershell >nul 2>nul
if %errorlevel% neq 0 (
    echo ❌ PowerShell not found. Please install PowerShell.
    pause
    exit /b 1
)

REM Run the PowerShell auto-commit script
powershell.exe -ExecutionPolicy Bypass -File "%~dp0auto-commit.ps1" %*

REM Keep window open to see results
echo.
echo Press any key to close...
pause >nul