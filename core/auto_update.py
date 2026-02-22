import requests
import os
import sys
import zipfile
import shutil
import time
import platform
import json
import subprocess
from pathlib import Path
from datetime import datetime
from colorama import Fore, Style

# =========================
# Config
# =========================
CURRENT_VERSION = "3.3"
GITHUB_REPO = "Marijuana1999/CyberHUD"
UPDATE_LOG_FILE = "update_log.txt"
CACHE_FILE = "update_cache.json"
CACHE_DURATION = 3600 
_last_update_check = 0
_cached_info = None

# =========================
# Cache Management
# =========================
def load_cache():
    try:
        if os.path.exists(CACHE_FILE):
            with open(CACHE_FILE, 'r') as f:
                return json.load(f)
    except:
        pass
    return {"last_check": 0, "data": None}

def save_cache(data):
    try:
        cache = {
            "last_check": time.time(),
            "data": data
        }
        with open(CACHE_FILE, 'w') as f:
            json.dump(cache, f)
    except:
        pass

# =========================
# Version Handling
# =========================
def get_current_version():
    return CURRENT_VERSION

def get_latest_release_info(force_refresh=False):
    global _cached_info, _last_update_check
    
    current_time = time.time()
    
    if not force_refresh and _cached_info and (current_time - _last_update_check) < CACHE_DURATION:
        return _cached_info

    cache = load_cache()
    if not force_refresh and (current_time - cache["last_check"]) < CACHE_DURATION and cache["data"]:
        _cached_info = cache["data"]
        _last_update_check = cache["last_check"]
        return _cached_info
    
    url = f"https://api.github.com/repos/{GITHUB_REPO}/releases/latest"
    headers = {
        "Accept": "application/vnd.github.v3+json",
        "User-Agent": "CyberHUD-Updater"
    }
    
    try:
        resp = requests.get(url, headers=headers, timeout=5)
        
        if resp.status_code == 403:
            # Rate limit 
            if cache["data"]:
                _cached_info = cache["data"]
                _last_update_check = cache["last_check"]
                return _cached_info
            return None
            
        if resp.status_code != 200:
            return None
            
        resp.raise_for_status()
        data = resp.json()
        
        latest_version = data.get("tag_name", "").replace("v", "")
        
        download_url = None
        asset_name = None
        assets = data.get("assets", [])
        
        for asset in assets:
            name = asset.get("name", "")
            if name.endswith((".zip", ".rar")):
                download_url = asset.get("browser_download_url")
                asset_name = name
                break
        
        if not download_url:
            return None
        
        result = {
            "version": latest_version,
            "download_url": download_url,
            "asset_name": asset_name,
            "published_at": data.get("published_at", ""),
            "body": data.get("body", "No release notes")
        }
        
        
        _cached_info = result
        _last_update_check = current_time
        save_cache(result)
        return result
        
    except:
        
        if cache["data"]:
            _cached_info = cache["data"]
            _last_update_check = cache["last_check"]
            return _cached_info
        return None

def compare_versions(latest, current):
    try:
        latest_parts = list(map(int, latest.split(".")))
        current_parts = list(map(int, current.split(".")))
        return latest_parts > current_parts
    except:
        return False

# =========================
# Download with progress
# =========================
def download_with_progress(url, output_file):
    print(f"\n{Fore.CYAN}📥 Downloading update...{Style.RESET_ALL}")
    try:
        r = requests.get(url, stream=True, timeout=30)
        r.raise_for_status()
        
        total_size = int(r.headers.get('content-length', 0))
        chunk_size = 8192
        downloaded = 0

        with open(output_file, "wb") as f:
            for chunk in r.iter_content(chunk_size):
                if chunk:
                    f.write(chunk)
                    downloaded += len(chunk)
                    if total_size > 0:
                        percent = (downloaded / total_size) * 100
                        done = int(50 * downloaded / total_size)
                        sys.stdout.write(
                            f"\r[{('█' * done)}{('░' * (50 - done))}] {percent:.1f}%"
                        )
                        sys.stdout.flush()
        print(f"\n{Fore.GREEN}✅ Download complete.{Style.RESET_ALL}")
        print(f"  📁 Saved as: {output_file} ({total_size} bytes)")
        return True
        
    except Exception as e:
        print(f"{Fore.RED}❌ Download failed: {e}{Style.RESET_ALL}")
        return False

# =========================
# Ask for replacement permission
# =========================
def ask_replace_permission(file_path):
    
    print(f"\n{Fore.YELLOW}⚠️ File already exists: {file_path}{Style.RESET_ALL}")
    choice = input(f"{Fore.YELLOW}Do you want to replace it? (y/n): {Style.RESET_ALL}").strip().lower()
    return choice == 'y'

