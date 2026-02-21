#!/usr/bin/env python3

import os
import platform
import subprocess
import sys
import venv
from pathlib import Path
from colorama import Fore, Style, init

init(autoreset=True)

# =========================================================
# COLORS
# =========================================================
G = Fore.GREEN
R = Fore.RED
Y = Fore.YELLOW
C = Fore.CYAN
B = Fore.BLUE
RS = Style.RESET_ALL


# =========================================================
# RUN SYSTEM COMMAND
# =========================================================
def run_cmd(cmd, check_error=True):
    try:
        print(C + f"[*] Running: {cmd}" + RS)
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        
        if result.returncode == 0:
            print(G + "[✓] Success" + RS)
            return True, result.stdout
        else:
            if check_error:
                print(R + f"[✗] Failed with error: {result.stderr}" + RS)
            return False, result.stderr
    except Exception as e:
        print(R + f"[!] Error: {e}" + RS)
        return False, str(e)


# =========================================================
# CHECK IF KALI LINUX
# =========================================================
def is_kali_linux():
    if platform.system().lower() != "linux":
        return False
    
    # Check for Kali-specific files
    kali_indicators = [
        "/etc/kali-release",
        "/etc/os-release"
    ]
    
    for indicator in kali_indicators:
        if os.path.exists(indicator):
            try:
                with open(indicator, 'r') as f:
                    content = f.read().lower()
                    if 'kali' in content:
                        return True
            except:
                pass
    
    # Check if it's Kali by looking at the message in the error
    return False


# =========================================================
# ENVIRONMENT DETECT
# =========================================================
def detect_environment():
    system = platform.system().lower()

    if system == "windows":
        return "windows"

    if system == "linux":
        home = os.path.expanduser("~")
        if home.startswith("/data/data/com.termux/files/home"):
            return "termux"
        
        # Check if it's Kali Linux
        if is_kali_linux():
            return "kali"
        
        return "linux"

    return "unknown"


# =========================================================
# USER MENU SELECT
# =========================================================
def choose_env():
    print(C + "\nSelect installation environment:\n" + RS)
    print("1) Windows")
    print("2) Linux (Ubuntu/Debian)")
    print("3) Kali Linux")
    print("4) Termux")
    print("5) Auto Detect\n")

    choice = input(Y + "Enter choice (1-5): " + RS).strip()

    if choice == "1":
        return "windows"
    if choice == "2":
        return "linux"
    if choice == "3":
        return "kali"
    if choice == "4":
        return "termux"
    if choice == "5":
        return detect_environment()

    return detect_environment()


# =========================================================
# CREATE VIRTUAL ENVIRONMENT FOR KALI
# =========================================================
def setup_kali_venv():
    venv_path = os.path.join(os.path.expanduser("~"), ".cybersec-framework-venv")
    
    print(Y + f"\n[*] Creating virtual environment at {venv_path}..." + RS)
    
    # Check if venv already exists
    if os.path.exists(venv_path):
        print(Y + "[*] Virtual environment already exists. Using existing one." + RS)
    else:
        try:
            # Create virtual environment
            venv.create(venv_path, with_pip=True)
            print(G + "[✓] Virtual environment created successfully" + RS)
        except Exception as e:
            print(R + f"[!] Failed to create virtual environment: {e}" + RS)
            print(Y + "[*] Trying with python3-venv package..." + RS)
            
            # Try installing python3-venv first
            run_cmd("sudo apt update && sudo apt install python3-venv -y")
            
            try:
                venv.create(venv_path, with_pip=True)
                print(G + "[✓] Virtual environment created successfully" + RS)
            except Exception as e:
                print(R + f"[!] Still failed: {e}" + RS)
                sys.exit(1)
    
    # Get the pip path
    if platform.system().lower() == "windows":
        pip_path = os.path.join(venv_path, "Scripts", "pip")
    else:
        pip_path = os.path.join(venv_path, "bin", "pip")
    
    # Upgrade pip
    print(Y + "[*] Upgrading pip..." + RS)
    run_cmd(f"{pip_path} install --upgrade pip")
    
    return pip_path


# =========================================================
# INSTALL PACKAGES
# =========================================================
def install_packages(pip_cmd, packages, env_type=None):
    print(Y + "\n[*] Installing dependencies...\n" + RS)
    
    success_count = 0
    fail_count = 0
    
    for pkg in packages:
        print(B + f"• Installing {pkg}..." + RS)
        
        # Different pip commands based on environment
        if env_type == "kali":
            # For Kali with venv, use normal pip
            success, _ = run_cmd(f"{pip_cmd} install {pkg}")
        elif env_type == "linux" and "pip3" in pip_cmd:
            # For regular Linux, try with --user flag
            success, _ = run_cmd(f"{pip_cmd} install --user {pkg}")
        else:
            # For Windows and others
            success, _ = run_cmd(f"{pip_cmd} install {pkg}")
        
        if success:
            success_count += 1
        else:
            fail_count += 1
            print(Y + f"[*] Trying alternative method for {pkg}..." + RS)
            
            # Alternative installation methods
            if env_type == "linux" or env_type == "kali":
                # Try with apt for system packages
                apt_pkg = f"python3-{pkg}"
                run_cmd(f"sudo apt install -y {apt_pkg}", check_error=False)
    
    print(Y + f"\n[*] Summary: {success_count} installed, {fail_count} failed" + RS)
    return success_count, fail_count


