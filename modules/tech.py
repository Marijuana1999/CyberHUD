#!/usr/bin/env python3

# modules/tech.py
import re
import requests
from core.core import Color, save_log, safe_request

# ======================================================================
# TECHNOLOGY SIGNATURES DATABASE
# ======================================================================

TECH_SIGNATURES = {
    # CMS
    "WordPress": {
        "headers": [],
        "html": [
            r"wp-content",
            r"wp-includes",
            r"wp-json",
            r"wordpress",
            r"wp-embed"
        ],
        "cookies": ["wordpress_", "wp-settings"],
        "version": r"content=\"WordPress ([0-9\.]+)\"",
        "category": "CMS",
        "risk": "HIGH — Frequent vulnerabilities, especially outdated versions"
    },
    "Joomla": {
        "headers": [],
        "html": [
            r"joomla",
            r"com_content",
            r"com_modules",
            r"media/jui"
        ],
        "cookies": ["joomla_"],
        "version": None,
        "category": "CMS",
        "risk": "HIGH"
    },
    "Drupal": {
        "headers": [],
        "html": [
            r"drupal",
            r"sites/default",
            r"core/misc/drupal"
        ],
        "cookies": ["Drupal"],
        "version": r"Drupal ([0-9\.]+)",
        "category": "CMS",
        "risk": "MEDIUM"
    },
    "Magento": {
        "headers": [],
        "html": [
            r"magento",
            r"mage/",
            r"skin/frontend"
        ],
        "cookies": ["frontend"],
        "version": None,
        "category": "E-commerce",
        "risk": "HIGH"
    },
    "PrestaShop": {
        "headers": ["powered-by: prestashop"],
        "html": [
            r"prestashop",
            r"ps_shoppingcart"
        ],
        "cookies": ["PrestaShop"],
        "version": None,
        "category": "E-commerce",
        "risk": "MEDIUM"
    },
    
    # Frameworks
    "Laravel": {
        "headers": ["x-powered-by: laravel"],
        "html": [
            r"laravel_session",
            r"csrf-token",
            r"csrf_token"
        ],
        "cookies": ["laravel_session"],
        "version": None,
        "category": "PHP Framework",
        "risk": "MEDIUM — Check for .env exposure"
    },
    "Django": {
        "headers": [],
        "html": [
            r"csrfmiddlewaretoken",
            r"django",
            r"__admin"
        ],
        "cookies": ["csrftoken", "sessionid"],
        "version": None,
        "category": "Python Framework",
        "risk": "LOW"
    },
    "Flask": {
        "headers": [],
        "html": [],
        "cookies": ["session"],
        "version": None,
        "category": "Python Framework",
        "risk": "LOW"
    },
    "Ruby on Rails": {
        "headers": ["x-powered-by: phusion", "x-powered-by: rails"],
        "html": [
            r"csrf-param",
            r"rails-ujs"
        ],
        "cookies": ["_session_id"],
        "version": None,
        "category": "Ruby Framework",
        "risk": "MEDIUM"
    },
    "Express": {
        "headers": ["x-powered-by: express"],
        "html": [],
        "cookies": [],
        "version": None,
        "category": "Node.js Framework",
        "risk": "LOW"
    },
    "Spring Boot": {
        "headers": [],
        "html": [
            r"whitelabel error page",
            r"spring"
        ],
        "cookies": [],
        "version": None,
        "category": "Java Framework",
        "risk": "MEDIUM"
    },
    "ASP.NET": {
        "headers": ["x-aspnet-version", "x-powered-by: asp.net"],
        "html": [
            r"__viewstate",
            r"__eventvalidation",
            r"asp.net"
        ],
        "cookies": ["asp.net_sessionid", "aspsessionid"],
        "version": r"x-aspnet-version: (.*)",
        "category": ".NET Framework",
        "risk": "MEDIUM"
    },
    
    # JavaScript Frontend
    "React": {
        "headers": [],
        "html": [
            r"react",
            r"data-reactroot",
            r"data-reactid",
            r"react-dom"
        ],
        "cookies": [],
        "version": None,
        "category": "JavaScript Library",
        "risk": "LOW"
    },
    "Vue.js": {
        "headers": [],
        "html": [
            r"vue",
            r"vuejs",
            r"v-bind",
            r"v-model",
            r"vue-router"
        ],
        "cookies": [],
        "version": r"vue@([0-9\.]+)",
        "category": "JavaScript Library",
        "risk": "LOW"
    },
    "Angular": {
        "headers": [],
        "html": [
            r"ng-version",
            r"angular",
            r"ng-app"
        ],
        "cookies": [],
        "version": r"ng-version=\"([0-9\.]+)\"",
        "category": "JavaScript Library",
        "risk": "LOW"
    },
    "jQuery": {
        "headers": [],
        "html": [
            r"jquery",
            r"jquery.js",
            r"jquery.min.js"
        ],
        "cookies": [],
        "version": r"jquery[.-]([0-9\.]+)",
        "category": "JavaScript Library",
        "risk": "MEDIUM — Outdated versions have known XSS"
    },
    "Bootstrap": {
        "headers": [],
        "html": [
            r"bootstrap",
            r"bootstrap.min.css",
            r"bootstrap.bundle"
        ],
        "cookies": [],
        "version": r"bootstrap[.-]v?([0-9\.]+)",
        "category": "CSS Framework",
        "risk": "LOW"
    },
    "Tailwind CSS": {
        "headers": [],
        "html": [
            r"tailwindcss",
            r"@tailwind",
            r"bg-gray-",
            r"text-white"
        ],
        "cookies": [],
        "version": None,
        "category": "CSS Framework",
        "risk": "LOW"
    },
    
    # Web Servers
    "Nginx": {
        "headers": ["server: nginx"],
        "html": [],
        "cookies": [],
        "version": r"nginx/([0-9\.]+)",
        "category": "Web Server",
        "risk": "LOW"
    },
    "Apache": {
        "headers": ["server: apache"],
        "html": [],
        "cookies": [],
        "version": r"apache/([0-9\.]+)",
        "category": "Web Server",
        "risk": "MEDIUM — Check for directory listing"
    },
    "IIS": {
        "headers": ["server: microsoft-iis", "x-powered-by: asp.net"],
        "html": [],
        "cookies": [],
        "version": r"microsoft-iis/([0-9\.]+)",
        "category": "Web Server",
        "risk": "MEDIUM"
    },
    "Caddy": {
        "headers": ["server: caddy"],
        "html": [],
        "cookies": [],
        "version": r"caddy/([0-9\.]+)",
        "category": "Web Server",
        "risk": "LOW"
    },
    "OpenResty": {
        "headers": ["server: openresty"],
        "html": [],
        "cookies": [],
        "version": r"openresty/([0-9\.]+)",
        "category": "Web Server",
        "risk": "LOW"
    },
    
    # CDN / Proxy
    "Cloudflare": {
        "headers": ["server: cloudflare", "cf-ray"],
        "html": [],
        "cookies": ["__cfduid"],
        "version": None,
        "category": "CDN",
        "risk": "LOW"
    },
    "Akamai": {
        "headers": ["server: akamai", "x-akamai-"],
        "html": [],
        "cookies": ["ak_bmsc"],
        "version": None,
        "category": "CDN",
        "risk": "LOW"
    },
    "Fastly": {
        "headers": ["x-served-by", "x-cache-hits"],
        "html": [],
        "cookies": [],
        "version": None,
        "category": "CDN",
        "risk": "LOW"
    },
    "Varnish": {
        "headers": ["via: varnish", "x-varnish"],
        "html": [],
        "cookies": [],
        "version": None,
        "category": "Cache",
        "risk": "LOW"
    },
    
    # Analytics
    "Google Analytics": {
        "headers": [],
        "html": [
            r"google-analytics",
            r"ga\.js",
            r"gtag"
        ],
        "cookies": ["_ga", "_gid"],
        "version": None,
        "category": "Analytics",
        "risk": "LOW"
    },
    "Matomo": {
        "headers": [],
        "html": [
            r"matomo",
            r"piwik"
        ],
        "cookies": ["_pk_id"],
        "version": None,
        "category": "Analytics",
        "risk": "LOW"
    },
    
    # Programming Languages
    "PHP": {
        "headers": ["x-powered-by: php"],
        "html": [
            r"\.php",
            r"php"
        ],
        "cookies": ["phpsessid"],
        "version": r"php/([0-9\.]+)",
        "category": "Language",
        "risk": "HIGH — Outdated PHP is critical"
    },
    "Python": {
        "headers": [],
        "html": [],
        "cookies": [],
        "version": None,
        "category": "Language",
        "risk": "LOW"
    },
    "Node.js": {
        "headers": [],
        "html": [],
        "cookies": [],
        "version": None,
        "category": "Language",
        "risk": "LOW"
    },
    "Java": {
        "headers": ["x-powered-by: jsp"],
        "html": [
            r"\.jsp",
            r"\.do"
        ],
        "cookies": ["jsessionid"],
        "version": None,
        "category": "Language",
        "risk": "MEDIUM"
    }
}

