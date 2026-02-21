#!/usr/bin/env python3

# modules/cookies.py
import requests
from core.core import Color, save_log, safe_request

def analyze_cookie_security(cookie):
    """Analyze a single cookie for security issues"""
    issues = []
    
    name = cookie.name if hasattr(cookie, 'name') else ''
    value = cookie.value if hasattr(cookie, 'value') else ''
    
    # Check flags
    secure = False
    httponly = False
    samesite = None
    
    # Different cookie libraries have different attributes
    if hasattr(cookie, 'secure'):
        secure = cookie.secure
    
    if hasattr(cookie, 'has_nonstandard_attr'):
        httponly = cookie.has_nonstandard_attr('HttpOnly')
    elif hasattr(cookie, '_rest'):
        httponly = 'httponly' in cookie._rest
    
    if hasattr(cookie, '_rest') and 'samesite' in cookie._rest:
        samesite = cookie._rest['samesite'].lower()
    
    # Check value length (session IDs should be long)
    value_length = len(value)
    if value_length < 16 and ('session' in name.lower() or 'id' in name.lower()):
        issues.append(f"Short session ID ({value_length} chars)")
    
    # Missing Secure flag
    if not secure:
        issues.append("Missing Secure flag")
    
    # Missing HttpOnly for session cookies
    if not httponly and ('session' in name.lower() or 'id' in name.lower()):
        issues.append("Missing HttpOnly flag on session cookie")
    
    # SameSite analysis
    if not samesite:
        issues.append("Missing SameSite attribute")
    elif samesite == 'none' and not secure:
        issues.append("SameSite=None without Secure flag")
    elif samesite == 'lax':
        pass  # This is actually good
    elif samesite == 'strict':
        pass  # This is very good
    
    # Domain scope (if too broad)
    if hasattr(cookie, 'domain') and cookie.domain and cookie.domain.startswith('.'):
        issues.append(f"Broad domain scope: {cookie.domain}")
    
    # Path scope
    if hasattr(cookie, 'path') and cookie.path == '/':
        # This is normal, not an issue
        pass
    
    return {
        "name": name,
        "value_length": value_length,
        "secure": secure,
        "httponly": httponly,
        "samesite": samesite,
        "domain": getattr(cookie, 'domain', None),
        "path": getattr(cookie, 'path', None),
        "expires": getattr(cookie, 'expires', None),
        "issues": issues
    }

def analyze_all_cookies(cookies):
    """Analyze all cookies from a response"""
    results = []
    all_issues = []
    
    for cookie in cookies:
        analysis = analyze_cookie_security(cookie)
        results.append(analysis)
        all_issues.extend([f"{analysis['name']}: {issue}" for issue in analysis['issues']])
    
    return results, all_issues

def check_session_fingerprinting(cookies):
    """Check if cookies can be used for fingerprinting"""
    fp_indicators = []
    
    for cookie in cookies:
        name = cookie.name.lower() if hasattr(cookie, 'name') else ''
        value = cookie.value if hasattr(cookie, 'value') else ''
        
        # Check for fingerprinting patterns
        if any(x in name for x in ['ga', '_gid', '_ga', '_fbp', '_hj']):
            fp_indicators.append(f"Analytics cookie: {cookie.name}")
        
        # Check for tracking parameters in value
        if len(value) > 50 and any(x in name for x in ['id', 'token']):
            fp_indicators.append(f"Long identifier: {cookie.name}")
    
    return fp_indicators

