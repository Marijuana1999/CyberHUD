#!/usr/bin/env python3

import os
import json
import time
from datetime import datetime
import platform
import sys

# ============================================================
# COLOR CLASS (Cross-Platform)
# ============================================================
class Color:
    """Cross-platform color codes - works in Windows, Linux, Termux"""
    
    # Detect if Windows (to disable colors if needed)
    IS_WINDOWS = platform.system().lower() == "windows"
    
    # ANSI color codes
    if IS_WINDOWS:
        # Try to enable ANSI on Windows 10+
        try:
            import ctypes
            kernel32 = ctypes.windll.kernel32
            kernel32.SetConsoleMode(kernel32.GetStdHandle(-11), 7)
        except:
            pass
    
    # Colors - always defined, will work if terminal supports ANSI
    G = '\033[92m'  # Green
    R = '\033[91m'  # Red
    Y = '\033[93m'  # Yellow
    C = '\033[96m'  # Cyan
    B = '\033[94m'  # Blue
    M = '\033[95m'  # Magenta
    N = '\033[0m'   # Reset
    W = '\033[97m'  # White
    
    # Bold versions
    BG = '\033[1;92m'
    BR = '\033[1;91m'
    BY = '\033[1;93m'
    BC = '\033[1;96m'
    BB = '\033[1;94m'
    BM = '\033[1;95m'
    
    @classmethod
    def disable_colors(cls):
        """Disable colors (useful for Termux or dumb terminals)"""
        cls.G = cls.R = cls.Y = cls.C = cls.B = cls.M = cls.N = cls.W = ""
        cls.BG = cls.BR = cls.BY = cls.BC = cls.BB = cls.BM = ""


# ============================================================
# CLEAR SCREEN (FIXED VERSION)
# ============================================================
def clear_screen():
    """Clear terminal screen (cross-platform) - FIXED"""
    try:
        # برای ویندوز
        if platform.system().lower() == "windows":
            os.system('cls')
        # برای لینوکس، مک، ترماکس
        else:
            sys.stdout.write('\033[2J\033[H')
            sys.stdout.flush()

            os.system('clear')
    except:
        print('\n' * 100)


# ============================================================
# GLOBAL TARGET
# ============================================================
_current_target = None


def set_target(target):
    """Set the global target"""
    global _current_target
    if target:
        _current_target = target.strip().lower()
        # Remove http:// or https:// if present
        _current_target = _current_target.replace("http://", "").replace("https://", "").split("/")[0]


def get_target():
    """Get the global target"""
    return _current_target


# ============================================================
# SAVE LOG FUNCTION
# ============================================================
def save_log(target, module_name, data):
    """
    Save scan results to JSON file
    Returns: filename
    """
    # Create logs directory if not exists
    if not os.path.exists("logs"):
        os.makedirs("logs")
    
    # Create module-specific subdirectory
    module_dir = os.path.join("logs", module_name)
    if not os.path.exists(module_dir):
        os.makedirs(module_dir)
    
    # Generate filename with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_target = target.replace(".", "_").replace("/", "_")
    filename = os.path.join(module_dir, f"{safe_target}_{timestamp}.json")
    
    # Add metadata
    output = {
        "target": target,
        "module": module_name,
        "timestamp": datetime.now().isoformat(),
        "data": data
    }
    
    # Save to file
    try:
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(output, f, indent=2, ensure_ascii=False)
    except Exception as e:
        print(Color.R + f"[!] Failed to save log: {e}" + Color.N)
        # Try without encoding for Windows
        try:
            with open(filename, "w") as f:
                json.dump(output, f, indent=2)
        except:
            pass
    
    return filename


