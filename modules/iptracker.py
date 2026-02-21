#!/usr/bin/env python3

# modules/iptracker.py
import socket
import requests
import json
import platform
import subprocess
import sys
from core.core import Color, save_log, safe_request

class IPTracker:
    """IP Address Tracker and Geolocation"""
    
    def __init__(self):
        self.results = {}
    
    def get_public_ip(self):
        """Get your own public IP"""
        try:
            response, error = safe_request("https://api.ipify.org?format=json", timeout=5)
            if not error and response.status_code == 200:
                return response.json().get('ip')
        except:
            pass
        
        try:
            response, error = safe_request("https://httpbin.org/ip", timeout=5)
            if not error and response.status_code == 200:
                return response.json().get('origin')
        except:
            pass
        
        return None
    
    def get_ip_info_comprehensive(self, ip_address):
        """Get comprehensive IP information from multiple sources"""
        results = {}
        
        # Method 1: ipapi.co
        try:
            url = f"https://ipapi.co/{ip_address}/json/"
            response, error = safe_request(url, timeout=10)
            
            if not error and response.status_code == 200:
                data = response.json()
                if not data.get('error'):
                    results['ipapi'] = {
                        'ip': data.get('ip'),
                        'city': data.get('city'),
                        'region': data.get('region'),
                        'country': data.get('country_name'),
                        'country_code': data.get('country_code'),
                        'latitude': data.get('latitude'),
                        'longitude': data.get('longitude'),
                        'timezone': data.get('timezone'),
                        'isp': data.get('org'),
                        'asn': data.get('asn'),
                        'postal': data.get('postal'),
                        'currency': data.get('currency')
                    }
        except Exception as e:
            pass
        
        # Method 2: ip-api.com
        try:
            url = f"http://ip-api.com/json/{ip_address}?fields=66846719"
            response, error = safe_request(url, timeout=10)
            
            if not error and response.status_code == 200:
                data = response.json()
                if data.get('status') == 'success':
                    results['ip-api'] = {
                        'ip': data.get('query'),
                        'city': data.get('city'),
                        'region': data.get('regionName'),
                        'country': data.get('country'),
                        'country_code': data.get('countryCode'),
                        'latitude': data.get('lat'),
                        'longitude': data.get('lon'),
                        'timezone': data.get('timezone'),
                        'isp': data.get('isp'),
                        'org': data.get('org'),
                        'as': data.get('as'),
                        'zip': data.get('zip'),
                        'mobile': data.get('mobile'),
                        'proxy': data.get('proxy'),
                        'hosting': data.get('hosting')
                    }
        except Exception as e:
            pass
        
        # Method 3: ipinfo.io
        try:
            url = f"https://ipinfo.io/{ip_address}/json"
            response, error = safe_request(url, timeout=10)
            
            if not error and response.status_code == 200:
                data = response.json()
                loc = data.get('loc', '').split(',')
                results['ipinfo'] = {
                    'ip': data.get('ip'),
                    'city': data.get('city'),
                    'region': data.get('region'),
                    'country': data.get('country'),
                    'latitude': float(loc[0]) if len(loc) > 0 else None,
                    'longitude': float(loc[1]) if len(loc) > 1 else None,
                    'timezone': data.get('timezone'),
                    'isp': data.get('org'),
                    'hostname': data.get('hostname'),
                    'postal': data.get('postal')
                }
        except Exception as e:
            pass
        
        return results
    
    def get_reverse_dns(self, ip_address):
        """Get reverse DNS lookup"""
        try:
            hostname, aliaslist, ipaddrlist = socket.gethostbyaddr(ip_address)
            return hostname
        except:
            return None
    
    def ping_ip(self, ip_address):
        """Ping the IP to check if it's active"""
        try:
            # Ping parameters differ by OS
            param = '-n' if platform.system().lower() == 'windows' else '-c'
            command = ['ping', param, '2', '-W', '2', ip_address]
            
            result = subprocess.run(
                command, 
                capture_output=True, 
                text=True, 
                timeout=10
            )
            
            if result.returncode == 0:
                # Extract average ping time
                lines = result.stdout.lower()
                if 'time=' in lines or 'time<' in lines:
                    return True, "Active"
                else:
                    return True, "Responding"
            else:
                return False, "No response"
        except subprocess.TimeoutExpired:
            return False, "Timeout"
        except Exception as e:
            return False, str(e)[:30]
    
    def trace_route(self, ip_address, max_hops=15):
        """Simplified traceroute (first few hops)"""
        hops = []
        
        try:
            if platform.system().lower() == 'windows':
                # Windows tracert
                command = ['tracert', '-h', str(max_hops), '-w', '2', ip_address]
            else:
                # Linux traceroute
                command = ['traceroute', '-m', str(max_hops), '-w', '2', ip_address]
            
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            # Parse output (simplified)
            lines = result.stdout.split('\n')
            for line in lines[1:max_hops+1]:  # Skip first line
                if line.strip() and '*' not in line[:10]:
                    hops.append(line.strip()[:60])
            
            return hops
        except:
            return []
    
    def check_threat_intel(self, ip_address):
        """Check IP against threat intelligence (simplified)"""
        threats = []
        
        # Check if IP is from known VPN/Proxy (via ip-api)
        try:
            url = f"http://ip-api.com/json/{ip_address}?fields=proxy,hosting,mobile"
            response, error = safe_request(url, timeout=5)
            
            if not error and response.status_code == 200:
                data = response.json()
                if data.get('proxy'):
                    threats.append("VPN/Proxy detected")
                if data.get('hosting'):
                    threats.append("Hosting/Datacenter")
        except:
            pass
        
        # Check against abuseipdb (would need API key)
        # This is a placeholder for future enhancement
        
        return threats
    
    def get_whois_info(self, ip_address):
        """Simplified WHOIS info"""
        whois = {}
        
        try:
            # Try ARIN WHOIS
            url = f"https://whois.arin.net/rest/ip/{ip_address}.json"
            response, error = safe_request(url, timeout=10)
            
            if not error and response.status_code == 200:
                data = response.json()
                net = data.get('net', {})
                
                whois['arin'] = {
                    'name': net.get('name'),
                    'handle': net.get('handle'),
                    'registration': net.get('registrationDate'),
                    'ref': net.get('ref')
                }
        except:
            pass
        
        return whois
    
    def create_google_maps_link(self, latitude, longitude):
        """Create Google Maps link from coordinates"""
        if latitude and longitude and latitude != 0 and longitude != 0:
            return f"https://www.google.com/maps?q={latitude},{longitude}"
        return None
    
    def format_results(self, ip, location_data, reverse_dns, ping_status, threats):
        """Format results for display"""
        output = []
        output.append(f"\n{Color.C}╔══════════════════════════════════════════════════════════╗{Color.N}")
        output.append(f"{Color.C}║{Color.BG}                    IP TRACKER RESULTS                    {Color.C}║{Color.N}")
        output.append(f"{Color.C}╚══════════════════════════════════════════════════════════╝{Color.N}")
        
        output.append(f"\n{Color.Y}Target IP:{Color.N} {Color.G}{ip}{Color.N}")
        
        if reverse_dns:
            output.append(f"{Color.Y}Reverse DNS:{Color.N} {Color.G}{reverse_dns}{Color.N}")
        
        if ping_status[0]:
            output.append(f"{Color.Y}Status:{Color.N} {Color.G}{ping_status[1]}{Color.N}")
        else:
            output.append(f"{Color.Y}Status:{Color.N} {Color.R}{ping_status[1]}{Color.N}")
        
        # Location data (use first available source)
        if location_data:
            source = list(location_data.keys())[0]
            data = location_data[source]
            
            output.append(f"\n{Color.C}┌─ LOCATION INFORMATION ({source}) ─────────────────┐{Color.N}")
            
            if data.get('city'):
                output.append(f"  {Color.Y}City:{Color.N}      {data['city']}")
            if data.get('region'):
                output.append(f"  {Color.Y}Region:{Color.N}    {data['region']}")
            if data.get('country'):
                output.append(f"  {Color.Y}Country:{Color.N}   {data['country']}")
            
            lat = data.get('latitude')
            lon = data.get('longitude')
            if lat and lon:
                output.append(f"  {Color.Y}Lat/Lon:{Color.N}   {lat}, {lon}")
                
                maps_link = self.create_google_maps_link(lat, lon)
                if maps_link:
                    output.append(f"  {Color.Y}Map:{Color.N}       {maps_link[:50]}...")
            
            if data.get('timezone'):
                output.append(f"  {Color.Y}Timezone:{Color.N}  {data['timezone']}")
            if data.get('postal'):
                output.append(f"  {Color.Y}Postal:{Color.N}    {data['postal']}")
            
            output.append(f"{Color.C}└─────────────────────────────────────────────────┘{Color.N}")
            
            # ISP Info
            output.append(f"\n{Color.C}┌─ NETWORK INFORMATION ───────────────────────────┐{Color.N}")
            
            isp = data.get('isp') or data.get('org')
            if isp:
                output.append(f"  {Color.Y}ISP/ORG:{Color.N} {isp}")
            
            if data.get('asn') or data.get('as'):
                asn = data.get('asn') or data.get('as')
                output.append(f"  {Color.Y}ASN:{Color.N}     {asn}")
            
            output.append(f"{Color.C}└─────────────────────────────────────────────────┘{Color.N}")
        
        # Threats
        if threats:
            output.append(f"\n{Color.R}┌─ THREAT INTELLIGENCE ────────────────────────────┐{Color.N}")
            for threat in threats:
                output.append(f"  {Color.R}⚠ {threat}{Color.N}")
            output.append(f"{Color.R}└─────────────────────────────────────────────────┘{Color.N}")
        
        return '\n'.join(output)

