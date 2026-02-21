#!/usr/bin/env python3

# core/security_checker.py
import socket
import requests
import platform
import subprocess
import re
from datetime import datetime

class SecurityChecker:
    def __init__(self):
        self.results = {
            'vpn': False,
            'vpn_name': None,
            'location': 'Unknown',
            'ip': 'Unknown',
            'dns': 'Unknown',
            'dns_servers': [],
            'country': 'Unknown',
            'city': 'Unknown',
            'isp': 'Unknown',
            'proxy': False,
            'tor': False,
            'hosting': False
        }
        
        # لیست VPNهای معروف
        self.vpn_processes = [
            ('openvpn', 'OpenVPN'),
            ('nordvpn', 'NordVPN'),
            ('expressvpn', 'ExpressVPN'),
            ('wireguard', 'WireGuard'),
            ('protonvpn', 'ProtonVPN'),
            ('surfshark', 'Surfshark'),
            ('cyberghost', 'CyberGhost'),
            ('private internet access', 'PIA'),
            ('pia', 'Private Internet Access'),
            ('mullvad', 'Mullvad'),
            ('vyprvpn', 'VyprVPN'),
            ('hotspot shield', 'Hotspot Shield'),
            ('windscribe', 'Windscribe'),
            ('tunnelbear', 'TunnelBear'),
            ('ipvanish', 'IPVanish'),
            ('purevpn', 'PureVPN'),
            ('zenmate', 'ZenMate')
        ]
        
        # DNS سرورهای امن
        self.secure_dns = {
            '1.1.1.1': 'Cloudflare',
            '1.0.0.1': 'Cloudflare',
            '8.8.8.8': 'Google',
            '8.8.4.4': 'Google',
            '9.9.9.9': 'Quad9',
            '149.112.112.112': 'Quad9',
            '208.67.222.222': 'OpenDNS',
            '208.67.220.220': 'OpenDNS',
            '94.140.14.14': 'AdGuard',
            '94.140.15.15': 'AdGuard'
        }
    
    def get_public_ip(self):
        """گرفتن IP واقعی از چند منبع مختلف"""
        services = [
            'https://api.ipify.org?format=json',
            'https://api.myip.com',
            'https://ipapi.co/json/',
            'https://ipinfo.io/json'
        ]
        
        for service in services:
            try:
                r = requests.get(service, timeout=3)
                if r.status_code == 200:
                    data = r.json()
                    if 'ip' in data:
                        return data['ip']
                    elif 'query' in data:
                        return data['query']
            except:
                continue
        return None
    
    def get_ip_details(self, ip):
        """گرفتن اطلاعات کامل IP"""
        try:
            # ip-api.com اطلاعات دقیق‌تری میده
            r = requests.get(f'http://ip-api.com/json/{ip}?fields=66846719', timeout=3)
            if r.status_code == 200:
                data = r.json()
                if data.get('status') == 'success':
                    return {
                        'country': data.get('country', 'Unknown'),
                        'countryCode': data.get('countryCode', 'Unknown'),
                        'region': data.get('regionName', 'Unknown'),
                        'city': data.get('city', 'Unknown'),
                        'zip': data.get('zip', 'Unknown'),
                        'lat': data.get('lat', 0),
                        'lon': data.get('lon', 0),
                        'timezone': data.get('timezone', 'Unknown'),
                        'isp': data.get('isp', 'Unknown'),
                        'org': data.get('org', 'Unknown'),
                        'as': data.get('as', 'Unknown'),
                        'proxy': data.get('proxy', False),
                        'hosting': data.get('hosting', False)
                    }
        except:
            pass
        
        # Fallback به ipinfo.io
        try:
            r = requests.get(f'https://ipinfo.io/{ip}/json', timeout=3)
            if r.status_code == 200:
                data = r.json()
                loc = data.get('loc', '0,0').split(',')
                return {
                    'country': data.get('country', 'Unknown'),
                    'region': data.get('region', 'Unknown'),
                    'city': data.get('city', 'Unknown'),
                    'isp': data.get('org', 'Unknown'),
                    'org': data.get('org', 'Unknown'),
                    'proxy': False,
                    'hosting': 'hosting' in data.get('org', '').lower()
                }
        except:
            pass
        
        return {
            'country': 'Unknown',
            'city': 'Unknown',
            'isp': 'Unknown',
            'proxy': False,
            'hosting': False
        }
    
    def check_vpn_windows(self):
        """بررسی VPN در ویندوز"""
        try:
            # بررسی پروسس‌ها
            result = subprocess.run(['tasklist'], capture_output=True, text=True, timeout=3)
            procs = result.stdout.lower()
            
            for proc, name in self.vpn_processes:
                if proc in procs:
                    self.results['vpn'] = True
                    self.results['vpn_name'] = name
                    return True
            
            # بررسی سرویس‌ها
            result = subprocess.run(['sc', 'query', 'state=', 'all'], capture_output=True, text=True, timeout=3)
            services = result.stdout.lower()
            
            for proc, name in self.vpn_processes:
                if proc in services:
                    self.results['vpn'] = True
                    self.results['vpn_name'] = name
                    return True
            
            # بررسی شبکه (TAP adapters)
            result = subprocess.run(['ipconfig', '/all'], capture_output=True, text=True, timeout=3)
            if 'tap' in result.stdout.lower() or 'tun' in result.stdout.lower():
                self.results['vpn'] = True
                self.results['vpn_name'] = 'VPN Adapter'
                return True
                
        except:
            pass
        return False
    
    def check_vpn_linux(self):
        """بررسی VPN در لینوکس"""
        try:
            # بررسی پروسس‌ها
            result = subprocess.run(['ps', 'aux'], capture_output=True, text=True, timeout=3)
            procs = result.stdout.lower()
            
            for proc, name in self.vpn_processes:
                if proc in procs:
                    self.results['vpn'] = True
                    self.results['vpn_name'] = name
                    return True
            
            # بررسی network interfaces
            result = subprocess.run(['ip', 'link', 'show'], capture_output=True, text=True, timeout=3)
            if 'tun' in result.stdout or 'tap' in result.stdout:
                self.results['vpn'] = True
                self.results['vpn_name'] = 'TUN/TAP Interface'
                return True
            
            # بررسی routing table
            result = subprocess.run(['route', '-n'], capture_output=True, text=True, timeout=3)
            if 'tun' in result.stdout or 'tap' in result.stdout:
                self.results['vpn'] = True
                return True
                
        except:
            pass
        return False
    
    def check_vpn(self):
        """بررسی VPN بودن"""
        if platform.system() == "Windows":
            return self.check_vpn_windows()
        else:
            return self.check_vpn_linux()
    
    def get_dns_windows(self):
        """گرفتن DNS سرورها در ویندوز"""
        dns_servers = []
        try:
            # روش اول: nslookup
            result = subprocess.run(['nslookup', 'localhost'], capture_output=True, text=True, timeout=3)
            for line in result.stdout.split('\n'):
                if 'Address:' in line and '#' not in line:
                    parts = line.split()
                    if len(parts) > 1:
                        ip = parts[1].strip()
                        if re.match(r'^\d+\.\d+\.\d+\.\d+$', ip):
                            dns_servers.append(ip)
            
            # روش دوم: ipconfig
            result = subprocess.run(['ipconfig', '/all'], capture_output=True, text=True, timeout=3)
            lines = result.stdout.split('\n')
            for i, line in enumerate(lines):
                if 'DNS Servers' in line or 'dns server' in line.lower():
                    # خط بعدی IP هست
                    if i + 1 < len(lines):
                        ip_match = re.search(r'(\d+\.\d+\.\d+\.\d+)', lines[i+1])
                        if ip_match:
                            dns_servers.append(ip_match.group(1))
        except:
            pass
        
        return list(set(dns_servers))  # حذف تکراری‌ها
    
    def get_dns_linux(self):
        """گرفتن DNS سرورها در لینوکس"""
        dns_servers = []
        try:
            # روش اول: /etc/resolv.conf
            with open('/etc/resolv.conf', 'r') as f:
                for line in f:
                    if line.startswith('nameserver'):
                        parts = line.split()
                        if len(parts) > 1:
                            dns_servers.append(parts[1].strip())
            
            # روش دوم: systemd-resolve
            try:
                result = subprocess.run(['systemd-resolve', '--status'], capture_output=True, text=True, timeout=3)
                for line in result.stdout.split('\n'):
                    if 'DNS Servers' in line:
                        ip_match = re.search(r'(\d+\.\d+\.\d+\.\d+)', line)
                        if ip_match:
                            dns_servers.append(ip_match.group(1))
            except:
                pass
        except:
            pass
        
        return list(set(dns_servers))
    
    def check_dns(self):
        """بررسی DNS سرورها"""
        if platform.system() == "Windows":
            dns_servers = self.get_dns_windows()
        else:
            dns_servers = self.get_dns_linux()
        
        self.results['dns_servers'] = dns_servers
        
        if not dns_servers:
            return 'Unknown'
        
        # بررسی امنیت DNS
        secure_found = []
        insecure_found = []
        
        for dns in dns_servers:
            if dns in self.secure_dns:
                secure_found.append(f"{dns} ({self.secure_dns[dns]})")
            else:
                insecure_found.append(dns)
        
        if secure_found:
            if insecure_found:
                return f"Mixed ({', '.join(secure_found)})"
            else:
                return f"Secure ({', '.join(secure_found)})"
        else:
            return f"Insecure ({', '.join(insecure_found)})"
    
    def check_tor(self):
        """بررسی Tor"""
        try:
            # چک کردن پورت Tor
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(1)
            result = sock.connect_ex(('127.0.0.1', 9050))
            sock.close()
            if result == 0:
                return True
            
            # چک کردن پروسس Tor
            if platform.system() == "Windows":
                result = subprocess.run(['tasklist'], capture_output=True, text=True, timeout=2)
                if 'tor' in result.stdout.lower():
                    return True
            else:
                result = subprocess.run(['ps', 'aux'], capture_output=True, text=True, timeout=2)
                if 'tor' in result.stdout.lower():
                    return True
        except:
            pass
        return False
    
    def check_proxy_env(self):
        """بررسی proxy در environment variables"""
        proxy_vars = ['HTTP_PROXY', 'HTTPS_PROXY', 'ALL_PROXY', 'FTP_PROXY']
        for var in proxy_vars:
            if os.environ.get(var) or os.environ.get(var.lower()):
                return True
        return False
    
    def run_check(self, silent=False):
        """اجرای همه چک‌ها"""
        print("\n" + "="*60)
        print("🔍 SECURITY CHECKER - Marijuana1999")
        print("="*60)

        

        # IP Public
        print("\n📡 Getting public IP...")
        ip = self.get_public_ip()
        if ip:
            self.results['ip'] = ip
            print(f"   → {ip}")
            
            print("📍 Getting location details...")
            details = self.get_ip_details(ip)
            self.results['country'] = details.get('country', 'Unknown')
            self.results['city'] = details.get('city', 'Unknown')
            self.results['isp'] = details.get('isp', 'Unknown')
            self.results['proxy'] = details.get('proxy', False)
            self.results['hosting'] = details.get('hosting', False)
            
            if self.results['city'] != 'Unknown':
                self.results['location'] = f"{self.results['city']}, {self.results['country']}"
            else:
                self.results['location'] = self.results['country']
            
            print(f"   → Location: {self.results['location']}")
            print(f"   → ISP: {self.results['isp']}")
            
            if self.results['proxy']:
                print(f"   ⚠️  Proxy/VPN detected by IP database")
            if self.results['hosting']:
                print(f"   ⚠️  Hosting/Datacenter detected")
        else:
            print("   ❌ Failed to get public IP")
        
        # VPN
        print("\n🛡️  Checking VPN...")
        if self.check_vpn():
            print(f"   → ACTIVE ({self.results['vpn_name']})")
        else:
            print("   → INACTIVE")
        
        # Tor
        print("\� Checking Tor...")
        if self.check_tor():
            print("   → ACTIVE")
            self.results['tor'] = True
        else:
            print("   → INACTIVE")
        
        # Proxy
        print("\n🔌 Checking Proxy...")
        if self.check_proxy_env():
            print("   → DETECTED (environment variables)")
            self.results['proxy'] = True
        else:
            print("   → Not detected")
        
        # DNS
        print("\n🌐 Checking DNS...")
        dns_status = self.check_dns()
        self.results['dns'] = dns_status
        
        if self.results['dns_servers']:
            print(f"   → Servers: {', '.join(self.results['dns_servers'])}")
            print(f"   → Status: {dns_status}")
        else:
            print("   → Could not detect DNS servers")
        
        # Summary
        print("\n" + "="*60)
        print("📊 SUMMARY")
        print("="*60)
        print(f"IP Address:    {self.results['ip']}")
        print(f"Location:      {self.results['location']}")
        print(f"ISP:           {self.results['isp']}")
        print(f"VPN:           {'ACTIVE (' + self.results['vpn_name'] + ')' if self.results['vpn'] else 'INACTIVE'}")
        print(f"Tor:           {'ACTIVE' if self.results['tor'] else 'INACTIVE'}")
        print(f"Proxy:         {'DETECTED' if self.results['proxy'] else 'Not detected'}")
        print(f"DNS:           {self.results['dns']}")
        
        # Recommendations
        if not self.results['vpn']:
            print("\n⚠️  Recommendation: Use VPN to hide your real IP")
        if 'Insecure' in self.results['dns']:
            print("⚠️  Recommendation: Use secure DNS (1.1.1.1, 8.8.8.8)")
        if self.results['proxy']:
            print("⚠️  Recommendation: Disable proxy if not needed")
        
        return self.results
    
    def run(self, target=None):
        """تابع اصلی برای فراخوانی از منو"""
        self.run_check()
        print("\n" + "-"*40)
        input("Press ENTER to continue...")


def run(target=None):
    """تابع برای فراخوانی از ماژول"""
    checker = SecurityChecker()
    checker.run()