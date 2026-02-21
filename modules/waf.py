#!/usr/bin/env python3

# modules/waf.py
import re
from core.core import Color, save_log, safe_request

# WAF Signatures Database
WAF_SIGNATURES = {
    "Cloudflare": {
        "headers": ["cf-ray", "cf-cache-status", "cf-request-id"],
        "cookies": ["__cfduid", "__cf_bm"],
        "html": ["cloudflare", "cf-browser-verification", "cdn-cgi"],
        "response": [403, 503],
        "description": "Cloudflare CDN & Security"
    },
    "Sucuri": {
        "headers": ["x-sucuri-id", "x-sucuri-cache"],
        "cookies": ["sucuri_cloudproxy"],
        "html": ["sucuri", "cloudproxy"],
        "response": [403],
        "description": "Sucuri Website Firewall"
    },
    "Imperva (Incapsula)": {
        "headers": ["x-iinfo", "x-cdn"],
        "cookies": ["incap_ses", "visid_incap"],
        "html": ["incapsula", "_incapsula"],
        "response": [403],
        "description": "Imperva Incapsula WAF"
    },
    "AWS WAF": {
        "headers": ["x-amzn-requestid", "x-amz-cf-id"],
        "cookies": ["aws-waf-token"],
        "html": ["aws", "amazonaws"],
        "response": [403, 405],
        "description": "Amazon AWS WAF"
    },
    "ModSecurity": {
        "headers": ["x-modsecurity", "x-modsecurity-id"],
        "cookies": [],
        "html": ["mod_security", "modsecurity"],
        "response": [403, 406],
        "description": "ModSecurity Open Source WAF"
    },
    "F5 BIG-IP ASM": {
        "headers": ["x-waf", "x-waf-attack", "x-waf-score"],
        "cookies": ["TS", "BIGipServer"],
        "html": ["big-ip", "f5"],
        "response": [403],
        "description": "F5 BIG-IP Application Security Manager"
    },
    "Akamai": {
        "headers": ["x-akamai-", "x-akamai-cache"],
        "cookies": ["ak_bmsc", "bm_sz"],
        "html": ["akamai", "akamaighost"],
        "response": [403],
        "description": "Akamai Kona Site Defender"
    },
    "Barracuda": {
        "headers": ["x-barracuda", "x-waf"],
        "cookies": ["barra"],
        "html": ["barracuda"],
        "response": [403],
        "description": "Barracuda WAF"
    },
    "Fortinet FortiWeb": {
        "headers": ["x-fortiweb"],
        "cookies": ["fortiweb"],
        "html": ["fortiweb", "fortinet"],
        "response": [403],
        "description": "Fortinet FortiWeb"
    },
    "Citrix NetScaler": {
        "headers": ["x-netscaler", "via"],
        "cookies": ["netscaler"],
        "html": ["citrix", "netscaler"],
        "response": [403],
        "description": "Citrix NetScaler AppFirewall"
    },
    "Wordfence": {
        "headers": ["x-wordfence"],
        "cookies": ["wfvt"],
        "html": ["wordfence"],
        "response": [403],
        "description": "Wordfence WordPress Firewall"
    },
    "StackPath": {
        "headers": ["x-stackpath"],
        "cookies": ["stackpath"],
        "html": ["stackpath"],
        "response": [403],
        "description": "StackPath WAF"
    },
    "Comodo": {
        "headers": ["x-comodo"],
        "cookies": ["comodo"],
        "html": ["comodo"],
        "response": [403],
        "description": "Comodo WAF"
    },
    "Reblaze": {
        "headers": ["x-reblaze"],
        "cookies": ["reblaze"],
        "html": ["reblaze"],
        "response": [403],
        "description": "Reblaze WAF"
    }
}

def check_waf_by_headers(headers, cookies):
    """Check WAF signatures in headers and cookies"""
    detected = []
    headers_lower = {k.lower(): v.lower() for k, v in headers.items()}
    
    for waf_name, signatures in WAF_SIGNATURES.items():
        # Check headers
        for pattern in signatures["headers"]:
            if any(pattern.lower() in h for h in headers_lower.keys()):
                detected.append(waf_name)
                break
            if any(pattern.lower() in v for v in headers_lower.values()):
                if waf_name not in detected:
                    detected.append(waf_name)
                break
        
        # Check cookies if not already detected
        if waf_name not in detected and cookies:
            cookie_str = " ".join([f"{k}={v}" for k, v in cookies.items()]).lower()
            for pattern in signatures["cookies"]:
                if pattern.lower() in cookie_str:
                    detected.append(waf_name)
                    break
    
    return detected

def check_waf_by_html(html):
    """Check WAF signatures in HTML content"""
    detected = []
    html_lower = html.lower()
    
    for waf_name, signatures in WAF_SIGNATURES.items():
        for pattern in signatures["html"]:
            if pattern.lower() in html_lower:
                detected.append(waf_name)
                break
    
    return detected

