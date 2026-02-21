#!/usr/bin/env python3

# modules/js_analyzer.py
import re
import json
import threading
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
from core.core import Color, save_log, safe_request

# ============================================================
# SIGNATURES - بهبود یافته و کاملتر
# ============================================================

API_REGEX = [
    r'["\'](/api/[a-zA-Z0-9_\-/]+)["\']',
    r'["\'](/v[0-9]/[a-zA-Z0-9_\-/]+)["\']',
    r'["\'](/graphql)["\']',
    r'["\'](/rest/[a-zA-Z0-9_\-/]+)["\']',
    r'["\'](/oauth/[a-zA-Z0-9_\-/]+)["\']',
    r'["\'](/auth/[a-zA-Z0-9_\-/]+)["\']',
    r'["\'](/user/[a-zA-Z0-9_\-/]+)["\']',
    r'["\'](/admin/[a-zA-Z0-9_\-/]+)["\']',
]

FETCH_REGEX = [
    r'fetch\([\'"]([^\'"]+)[\'"]',
    r'axios\.(?:get|post|put|delete|patch)\([\'"]([^\'"]+)[\'"]',
    r'\$\.(?:get|post|ajax)\([\'"]([^\'"]+)[\'"]',
    r'xhr\.open\([\'"]GET[\'"],\s*[\'"]([^\'"]+)[\'"]',
    r'XMLHttpRequest\([^)]*\)[^;]*\.open\([^,]+,\s*[\'"]([^\'"]+)[\'"]',
]

SECRET_REGEX = [
    # Google
    (r'AIza[0-9A-Za-z\-_]{35}', 'Google API Key'),
    (r'ya29\.[0-9A-Za-z\-_]+', 'Google OAuth Token'),
    
    # AWS
    (r'AKIA[0-9A-Z]{16}', 'AWS Access Key'),
    (r'[A-Za-z0-9+/]{40}', 'AWS Secret Key'),
    
    # Stripe
    (r'sk_live_[0-9a-zA-Z]{24}', 'Stripe Live Key'),
    (r'sk_test_[0-9a-zA-Z]{24}', 'Stripe Test Key'),
    (r'pk_live_[0-9a-zA-Z]{24}', 'Stripe Live Publishable'),
    (r'pk_test_[0-9a-zA-Z]{24}', 'Stripe Test Publishable'),
    
    # GitHub
    (r'ghp_[0-9a-zA-Z]{36}', 'GitHub Token'),
    (r'github_pat_[0-9a-zA-Z_]{82}', 'GitHub PAT'),
    
    # Slack
    (r'xox[baprs]-[0-9a-zA-Z]{10,48}', 'Slack Token'),
    
    # Discord
    (r'[MN][A-Za-z\d]{23,25}\.[A-Za-z\d]{6}\.[A-Za-z\d\-_]{27,38}', 'Discord Token'),
    
    # Firebase
    (r'firebaseConfig\s*=\s*\{[^}]+\}', 'Firebase Config'),
    
    # JWT
    (r'eyJ[A-Za-z0-9\-_=]+\.[A-Za-z0-9\-_=]+\.[A-Za-z0-9\-_=]+', 'JWT Token'),
    
    # Generic
    (r'api[_-]?key[\s]*[:=][\s]*[\'"]([^\'"]+)[\'"]', 'API Key'),
    (r'secret[\s]*[:=][\s]*[\'"]([^\'"]+)[\'"]', 'Secret'),
    (r'token[\s]*[:=][\s]*[\'"]([^\'"]+)[\'"]', 'Token'),
    (r'password[\s]*[:=][\s]*[\'"]([^\'"]+)[\'"]', 'Password'),
    (r'auth[\s]*[:=][\s]*[\'"]([^\'"]+)[\'"]', 'Auth Token'),
]

PARAM_REGEX = [
    r'[?&]([a-zA-Z0-9_]+)=',
    r'\$\{([a-zA-Z0-9_]+)\}',
    r'%\{([a-zA-Z0-9_]+)\}',
    r'{{([a-zA-Z0-9_]+)}}',
]

RISKY_FUNCS = [
    ('eval(', 'Dynamic code execution'),
    ('new Function(', 'Dynamic function creation'),
    ('innerHTML', 'DOM XSS risk'),
    ('outerHTML', 'DOM XSS risk'),
    ('document.write(', 'DOM XSS risk'),
    ('setTimeout("', 'Code injection risk'),
    ('setInterval("', 'Code injection risk'),
    ('execScript(', 'Code execution (IE)'),
    ('crypto.randomBytes', 'May need secure randomness'),
    ('Math.random', 'Insecure randomness for crypto'),
]

