#!/usr/bin/env python3

# ======================================================================
# Security Advisor - User Security Monitoring System
# Author: Marijuana1999
# GitHub: https://github.com/Marijuana1999
# ======================================================================

import os
import socket
import subprocess
import platform
import requests
import json
from datetime import datetime
from pathlib import Path

class SecurityAdvisor:
    def __init__(self):
        self.system = platform.system().lower()
        self.status = {
            "vpn": {"status": False, "name": None, "score": 30},
            "dns": {"status": "default", "servers": [], "score": 20},
            "proxy": {"status": False, "score": 10},
            "ip": {"public": None, "local": None, "hidden": False, "score": 20},
            "mac": {"changed": False, "original": None, "current": None, "score": 10},
            "firewall": {"status": False, "score": 10},
            "overall_score": 0,
            "recommendations": []
        }
        
        # Secure DNS servers
        self.secure_dns = {
            "Cloudflare": "1.1.1.1",
            "Google": "8.8.8.8",
            "Quad9": "9.9.9.9",
            "OpenDNS": "208.67.222.222"
        }
        
        # VPN indicators (process names)
        self.vpn_processes = [
            "openvpn", "wireguard", "nordvpn", "expressvpn", 
            "surfshark", "protonvpn", "windscribe", "tunnelbear",
            "vyprvpn", "pia", "private internet access", "cyberghost"
        ]
        
        # VPN ports
        self.vpn_ports = [1194, 1723, 1701, 500, 4500, 51820]

    def check_vpn(self):
        """Check if VPN is active"""
        # Check by processes
        for proc in self.vpn_processes:
            if self.system == "windows":
                cmd = f'tasklist /fi "IMAGENAME eq {proc}.exe" 2>nul'
            else:
                cmd = f'ps aux | grep -i "{proc}" | grep -v grep'
            
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            if result.stdout.strip():
                self.status["vpn"]["status"] = True
                self.status["vpn"]["name"] = proc
                return True
        
        # Check by open ports
        for port in self.vpn_ports:
            if self.check_port(port):
                self.status["vpn"]["status"] = True
                self.status["vpn"]["name"] = f"VPN (port {port})"
                return True
        
        return False

    def check_port(self, port):
        """Check if a port is in use"""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            result = sock.connect_ex(("127.0.0.1", port))
            sock.close()
            return result == 0
        except:
            return False

    def check_dns(self):
        """Check current DNS servers"""
        dns_servers = []
        
        if self.system == "windows":
            try:
                result = subprocess.run(['nslookup', 'localhost'], capture_output=True, text=True)
                for line in result.stdout.split('\n'):
                    if 'Address:' in line and '#' not in line:
                        parts = line.split()
                        if len(parts) > 1:
                            dns_servers.append(parts[1])
            except:
                pass
        
        elif self.system == "linux":
            try:
                with open('/etc/resolv.conf', 'r') as f:
                    for line in f:
                        if line.startswith('nameserver'):
                            dns_servers.append(line.split()[1])
            except:
                pass
        
        self.status["dns"]["servers"] = dns_servers
        
        # Check if using secure DNS
        for name, ip in self.secure_dns.items():
            if ip in dns_servers:
                self.status["dns"]["status"] = f"secure ({name})"
                return True
        
        if dns_servers:
            self.status["dns"]["status"] = "insecure"
            return False
        else:
            self.status["dns"]["status"] = "unknown"
            return False

    def check_proxy(self):
        """Check system proxy settings"""
        proxy_vars = ['HTTP_PROXY', 'HTTPS_PROXY', 'ALL_PROXY']
        for var in proxy_vars:
            if os.environ.get(var) or os.environ.get(var.lower()):
                self.status["proxy"]["status"] = True
                return True
        
        if self.system == "windows":
            try:
                import winreg
                key = winreg.OpenKey(winreg.HKEY_CURRENT_USER,
                                    r"Software\Microsoft\Windows\CurrentVersion\Internet Settings")
                proxy_enable, _ = winreg.QueryValueEx(key, "ProxyEnable")
                if proxy_enable:
                    self.status["proxy"]["status"] = True
                    return True
            except:
                pass
        
        return False

    def get_ip_info(self):
        """Get public and local IP"""
        # Local IP
        try:
            hostname = socket.gethostname()
            self.status["ip"]["local"] = socket.gethostbyname(hostname)
        except:
            self.status["ip"]["local"] = "Unknown"
        
        # Public IP
        try:
            response = requests.get('https://api.ipify.org?format=json', timeout=5)
            if response.status_code == 200:
                self.status["ip"]["public"] = response.json().get('ip')
                
                # Get IP details
                details = requests.get(f'http://ip-api.com/json/{self.status["ip"]["public"]}', timeout=5)
                if details.status_code == 200:
                    data = details.json()
                    self.status["ip"]["location"] = f"{data.get('city', 'Unknown')}, {data.get('country', 'Unknown')}"
                    self.status["ip"]["isp"] = data.get('isp', 'Unknown')
        except:
            self.status["ip"]["public"] = "Unknown"

    def check_firewall(self):
        """Check if firewall is active"""
        if self.system == "windows":
            try:
                result = subprocess.run(['netsh', 'advfirewall', 'show', 'allprofiles'], 
                                      capture_output=True, text=True)
                self.status["firewall"]["status"] = 'ON' in result.stdout
            except:
                pass
        
        elif self.system == "linux":
            try:
                result = subprocess.run(['sudo', 'ufw', 'status'], capture_output=True, text=True)
                self.status["firewall"]["status"] = 'active' in result.stdout
            except:
                try:
                    result = subprocess.run(['iptables', '-L'], capture_output=True, text=True)
                    self.status["firewall"]["status"] = len(result.stdout.split('\n')) > 5
                except:
                    pass
        
        return self.status["firewall"]["status"]

    def check_mac(self):
        """Check MAC address status"""
        if self.system in ["linux", "darwin"]:
            try:
                result = subprocess.run(['ifconfig'], capture_output=True, text=True)
                # اینجا می‌تونی MAC اصلی رو ذخیره کنی
                self.status["mac"]["changed"] = False  # پیش‌فرض
            except:
                pass

    def calculate_score(self):
        """Calculate overall security score"""
        score = 0
        
        if self.status["vpn"]["status"]:
            score += 30
        else:
            self.recommendations.append("🔴 Turn on VPN to hide your IP")
        
        if self.status["dns"]["status"] == "secure":
            score += 20
        elif self.status["dns"]["status"] == "insecure":
            self.recommendations.append("🟡 Use secure DNS (Cloudflare/Google/Quad9)")
        
        if not self.status["proxy"]["status"]:
            score += 10
        else:
            self.recommendations.append("🟡 Proxy detected - may leak your real IP")
        
        if self.status["firewall"]["status"]:
            score += 10
        else:
            self.recommendations.append("🔴 Enable firewall for protection")
        
        if self.status["mac"]["changed"]:
            score += 10
        
        self.status["overall_score"] = score
        return score

    def get_recommendations(self):
        """Get security recommendations"""
        recs = []
        
        if self.status["overall_score"] < 50:
            recs.append("❌ CRITICAL: Your privacy is at risk!")
        
        if not self.status["vpn"]["status"]:
            recs.append("• Install a VPN (ProtonVPN, Windscribe are free)")
        
        if self.status["dns"]["status"] == "insecure":
            recs.append("• Change DNS to 1.1.1.1 (Cloudflare) or 8.8.8.8 (Google)")
        
        if self.status["proxy"]["status"]:
            recs.append("• Disable proxy if not needed")
        
        if not self.status["firewall"]["status"]:
            recs.append("• Enable system firewall")
        
        return recs

    def run_full_check(self):
        """Run all security checks"""
        self.check_vpn()
        self.check_dns()
        self.check_proxy()
        self.get_ip_info()
        self.check_firewall()
        self.calculate_score()
        self.status["recommendations"] = self.get_recommendations()
        
        return self.status

    def get_status_icon(self):
        """Get status icon for display"""
        score = self.status["overall_score"]
        if score >= 80:
            return "🟢", "Excellent"
        elif score >= 60:
            return "🟡", "Good"
        elif score >= 40:
            return "🟠", "Warning"
        else:
            return "🔴", "Critical"

    def print_summary(self):
        """Print colorful summary"""
        from core.core import Color
        
        icon, level = self.get_status_icon()
        
        print(f"\n{Color.C}════════════════════════════════════════════════════{Color.N}")
        print(f"{Color.C}         🔐 SECURITY ADVISOR - Marijuana1999        {Color.N}")
        print(f"{Color.C}════════════════════════════════════════════════════{Color.N}")
        
        print(f"\n{Color.Y}Overall Security: {icon} {level} ({self.status['overall_score']}/100){Color.N}")
        
        print(f"\n{Color.C}─── Network Status ───{Color.N}")
        vpn_status = "✅ ACTIVE" if self.status["vpn"]["status"] else "❌ NOT ACTIVE"
        vpn_color = Color.G if self.status["vpn"]["status"] else Color.R
        print(f"VPN: {vpn_color}{vpn_status}{Color.N}")
        
        dns_status = self.status["dns"]["status"]
        dns_color = Color.G if "secure" in str(dns_status) else Color.Y if dns_status == "insecure" else Color.R
        print(f"DNS: {dns_color}{dns_status}{Color.N}")
        
        proxy_status = "⚠️ ACTIVE" if self.status["proxy"]["status"] else "✅ NOT ACTIVE"
        proxy_color = Color.R if self.status["proxy"]["status"] else Color.G
        print(f"Proxy: {proxy_color}{proxy_status}{Color.N}")
        
        firewall_status = "✅ ACTIVE" if self.status["firewall"]["status"] else "❌ NOT ACTIVE"
        firewall_color = Color.G if self.status["firewall"]["status"] else Color.R
        print(f"Firewall: {firewall_color}{firewall_status}{Color.N}")
        
        print(f"\n{Color.C}─── IP Information ───{Color.N}")
        print(f"Public IP: {Color.G}{self.status['ip'].get('public', 'Unknown')}{Color.N}")
        print(f"Location: {Color.Y}{self.status['ip'].get('location', 'Unknown')}{Color.N}")
        print(f"ISP: {Color.Y}{self.status['ip'].get('isp', 'Unknown')}{Color.N}")
        print(f"Local IP: {Color.B}{self.status['ip'].get('local', 'Unknown')}{Color.N}")
        
        if self.status["recommendations"]:
            print(f"\n{Color.R}─── Recommendations ───{Color.N}")
            for rec in self.status["recommendations"]:
                print(f"  {rec}")
        
        print(f"\n{Color.B}─── Quick Actions ───{Color.N}")
        print("  • Use 'Security Tools' menu for more options")
        print("  • MAC Changer available in Security menu")

    def get_minimap_status(self):
        """Get status string for minimap"""
        icon, _ = self.get_status_icon()
        vpn = "VPN" if self.status["vpn"]["status"] else "NoVPN"
        dns = "DNS🔒" if "secure" in str(self.status["dns"]["status"]) else "DNS⚠️"
        return f"{icon} {vpn} {dns}"


# =========================================================
# Main function for menu
# =========================================================

def run(target=None):
    """Run security advisor"""
    from core.core import Color, clear_screen
    
    clear_screen()
    print(f"{Color.C}╔════════════════════════════════════════════════════╗{Color.N}")
    print(f"{Color.C}║{Color.G}         SECURITY ADVISOR - Marijuana1999          {Color.C}║{Color.N}")
    print(f"{Color.C}╚════════════════════════════════════════════════════╝{Color.N}")
    
    advisor = SecurityAdvisor()
    advisor.run_full_check()
    advisor.print_summary()
    
    print(f"\n{Color.Y}Press ENTER to continue...{Color.N}")
    input()


if __name__ == "__main__":
    run()