# ============================================================
# LOAD LAST LOG
# ============================================================
def load_last_log(target, module_name):
    """
    Load the most recent log for a target/module
    """
    module_dir = os.path.join("logs", module_name)
    if not os.path.exists(module_dir):
        return None
    
    # Find all logs for this target
    safe_target = target.replace(".", "_").replace("/", "_")
    logs = [f for f in os.listdir(module_dir) if f.startswith(safe_target)]
    
    if not logs:
        return None
    
    # Get most recent
    latest = sorted(logs)[-1]
    try:
        with open(os.path.join(module_dir, latest), "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        try:
            with open(os.path.join(module_dir, latest), "r") as f:
                return json.load(f)
        except:
            return None


# ============================================================
# ENVIRONMENT DETECTION
# ============================================================
def detect_environment():
    """
    Detect current environment: windows, linux, kali, termux
    """
    system = platform.system().lower()
    
    if system == "windows":
        return "windows"
    
    if system == "linux":
        # Check for Termux
        home = os.path.expanduser("~")
        if "/data/data/com.termux" in home:
            return "termux"
        
        # Check for Kali
        try:
            with open("/etc/os-release", "r") as f:
                content = f.read().lower()
                if "kali" in content:
                    return "kali"
        except:
            pass
        
        return "linux"
    
    return "unknown"


# ============================================================
# GET PIP COMMAND
# ============================================================
def get_pip_command(env=None):
    """
    Get the appropriate pip command for the environment
    """
    if env is None:
        env = detect_environment()
    
    if env == "windows":
        return "pip"
    elif env == "termux":
        return "pip"
    else:  # linux, kali
        return "pip3"


# ============================================================
# CHECK IF MODULE AVAILABLE
# ============================================================
def is_module_available(module_name, env=None):
    """
    Check if a module is available in current environment
    """
    if env is None:
        env = detect_environment()
    
    # Modules that work everywhere
    universal_modules = [
        'ports', 'dns_enum', 'reverse_ip', 'asn', 'crawler', 'tech',
        'headers', 'waf', 'cors', 'cookies', 'robots', 'xss_passive',
        'sqli_passive', 'backup_finder', 'backup_exploit', 'dirs',
        'rate_limit', 'iptracker'
    ]
    
    if module_name in universal_modules:
        return True
    
    # SSL scan needs ssl module (works everywhere except some old Windows)
    if module_name == 'ssl_scan':
        try:
            import ssl
            return True
        except:
            return False
    
    # Screenshot needs selenium (not in Termux)
    if module_name == 'screenshot':
        if env == 'termux':
            return False
        try:
            import selenium
            return True
        except:
            return False
    
    return False


# ============================================================
# SAFE REQUEST FUNCTION
# ============================================================
def safe_request(url, method="GET", timeout=10, headers=None, allow_redirects=True):
    """
    Safe HTTP request with error handling
    """
    try:
        import requests
        
        default_headers = {
            "User-Agent": "Mozilla/5.0 (CyberSec Framework; Passive Mode)"
        }
        
        if headers:
            default_headers.update(headers)
        
        if method.upper() == "GET":
            response = requests.get(
                url, 
                headers=default_headers, 
                timeout=timeout,
                allow_redirects=allow_redirects
            )
        elif method.upper() == "HEAD":
            response = requests.head(
                url, 
                headers=default_headers, 
                timeout=timeout,
                allow_redirects=allow_redirects
            )
        else:
            return None, "Unsupported method"
        
        return response, None
    
    except ImportError:
        return None, "Requests module not installed"
    except Exception as e:
        return None, str(e)


# ============================================================
# LOADING ANIMATION
# ============================================================
def loading_animation(text="Loading", duration=1.0):
    """
    Simple loading animation
    """
    import sys
    import time
    
    dots = ["⠁", "⠃", "⠇", "⠧", "⠷", "⠿", "⠷", "⠧", "⠇", "⠃"]
    end_time = time.time() + duration
    
    i = 0
    while time.time() < end_time:
        sys.stdout.write(f"\r{text} {dots[i % len(dots)]}")
        sys.stdout.flush()
        time.sleep(0.07)
        i += 1
    
    sys.stdout.write("\r" + " " * (len(text) + 5) + "\r")
    sys.stdout.flush()


# ============================================================
# PRINT BANNER
# ============================================================
def print_banner():
    """Print CyberSec Framework banner"""
    banner = f"""
{Color.BC}╔══════════════════════════════════════════════════════════╗
{Color.BC}║     {Color.BG}CYBERSEC FRAMEWORK {Color.BC} - Passive Reconnaissance       ║
{Color.BC}║     {Color.Y}Version 3.0 {Color.BC} | {Color.C}Multi-Platform{Color.BC} | {Color.G}Stealth Mode{Color.BC}        ║
{Color.BC}╚══════════════════════════════════════════════════════════╝{Color.N}
"""
    print(banner)


# ============================================================
# PAUSE FUNCTION
# ============================================================
def pause(message="Press ENTER to continue..."):
    """Pause until user presses ENTER"""
    try:
        input(f"{Color.Y}{message}{Color.N}")
    except KeyboardInterrupt:
        print()
        pass
