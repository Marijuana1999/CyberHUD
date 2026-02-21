#!/usr/bin/env python3

# modules/open_redirect.py
import re
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse
from core.core import Color, save_log, safe_request

# ============================================================
# CONFIGURATION
# ============================================================

REDIRECT_PARAMS = [
    # Common redirect parameters
    "url", "next", "redirect", "return", "return_to", "return_url",
    "redirect_to", "redirect_url", "goto", "dest", "destination",
    "out", "view", "dir", "path", "continue", "continue_to",
    "forward", "forward_to", "to", "target", "r", "link", "href",
    "page", "file", "load", "read", "document", "folder",
    "site", "html", "data", "location", "uri", "u", "q",
    
    # Less common but still used
    "callback", "cback", "next_page", "prev", "previous",
    "ret_url", "ret_uri", "redir", "redirect_uri", "redirect_uri",
    "referer", "referrer", "source", "src"
]

TEST_PAYLOADS = [
    # External domains
    "https://evil.com",
    "https://attacker.com",
    "https://google.com",
    "//evil.com",
    "//google.com",
    
    # Protocol bypass
    "///evil.com",
    "////evil.com",
    "https:/evil.com",
    "http:/evil.com",
    
    # URL encoding
    "https%3A%2F%2Fevil.com",
    "%68%74%74%70%73%3a%2f%2f%65%76%69%6c%2e%63%6f%6d",
    
    # Domain confusion
    "https://evil.com@google.com",
    "https://google.com.evil.com",
    "https://evil.com/google.com",
    
    # Path traversal
    "/\\evil.com",
    "//evil.com/",
    "https://evil.com?",
    
    # Data URIs (rare but possible)
    "data:text/html;base64,PHNjcmlwdD5hbGVydCgxKTwvc2NyaXB0Pg==",
    
    # JavaScript
    "javascript:alert(1)",
    "javascript:window.location='https://evil.com'",
    
    # Null byte (for old PHP versions)
    "https://evil.com%00",
    
    # Basic auth bypass
    "https://evil.com@google.com",
    "https://evil.com#@google.com",
]

# ============================================================
# DETECTION FUNCTIONS
# ============================================================

def detect_redirect(response, follow=False):
    """Detect redirect in response"""
    result = {
        "is_redirect": False,
        "type": None,
        "location": None,
        "code": response.status_code
    }
    
    # HTTP redirect codes
    if response.status_code in [301, 302, 303, 307, 308]:
        result["is_redirect"] = True
        result["type"] = "HTTP"
        result["location"] = response.headers.get("Location")
        return result
    
    # Check for meta refresh
    text = response.text.lower()
    meta_refresh = re.search(r'<meta.*?http-equiv=["\']refresh["\'].*?content=["\'](\d+);\s*url=([^"\']+)', text, re.IGNORECASE)
    if meta_refresh:
        result["is_redirect"] = True
        result["type"] = "Meta Refresh"
        result["location"] = meta_refresh.group(2)
        return result
    
    # Check for JavaScript redirect
    js_patterns = [
        r'window\.location\s*=\s*["\']([^"\']+)',
        r'window\.location\.href\s*=\s*["\']([^"\']+)',
        r'window\.location\.replace\(["\']([^"\']+)',
        r'document\.location\s*=\s*["\']([^"\']+)',
        r'document\.location\.href\s*=\s*["\']([^"\']+)',
        r'window\.navigate\(["\']([^"\']+)',
        r'location\.href\s*=\s*["\']([^"\']+)',
        r'location\.replace\(["\']([^"\']+)',
        r'window\.open\(["\']([^"\']+)',
    ]
    
    for pattern in js_patterns:
        match = re.search(pattern, text)
        if match:
            result["is_redirect"] = True
            result["type"] = "JavaScript"
            result["location"] = match.group(1)
            return result
    
    return result

def is_same_domain(url1, url2):
    """Check if two URLs have the same domain"""
    try:
        dom1 = urlparse(url1).netloc.lower()
        dom2 = urlparse(url2).netloc.lower()
        return dom1 == dom2
    except:
        return False

def extract_urls_with_params(base_url, target_domain):
    """Extract URLs with parameters from base URL"""
    urls = [base_url]
    
    # Try to parse parameters from base URL
    parsed = urlparse(base_url)
    if parsed.query:
        urls.append(base_url)
    
    return urls

def build_test_url(base_url, param_name, payload):
    """Build test URL with payload"""
    parsed = urlparse(base_url)
    params = parse_qs(parsed.query)
    
    # Add or replace parameter
    params[param_name] = [payload]
    
    new_query = urlencode(params, doseq=True)
    new_parsed = parsed._replace(query=new_query)
    return urlunparse(new_parsed)

# ============================================================
# MAIN FUNCTION
# ============================================================

