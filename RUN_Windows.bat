@echo off
title CyberHUD - Marijuana1999

:: ======================================================================
:: CyberHUD Windows Runner with Auto Installer - FULL COLOR EDITION
:: Author: Marijuana1999
:: GitHub: https://github.com/Marijuana1999
:: Version: 3.0
:: ======================================================================

:: Set colors for different sections
set "HEADER_COLOR=0B"     & REM Light Cyan
set "SUCCESS_COLOR=0A"    & REM Light Green
set "ERROR_COLOR=0C"      & REM Light Red
set "WARNING_COLOR=0E"    & REM Light Yellow
set "INFO_COLOR=0F"       & REM White
set "MODULE_COLOR=0D"     & REM Light Magenta

cls

:: ===== HEADER =====
color %HEADER_COLOR%
echo ╔══════════════════════════════════════════════════════════╗
echo ║           CYBER HUD - Marijuana1999                      ║
echo ║     https://github.com/Marijuana1999                     ║
echo ╠══════════════════════════════════════════════════════════╣
echo ║              Windows Runner v3.0                         ║
echo ╚══════════════════════════════════════════════════════════╝
echo.

:: ===== PYTHON CHECK =====
color %INFO_COLOR%
echo [*] Checking Python installation...

python --version >nul 2>&1
if errorlevel 1 (
    color %ERROR_COLOR%
    echo [ERROR] Python is not installed!
    echo.
    echo Please download Python from: https://www.python.org/downloads/
    echo.
    pause
    exit /b 1
)

:: Show Python version
for /f "tokens=2" %%i in ('python --version 2^>^&1') do set pyver=%%i
color %SUCCESS_COLOR%
echo [✓] Python %pyver% detected
echo.

:: ===== FIND MAIN FILE =====
color %INFO_COLOR%
echo [*] Looking for main menu file...

set MAIN_FILE=
if exist "cyberhud.py" set MAIN_FILE=cyberhud.py
if exist "menu.py" set MAIN_FILE=menu.py

if "%MAIN_FILE%"=="" (
    color %ERROR_COLOR%
    echo [ERROR] Main menu file not found!
    echo.
    echo Looking for: cyberhud.py, menu.py
    echo.
    pause
    exit /b 1
)

color %SUCCESS_COLOR%
echo [✓] Found main file: %MAIN_FILE%
echo.

:: ===== CHECK DEPENDENCIES =====
color %INFO_COLOR%
echo [*] Checking required packages...
echo.

set NEED_INSTALL=0

:: Check each package with different colors
python -c "import requests" 2>nul
if errorlevel 1 (
    color %ERROR_COLOR%
    echo [✗] requests is missing
    set NEED_INSTALL=1
) else (
    color %SUCCESS_COLOR%
    echo [✓] requests is installed
)

python -c "import bs4" 2>nul
if errorlevel 1 (
    color %ERROR_COLOR%
    echo [✗] beautifulsoup4 is missing
    set NEED_INSTALL=1
) else (
    color %SUCCESS_COLOR%
    echo [✓] beautifulsoup4 is installed
)

python -c "import colorama" 2>nul
if errorlevel 1 (
    color %ERROR_COLOR%
    echo [✗] colorama is missing
    set NEED_INSTALL=1
) else (
    color %SUCCESS_COLOR%
    echo [✓] colorama is installed
)

python -c "import dns" 2>nul
if errorlevel 1 (
    color %ERROR_COLOR%
    echo [✗] dnspython is missing
    set NEED_INSTALL=1
) else (
    color %SUCCESS_COLOR%
    echo [✓] dnspython is installed
)

python -c "import cryptography" 2>nul
if errorlevel 1 (
    color %ERROR_COLOR%
    echo [✗] cryptography is missing
    set NEED_INSTALL=1
) else (
    color %SUCCESS_COLOR%
    echo [✓] cryptography is installed
)

python -c "import jwt" 2>nul
if errorlevel 1 (
    color %WARNING_COLOR%
    echo [!] pyjwt is missing (optional)
) else (
    color %SUCCESS_COLOR%
    echo [✓] pyjwt is installed
)

python -c "import graphql" 2>nul
if errorlevel 1 (
    color %WARNING_COLOR%
    echo [!] graphql-core is missing (optional)
) else (
    color %SUCCESS_COLOR%
    echo [✓] graphql-core is installed
)

echo.

:: ===== INSTALL MISSING PACKAGES =====
if %NEED_INSTALL%==1 (
    color %WARNING_COLOR%
    echo [*] Some packages are missing.
    echo [*] Running installer...
    echo.
    
    if exist "installer.py" (
        color %MODULE_COLOR%
        echo [→] Starting installer.py
        python installer.py
        if errorlevel 1 (
            color %ERROR_COLOR%
            echo [ERROR] Installer failed!
        ) else (
            color %SUCCESS_COLOR%
            echo [✓] Installer completed successfully
        )
        echo.
    ) else (
        color %WARNING_COLOR%
        echo [WARNING] installer.py not found!
        echo.
        color %INFO_COLOR%
        echo [*] Trying to install with pip...
        pip install requests beautifulsoup4 colorama dnspython cryptography pyjwt graphql-core
    )
) else (
    color %SUCCESS_COLOR%
    echo [✓] All required packages are installed!
)

echo.
color %HEADER_COLOR%
echo ╔══════════════════════════════════════════════════════════╗
echo ║                    LAUNCHING MODULE                      ║
echo ╚══════════════════════════════════════════════════════════╝
echo.

:: ===== LAUNCH MAIN MENU =====
color %MODULE_COLOR%
echo [→] Starting: %MAIN_FILE%
echo.

:: Run the main menu
python "%MAIN_FILE%"

:: ===== AFTER CLOSING =====
echo.
color %SUCCESS_COLOR%
echo [✓] CyberHUD session ended
echo.
color %INFO_COLOR%
echo Press any key to exit...
pause >nul

:: Reset color
color 07