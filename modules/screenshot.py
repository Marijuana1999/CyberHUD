#!/usr/bin/env python3

# modules/screenshot.py
import os
import sys
import platform
from core.core import Color, safe_request

# تلاش برای import سلیونوم - اگه نصب نباشه خطا نمیده
try:
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options as ChromeOptions
    from selenium.webdriver.firefox.options import Options as FirefoxOptions
    from selenium.webdriver.edge.options import Options as EdgeOptions
    SELENIUM_AVAILABLE = True
except ImportError:
    SELENIUM_AVAILABLE = False

# برای Termux و لینوکس بدون GUI
try:
    from selenium.webdriver.chrome.service import Service
    from webdriver_manager.chrome import ChromeDriverManager
    WEBDRIVER_MANAGER = True
except ImportError:
    WEBDRIVER_MANAGER = False

def detect_environment():
    """Detect current environment"""
    system = platform.system().lower()
    
    if system == "windows":
        return "windows"
    
    if system == "linux":
        # Check for Termux
        home = os.path.expanduser("~")
        if "/data/data/com.termux" in home:
            return "termux"
        return "linux"
    
    return system

def is_selenium_working():
    """Check if selenium is properly installed"""
    if not SELENIUM_AVAILABLE:
        return False, "selenium not installed"
    
    try:
        # Just check imports, don't try to launch
        return True, "selenium available"
    except Exception as e:
        return False, str(e)

def take_screenshot_alternative(url, output_path):
    """Alternative screenshot methods when selenium fails"""
    
    # Method 1: Try using requests to get page and save HTML
    try:
        resp, error = safe_request(url, timeout=10)
        if not error and resp and resp.status_code == 200:
            html_path = output_path.replace('.png', '.html')
            with open(html_path, 'w', encoding='utf-8') as f:
                f.write(resp.text)
            print(Color.Y + f"  [i] HTML saved to: {html_path}" + Color.N)
            return True, "HTML saved"
    except:
        pass
    
    # Method 2: Try using curl (for Termux/Linux)
    if platform.system().lower() != "windows":
        try:
            import subprocess
            curl_cmd = f"curl -I {url}"
            result = subprocess.run(curl_cmd, shell=True, capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                print(Color.G + "  [✓] Website is accessible via curl" + Color.N)
                return True, "accessible"
        except:
            pass
    
    return False, "no screenshot method available"

def take_screenshot_selenium(url, output_path, env):
    """Take screenshot using selenium"""
    if not SELENIUM_AVAILABLE:
        return False, "selenium not installed"
    
    driver = None
    
    try:
        # Choose appropriate driver based on environment
        if env == "windows":
            # Windows - try Chrome
            options = ChromeOptions()
            options.add_argument("--headless=new")
            options.add_argument("--disable-gpu")
            options.add_argument("--window-size=1920,1080")
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            
            if WEBDRIVER_MANAGER:
                service = Service(ChromeDriverManager().install())
                driver = webdriver.Chrome(service=service, options=options)
            else:
                driver = webdriver.Chrome(options=options)
        
        elif env == "linux":
            # Linux - try Firefox (more stable headless)
            try:
                options = FirefoxOptions()
                options.add_argument("--headless")
                options.add_argument("--window-size=1920,1080")
                driver = webdriver.Firefox(options=options)
            except:
                # Fallback to Chrome
                options = ChromeOptions()
                options.add_argument("--headless=new")
                options.add_argument("--disable-gpu")
                options.add_argument("--window-size=1920,1080")
                options.add_argument("--no-sandbox")
                options.add_argument("--disable-dev-shm-usage")
                driver = webdriver.Chrome(options=options)
        
        elif env == "termux":
            # Termux - try lightweight options
            print(Color.Y + "  [i] Termux detected - screenshot may not work" + Color.N)
            return False, "termux not supported for selenium"
        
        else:
            return False, f"unsupported environment: {env}"
        
        if not driver:
            return False, "could not create driver"
        
        # Take screenshot
        print(Color.Y + f"  [i] Loading {url}..." + Color.N)
        driver.get(url)
        driver.save_screenshot(output_path)
        driver.quit()
        
        if os.path.exists(output_path) and os.path.getsize(output_path) > 1000:
            return True, "screenshot saved"
        else:
            return False, "screenshot file too small"
    
    except Exception as e:
        if driver:
            try:
                driver.quit()
            except:
                pass
        return False, str(e)

def run(target):
    """Main screenshot function"""
    print(Color.C + "\n[+] Screenshot Capture\n" + Color.N)
    
    if not target:
        print(Color.R + "[!] No target set" + Color.N)
        return
    
    env = detect_environment()
    print(Color.Y + f"[*] Environment: {env.upper()}" + Color.N)
    
    # Create folder
    folder = "logs/image"
    try:
        os.makedirs(folder, exist_ok=True)
    except:
        folder = "logs"
        os.makedirs(folder, exist_ok=True)
    
    # Generate filename
    safe_target = target.replace('.', '_').replace('/', '_').replace(':', '_')
    out = os.path.join(folder, f"{safe_target}.png")
    url = f"https://{target}"
    
    print(Color.Y + f"[*] Target URL: {url}" + Color.N)
    print(Color.Y + f"[*] Output: {out}\n" + Color.N)
    
    # Check if we can use selenium
    selenium_ok, selenium_msg = is_selenium_working()
    
    if env == "termux":
        print(Color.Y + "[!] Termux detected - screenshot functionality limited" + Color.N)
        success, message = take_screenshot_alternative(url, out)
        
        if success:
            print(Color.Y + f"  [i] {message}" + Color.N)
        else:
            print(Color.Y + "  [i] Try installing: pkg install chromium" + Color.N)
    
    elif selenium_ok:
        print(Color.G + "[✓] Selenium available" + Color.N)
        success, message = take_screenshot_selenium(url, out, env)
        
        if success:
            full_path = os.path.abspath(out)
            print(Color.G + f"\n[✓] Screenshot saved successfully!" + Color.N)
            print(Color.C + f"    📁 {full_path}" + Color.N)
            
            # Show file size
            size = os.path.getsize(out) / 1024
            print(Color.C + f"    📦 Size: {size:.1f} KB" + Color.N)
        else:
            print(Color.R + f"\n[✗] Failed to take screenshot: {message}" + Color.N)
            print(Color.Y + "    Trying alternative method..." + Color.N)
            take_screenshot_alternative(url, out)
    else:
        print(Color.Y + f"[!] Selenium not available: {selenium_msg}" + Color.N)
        print(Color.Y + "    Using alternative method..." + Color.N)
        take_screenshot_alternative(url, out)
    
    # Final message
    print(Color.Y + f"\n[*] Screenshot saved to: {out}" + Color.N)
    
    # Check if file exists
    if os.path.exists(out):
        print(Color.G + f"[✓] File exists: {os.path.getsize(out)} bytes" + Color.N)
    else:
        print(Color.Y + "[i] No screenshot file created" + Color.N)
    
    print()