def run(target):
    """Main open redirect scanner"""
    print(Color.C + "\n[+] Open Redirect Scanner\n" + Color.N)
    
    if not target:
        print(Color.R + "[!] No target set" + Color.N)
        return
    
    # Try both HTTP and HTTPS
    base_urls = [f"https://{target}", f"http://{target}"]
    
    result = {
        "target": target,
        "url_used": None,
        "tested_urls": [],
        "vulnerable": [],
        "safe": [],
        "errors": [],
        "summary": {
            "total_tests": 0,
            "vulnerable_count": 0,
            "safe_count": 0,
            "params_tested": 0
        }
    }
    
    response = None
    base_used = None
    
    # Determine which base URL works
    for base in base_urls:
        print(Color.Y + f"[*] Testing {base}..." + Color.N)
        resp, error = safe_request(base, timeout=8)
        
        if not error and resp and resp.status_code < 500:
            response = resp
            base_used = base
            result["url_used"] = base
            print(Color.G + f"[✓] Connected to {base}" + Color.N)
            break
        elif resp:
            print(Color.Y + f"    Response: {resp.status_code}" + Color.N)
        else:
            print(Color.Y + f"    Error: {error}" + Color.N)
    
    if not response:
        print(Color.R + "[!] Could not connect to target" + Color.N)
        return
    
    # Get base domain for comparison
    base_domain = urlparse(base_used).netloc.lower()
    
    # Extract URLs to test (from current page if needed)
    urls_to_test = [base_used]
    
    print(Color.Y + f"\n[*] Found {len(urls_to_test)} URLs to test" + Color.N)
    print(Color.Y + f"[*] Testing {len(REDIRECT_PARAMS)} redirect parameters with {len(TEST_PAYLOADS)} payloads\n" + Color.N)
    
    # Test each URL
    for url in urls_to_test:
        parsed = urlparse(url)
        params = parse_qs(parsed.query)
        
        # If no params, try adding test params
        if not params:
            params = {"test": ["1"]}
        
        result["summary"]["params_tested"] += len(params)
        
        # Test each parameter
        for param_name in params.keys():
            if param_name.lower() not in REDIRECT_PARAMS:
                continue  # Skip non-redirect parameters
            
            print(Color.C + f"\n[Testing] Parameter: {Color.Y}{param_name}{Color.N}")
            
            # Test each payload
            for payload in TEST_PAYLOADS:
                test_url = build_test_url(url, param_name, payload)
                result["tested_urls"].append(test_url)
                result["summary"]["total_tests"] += 1
                
                # Make request
                resp, error = safe_request(test_url, timeout=8, allow_redirects=False)
                
                if error:
                    print(f"  {Color.R}✗ Error: {error}{Color.N}")
                    result["errors"].append({"url": test_url, "error": error})
                    continue
                
                # Check for redirect
                redirect_info = detect_redirect(resp)
                
                if redirect_info["is_redirect"]:
                    location = redirect_info["location"]
                    
                    # Check if redirect goes to external domain
                    if location:
                        # Check if it's our payload
                        if any(p in location for p in ['evil', 'attacker', 'google']):
                            print(f"  {Color.R}⚠ VULNERABLE: {param_name}={payload} → {location[:50]}{Color.N}")
                            
                            result["vulnerable"].append({
                                "url": test_url,
                                "parameter": param_name,
                                "payload": payload,
                                "redirect_to": location,
                                "redirect_type": redirect_info["type"],
                                "status_code": resp.status_code
                            })
                            result["summary"]["vulnerable_count"] += 1
                        else:
                            # Redirect but not to our payload (might be safe)
                            redirect_domain = urlparse(location).netloc.lower()
                            if redirect_domain and redirect_domain != base_domain and 'evil' not in location:
                                print(f"  {Color.Y}⚠ Redirect to: {location[:50]}{Color.N}")
                            else:
                                print(f"  {Color.G}✓ Safe redirect (same domain){Color.N}")
                            
                            result["safe"].append({
                                "url": test_url,
                                "parameter": param_name,
                                "payload": payload,
                                "redirect_to": location,
                                "redirect_type": redirect_info["type"]
                            })
                            result["summary"]["safe_count"] += 1
                    else:
                        print(f"  {Color.G}✓ No redirect{Color.N}")
                        result["safe"].append({
                            "url": test_url,
                            "parameter": param_name,
                            "payload": payload,
                            "result": "no_redirect"
                        })
                        result["summary"]["safe_count"] += 1
                else:
                    print(f"  {Color.G}✓ No redirect{Color.N}")
                    result["safe"].append({
                        "url": test_url,
                        "parameter": param_name,
                        "payload": payload,
                        "result": "no_redirect"
                    })
                    result["summary"]["safe_count"] += 1
    
    # Summary
    print(Color.C + "\n┌─ OPEN REDIRECT SUMMARY ──────────────┐" + Color.N)
    print(f"  {Color.Y}Total Tests:{Color.N} {result['summary']['total_tests']}")
    print(f"  {Color.Y}Parameters Tested:{Color.N} {result['summary']['params_tested']}")
    
    vuln_color = Color.R if result['summary']['vulnerable_count'] > 0 else Color.G
    print(f"  {Color.Y}Vulnerable:{Color.N} {vuln_color}{result['summary']['vulnerable_count']}{Color.N}")
    
    safe_color = Color.G
    print(f"  {Color.Y}Safe:{Color.N} {safe_color}{result['summary']['safe_count']}{Color.N}")
    
    if result['errors']:
        print(f"  {Color.Y}Errors:{Color.N} {Color.R}{len(result['errors'])}{Color.N}")
    
    print(Color.C + "└────────────────────────────────────┘" + Color.N)
    
    if result['vulnerable']:
        print(Color.R + f"\n[!] Found {result['summary']['vulnerable_count']} open redirect vulnerabilities!" + Color.N)
        print(Color.Y + "    These can be used for phishing attacks." + Color.N)
        
        for vuln in result['vulnerable'][:10]:
            print(f"  {Color.R}• {vuln['parameter']} = {vuln['payload']}{Color.N}")
    
    # Save results
    filename = save_log(target, "open_redirect", result)
    print(Color.Y + f"\nSaved → {filename}\n" + Color.N)