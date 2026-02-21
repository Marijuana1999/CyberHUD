#!/usr/bin/env python3

# modules/headers.py
import requests
from core.core import Color, save_log, safe_request

SECURITY_HEADERS = {
    "strict-transport-security": {
        "description": "Enforces HTTPS to prevent downgrade attacks",
        "risk": "HIGH"
    },
    "content-security-policy": {
        "description": "Prevents XSS and data injection",
        "risk": "CRITICAL"
    },
    "x-frame-options": {
        "description": "Protects against Clickjacking",
        "risk": "HIGH"
    },
    "x-content-type-options": {
        "description": "Prevents MIME sniffing",
        "risk": "MEDIUM"
    },
    "referrer-policy": {
        "description": "Controls referrer info leakage",
        "risk": "MEDIUM"
    },
    "permissions-policy": {
        "description": "Controls browser feature permissions",
        "risk": "MEDIUM"
    },
    "expect-ct": {
        "description": "Prevents misissued certificates",
        "risk": "LOW"
    },
    "x-xss-protection": {
        "description": "Legacy XSS protection (deprecated but still used)",
        "risk": "LOW"
    },
    "access-control-allow-origin": {
        "description": "CORS policy",
        "risk": "MEDIUM"
    }
}

INFO_HEADERS = {
    "server": "Web server software",
    "x-powered-by": "Technology stack",
    "via": "Proxy/CDN information",
    "x-aspnet-version": "ASP.NET version",
    "x-aspnetmvc-version": "ASP.NET MVC version"
}

def analyze_cors(headers):
    """Analyze CORS configuration"""
    issues = []
    acao = headers.get("access-control-allow-origin")
    
    if acao:
        if acao == "*":
            issues.append("Wildcard CORS (*) - Allows any origin")
        elif acao.startswith("http"):
            issues.append(f"Specific origin allowed: {acao}")
    
    acc = headers.get("access-control-allow-credentials")
    if acc and acc.lower() == "true" and acao == "*":
        issues.append("CRITICAL: Credentials allowed with wildcard CORS")
    
    return issues

def analyze_cookies(response):
    """Analyze cookie security from response"""
    cookie_issues = []
    
    if hasattr(response, 'cookies') and response.cookies:
        for cookie in response.cookies:
            name = cookie.name
            secure = cookie.secure if hasattr(cookie, 'secure') else False
            httponly = cookie.has_nonstandard_attr("HttpOnly") if hasattr(cookie, 'has_nonstandard_attr') else False
            
            if not secure:
                cookie_issues.append(f"Cookie '{name}' missing Secure flag")
            if not httponly:
                cookie_issues.append(f"Cookie '{name}' missing HttpOnly flag")
    
    return cookie_issues

def run(target):
    """Main HTTP headers scanner"""
    print(Color.C + "\n[+] HTTP Security Headers Audit\n" + Color.N)
    
    if not target:
        print(Color.R + "[!] No target set" + Color.N)
        return
    
    # Try both HTTP and HTTPS
    urls = [f"https://{target}", f"http://{target}"]
    
    result = {
        "target": target,
        "url_used": None,
        "status_code": None,
        "headers": {},
        "security_headers": {},
        "info_headers": {},
        "missing": [],
        "cors_issues": [],
        "cookie_issues": [],
        "raw_headers": {}
    }
    
    response = None
    url_used = None
    
    # Try URLs
    for url in urls:
        print(Color.Y + f"[*] Trying {url}..." + Color.N)
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
    
    # Get headers (case-insensitive)
    headers = {k.lower(): v for k, v in response.headers.items()}
    result["raw_headers"] = dict(response.headers)
    result["headers"] = headers
    
    print(Color.Y + f"\n[*] Analyzing security headers for: {url_used}\n" + Color.N)
    
    # Check security headers
    print(Color.C + "┌─ SECURITY HEADERS ───────────────────┐" + Color.N)
    
    for header, info in SECURITY_HEADERS.items():
        if header in headers:
            status = Color.G + "✓ PRESENT" + Color.N
            result["security_headers"][header] = headers[header]
            
            # Special analysis for certain headers
            if header == "access-control-allow-origin":
                cors_issues = analyze_cors(headers)
                result["cors_issues"].extend(cors_issues)
        else:
            status = Color.R + "✗ MISSING" + Color.N
            result["missing"].append({
                "header": header,
                "description": info["description"],
                "risk": info["risk"]
            })
        
        print(f"  {Color.Y}{header:30}{Color.N} {status}")
    
    print(Color.C + "└────────────────────────────────────┘" + Color.N)
    
    # Information disclosure headers
    print(Color.C + "\n┌─ INFORMATION HEADERS ────────────────┐" + Color.N)
    
    for header, description in INFO_HEADERS.items():
        if header in headers:
            value = headers[header]
            print(f"  {Color.Y}{header:20}{Color.N} {Color.C}{value[:50]}{Color.N}")
            result["info_headers"][header] = value
            if len(value) > 50:
                print(f"  {' ' * 22}{Color.C}{value[50:100]}{Color.N}")
    
    print(Color.C + "└────────────────────────────────────┘" + Color.N)
    
    # Cookie analysis
    cookie_issues = analyze_cookies(response)
    if cookie_issues:
        result["cookie_issues"] = cookie_issues
        print(Color.C + "\n┌─ COOKIE ISSUES ──────────────────────┐" + Color.N)
        for issue in cookie_issues:
            print(f"  {Color.R}⚠ {issue}{Color.N}")
        print(Color.C + "└────────────────────────────────────┘" + Color.N)
    
    # Summary of missing critical headers
    if result["missing"]:
        critical_missing = [h for h in result["missing"] if h["risk"] == "CRITICAL"]
        high_missing = [h for h in result["missing"] if h["risk"] == "HIGH"]
        
        if critical_missing:
            print(Color.R + f"\n[!] Missing {len(critical_missing)} CRITICAL security headers!" + Color.N)
        if high_missing:
            print(Color.Y + f"[!] Missing {len(high_missing)} HIGH security headers" + Color.N)
    
    # CORS issues
    if result["cors_issues"]:
        print(Color.R + f"\n[!] CORS Issues: {len(result['cors_issues'])}" + Color.N)
        for issue in result["cors_issues"]:
            print(f"  {Color.R}⚠ {issue}{Color.N}")
    
    # Save results
    filename = save_log(target, "headers", result)
    print(Color.Y + f"\nSaved → {filename}\n" + Color.N)