#!/usr/bin/env python3

# modules/cors.py
import requests
from core.core import Color, save_log, safe_request

TEST_ORIGINS = [
    "https://evil.com",
    "https://attacker.com",
    "http://localhost",
    "null",
    "https://example.com",
    "http://192.168.1.1",
    "https://evil.com:8080",
    "https://sub.evil.com"
]

SENSITIVE_METHODS = ["GET", "POST", "PUT", "DELETE", "OPTIONS"]

def analyze_cors_headers(headers, origin_tested=None):
    """Analyze CORS headers for misconfigurations"""
    issues = []
    
    acao = headers.get("access-control-allow-origin")
    acc = headers.get("access-control-allow-credentials")
    acac = headers.get("access-control-allow-credentials")
    acah = headers.get("access-control-allow-headers", "")
    acam = headers.get("access-control-allow-methods", "")
    acma = headers.get("access-control-max-age")
    aceh = headers.get("access-control-expose-headers")
    
    analysis = {
        "acao": acao,
        "credentials": acc,
        "allow_headers": acah,
        "allow_methods": acam,
        "max_age": acma,
        "expose_headers": aceh,
        "issues": []
    }
    
    # Check for wildcard with credentials
    if acao == "*" and acc and acc.lower() == "true":
        issues.append("CRITICAL: Wildcard ACAO (*) with credentials allowed")
        analysis["severity"] = "CRITICAL"
    
    # Check for null origin
    if acao == "null":
        issues.append("HIGH: Null origin allowed - dangerous for file:// origins")
        analysis["severity"] = "HIGH"
    
    # Check for origin reflection
    if origin_tested and acao == origin_tested:
        issues.append(f"HIGH: Origin reflection - ACAO echoes '{origin_tested}'")
        analysis["severity"] = "HIGH"
        analysis["reflection"] = True
    
    # Check for missing ACAO with sensitive data
    if not acao and acc:
        issues.append("MEDIUM: Credentials allowed but no ACAO specified")
    
    # Check for overly permissive methods
    if acam and "*" in acam:
        issues.append("MEDIUM: Wildcard allowed methods (*)")
    
    # Check for overly permissive headers
    if acah and "*" in acah:
        issues.append("LOW: Wildcard allowed headers (*)")
    
    # Check for sensitive methods exposed
    if acam:
        methods = [m.strip().upper() for m in acam.split(",")]
        sensitive = [m for m in methods if m in SENSITIVE_METHODS and m not in ["GET", "POST"]]
        if sensitive:
            issues.append(f"MEDIUM: Exposed sensitive methods: {', '.join(sensitive)}")
    
    analysis["issues"] = issues
    return analysis

def test_preflight_request(url, origin, method="GET"):
    """Test CORS preflight (OPTIONS) request"""
    headers = {
        "Origin": origin,
        "Access-Control-Request-Method": method,
        "Access-Control-Request-Headers": "X-Custom-Header"
    }
    
    try:
        resp, error = safe_request(url, method="OPTIONS", headers=headers, timeout=8)
        if not error and resp:
            return {
                "status": resp.status_code,
                "headers": dict(resp.headers),
                "success": True
            }
    except:
        pass
    
    return {"success": False}