def extract_version(pattern, text):
    """Extract version using regex pattern"""
    if not pattern:
        return None
    try:
        match = re.search(pattern, text, re.IGNORECASE)
        return match.group(1) if match else None
    except:
        return None

def check_cookies(cookies, signatures):
    """Check cookies for technology signatures"""
    if not cookies:
        return []
    
    found = []
    cookie_dict = {}
    for cookie in cookies:
        if hasattr(cookie, 'name'):
            cookie_dict[cookie.name.lower()] = cookie.value
    
    for tech, data in signatures.items():
        for pattern in data.get("cookies", []):
            if any(pattern.lower() in name for name in cookie_dict.keys()):
                found.append(tech)
                break
    
    return found

def check_headers(headers, signatures):
    """Check headers for technology signatures"""
    if not headers:
        return []
    
    found = []
    headers_lower = {k.lower(): v.lower() for k, v in headers.items()}
    
    for tech, data in signatures.items():
        for pattern in data.get("headers", []):
            header_name = pattern.split(":")[0].strip().lower()
            header_value = pattern.split(":")[1].strip().lower() if ":" in pattern else ""
            
            if header_name in headers_lower:
                if not header_value or header_value in headers_lower[header_name]:
                    found.append(tech)
                    break
    
    return found

def check_html(html, signatures):
    """Check HTML content for technology signatures"""
    if not html:
        return []
    
    found = []
    html_lower = html.lower()
    
    for tech, data in signatures.items():
        for pattern in data.get("html", []):
            if re.search(pattern, html_lower, re.IGNORECASE):
                found.append(tech)
                break
    
    return found