# =========================
# Extract & Replace with permission
# =========================
def extract_update(update_file="update.zip"):
    temp_dir = Path("update_temp")
    
    if not Path(update_file).exists():
        print(f"{Fore.RED}❌ Update file not found!{Style.RESET_ALL}")
        return False

    
    if temp_dir.exists():
        shutil.rmtree(temp_dir)
    temp_dir.mkdir(parents=True, exist_ok=True)

    try:
        print(f"\n{Fore.CYAN}📦 Extracting update...{Style.RESET_ALL}")
        
        if update_file.endswith('.zip'):
            print(f"  Detected ZIP file")
            with zipfile.ZipFile(update_file, "r") as zip_ref:
                zip_ref.extractall(temp_dir)
                print(f"  Files in zip: {len(zip_ref.namelist())}")
        
        elif update_file.endswith('.rar'):
            print(f"  Detected RAR file")
            try:
                
                if platform.system() == "Windows":
                    try:
                        result = subprocess.run(['7z', 'x', update_file, f'-o{temp_dir}', '-y'], 
                                              capture_output=True, text=True)
                        if result.returncode == 0:
                            print(f"  ✅ Extracted with 7z")
                        else:
                            print(f"{Fore.RED}  ❌ 7z failed: {result.stderr}{Style.RESET_ALL}")
                            return False
                    except FileNotFoundError:
                        print(f"{Fore.RED}  ❌ 7z not found!{Style.RESET_ALL}")
                        print(f"  Please install 7-Zip from: https://www.7-zip.org/")
                        return False
                else:
                    
                    try:
                        result = subprocess.run(['unrar', 'x', '-y', update_file, str(temp_dir)], 
                                              capture_output=True, text=True)
                        if result.returncode == 0:
                            print(f"  ✅ RAR extracted successfully")
                        else:
                            print(f"{Fore.RED}  ❌ unrar failed: {result.stderr}{Style.RESET_ALL}")
                            return False
                    except FileNotFoundError:
                        print(f"{Fore.RED}  ❌ unrar not found!{Style.RESET_ALL}")
                        print(f"  Install with: sudo apt install unrar")
                        return False
            except Exception as e:
                print(f"{Fore.RED}  ❌ RAR extraction failed: {e}{Style.RESET_ALL}")
                return False
        else:
            print(f"{Fore.RED}❌ Unsupported format! Only .zip or .rar{Style.RESET_ALL}")
            return False

        
        extracted_items = list(temp_dir.iterdir())
        if len(extracted_items) == 1 and extracted_items[0].is_dir():
            source_dir = extracted_items[0]
            print(f"  📂 Root directory: {source_dir.name}")
        else:
            source_dir = temp_dir
            print(f"  📂 Extracted to root")

        replaced_count = 0
        new_count = 0
        skipped_count = 0

        print(f"\n{Fore.CYAN}📁 Updating files...{Style.RESET_ALL}")
        
        
        replace_files = []
        for root, dirs, files in os.walk(source_dir):
            for file in files:
                source_file = Path(root) / file
                rel_path = source_file.relative_to(source_dir)
                target_file = Path.cwd() / rel_path
                
                if target_file.exists():
                    replace_files.append({
                        "source": source_file,
                        "target": target_file,
                        "rel_path": rel_path
                    })
                else:
                    new_count += 1

        
        if replace_files:
            print(f"\n{Fore.YELLOW}⚠️ {len(replace_files)} file(s) will be replaced.{Style.RESET_ALL}")
            
           
            for i, item in enumerate(replace_files[:5]):
                print(f"    {i+1}. {item['rel_path']}")
            if len(replace_files) > 5:
                print(f"    ... and {len(replace_files)-5} more")
            
            choice = input(f"\n{Fore.YELLOW}Do you want to proceed with replacement? (y/n): {Style.RESET_ALL}").strip().lower()
            
            if choice == 'y':
               
                for item in replace_files:
                    try:
                        item['target'].parent.mkdir(parents=True, exist_ok=True)
                        shutil.copy2(item['source'], item['target'])
                        print(f"  🔄 Replaced: {item['rel_path']}")
                        replaced_count += 1
                    except PermissionError:
                        print(f"{Fore.RED}  ❌ Permission denied: {item['rel_path']}{Style.RESET_ALL}")
                        print(f"  Please run the program as administrator")
                        return False
                    except Exception as e:
                        print(f"{Fore.RED}  ❌ Error replacing {item['rel_path']}: {e}{Style.RESET_ALL}")
                        skipped_count += 1
            else:
                print(f"{Fore.YELLOW}  ⏭️ Replacement cancelled by user{Style.RESET_ALL}")
                return False

        
        if new_count > 0:
            print(f"\n{Fore.CYAN}📁 Adding new files...{Style.RESET_ALL}")
            for root, dirs, files in os.walk(source_dir):
                for file in files:
                    source_file = Path(root) / file
                    rel_path = source_file.relative_to(source_dir)
                    target_file = Path.cwd() / rel_path
                    
                    if not target_file.exists():
                        try:
                            target_file.parent.mkdir(parents=True, exist_ok=True)
                            shutil.copy2(source_file, target_file)
                            print(f"  ➕ Added: {rel_path}")
                        except Exception as e:
                            print(f"{Fore.RED}  ❌ Error adding {rel_path}: {e}{Style.RESET_ALL}")

        print(f"\n{Fore.GREEN}✅ Update summary: {new_count} new, {replaced_count} replaced, {skipped_count} skipped{Style.RESET_ALL}")
        
        
        try:
            if Path(update_file).exists():
                Path(update_file).unlink()
                print(f"  🧹 Cleaned up update file")
        except:
            pass
            
        return True

    except zipfile.BadZipFile:
        print(f"{Fore.RED}❌ Invalid ZIP file!{Style.RESET_ALL}")
        return False
    except Exception as e:
        print(f"{Fore.RED}❌ Extraction failed: {e}{Style.RESET_ALL}")
        return False
    finally:
        
        try:
            if temp_dir.exists():
                shutil.rmtree(temp_dir)
                print(f"  🧹 Cleaned up temp directory")
        except:
            pass