def run(target):
    """Main IP tracker function"""
    tracker = IPTracker()
    
    print(Color.C + "\n[+] IP Address Tracker & Geolocation\n" + Color.N)
    
    result = {
        "target": target,
        "ip": None,
        "location_data": {},
        "reverse_dns": None,
        "threats": [],
        "ping_status": None
    }
    
    # Validate and resolve IP
    try:
        # Check if target is IP
        socket.inet_aton(target)
        ip = target
        print(Color.G + f"[✓] Target is IP: {ip}" + Color.N)
    except socket.error:
        # Target is domain
        try:
            ip = socket.gethostbyname(target)
            print(Color.G + f"[✓] Resolved {target} → {ip}" + Color.N)
        except socket.gaierror:
            print(Color.R + f"[!] Could not resolve {target}" + Color.N)
            return
        except Exception as e:
            print(Color.R + f"[!] Error: {e}" + Color.N)
            return
    
    result["ip"] = ip
    
    # Get reverse DNS
    print(Color.Y + f"\n[*] Getting reverse DNS..." + Color.N)
    reverse_dns = tracker.get_reverse_dns(ip)
    if reverse_dns:
        print(Color.G + f"[✓] Reverse DNS: {reverse_dns}" + Color.N)
        result["reverse_dns"] = reverse_dns
    else:
        print(Color.Y + "[-] No reverse DNS record" + Color.N)
    
    # Ping check
    print(Color.Y + f"\n[*] Checking host status..." + Color.N)
    ping_status = tracker.ping_ip(ip)
    print(Color.G + f"[✓] {ping_status[1]}" + Color.N)
    result["ping_status"] = ping_status[1]
    
    # Get location data
    print(Color.Y + f"\n[*] Gathering location data..." + Color.N)
    location_data = tracker.get_ip_info_comprehensive(ip)
    
    if location_data:
        result["location_data"] = location_data
        
        # Check threats
        print(Color.Y + f"\n[*] Checking threat intelligence..." + Color.N)
        threats = tracker.check_threat_intel(ip)
        if threats:
            result["threats"] = threats
            for threat in threats:
                print(Color.Y + f"[!] {threat}" + Color.N)
        else:
            print(Color.G + "[✓] No immediate threats detected" + Color.N)
        
        # Display formatted results
        print(tracker.format_results(ip, location_data, reverse_dns, ping_status, threats))
    else:
        print(Color.R + "[!] Could not retrieve location data" + Color.N)
    
    # Save results
    filename = save_log(target, "iptracker", result)
    print(Color.Y + f"\nSaved → {filename}\n" + Color.N)