def wordpress_deep_scan(html, base_url):
    """Deep WordPress scan for themes, plugins, etc."""
    info = {}
    
    # Find theme
    theme_patterns = [
        r"wp-content/themes/([^/\"]+)",
        r"wp-content/theme/([^/\"]+)",
        r"themes/([^/\"]+)/style.css"
    ]
    
    for pattern in theme_patterns:
        themes = re.findall(pattern, html)
        if themes:
            info["theme"] = list(set(themes))[0]
            break
    
    # Find plugins
    plugin_patterns = [
        r"wp-content/plugins/([^/\"]+)",
        r"wp-content/plugin/([^/\"]+)"
    ]
    
    plugins = []
    for pattern in plugin_patterns:
        found = re.findall(pattern, html)
        plugins.extend(found)
    
    if plugins:
        info["plugins"] = list(set(plugins))
    
    # Check REST API
    if "/wp-json" in html:
        info["rest_api"] = "enabled"
    
    # Check version from generator
    version = extract_version(r"content=\"WordPress ([0-9\.]+)\"", html)
    if version:
        info["version"] = version
    
    return info

def run(target):
    """Main technology fingerprinting function"""
    print(Color.C + "\n[+] Technology Fingerprinting\n" + Color.N)
    
    if not target:
        print(Color.R + "[!] No target set" + Color.N)
        return
    
    # Try both HTTP and HTTPS
    urls = [f"https://{target}", f"http://{target}"]
    
    result = {
        "target": target,
        "technologies": [],
        "categories": {},
        "wordpress_details": {},
        "headers": {},
        "cookies": [],
        "url_used": None
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
    
    # Get response data
    html = response.text
    headers = dict(response.headers)
    cookies = response.cookies
    
    result["headers"] = {k.lower(): v for k, v in headers.items()}
    
    # Store cookies info
    for cookie in cookies:
        result["cookies"].append({
            "name": cookie.name,
            "value_length": len(cookie.value)
        })
    
    print(Color.Y + f"\n[*] Analyzing technologies...\n" + Color.N)
    
    # Check all signatures
    detected = []
    
    # Check headers
    header_matches = check_headers(headers, TECH_SIGNATURES)
    detected.extend(header_matches)
    
    # Check cookies
    cookie_matches = check_cookies(cookies, TECH_SIGNATURES)
    detected.extend(cookie_matches)
    
    # Check HTML
    html_matches = check_html(html, TECH_SIGNATURES)
    detected.extend(html_matches)
    
    # Remove duplicates and sort
    detected = list(set(detected))
    
    # Get detailed info for each detected technology
    for tech in sorted(detected):
        if tech in TECH_SIGNATURES:
            data = TECH_SIGNATURES[tech]
            
            # Extract version
            version = None
            if data.get("version"):
                # Try headers first
                if data.get("headers"):
                    for header_pattern in data["headers"]:
                        if ":" in header_pattern:
                            header_name = header_pattern.split(":")[0].strip().lower()
                            if header_name in result["headers"]:
                                v = extract_version(data["version"], result["headers"][header_name])
                                if v:
                                    version = v
                                    break
                
                # Then try HTML
                if not version:
                    version = extract_version(data["version"], html)
            
            tech_info = {
                "name": tech,
                "category": data.get("category", "Unknown"),
                "version": version,
                "risk": data.get("risk", "Unknown")
            }
            
            result["technologies"].append(tech_info)
            
            # Count by category
            cat = data.get("category", "Other")
            if cat not in result["categories"]:
                result["categories"][cat] = 0
            result["categories"][cat] += 1
            
            # Display
            risk_color = Color.G
            if "HIGH" in data.get("risk", ""):
                risk_color = Color.R
            elif "MEDIUM" in data.get("risk", ""):
                risk_color = Color.Y
            
            print(f"{Color.C}[+] {tech}{Color.N}")
            if version:
                print(f"    Version: {Color.G}{version}{Color.N}")
            print(f"    Category: {Color.B}{data.get('category', 'Unknown')}{Color.N}")
            print(f"    Risk: {risk_color}{data.get('risk', 'Unknown')}{Color.N}")
            print()
    
    # WordPress deep scan
    if "WordPress" in detected:
        print(Color.Y + "[*] Performing WordPress deep scan..." + Color.N)
        wp_info = wordpress_deep_scan(html, url_used)
        result["wordpress_details"] = wp_info
        
        if wp_info.get("theme"):
            print(f"    Theme: {Color.G}{wp_info['theme']}{Color.N}")
        if wp_info.get("plugins"):
            print(f"    Plugins: {Color.G}{', '.join(wp_info['plugins'][:5])}{Color.N}")
            if len(wp_info['plugins']) > 5:
                print(f"        ... and {len(wp_info['plugins'])-5} more")
        if wp_info.get("version"):
            print(f"    Version: {Color.G}{wp_info['version']}{Color.N}")
        if wp_info.get("rest_api"):
            print(f"    REST API: {Color.Y}Enabled{Color.N}")
        print()
    
    # Summary by category
    if result["categories"]:
        print(Color.C + "┌─ SUMMARY BY CATEGORY ─────────────────┐" + Color.N)
        for cat, count in result["categories"].items():
            print(f"  {Color.Y}{cat}:{Color.N} {Color.G}{count}{Color.N}")
        print(Color.C + "└──────────────────────────────────────┘" + Color.N)
    
    if not detected:
        print(Color.Y + "[-] No technologies detected" + Color.N)
        print(Color.Y + "    This could be due to:" + Color.N)
        print(Color.Y + "    • Custom/obscure framework" + Color.N)
        print(Color.Y + "    • Technology hiding techniques" + Color.N)
        print(Color.Y + "    • Static HTML site" + Color.N)
    
    # Save results
    filename = save_log(target, "tech", result)
    print(Color.Y + f"\nSaved → {filename}\n" + Color.N)