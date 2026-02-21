#!/usr/bin/env python3

# ======================================================================
# DNS Leak Test Module
# Author: Marijuana1999
# GitHub: https://github.com/Marijuana1999
# ======================================================================

import socket
import requests
import subprocess
import platform

class DNSLeakTester:
    def __init__(self):
        self.test_domains = [
            'ipleak.net',
            'whoer.net',
            'dnsleaktest.com'
        ]
    
    def get_current_dns(self):
        """Get current DNS servers"""
        dns_servers = []
        system = platform.system().lower()
        
        if system == "windows":
            try:
                result = subprocess.run(['nslookup', 'localhost'], capture_output=True, text=True)
                for line in result.stdout.split('\n'):
                    if 'Address:' in line and '#' not in line:
                        parts = line.split()
                        if len(parts) > 1:
                            dns_servers.append(parts[1])
            except:
                pass
        
        elif system == "linux":
            try:
                with open('/etc/resolv.conf', 'r') as f:
                    for line in f:
                        if line.startswith('nameserver'):
                            dns_servers.append(line.split()[1])
            except:
                pass
        
        return dns_servers
    
    def test_dns_leak(self):
        """Test for DNS leaks"""
        print("\n" + "="*60)
        print("🔍 DNS LEAK TEST - Marijuana1999")
        print("="*60)
        
        # Get current DNS
        dns_servers = self.get_current_dns()
        print(f"\n[*] Current DNS Servers: {', '.join(dns_servers) if dns_servers else 'Unknown'}")
        
        # Test each domain
        leaks_found = False
        print("\n[*] Testing for DNS leaks...")
        
        for domain in self.test_domains:
            try:
                # Resolve domain
                ip = socket.gethostbyname(domain)
                print(f"[*] {domain} → {ip}")
                
                # Check if IP matches DNS server
                for dns in dns_servers:
                    if dns in ip:
                        print(f"[⚠] Possible DNS leak: {dns} in response")
                        leaks_found = True
                
            except Exception as e:
                print(f"[!] Error testing {domain}: {e}")
        
        # Try to get public IP and compare
        try:
            public_ip = requests.get('https://api.ipify.org', timeout=5).text
            print(f"\n[*] Your Public IP: {public_ip}")
            
            # Check if any DNS matches public IP
            if public_ip in dns_servers:
                print("[⚠] DNS server matches your IP - Possible leak")
                leaks_found = True
            
        except:
            print("[!] Could not get public IP")
        
        # Result
        print("\n" + "-"*40)
        if leaks_found:
            print("[!] DNS LEAK DETECTED!")
            print("    Your DNS queries may be exposed.")
            print("    Recommendations:")
            print("    • Use a VPN")
            print("    • Change DNS to 1.1.1.1 or 8.8.8.8")
            print("    • Use DNS leak protection")
        else:
            print("[✓] No DNS leaks detected!")
            print("    Your DNS is secure.")
        
        return leaks_found


def run(target=None):
    """Main function"""
    tester = DNSLeakTester()
    tester.test_dns_leak()
    print("\n" + "-"*40)
    input("Press ENTER to continue...")