#!/usr/bin/env python3

# ======================================================================
# IP Hider - Hide your real IP using DNS/Proxy
# Author: Marijuana1999
# GitHub: https://github.com/Marijuana1999
# ======================================================================

import os
import sys
import subprocess
import platform
import socket
import requests
import time

class IPHider:
    def __init__(self):
        self.system = platform.system().lower()
        self.current_ip = None
        self.hidden_ip = None
        
    def get_current_ip(self):
        """Get current public IP"""
        try:
            response = requests.get('https://api.ipify.org?format=json', timeout=5)
            if response.status_code == 200:
                self.current_ip = response.json().get('ip')
                return self.current_ip
        except:
            return None
    
    def change_dns(self, dns_server="1.1.1.1"):
        """Change DNS server (requires admin)"""
        print(f"\n[*] Changing DNS to {dns_server}...")
        
        if self.system == "windows":
            # Find active interface
            result = subprocess.run(['netsh', 'interface', 'show', 'interface'], 
                                   capture_output=True, text=True)
            interfaces = []
            for line in result.stdout.split('\n'):
                if 'Connected' in line:
                    parts = line.split()
                    if len(parts) > 3:
                        interfaces.append(parts[-1])
            
            if interfaces:
                for interface in interfaces:
                    cmd = f'netsh interface ip set dns "{interface}" static {dns_server}'
                    subprocess.run(cmd, shell=True)
                print(f"[✓] DNS changed to {dns_server}")
                return True
        
        elif self.system == "linux":
            try:
                with open('/etc/resolv.conf', 'w') as f:
                    f.write(f'nameserver {dns_server}\n')
                print(f"[✓] DNS changed to {dns_server}")
                return True
            except:
                print("[!] Need sudo for DNS change")
                return False
        
        return False
    
    def reset_dns(self):
        """Reset DNS to default"""
        if self.system == "windows":
            result = subprocess.run(['netsh', 'interface', 'show', 'interface'], 
                                   capture_output=True, text=True)
            interfaces = []
            for line in result.stdout.split('\n'):
                if 'Connected' in line:
                    parts = line.split()
                    if len(parts) > 3:
                        interfaces.append(parts[-1])
            
            for interface in interfaces:
                cmd = f'netsh interface ip set dns "{interface}" dhcp'
                subprocess.run(cmd, shell=True)
            print("[✓] DNS reset to default")
        
        elif self.system == "linux":
            try:
                subprocess.run(['sudo', 'systemctl', 'restart', 'systemd-resolved'])
                print("[✓] DNS reset to default")
            except:
                pass
    
    def check_dns_leak(self):
        """Check if DNS is leaking"""
        try:
            import dns.resolver
            resolver = dns.resolver.Resolver()
            answers = resolver.resolve('ipleak.net', 'A')
            
            if len(answers) > 1:
                print("[⚠️] DNS Leak detected!")
                return True
            else:
                print("[✅] No DNS leak")
                return False
        except:
            return None
    
    def hide_ip_menu(self):
        """Interactive menu to hide IP"""
        from core.core import Color, clear_screen
        
        while True:
            clear_screen()
            print(f"{Color.C}╔════════════════════════════════════════════════════╗{Color.N}")
            print(f"{Color.C}║{Color.G}              IP HIDER - Marijuana1999            {Color.C}║{Color.N}")
            print(f"{Color.C}╚════════════════════════════════════════════════════╝{Color.N}")
            
            current = self.get_current_ip()
            print(f"\n{Color.Y}Current IP:{Color.N} {Color.G}{current}{Color.N}")
            
            print(f"\n{Color.C}─── Options ───{Color.N}")
            print("1. Change DNS to Cloudflare (1.1.1.1) - Secure")
            print("2. Change DNS to Google (8.8.8.8) - Secure")
            print("3. Change DNS to Quad9 (9.9.9.9) - Secure")
            print("4. Check DNS Leak")
            print("5. Reset DNS to Default")
            print("6. Back to Main Menu")
            
            choice = input(f"\n{Color.Y}Select: {Color.N}").strip()
            
            if choice == "1":
                self.change_dns("1.1.1.1")
                time.sleep(2)
            elif choice == "2":
                self.change_dns("8.8.8.8")
                time.sleep(2)
            elif choice == "3":
                self.change_dns("9.9.9.9")
                time.sleep(2)
            elif choice == "4":
                self.check_dns_leak()
                input("\nPress ENTER...")
            elif choice == "5":
                self.reset_dns()
                time.sleep(2)
            elif choice == "6":
                break


def run(target=None):
    """Run IP hider"""
    hider = IPHider()
    hider.hide_ip_menu()