# =========================
# Auto Update Main
# =========================
_update_checked = False

def check_for_update(prompt_user=True):
    
    global _update_checked
    
    if _update_checked:
        return False
    
    _update_checked = True
    
    print(f"\n{Fore.YELLOW}🔍 Checking for updates...{Style.RESET_ALL}")
    
    latest_info = get_latest_release_info(force_refresh=True)
    if not latest_info:
        print(f"{Fore.RED}⚠️ Could not check for updates{Style.RESET_ALL}")
        return False

    latest_version = latest_info.get("version", "")
    download_url = latest_info.get("download_url", "")
    asset_name = latest_info.get("asset_name", "")
    current_version = get_current_version()

    if not latest_version or not download_url:
        print(f"{Fore.RED}⚠️ Invalid release info{Style.RESET_ALL}")
        return False

    print(f"  Current version: {current_version}")
    print(f"  Latest version:  {latest_version}")
    print(f"  Asset:           {asset_name}")

    if compare_versions(latest_version, current_version):
        print(f"\n{Fore.GREEN}✨ New version {latest_version} available!{Style.RESET_ALL}")
        
        if prompt_user:
            print(f"\n{Fore.CYAN}{'='*50}{Style.RESET_ALL}")
            print(f"{Fore.CYAN}📝 Release Notes:{Style.RESET_ALL}")
            print(latest_info.get("body", "No release notes"))
            print(f"{Fore.CYAN}{'='*50}{Style.RESET_ALL}")
            
            choice = input(f"\n{Fore.YELLOW}⬇️ Download and install now? (y/n): {Style.RESET_ALL}").strip().lower()
            
            if choice == 'y':
                
                if asset_name.endswith('.rar'):
                    update_file = "update.rar"
                else:
                    update_file = "update.zip"
                
                if download_with_progress(download_url, update_file):
                    
                    print(f"\n{Fore.CYAN}The update will replace some files.{Style.RESET_ALL}")
                    extract_choice = input(f"{Fore.YELLOW}Proceed with extraction? (y/n): {Style.RESET_ALL}").strip().lower()
                    
                    if extract_choice == 'y':
                        if extract_update(update_file):
                            print(f"\n{Fore.GREEN}✅ Update applied successfully!{Style.RESET_ALL}")
                            print(f"\n{Fore.CYAN}🔄 Restarting...{Style.RESET_ALL}")
                            time.sleep(2)
                            python = sys.executable
                            os.execl(python, python, *sys.argv)
                            return True
                        else:
                            print(f"{Fore.RED}❌ Update failed{Style.RESET_ALL}")
                            return False
                    else:
                        print(f"{Fore.YELLOW}⏭️ Extraction cancelled{Style.RESET_ALL}")
                        
                        try:
                            if Path(update_file).exists():
                                Path(update_file).unlink()
                        except:
                            pass
                        return False
                else:
                    print(f"{Fore.RED}❌ Download failed{Style.RESET_ALL}")
                    return False
            else:
                print(f"{Fore.YELLOW}⏭️ Update skipped{Style.RESET_ALL}")
                return False
    else:
        print(f"{Fore.GREEN}✅ You're using the latest version!{Style.RESET_ALL}")
        return False

# =========================
# Menu Status
# =========================
def get_update_status_for_menu():
    
    try:
        info = get_latest_release_info(force_refresh=False)
        if not info:
            return f"Version: {get_current_version()}"
        
        latest = info.get("version", "")
        current = get_current_version()
        
        if compare_versions(latest, current):
            return f"⬆️ New version {latest} available!"
        else:
            return f"✓ Version {current}"
    except:
        pass
    
    return f"Version: {get_current_version()}"