def check_waf_by_response(status_code):
    """Check if response code indicates WAF"""
    suspicious = []
    
    # Common WAF block responses
    if status_code in [403, 406, 429, 503]:
        suspicious.append(f"Block page detected (HTTP {status_code})")
    
    return suspicious

def detect_waf_challenge(html):
    """Detect WAF challenge pages"""
    challenges = []
    
    challenge_patterns = [
        (r"cf-chl-bypass", "Cloudflare Challenge"),
        (r"cf-browser-verification", "Cloudflare Browser Check"),
        (r"captcha", "CAPTCHA Challenge"),
        (r"javascript challenge", "JavaScript Challenge"),
        (r"DDoS protection", "DDoS Protection"),
        (r"access denied", "Access Denied"),
        (r"security check", "Security Check")
    ]
    
    html_lower = html.lower()
    for pattern, name in challenge_patterns:
        if pattern.lower() in html_lower:
            challenges.append(name)
    
    return challenges

def run(target):
    """Main WAF detection function"""
    print(Color.C + "\n[+] WAF / Firewall Detection\n" + Color.N)
    
    if not target:
        print(Color.R + "[!] No target set" + Color.N)
        return
    
    # Try both HTTP and HTTPS
    urls = [f"https://{target}", f"http://{target}"]
    
    result = {
        "target": target,
        "url_used": None,
        "status_code": None,
        "detected_wafs": [],
        "possible_wafs": [],
        "challenges": [],
        "confidence": "Low",
        "raw_headers": {},
        "analysis": {}
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
    
    # Get response data
    headers = dict(response.headers)
    cookies = response.cookies
    cookies_dict = {}
    for cookie in cookies:
        cookies_dict[cookie.name] = cookie.value
    
    html = response.text
    
    result["raw_headers"] = headers
    
    print(Color.Y + f"\n[*] Analyzing for WAF signatures...\n" + Color.N)
    
    # Check headers and cookies
    header_matches = check_waf_by_headers(headers, cookies_dict)
    if header_matches:
        result["detected_wafs"].extend(header_matches)
        print(Color.G + "[✓] WAF detected via headers/cookies:" + Color.N)
        for waf in header_matches:
            desc = WAF_SIGNATURES.get(waf, {}).get("description", "Unknown")
            print(f"  {Color.C}• {waf}{Color.N} - {desc}")
    
    # Check HTML content
    html_matches = check_waf_by_html(html)
    if html_matches:
        for waf in html_matches:
            if waf not in result["detected_wafs"]:
                result["detected_wafs"].append(waf)
        print(Color.G + "\n[✓] WAF detected via HTML content:" + Color.N)
        for waf in html_matches:
            desc = WAF_SIGNATURES.get(waf, {}).get("description", "Unknown")
            print(f"  {Color.C}• {waf}{Color.N} - {desc}")
    
    # Check for challenges
    challenges = detect_waf_challenge(html)
    if challenges:
        result["challenges"] = challenges
        print(Color.Y + "\n[!] Security challenges detected:" + Color.N)
        for challenge in challenges:
            print(f"  {Color.Y}⚠ {challenge}{Color.N}")
    
    # Check response codes
    suspicious = check_waf_by_response(response.status_code)
    if suspicious:
        result["suspicious_responses"] = suspicious
        print(Color.Y + "\n[!] Suspicious responses:" + Color.N)
        for s in suspicious:
            print(f"  {Color.Y}⚠ {s}{Color.N}")
    
    # Determine confidence level
    if len(result["detected_wafs"]) >= 2:
        result["confidence"] = "High"
    elif len(result["detected_wafs"]) == 1:
        result["confidence"] = "Medium"
    elif result["challenges"] or suspicious:
        result["confidence"] = "Low"
        result["possible_wafs"] = ["Generic WAF/Proxy detected"]
    
    # Display summary
    print(Color.C + "\n┌─ WAF DETECTION SUMMARY ──────────────┐" + Color.N)
    if result["detected_wafs"]:
        print(f"  {Color.Y}Detected:{Color.N} {Color.G}{', '.join(result['detected_wafs'])}{Color.N}")
    elif result["possible_wafs"]:
        print(f"  {Color.Y}Possible:{Color.N} {Color.Y}{', '.join(result['possible_wafs'])}{Color.N}")
    else:
        print(f"  {Color.Y}Result:{Color.N} {Color.R}No WAF detected{Color.N}")
    
    print(f"  {Color.Y}Confidence:{Color.N} {result['confidence']}")
    
    if result["challenges"]:
        print(f"  {Color.Y}Challenges:{Color.N} {len(result['challenges'])}")
    
    print(Color.C + "└────────────────────────────────────┘" + Color.N)
    
    # Tips
    if not result["detected_wafs"]:
        print(Color.Y + "\n[!] No WAF detected. This could mean:" + Color.N)
        print(Color.Y + "    • No firewall is present" + Color.N)
        print(Color.Y + "    • WAF is configured to be stealthy" + Color.N)
        print(Color.Y + "    • Custom WAF implementation" + Color.N)
    
    # Save results
    filename = save_log(target, "waf", result)
    print(Color.Y + f"\nSaved → {filename}\n" + Color.N)