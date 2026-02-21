#!/usr/bin/env python3

# modules/reverse_ip.py
import socket
import requests
from core.core import Color, save_log, safe_request

def is_private_ip(ip):
    """Check if IP is private"""
    try:
        parts = ip.split(".")
        if len(parts) != 4:
            return False
        
        p1 = int(parts[0])
        p2 = int(parts[1])
        
        # Private IP ranges
        if p1 == 10:
            return True
        if p1 == 172 and 16 <= p2 <= 31:
            return True
        if p1 == 192 and p2 == 168:
            return True
        if p1 == 127:  # localhost
            return True
    except:
        pass
    
    return False

def resolve_ip(target):
    """Resolve domain to IP"""
    try:
        # Try IPv4 first
        ip = socket.gethostbyname(target)
        return ip, None
    except socket.gaierror:
        return None, "Could not resolve hostname"
    except Exception as e:
        return None, str(e)

def reverse_ip_lookup(ip):
    """Perform reverse IP lookup using multiple APIs"""
    results = {}
    
    # Method 1: hackertarget.com (free, no API key)
    try:
        url = f"https://api.hackertarget.com/reverseiplookup/?q={ip}"
        response, error = safe_request(url, timeout=10)
        
        if not error and response.status_code == 200:
            text = response.text.strip()
            if "error" not in text.lower():
                domains = [d.strip() for d in text.split("\n") if d.strip()]
                if domains:
                    results["hackertarget"] = domains
    except:
        pass
    
    # Method 2: ip-api.com (alternative)
    try:
        url = f"http://ip-api.com/json/{ip}?fields=status,reverse,query"
        response, error = safe_request(url, timeout=10)
        
        if not error and response.status_code == 200:
            data = response.json()
            if data.get("status") == "success" and data.get("reverse"):
                results["ip-api"] = [data["reverse"]]
    except:
        pass
    
    # Method 3: viewdns.info (alternative)
    try:
        url = f"https://api.viewdns.info/reverseip/?host={ip}&apikey=yourkey&output=json"
        # Note: This requires API key, but we'll try without
        response, error = safe_request(url, timeout=10)
        # Just a placeholder, actual implementation would need API key
    except:
        pass
    
    return results

def run(target):
    """Main reverse IP function"""
    print(Color.C + "\n[+] Reverse IP Lookup (Passive)\n" + Color.N)
    
    if not target:
        print(Color.R + "[!] No target set" + Color.N)
        return
    
    result = {
        "target": target,
        "ip": None,
        "domains": [],
        "sources": {},
        "count": 0
    }
    
    # Resolve IP
    print(Color.Y + f"[*] Resolving {target}..." + Color.N)
    ip, error = resolve_ip(target)
    
    if error:
        print(Color.R + f"[!] {error}" + Color.N)
        result["error"] = error
        filename = save_log(target, "reverse_ip", result)
        print(Color.Y + f"\nSaved → {filename}\n" + Color.N)
        return
    
    result["ip"] = ip
    print(Color.G + f"[✓] Resolved IP: {ip}\n" + Color.N)
    
    # Check if private IP
    if is_private_ip(ip):
        print(Color.Y + "[!] Private IP detected - No reverse lookup available" + Color.N)
        print(Color.Y + "    This is likely a local/internal server" + Color.N)
        filename = save_log(target, "reverse_ip", result)
        print(Color.Y + f"\nSaved → {filename}\n" + Color.N)
        return
    
    # Perform reverse lookup
    print(Color.Y + f"[*] Querying reverse IP databases for {ip} ..." + Color.N)
    
    api_results = reverse_ip_lookup(ip)
    
    if not api_results:
        print(Color.R + "[!] No reverse IP data found" + Color.N)
        print(Color.Y + "    Try manual lookup at: https://www.yougetsignal.com/tools/web-sites-on-web-server/" + Color.N)
        filename = save_log(target, "reverse_ip", result)
        print(Color.Y + f"\nSaved → {filename}\n" + Color.N)
        return
    
    # Process results
    all_domains = []
    result["sources"] = api_results
    
    for source, domains in api_results.items():
        all_domains.extend(domains)
    
    # Remove duplicates
    all_domains = list(set(all_domains))
    result["domains"] = all_domains
    result["count"] = len(all_domains)
    
    # Display results
    if len(all_domains) == 1 and all_domains[0] == target:
        print(Color.G + "\n[✓] Only one domain on this IP (Dedicated Hosting)" + Color.N)
    else:
        print(Color.G + f"\n[✓] Found {len(all_domains)} domains on this IP:\n" + Color.N)
        
        # Show domains in groups
        for i, domain in enumerate(all_domains[:20], 1):
            print(f"  {Color.C}{i:2}.{Color.N} {domain}")
        
        if len(all_domains) > 20:
            print(f"\n  {Color.Y}... and {len(all_domains)-20} more{Color.N}")
    
    # Save results
    filename = save_log(target, "reverse_ip", result)
    print(Color.Y + f"\nSaved → {filename}\n" + Color.N)