def run(target):
    """Main CORS analyzer function"""
    print(Color.C + "\n[+] CORS Misconfiguration Analyzer\n" + Color.N)
    
    if not target:
        print(Color.R + "[!] No target set" + Color.N)
        return
    
    # Try both HTTP and HTTPS
    urls = [f"https://{target}", f"http://{target}"]
    
    result = {
        "target": target,
        "url_used": None,
        "status_code": None,
        "cors_configuration": {},
        "origin_tests": {},
        "preflight_tests": {},
        "issues": [],
        "risk_level": "LOW",
        "raw_headers": {}
    }
    
    response = None
    url_used = None
    
    # Try URLs
    for url in urls:
        print(Color.Y + f"[*] Testing {url}..." + Color.N)
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
    
    # Get initial CORS headers
    headers = dict(response.headers)
    result["raw_headers"] = headers
    
    initial_analysis = analyze_cors_headers(headers)
    result["cors_configuration"]["initial"] = initial_analysis
    result["issues"].extend(initial_analysis["issues"])
    
    print(Color.Y + f"\n[*] Analyzing CORS configuration...\n" + Color.N)
    
    # Display initial CORS headers
    print(Color.C + "┌─ INITIAL CORS HEADERS ───────────────┐" + Color.N)
    cors_headers = {k: v for k, v in headers.items() if k.lower().startswith("access-control")}
    
    if cors_headers:
        for h, v in cors_headers.items():
            print(f"  {Color.Y}{h}:{Color.N} {Color.C}{v}{Color.N}")
    else:
        print(f"  {Color.Y}No CORS headers detected{Color.N}")
    print(Color.C + "└────────────────────────────────────┘" + Color.N)
    
    # Test different origins
    print(Color.C + "\n┌─ ORIGIN REFLECTION TESTS ────────────┐" + Color.N)
    
    for origin in TEST_ORIGINS[:5]:  # Test first 5 origins
        print(f"  {Color.Y}Testing origin: {origin}{Color.N}")
        
        test_headers = {"Origin": origin}
        resp, error = safe_request(url_used, headers=test_headers, timeout=8)
        
        if not error and resp:
            acao = resp.headers.get("Access-Control-Allow-Origin")
            acc = resp.headers.get("Access-Control-Allow-Credentials")
            
            result["origin_tests"][origin] = {
                "acao": acao,
                "credentials": acc,
                "status": resp.status_code
            }
            
            if acao == origin:
                print(f"    {Color.R}⚠ REFLECTED! ACAO = {origin}{Color.N}")
                result["issues"].append(f"Origin reflection for {origin}")
            elif acao:
                print(f"    {Color.G}✓ ACAO = {acao}{Color.N}")
            else:
                print(f"    {Color.G}✓ No ACAO header{Color.N}")
    
    print(Color.C + "└────────────────────────────────────┘" + Color.N)
    
    # Test preflight requests
    print(Color.C + "\n┌─ PREFLIGHT (OPTIONS) TESTS ──────────┐" + Color.N)
    
    for method in ["GET", "POST", "PUT", "DELETE"]:
        print(f"  {Color.Y}Testing OPTIONS with {method}...{Color.N}")
        
        preflight = test_preflight_request(url_used, "https://evil.com", method)
        result["preflight_tests"][method] = preflight
        
        if preflight["success"]:
            acam = preflight["headers"].get("access-control-allow-methods", "")
            if method in acam:
                print(f"    {Color.R}⚠ {method} allowed in preflight{Color.N}")
            else:
                print(f"    {Color.G}✓ {method} properly restricted{Color.N}")
    
    print(Color.C + "└────────────────────────────────────┘" + Color.N)
    
    # Determine risk level
    critical_issues = [i for i in result["issues"] if "CRITICAL" in i]
    high_issues = [i for i in result["issues"] if "HIGH" in i]
    medium_issues = [i for i in result["issues"] if "MEDIUM" in i]
    
    if critical_issues:
        result["risk_level"] = "CRITICAL"
    elif high_issues:
        result["risk_level"] = "HIGH"
    elif medium_issues:
        result["risk_level"] = "MEDIUM"
    elif result["issues"]:
        result["risk_level"] = "LOW"
    
    # Summary
    print(Color.C + "\n┌─ CORS ANALYSIS SUMMARY ──────────────┐" + Color.N)
    
    risk_color = Color.G
    if result["risk_level"] == "CRITICAL":
        risk_color = Color.R
    elif result["risk_level"] == "HIGH":
        risk_color = Color.R
    elif result["risk_level"] == "MEDIUM":
        risk_color = Color.Y
    
    print(f"  {Color.Y}Risk Level:{Color.N} {risk_color}{result['risk_level']}{Color.N}")
    print(f"  {Color.Y}Issues Found:{Color.N} {len(result['issues'])}")
    print(f"  {Color.Y}Origins Tested:{Color.N} {len(result['origin_tests'])}")
    
    print(Color.C + "└────────────────────────────────────┘" + Color.N)
    
    if result["issues"]:
        print(Color.R + f"\n[!] CORS Issues Detected:" + Color.N)
        for issue in result["issues"][:10]:
            print(f"  {Color.R}⚠ {issue}{Color.N}")
        if len(result["issues"]) > 10:
            print(f"  {Color.Y}... and {len(result['issues'])-10} more{Color.N}")
    else:
        print(Color.G + "\n[✓] No CORS misconfigurations detected" + Color.N)
    
    # Save results
    filename = save_log(target, "cors", result)
    print(Color.Y + f"\nSaved → {filename}\n" + Color.N)