def run(target):
    """Main cookie analyzer function"""
    print(Color.C + "\n[+] Cookie Security Analyzer\n" + Color.N)
    
    if not target:
        print(Color.R + "[!] No target set" + Color.N)
        return
    
    # Try both HTTP and HTTPS
    urls = [f"https://{target}", f"http://{target}"]
    
    result = {
        "target": target,
        "url_used": None,
        "status_code": None,
        "cookies": [],
        "issues": [],
        "fingerprinting": [],
        "summary": {
            "total_cookies": 0,
            "secure_flags": 0,
            "httponly_flags": 0,
            "samesite_flags": 0
        }
    }
    
    response = None
    url_used = None
    
    # Try URLs
    for url in urls:
        print(Color.Y + f"[*] Checking {url}..." + Color.N)
        resp, error = safe_request(url, timeout=8)
        
        if not error and resp and resp.status_code < 500:
            response = resp
            url_used = url
            print(Color.G + f"[✓] Connected to {url}" + Color.N)
            break
        elif resp:
            print(Color.Y + f"    Response: {resp.status_code}" + Color.N)
        else:
            print(Color.Y + f"    Error: {error}" + Color.N)
    
    if not response:
        print(Color.R + "[!] Could not connect to target" + Color.N)
        return
    
    result["url_used"] = url_used
    result["status_code"] = response.status_code
    
    # Get cookies
    cookies = response.cookies
    cookie_list = list(cookies)
    
    if not cookie_list:
        print(Color.Y + "\n[!] No cookies were returned by the server." + Color.N)
        filename = save_log(target, "cookies", result)
        print(Color.Y + f"\nSaved → {filename}\n" + Color.N)
        return
    
    result["summary"]["total_cookies"] = len(cookie_list)
    print(Color.Y + f"\n[*] Found {len(cookie_list)} cookies.\n" + Color.N)
    
    # Analyze each cookie
    cookie_analyses, all_issues = analyze_all_cookies(cookie_list)
    result["cookies"] = cookie_analyses
    result["issues"] = all_issues
    
    # Update summary counts
    for cookie in cookie_analyses:
        if cookie["secure"]:
            result["summary"]["secure_flags"] += 1
        if cookie["httponly"]:
            result["summary"]["httponly_flags"] += 1
        if cookie["samesite"]:
            result["summary"]["samesite_flags"] += 1
    
    # Check for fingerprinting
    fp_indicators = check_session_fingerprinting(cookie_list)
    result["fingerprinting"] = fp_indicators
    
    # Display results
    for i, cookie in enumerate(cookie_analyses, 1):
        print(Color.C + f"[Cookie {i}] {Color.Y}{cookie['name']}{Color.N}")
        print(f"  {Color.B}Value length:{Color.N} {cookie['value_length']}")
        
        # Flags with colors
        secure_color = Color.G if cookie['secure'] else Color.R
        httponly_color = Color.G if cookie['httponly'] else Color.R
        samesite_color = Color.G if cookie['samesite'] else Color.R
        
        print(f"  {Color.B}Secure:{Color.N} {secure_color}{cookie['secure']}{Color.N}")
        print(f"  {Color.B}HttpOnly:{Color.N} {httponly_color}{cookie['httponly']}{Color.N}")
        print(f"  {Color.B}SameSite:{Color.N} {samesite_color}{cookie['samesite'] or 'None'}{Color.N}")
        
        if cookie.get('domain'):
            print(f"  {Color.B}Domain:{Color.N} {cookie['domain']}")
        if cookie.get('path'):
            print(f"  {Color.B}Path:{Color.N} {cookie['path']}")
        
        # Issues
        if cookie['issues']:
            print(f"  {Color.R}Issues:{Color.N}")
            for issue in cookie['issues']:
                print(f"    {Color.R}⚠ {issue}{Color.N}")
        else:
            print(f"  {Color.G}✓ No issues{Color.N}")
        
        print()
    
    # Summary
    print(Color.C + "┌─ COOKIE SECURITY SUMMARY ────────────┐" + Color.N)
    print(f"  {Color.Y}Total Cookies:{Color.N} {result['summary']['total_cookies']}")
    print(f"  {Color.Y}Secure Flag:{Color.N} {result['summary']['secure_flags']}/{result['summary']['total_cookies']}")
    print(f"  {Color.Y}HttpOnly Flag:{Color.N} {result['summary']['httponly_flags']}/{result['summary']['total_cookies']}")
    print(f"  {Color.Y}SameSite Flag:{Color.N} {result['summary']['samesite_flags']}/{result['summary']['total_cookies']}")
    print(Color.C + "└────────────────────────────────────┘" + Color.N)
    
    # Issues summary
    if result['issues']:
        print(Color.R + f"\n[!] Found {len(result['issues'])} cookie security issues:" + Color.N)
        for issue in result['issues'][:10]:
            print(f"  {Color.R}⚠ {issue}{Color.N}")
        if len(result['issues']) > 10:
            print(f"  {Color.Y}... and {len(result['issues'])-10} more{Color.N}")
    
    # Fingerprinting
    if result['fingerprinting']:
        print(Color.Y + f"\n[!] Possible fingerprinting cookies:" + Color.N)
        for fp in result['fingerprinting']:
            print(f"  {Color.Y}• {fp}{Color.N}")
    
    # Save results
    filename = save_log(target, "cookies", result)
    print(Color.Y + f"\nSaved → {filename}\n" + Color.N)