COMMENT_REGEX = [
    (r'//(.*?)$', 'Single-line comment'),
    (r'/\*(.*?)\*/', 'Multi-line comment', re.DOTALL),
    (r'<!--(.*?)-->', 'HTML comment'),
]

# ============================================================
# JS Analyzer Class
# ============================================================

class JSAnalyzer:
    def __init__(self):
        self.results = {}
        self.lock = threading.Lock()
    
    def analyze_js_file(self, js_url, base_url, results_dict):
        """Analyze a single JavaScript file"""
        
        print(Color.C + f"\n───────────── JS FILE ─────────────" + Color.N)
        print(Color.Y + f" File: {js_url}" + Color.N)
        
        # Download JS file with safe_request
        resp, error = safe_request(js_url, timeout=8)
        
        if error or not resp or resp.status_code != 200:
            print(Color.R + f"  ERROR: Cannot download file - {error or resp.status_code}" + Color.N)
            return
        
        content = resp.text
        size = len(content)
        print(Color.Y + f" Size: {size:,} bytes" + Color.N)
        
        # Check if minified
        is_minified = '.min.js' in js_url or size > 200000 or content.count('\n') < 10
        print(Color.R if is_minified else Color.G + 
              f" Minified: {'YES' if is_minified else 'No'}" + Color.N)
        
        # Data store for this file
        file_result = {
            "file": js_url,
            "size": size,
            "minified": is_minified,
            "apis": [],
            "params": [],
            "secrets": [],
            "risky_funcs": [],
            "comments": [],
            "endpoints": []
        }
        
        # Extract data
        self.extract_apis(content, file_result, results_dict)
        self.extract_params(content, file_result, results_dict)
        self.extract_secrets(content, file_result, results_dict)
        self.extract_risky_funcs(content, file_result)
        self.extract_comments(content, file_result, results_dict)
        self.extract_endpoints(content, file_result)
        
        # Save to main results
        with self.lock:
            results_dict["raw"].append(file_result)
        
        print(Color.C + "────────────────────────────────────" + Color.N)
    
    def extract_apis(self, content, file_result, results_dict):
        """Extract API endpoints"""
        found = []
        
        # API regex
        for pattern in API_REGEX:
            matches = re.findall(pattern, content)
            for match in matches:
                if match and match not in found:
                    found.append(match)
                    file_result["apis"].append(match)
                    with self.lock:
                        if match not in results_dict["api_endpoints"]:
                            results_dict["api_endpoints"].append(match)
        
        # Fetch regex
        for pattern in FETCH_REGEX:
            matches = re.findall(pattern, content)
            for match in matches:
                if match and match not in found:
                    found.append(match)
                    file_result["apis"].append(match)
                    with self.lock:
                        if match not in results_dict["api_endpoints"]:
                            results_dict["api_endpoints"].append(match)
        
        if found:
            print(Color.B + "\n [+] API ENDPOINTS" + Color.N)
            for api in found[:10]:
                print(Color.G + f"   → {api}" + Color.N)
            if len(found) > 10:
                print(Color.Y + f"   → ... and {len(found)-10} more" + Color.N)
    
    def extract_params(self, content, file_result, results_dict):
        """Extract parameters"""
        found = []
        
        for pattern in PARAM_REGEX:
            matches = re.findall(pattern, content)
            for match in matches:
                if match and match not in found:
                    found.append(match)
                    file_result["params"].append(match)
                    with self.lock:
                        if match not in results_dict["params"]:
                            results_dict["params"].append(match)
        
        if found:
            print(Color.B + "\n [+] PARAMETERS" + Color.N)
            for param in found[:10]:
                print(Color.Y + f"   → {param}" + Color.N)
    
    def extract_secrets(self, content, file_result, results_dict):
        """Extract secrets and keys"""
        found = []
        
        for pattern, name in SECRET_REGEX:
            matches = re.findall(pattern, content)
            for match in matches:
                if isinstance(match, tuple):
                    match = match[0]
                if match and len(str(match)) > 5 and match not in found:
                    found.append(f"{name}: {match[:30]}..." if len(match) > 30 else f"{name}: {match}")
                    file_result["secrets"].append({
                        "type": name,
                        "value": match[:100]
                    })
                    with self.lock:
                        if match not in results_dict["keys_found"]:
                            results_dict["keys_found"].append(match)
        
        if found:
            print(Color.B + "\n [+] SECRETS / KEYS" + Color.N)
            for secret in found[:10]:
                print(Color.R + f"   → {secret}" + Color.N)
    
    def extract_risky_funcs(self, content, file_result):
        """Extract risky functions"""
        found = []
        
        for func, desc in RISKY_FUNCS:
            if func in content:
                found.append(f"{func} - {desc}")
                file_result["risky_funcs"].append(func)
        
        if found:
            print(Color.B + "\n [+] SUSPICIOUS CODE" + Color.N)
            for func in found[:10]:
                print(Color.R + f"   → {func}" + Color.N)
    
    def extract_comments(self, content, file_result, results_dict):
        """Extract comments that might contain useful info"""
        found = []
        
        for pattern, name, *flags in COMMENT_REGEX:
            flag = flags[0] if flags else 0
            matches = re.findall(pattern, content, flag)
            for match in matches:
                if isinstance(match, tuple):
                    match = match[0]
                text = match.strip()
                if text and len(text) > 5 and len(text) < 200:
                    if not any(x in text.lower() for x in ['copyright', 'license', 'all rights']):
                        found.append(text[:100])
                        file_result["comments"].append(text[:500])
                        with self.lock:
                            if text[:100] not in results_dict["comments"]:
                                results_dict["comments"].append(text[:100])
        
        if found:
            print(Color.B + "\n [+] COMMENT LEAKS" + Color.N)
            for comment in found[:10]:
                print(Color.Y + f"   → {comment}" + Color.N)
    
    def extract_endpoints(self, content, file_result):
        """Extract potential endpoints from URLs in JS"""
        url_pattern = r'https?://[^\s"\'<>]+'
        matches = re.findall(url_pattern, content)
        
        for url in matches[:20]:
            file_result["endpoints"].append(url)