# =========================================================
# INSTALL SYSTEM DEPENDENCIES
# =========================================================
def install_system_deps(env):
    if env == "linux" or env == "kali":
        print(Y + "\n[*] Installing system dependencies..." + RS)
        
        # Update package list
        run_cmd("sudo apt update")
        
        # Install essential build tools and Python dev packages
        run_cmd("sudo apt install -y python3-dev build-essential")
        
        # For cryptography and other packages that need compilation
        run_cmd("sudo apt install -y libssl-dev libffi-dev")
        
        # Install Python packages that are available via apt
        apt_packages = [
            "python3-pip",
            "python3-venv",
            "python3-setuptools",
            "python3-wheel"
        ]
        
        for pkg in apt_packages:
            run_cmd(f"sudo apt install -y {pkg}")
    
    elif env == "termux":
        print(Y + "\n[*] Installing Termux native packages..." + RS)
        run_cmd("pkg update -y")
        run_cmd("pkg upgrade -y")
        run_cmd("pkg install -y python python-pip clang openssl rust libffi-dev")


# =========================================================
# DEPENDENCIES PER ENVIRONMENT
# =========================================================

WINDOWS_PKGS = [
    "requests", "beautifulsoup4", "dnspython", "colorama", "cryptography",
    "pyopenssl", "urllib3", "idna", "pillow", "fake-useragent",
    "lxml", "certifi", "charset-normalizer", "selenium"
]

LINUX_PKGS = [
    "requests", "beautifulsoup4", "dnspython", "colorama", "cryptography",
    "pyopenssl", "urllib3", "idna", "pillow", "fake-useragent",
    "lxml", "certifi", "charset-normalizer"
]

KALI_PKGS = [
    "requests", "beautifulsoup4", "dnspython", "colorama", "cryptography",
    "pyopenssl", "urllib3", "idna", "pillow", "fake-useragent",
    "lxml", "certifi", "charset-normalizer"
]

TERMUX_PKGS = [
    "requests", "beautifulsoup4", "dnspython", "colorama", "urllib3",
    "idna", "pillow", "fake-useragent", "lxml",
    "certifi", "charset-normalizer"
]


# =========================================================
# VERIFY INSTALLATION
# =========================================================
def verify_installation(packages, env_type):
    print(Y + "\n[*] Verifying installation..." + RS)
    
    if env_type == "kali":
        # For Kali, we need to activate the venv to test
        venv_path = os.path.join(os.path.expanduser("~"), ".cybersec-framework-venv")
        python_path = os.path.join(venv_path, "bin", "python")
    else:
        python_path = "python3" if env_type != "windows" else "python"
    
    working = []
    failed = []
    
    for pkg in packages:
        # Convert package name to import name (e.g., beautifulsoup4 -> bs4)
        import_name = pkg
        if pkg == "beautifulsoup4":
            import_name = "bs4"
        elif pkg == "pyopenssl":
            import_name = "OpenSSL"
        elif pkg == "pillow":
            import_name = "PIL"
        elif pkg == "fake-useragent":
            import_name = "fake_useragent"
        
        print(C + f"[*] Testing {pkg}..." + RS, end=" ")
        
        test_cmd = f"{python_path} -c \"import {import_name}\" 2>/dev/null"
        success, _ = run_cmd(test_cmd, check_error=False)
        
        if success:
            print(G + "✓ OK" + RS)
            working.append(pkg)
        else:
            print(R + "✗ Failed" + RS)
            failed.append(pkg)
    
    print(Y + f"\n[*] Verification complete: {len(working)} working, {len(failed)} failed" + RS)
    return working, failed


# =========================================================
# MAIN
# =========================================================
def main():
    print(B + "=== CyberSec Dependencies Installer ===\n" + RS)
    print(Y + "This script will install required Python packages for your CyberSec Framework\n" + RS)

    # Detect or choose environment
    env = choose_env()
    print(C + f"\n[+] Environment selected: {env.upper()}\n" + RS)

    # Install system dependencies first
    install_system_deps(env)

    # Setup pip command and packages based on environment
    if env == "windows":
        pip_cmd = "pip"
        packages = WINDOWS_PKGS
        env_type = "windows"
    
    elif env == "linux":
        pip_cmd = "pip3"
        packages = LINUX_PKGS
        env_type = "linux"
    
    elif env == "kali":
        # For Kali, use virtual environment
        pip_cmd = setup_kali_venv()
        packages = KALI_PKGS
        env_type = "kali"
        print(C + f"\n[+] Using pip from virtual environment: {pip_cmd}\n" + RS)
    
    elif env == "termux":
        pip_cmd = "pip"
        packages = TERMUX_PKGS
        env_type = "termux"
    
    else:
        print(R + "[!] Unknown environment detected." + RS)
        sys.exit(1)

    # Install Python packages
    success_count, fail_count = install_packages(pip_cmd, packages, env_type)

    # Verify installation
    if success_count > 0:
        verify_installation(packages, env_type)

    # Final message
    print(G + "\n" + "="*50 + RS)
    print(G + "✓ All done! Your CyberSec Framework is ready." + RS)
    print(G + "="*50 + "\n" + RS)

    # Additional instructions for Kali users
    if env == "kali":
        venv_path = os.path.join(os.path.expanduser("~"), ".cybersec-framework-venv")
        print(Y + "To use the installed packages in Kali Linux, activate the virtual environment:")
        print(C + f"    source {venv_path}/bin/activate" + RS)
        print(Y + "Or run your script directly with:")
        print(C + f"    {venv_path}/bin/python your_script.py" + RS)
        print()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(Y + "\n\n[*] Installation cancelled by user." + RS)
        sys.exit(0)
    except Exception as e:
        print(R + f"\n[!] Unexpected error: {e}" + RS)
        sys.exit(1)