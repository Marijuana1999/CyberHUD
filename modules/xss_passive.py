#!/usr/bin/env python3

# modules/xss_passive.py
import re
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse
from core.core import Color, save_log, safe_request

# XSS test payloads (passive - only checking reflection)
TEST_PAYLOADS = [
    "<xss>",
    "'>",
    "\">",
    "<script>",
    "javascript:",
    "onerror=",
    "onload=",
    "alert(1)",
    "prompt(1)",
    "confirm(1)"
]

# Context indicators
CONTEXT_PATTERNS = {
    "html": [r"<[^>]*?{payload}[^>]*?>", "HTML Tag"],
    "attribute": [r"=[\"'][^\"']*?{payload}[^\"']*?[\"']", "HTML Attribute"],
    "script": [r"<script[^>]*?>.*?{payload}.*?</script>", "JavaScript Block"],
    "url": [r"href=[\"'][^\"']*?{payload}[^\"']*?[\"']", "URL"],
    "event": [r"on\w+=[\"'][^\"']*?{payload}[^\"']*?[\"']", "Event Handler"]
}

def extract_parameters(url):
    """Extract parameters from URL"""
    parsed = urlparse(url)
    params = parse_qs(parsed.query)
    return parsed, params

def build_test_url(parsed, params, payload):
    """Build URL with test payload"""
    new_params = {}
    for key, values in params.items():
        # Add payload to each parameter
        new_params[key] = [values[0] + payload]
    
    new_query = urlencode(new_params, doseq=True)
    new_parsed = parsed._replace(query=new_query)
    return urlunparse(new_parsed)

def check_reflection(response_text, payload):
    """Check if payload is reflected in response"""
    if payload in response_text:
        # Find context
        context = detect_context(response_text, payload)
        return True, context
    return False, None

def detect_context(html, payload):
    """Detect the context where payload is reflected"""
    for ctx_name, (pattern, description) in CONTEXT_PATTERNS.items():
        try:
            regex = pattern.format(payload=re.escape(payload))
            if re.search(regex, html, re.IGNORECASE):
                return description
        except:
            pass
    
    # Generic reflection
    return "Plain Text"

def find_forms_in_html(html, base_url):
    """Extract forms from HTML"""
    forms = []
    
    # Simple regex to find forms (not perfect but works for passive)
    form_pattern = r'<form.*?action=[\"\'](.*?)[\"\'].*?>(.*?)</form>'
    input_pattern = r'<input.*?name=[\"\'](.*?)[\"\'].*?>'
    
    for form_match in re.finditer(form_pattern, html, re.IGNORECASE | re.DOTALL):
        action = form_match.group(1)
        form_html = form_match.group(2)
        
        inputs = re.findall(input_pattern, form_html, re.IGNORECASE)
        
        forms.append({
            "action": action,
            "inputs": inputs,
            "method": "GET" if "method=get" in form_html.lower() else "POST"
        })
    
    return forms

def run(target):
    """Main passive XSS scanner"""
    print(Color.C + "\n[+] Passive XSS Reflection Check\n" + Color.N)
    
    if not target:
        print(Color.R + "[!] No target set" + Color.N)
        return
    
    # Try both HTTP and HTTPS
    urls = [f"https://{target}", f"http://{target}"]
    
    result = {
        "target": target,
        "url_used": None,
        "tested_urls": [],
        "reflections": [],
        "forms": [],
        "parameters": {},
        "summary": {
            "total_tests": 0,
            "reflections_found": 0,
            "forms_found": 0,
            "parameters_found": 0
        }
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
    html = response.text
    
    # Extract parameters from URL
    parsed, params = extract_parameters(url_used)
    result["parameters"] = {k: v for k, v in params.items()}
    result["summary"]["parameters_found"] = len(params)
    
    if params:
        print(Color.Y + f"\n[*] Found {len(params)} parameters in URL" + Color.N)
        
        # Test each parameter with each payload
        for param in params.keys():
            print(Color.C + f"\n[Testing parameter: {param}]{Color.N}")
            
            for payload in TEST_PAYLOADS[:3]:  # Test first 3 payloads
                test_url = build_test_url(parsed, params, payload)
                result["tested_urls"].append(test_url)
                result["summary"]["total_tests"] += 1
                
                print(f"  {Color.Y}Testing: {payload}{Color.N}")
                
                # Make request with payload
                resp, error = safe_request(test_url, timeout=8)
                
                if not error and resp:
                    reflected, context = check_reflection(resp.text, payload)
                    
                    if reflected:
                        print(f"    {Color.R}⚠ REFLECTED in {context}{Color.N}")
                        result["reflections"].append({
                            "url": test_url,
                            "parameter": param,
                            "payload": payload,
                            "context": context
                        })
                        result["summary"]["reflections_found"] += 1
                    else:
                        print(f"    {Color.G}✓ Not reflected{Color.N}")
                else:
                    print(f"    {Color.Y}✗ Request failed{Color.N}")
    
    # Find forms
    forms = find_forms_in_html(html, url_used)
    if forms:
        result["forms"] = forms
        result["summary"]["forms_found"] = len(forms)
        
        print(Color.C + f"\n[+] Found {len(forms)} forms:{Color.N}")
        for i, form in enumerate(forms, 1):
            print(f"  {i}. Action: {form['action']}")
            print(f"     Method: {form['method']}")
            if form['inputs']:
                print(f"     Inputs: {', '.join(form['inputs'][:5])}")
    
    # Summary
    print(Color.C + "\n┌─ XSS SCAN SUMMARY ───────────────────┐" + Color.N)
    print(f"  {Color.Y}URLs Tested:{Color.N} {result['summary']['total_tests']}")
    print(f"  {Color.Y}Reflections:{Color.N} {Color.R if result['summary']['reflections_found'] > 0 else Color.G}{result['summary']['reflections_found']}{Color.N}")
    print(f"  {Color.Y}Parameters:{Color.N} {result['summary']['parameters_found']}")
    print(f"  {Color.Y}Forms Found:{Color.N} {result['summary']['forms_found']}")
    print(Color.C + "└────────────────────────────────────┘" + Color.N)
    
    if result["reflections"]:
        print(Color.R + f"\n[!] XSS Reflections detected! Manual testing recommended:" + Color.N)
        for ref in result["reflections"][:5]:
            print(f"  {Color.R}⚠ Parameter '{ref['parameter']}' with '{ref['payload']}' in {ref['context']}{Color.N}")
    
    # Save results
    filename = save_log(target, "xss_passive", result)
    print(Color.Y + f"\nSaved → {filename}\n" + Color.N)