# ============================================================
# MAIN FUNCTION
# ============================================================

def run(target):
    """Main JS analyzer function"""
    print(Color.C + "\n[+] JavaScript Deep Analyzer — Passive Mode\n" + Color.N)
    
    if not target:
        print(Color.R + "[!] No target set" + Color.N)
        return
    
    # Normalize target
    if not target.startswith(('http://', 'https://')):
        target = 'https://' + target
    
    result = {
        "target": target,
        "js_files": [],
        "api_endpoints": [],
        "keys_found": [],
        "params": [],
        "comments": [],
        "raw": []
    }
    
    # Fetch main page
    print(Color.Y + f"[*] Fetching main page: {target}" + Color.N)
    resp, error = safe_request(target, timeout=8)
    
    if error or not resp or resp.status_code >= 400:
        print(Color.R + f"[!] Connection failed: {error or resp.status_code}" + Color.N)
        return
    
    # Parse HTML and find JS files
    try:
        soup = BeautifulSoup(resp.text, 'html.parser')
    except:
        print(Color.R + "[!] Failed to parse HTML" + Color.N)
        return
    
    js_files = []
    for script in soup.find_all('script', src=True):
        src = script['src']
        if src.startswith('http'):
            js_files.append(src)
        else:
            js_files.append(urljoin(target, src))
    
    # Remove duplicates
    js_files = list(set(js_files))
    result["js_files"] = js_files
    
    print(Color.Y + f"\n[*] Found {len(js_files)} JavaScript files" + Color.N)
    
    if not js_files:
        print(Color.Y + "[-] No external JS files found" + Color.N)
        filename = save_log(target, "js_analyzer", result)
        print(Color.Y + f"\nSaved → {filename}\n" + Color.N)
        return
    
    # Analyze JS files (using threads but limited)
    analyzer = JSAnalyzer()
    threads = []
    max_threads = min(5, len(js_files))  # Limit threads
    
    for i in range(0, len(js_files), max_threads):
        batch = js_files[i:i+max_threads]
        for js_url in batch:
            t = threading.Thread(target=analyzer.analyze_js_file, args=(js_url, target, result))
            t.start()
            threads.append(t)
        
        # Wait for this batch
        for t in threads:
            t.join()
        threads = []
    
    # Summary
    print(Color.C + "\n┌─ JS ANALYSIS SUMMARY ─────────────────┐" + Color.N)
    print(f"  {Color.Y}JS Files Analyzed:{Color.N} {len(js_files)}")
    print(f"  {Color.Y}API Endpoints Found:{Color.N} {len(result['api_endpoints'])}")
    print(f"  {Color.Y}Secrets Found:{Color.N} {Color.R if result['keys_found'] else Color.G}{len(result['keys_found'])}{Color.N}")
    print(f"  {Color.Y}Parameters Found:{Color.N} {len(result['params'])}")
    print(f"  {Color.Y}Comments Found:{Color.N} {len(result['comments'])}")
    print(Color.C + "└────────────────────────────────────┘" + Color.N)
    
    if result['keys_found']:
        print(Color.R + f"\n[!] Found {len(result['keys_found'])} potential secrets!" + Color.N)
        print(Color.Y + "    Review these manually - they could be critical!" + Color.N)
    
    # Save results
    filename = save_log(target, "js_analyzer", result)
    print(Color.Y + f"\nSaved → {filename}\n" + Color.N)