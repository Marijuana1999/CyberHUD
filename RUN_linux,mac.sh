#!/bin/bash

# ======================================================================
# CyberHUD Linux/macOS Runner with Auto Installer - FULL COLOR EDITION
# Author: Marijuana1999
# GitHub: https://github.com/Marijuana1999
# Version: 3.0
# ======================================================================

# Colors
HEADER='\033[0;36m'      # Cyan
SUCCESS='\033[0;32m'     # Green
ERROR='\033[0;31m'       # Red
WARNING='\033[1;33m'     # Yellow
INFO='\033[0;37m'        # White
MODULE='\033[0;35m'      # Magenta
BOLD='\033[1m'
NC='\033[0m'             # No Color

clear
echo -e "${HEADER}╔══════════════════════════════════════════════════════════╗${NC}"
echo -e "${HEADER}║${SUCCESS}${BOLD}           CYBER HUD - Marijuana1999                      ${HEADER}║${NC}"
echo -e "${HEADER}║${WARNING}     https://github.com/Marijuana1999                     ${HEADER}║${NC}"
echo -e "${HEADER}╠══════════════════════════════════════════════════════════╣${NC}"
echo -e "${HEADER}║${MODULE}              Linux/macOS Runner v3.0                      ${HEADER}║${NC}"
echo -e "${HEADER}╚══════════════════════════════════════════════════════════╝${NC}"
echo ""

# ===== PYTHON CHECK =====
echo -e "${INFO}[*] Checking Python installation...${NC}"

if command -v python3 &> /dev/null; then
    PYTHON="python3"
    echo -e "${SUCCESS}[✓] Python 3 detected${NC}"
elif command -v python &> /dev/null; then
    PYTHON="python"
    echo -e "${SUCCESS}[✓] Python detected${NC}"
else
    echo -e "${ERROR}[ERROR] Python is not installed!${NC}"
    echo -e "${INFO}Please install Python 3.6 or higher${NC}"
    read -p "Press ENTER to exit..."
    exit 1
fi

# Show Python version
PY_VERSION=$($PYTHON --version 2>&1 | cut -d' ' -f2)
echo -e "${SUCCESS}[✓]${NC} Python version: ${BOLD}$PY_VERSION${NC}"
echo ""

# ===== FIND MAIN FILE =====
echo -e "${INFO}[*] Looking for main menu file...${NC}"

MAIN_FILE=""
if [ -f "cyberhud.py" ]; then
    MAIN_FILE="cyberhud.py"
    echo -e "${SUCCESS}[✓] Found: cyberhud.py${NC}"
elif [ -f "menu.py" ]; then
    MAIN_FILE="menu.py"
    echo -e "${SUCCESS}[✓] Found: menu.py${NC}"
else
    echo -e "${ERROR}[ERROR] Main menu file not found!${NC}"
    echo -e "${INFO}Looking for: cyberhud.py, menu.py${NC}"
    read -p "Press ENTER to exit..."
    exit 1
fi
echo ""

# ===== CHECK DEPENDENCIES =====
echo -e "${INFO}[*] Checking required packages...${NC}"
echo ""

NEED_INSTALL=0

# Check requests
$PYTHON -c "import requests" 2>/dev/null
if [ $? -eq 0 ]; then
    echo -e "${SUCCESS}[✓] requests is installed${NC}"
else
    echo -e "${ERROR}[✗] requests is missing${NC}"
    NEED_INSTALL=1
fi

# Check beautifulsoup4
$PYTHON -c "import bs4" 2>/dev/null
if [ $? -eq 0 ]; then
    echo -e "${SUCCESS}[✓] beautifulsoup4 is installed${NC}"
else
    echo -e "${ERROR}[✗] beautifulsoup4 is missing${NC}"
    NEED_INSTALL=1
fi

# Check colorama
$PYTHON -c "import colorama" 2>/dev/null
if [ $? -eq 0 ]; then
    echo -e "${SUCCESS}[✓] colorama is installed${NC}"
else
    echo -e "${ERROR}[✗] colorama is missing${NC}"
    NEED_INSTALL=1
fi

# Check dnspython
$PYTHON -c "import dns" 2>/dev/null
if [ $? -eq 0 ]; then
    echo -e "${SUCCESS}[✓] dnspython is installed${NC}"
else
    echo -e "${ERROR}[✗] dnspython is missing${NC}"
    NEED_INSTALL=1
fi

# Check cryptography
$PYTHON -c "import cryptography" 2>/dev/null
if [ $? -eq 0 ]; then
    echo -e "${SUCCESS}[✓] cryptography is installed${NC}"
else
    echo -e "${ERROR}[✗] cryptography is missing${NC}"
    NEED_INSTALL=1
fi

# Check pyjwt (optional)
$PYTHON -c "import jwt" 2>/dev/null
if [ $? -eq 0 ]; then
    echo -e "${SUCCESS}[✓] pyjwt is installed${NC}"
else
    echo -e "${WARNING}[!] pyjwt is missing (optional)${NC}"
fi

# Check graphql-core (optional)
$PYTHON -c "import graphql" 2>/dev/null
if [ $? -eq 0 ]; then
    echo -e "${SUCCESS}[✓] graphql-core is installed${NC}"
else
    echo -e "${WARNING}[!] graphql-core is missing (optional)${NC}"
fi

echo ""

# ===== INSTALL MISSING PACKAGES =====
if [ $NEED_INSTALL -eq 1 ]; then
    echo -e "${WARNING}[*] Some packages are missing.${NC}"
    echo -e "${WARNING}[*] Running installer...${NC}"
    echo ""
    
    if [ -f "installer.py" ]; then
        echo -e "${MODULE}[→] Starting installer.py${NC}"
        $PYTHON installer.py
        if [ $? -eq 0 ]; then
            echo -e "${SUCCESS}[✓] Installer completed successfully${NC}"
        else
            echo -e "${ERROR}[ERROR] Installer failed!${NC}"
        fi
        echo ""
    else
        echo -e "${WARNING}[WARNING] installer.py not found!${NC}"
        echo -e "${INFO}[*] Trying to install with pip...${NC}"
        $PYTHON -m pip install requests beautifulsoup4 colorama dnspython cryptography pyjwt graphql-core
        echo ""
    fi
else
    echo -e "${SUCCESS}[✓] All required packages are installed!${NC}"
fi

echo ""
echo -e "${HEADER}╔══════════════════════════════════════════════════════════╗${NC}"
echo -e "${HEADER}║${MODULE}${BOLD}                    LAUNCHING MODULE                      ${HEADER}║${NC}"
echo -e "${HEADER}╚══════════════════════════════════════════════════════════╝${NC}"
echo ""

# ===== LAUNCH MAIN MENU =====
echo -e "${MODULE}[→] Starting: $MAIN_FILE${NC}"
echo ""

# Run the main menu
$PYTHON "$MAIN_FILE"

# ===== AFTER CLOSING =====
echo ""
echo -e "${SUCCESS}[✓] CyberHUD session ended${NC}"
echo ""
echo -e "${INFO}Press ENTER to exit...${NC}"
read -p ""