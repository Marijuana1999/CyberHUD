#!/usr/bin/env python3

# ======================================================================
# Security Tools - Complete Security Suite
# Author: Marijuana1999
# GitHub: https://github.com/Marijuana1999
# ======================================================================

import os
import sys
import time
import subprocess
import platform
from core.core import Color, clear_screen
from core.security_advisor import SecurityAdvisor
from core.ip_hider import IPHider
from core.security_checker import SecurityChecker

class SecurityTools:
    def __init__(self):
        self.system = platform.system().lower()
        self.advisor = SecurityAdvisor()
        self.ip_hider = IPHider()
        self.checker = SecurityChecker()
    
    def show_dashboard(self):
        """Show real-time security dashboard"""
        clear_screen()
        print(f"{Color.C}╔════════════════════════════════════════════════════╗{Color.N}")
        print(f"{Color.C}║{Color.G}         SECURITY DASHBOARD - LIVE STATUS        {Color.C}║{Color.N}")
        print(f"{Color.C}╚════════════════════════════════════════════════════╝{Color.N}")
        
        status = self.advisor.run_full_check()
        
        print(f"\n{Color.Y}Real-time Protection Status:{Color.N}")
        print(f"{Color.C}────────────────────────────────────{Color.N}")
        
        vpn_icon = "✅" if status["vpn"]["status"] else "❌"
        print(f"{vpn_icon} VPN: {Color.G if status['vpn']['status'] else Color.R}{status['vpn']['status']}{Color.N}")
        
        dns_color = Color.G if "secure" in str(status["dns"]["status"]) else Color.R
        print(f"🌐 DNS: {dns_color}{status['dns']['status']}{Color.N}")
        
        proxy_icon = "⚠️" if status["proxy"]["status"] else "✅"
        proxy_color = Color.R if status["proxy"]["status"] else Color.G
        print(f"{proxy_icon} Proxy: {proxy_color}{status['proxy']['status']}{Color.N}")
        
        firewall_icon = "✅" if status["firewall"]["status"] else "❌"
        firewall_color = Color.G if status["firewall"]["status"] else Color.R
        print(f"🔥 Firewall: {firewall_color}{status['firewall']['status']}{Color.N}")
        
        print(f"\n{Color.Y}IP Information:{Color.N}")
        print(f"   Public: {Color.G}{status['ip'].get('public', 'Unknown')}{Color.N}")
        print(f"   Local: {Color.B}{status['ip'].get('local', 'Unknown')}{Color.N}")
        
        print(f"\n{Color.Y}Security Score: {Color.G}{status['overall_score']}/100{Color.N}")
        
        if status["recommendations"]:
            print(f"\n{Color.R}⚠️ Recommendations:{Color.N}")
            for rec in status["recommendations"][:3]:
                print(f"   • {rec}")
        
        input(f"\n{Color.Y}Press ENTER to continue...{Color.N}")
    
    def quick_fix(self):
        """Quick fix common security issues"""
        clear_screen()
        print(f"{Color.C}╔════════════════════════════════════════════════════╗{Color.N}")
        print(f"{Color.C}║{Color.G}           QUICK SECURITY FIX - 1-CLICK          {Color.C}║{Color.N}")
        print(f"{Color.C}╚════════════════════════════════════════════════════╝{Color.N}")
        
        print(f"\n{Color.Y}This will:{Color.N}")
        print("  • Set DNS to Cloudflare (1.1.1.1)")
        print("  • Check your VPN status")
        print("  • Test for DNS leaks")
        print("  • Give security recommendations")
        
        choice = input(f"\n{Color.Y}Apply quick fixes? (y/n): {Color.N}").strip().lower()
        
        if choice == 'y':
            print(f"\n{Color.C}[*] Applying fixes...{Color.N}")
            
            # Change DNS
            self.ip_hider.change_dns("1.1.1.1")
            time.sleep(1)
            
            # Check VPN
            self.advisor.check_vpn()
            if not self.advisor.status["vpn"]["status"]:
                print(f"{Color.Y}[i] VPN not detected - consider using one{Color.N}")
            
            # Check DNS leak
            self.ip_hider.check_dns_leak()
            
            print(f"\n{Color.G}[✓] Quick fixes applied!{Color.N}")
        
        input(f"\n{Color.Y}Press ENTER to continue...{Color.N}")
    
    def main_menu(self):
        """Main security tools menu"""
        while True:
            clear_screen()
            print(f"{Color.C}╔════════════════════════════════════════════════════╗{Color.N}")
            print(f"{Color.C}║{Color.G}            SECURITY TOOLS - Marijuana1999        {Color.C}║{Color.N}")
            print(f"{Color.C}╚════════════════════════════════════════════════════╝{Color.N}")
            
            # Show current status summary
            status = self.advisor.run_full_check()
            icon, level = self.advisor.get_status_icon()
            print(f"\n{Color.Y}Current Security: {icon} {level} ({status['overall_score']}/100){Color.N}")
            
            print(f"\n{Color.C}─── Available Tools ───{Color.N}")
            print("1. 🔐 Security Dashboard (Live Status)")
            print("2. 🛡️  Security Checker (Full Scan)")
            print("3. 🌐 IP Hider / DNS Changer")
            print("4. ⚡ Quick Security Fix (1-Click)")
            print("5. 📊 View Recommendations")
            print("6. 🔙 Back to Main Menu")
            
            choice = input(f"\n{Color.Y}Select: {Color.N}").strip()
            
            if choice == "1":
                self.show_dashboard()
            elif choice == "2":
                self.checker.run(None)
            elif choice == "3":
                self.ip_hider.hide_ip_menu()
            elif choice == "4":
                self.quick_fix()
            elif choice == "5":
                self.show_recommendations()
            elif choice == "6":
                break
    
    def show_recommendations(self):
        """Show detailed recommendations"""
        clear_screen()
        print(f"{Color.C}╔════════════════════════════════════════════════════╗{Color.N}")
        print(f"{Color.C}║{Color.G}           SECURITY RECOMMENDATIONS                {Color.C}║{Color.N}")
        print(f"{Color.C}╚════════════════════════════════════════════════════╝{Color.N}")
        
        status = self.advisor.run_full_check()
        
        print(f"\n{Color.Y}Your Security Score: {Color.G if status['overall_score']>=60 else Color.R}{status['overall_score']}/100{Color.N}")
        
        print(f"\n{Color.C}─── Why These Matter ───{Color.N}")
        print("• VPN: Hides your real IP from websites")
        print("• Secure DNS: Prevents ISP tracking")
        print("• Firewall: Blocks unwanted connections")
        print("• No Proxy: Ensures direct connection")
        
        print(f"\n{Color.Y}Your Current Issues:{Color.N}")
        for rec in status["recommendations"]:
            print(f"  {rec}")
        
        print(f"\n{Color.C}─── Quick Solutions ───{Color.N}")
        print("• Free VPNs: ProtonVPN, Windscribe")
        print("• Secure DNS: 1.1.1.1 (Cloudflare)")
        print("• Enable Firewall: System settings")
        
        input(f"\n{Color.Y}Press ENTER to continue...{Color.N}")


def run(target=None):
    """Run security tools"""
    tools = SecurityTools()
    tools.main_menu()