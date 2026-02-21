#!/usr/bin/env python3

# ======================================================================
# CYBER HUD - Advanced Security Testing Framework
# Author: Marijuana1999
# GitHub: https://github.com/Marijuana1999
# Version: 3.0 
# ======================================================================

import curses
import time
import json
import os
import random
import platform
import sys
from datetime import datetime

from core.core import clear_screen

# ======================================================================
# CONFIGURATION
# ======================================================================

THEME_FILE = "theme.json"
SETTINGS_FILE = "settings.json"

THEMES = {
    # ===== Classic Themes =====
    "dark_neon": {
        "name": "Dark Neon",
        "text": curses.COLOR_WHITE,
        "highlight": curses.COLOR_YELLOW,
        "glow": curses.COLOR_MAGENTA,
        "label": curses.COLOR_CYAN,
        "border": curses.COLOR_CYAN,
        "cmd_color": 10
    },
    "blue_soft": {
        "name": "Blue Soft",
        "text": curses.COLOR_WHITE,
        "highlight": curses.COLOR_BLUE,
        "glow": curses.COLOR_CYAN,
        "label": curses.COLOR_MAGENTA,
        "border": curses.COLOR_BLUE,
        "cmd_color": 9
    },
    "hacker_green": {
        "name": "Hacker Green",
        "text": curses.COLOR_GREEN,
        "highlight": curses.COLOR_YELLOW,
        "glow": curses.COLOR_GREEN,
        "label": curses.COLOR_GREEN,
        "border": curses.COLOR_GREEN,
        "cmd_color": 10
    },
    "matrix_reloaded": {
        "name": "Matrix Reloaded",
        "text": curses.COLOR_GREEN,
        "highlight": curses.COLOR_YELLOW,
        "glow": curses.COLOR_GREEN,
        "label": curses.COLOR_CYAN,
        "border": curses.COLOR_GREEN,
        "cmd_color": 10,
        "description": "Classic Matrix style with cyan accents"
    },
    "blood_red": {
        "name": "Blood Red",
        "text": curses.COLOR_RED,
        "highlight": curses.COLOR_YELLOW,
        "glow": curses.COLOR_MAGENTA,
        "label": curses.COLOR_WHITE,
        "border": curses.COLOR_RED,
        "cmd_color": 12,
        "description": "Aggressive red theme for dark ops"
    },
    "royal_purple": {
        "name": "Royal Purple",
        "text": curses.COLOR_MAGENTA,
        "highlight": curses.COLOR_YELLOW,
        "glow": curses.COLOR_CYAN,
        "label": curses.COLOR_WHITE,
        "border": curses.COLOR_MAGENTA,
        "cmd_color": 13,
        "description": "Elegant purple theme"
    },
    "ocean_deep": {
        "name": "Ocean Deep",
        "text": curses.COLOR_CYAN,
        "highlight": curses.COLOR_WHITE,
        "glow": curses.COLOR_BLUE,
        "label": curses.COLOR_GREEN,
        "border": curses.COLOR_CYAN,
        "cmd_color": 11,
        "description": "Deep blue ocean colors"
    },
    "sunset_orange": {
        "name": "Sunset Orange",
        "text": curses.COLOR_YELLOW,
        "highlight": curses.COLOR_RED,
        "glow": curses.COLOR_MAGENTA,
        "label": curses.COLOR_WHITE,
        "border": curses.COLOR_YELLOW,
        "cmd_color": 14,
        "description": "Warm sunset colors"
    },
    "midnight_blue": {
        "name": "Midnight Blue",
        "text": curses.COLOR_WHITE,
        "highlight": curses.COLOR_CYAN,
        "glow": curses.COLOR_BLUE,
        "label": curses.COLOR_MAGENTA,
        "border": curses.COLOR_BLUE,
        "cmd_color": 1,
        "description": "Dark blue with cyan highlights"
    },
    "amber_glow": {
        "name": "Amber Glow",
        "text": curses.COLOR_YELLOW,
        "highlight": curses.COLOR_WHITE,
        "glow": curses.COLOR_RED,
        "label": curses.COLOR_GREEN,
        "border": curses.COLOR_YELLOW,
        "cmd_color": 6,
        "description": "Retro amber terminal style"
    },
    "cyber_punk": {
        "name": "Cyber Punk",
        "text": curses.COLOR_MAGENTA,
        "highlight": curses.COLOR_GREEN,
        "glow": curses.COLOR_CYAN,
        "label": curses.COLOR_YELLOW,
        "border": curses.COLOR_MAGENTA,
        "cmd_color": 13,
        "description": "Cyberpunk 2077 style"
    },
    "ghost_white": {
        "name": "Ghost White",
        "text": curses.COLOR_WHITE,
        "highlight": curses.COLOR_CYAN,
        "glow": curses.COLOR_BLUE,
        "label": curses.COLOR_MAGENTA,
        "border": curses.COLOR_WHITE,
        "cmd_color": 15,
        "description": "Clean white with blue accents"
    },
    "forest_green": {
        "name": "Forest Green",
        "text": curses.COLOR_GREEN,
        "highlight": curses.COLOR_YELLOW,
        "glow": curses.COLOR_WHITE,
        "label": curses.COLOR_CYAN,
        "border": curses.COLOR_GREEN,
        "cmd_color": 2,
        "description": "Dark green forest theme"
    },
    "lava_red": {
        "name": "Lava Red",
        "text": curses.COLOR_RED,
        "highlight": curses.COLOR_YELLOW,
        "glow": curses.COLOR_WHITE,
        "label": curses.COLOR_MAGENTA,
        "border": curses.COLOR_RED,
        "cmd_color": 12,
        "description": "Hot lava red theme"
    },
    "arctic_ice": {
        "name": "Arctic Ice",
        "text": curses.COLOR_CYAN,
        "highlight": curses.COLOR_WHITE,
        "glow": curses.COLOR_BLUE,
        "label": curses.COLOR_GREEN,
        "border": curses.COLOR_CYAN,
        "cmd_color": 11,
        "description": "Cold arctic blue theme"
    },
    "retro_terminal": {
        "name": "Retro Terminal",
        "text": curses.COLOR_GREEN,
        "highlight": curses.COLOR_WHITE,
        "glow": curses.COLOR_YELLOW,
        "label": curses.COLOR_CYAN,
        "border": curses.COLOR_GREEN,
        "cmd_color": 2,
        "description": "Classic green monochrome"
    },
    "neon_pink": {
        "name": "Neon Pink",
        "text": curses.COLOR_MAGENTA,
        "highlight": curses.COLOR_YELLOW,
        "glow": curses.COLOR_CYAN,
        "label": curses.COLOR_WHITE,
        "border": curses.COLOR_MAGENTA,
        "cmd_color": 13,
        "description": "Bright neon pink style"
    }
}

DEFAULT_SETTINGS = {
    "waterfall": "intro",
    "mouse": False,
    "theme": "dark_neon"
}


# ======================================================================
# CMD Font Settings
# ======================================================================

CMD_FONTS = {
    "default": {
        "name": "Default",
        "size": 16,
        "weight": "normal",
        "family": "Consolas"
    },
    "large": {
        "name": "Large",
        "size": 20,
        "weight": "bold",
        "family": "Consolas"
    },
    "small": {
        "name": "Small",
        "size": 12,
        "weight": "normal",
        "family": "Consolas"
    },
    "retro": {
        "name": "Retro",
        "size": 18,
        "weight": "bold",
        "family": "Lucida Console"
    },
    "modern": {
        "name": "Modern",
        "size": 16,
        "weight": "normal",
        "family": "Courier New"
    }
}


def apply_cmd_theme(theme_name):
    if platform.system() != "Windows":
        return
    theme = THEMES.get(theme_name, THEMES["dark_neon"])
    cmd_color = theme.get("cmd_color", 10)
    os.system(f"color {cmd_color}")
    os.system(f"title CYBER HUD - {theme['name']}")


def load_theme():
    if not os.path.exists(THEME_FILE):
        save_theme(DEFAULT_SETTINGS["theme"])
        return THEMES[DEFAULT_SETTINGS["theme"]]
    try:
        with open(THEME_FILE, 'r') as f:
            data = json.load(f)
            theme_name = data.get("theme", DEFAULT_SETTINGS["theme"])
            apply_cmd_theme(theme_name)
            return THEMES.get(theme_name, THEMES["dark_neon"])
    except:
        save_theme(DEFAULT_SETTINGS["theme"])
        return THEMES["dark_neon"]


def save_theme(name):
    with open(THEME_FILE, "w") as f:
        json.dump({"theme": name}, f, indent=4)
    apply_cmd_theme(name)


def get_theme_list():
    themes = []
    for key, theme in THEMES.items():
        themes.append({
            "id": key,
            "name": theme["name"],
            "description": theme.get("description", ""),
            "cmd_color": theme.get("cmd_color", 7)
        })
    return themes


def get_font_list():
    fonts = []
    for key, font in CMD_FONTS.items():
        fonts.append({
            "id": key,
            "name": font["name"],
            "family": font["family"],
            "size": font["size"]
        })
    return fonts


def load_settings():
    if not os.path.exists(SETTINGS_FILE):
        save_settings(DEFAULT_SETTINGS)
        return DEFAULT_SETTINGS
    try:
        settings = json.load(open(SETTINGS_FILE))
        if "font" not in settings:
            settings["font"] = "default"
        return settings
    except:
        save_settings(DEFAULT_SETTINGS)
        return DEFAULT_SETTINGS


def save_settings(s):
    with open(SETTINGS_FILE, "w") as f:
        json.dump(s, f, indent=4)


def detect_environment():
    sysname = platform.system().lower()
    if sysname == "windows":
        return "windows"
    if sysname == "linux":
        if "/data/data/com.termux" in os.path.expanduser("~"):
            return "termux"
        return "linux"
    return "unknown"


class CyberHUD:
    def __init__(self, theme, settings):
        self.env = detect_environment()
        
        try:
            from core.core import get_target, set_target
            self.get_target = get_target
            self.set_target = set_target
        except ImportError as e:
            print(f"Error importing core: {e}")
            sys.exit(1)

        self.modules = {}
        self.import_modules()

        self.theme = theme
        self.theme_name = self.get_theme_name(theme)
        self.settings = settings
        self.sections = [
            ("TARGET", [
                {"name": "Set Target", "action": "set_target"},
                {"name": "Show Target", "action": "show_target"},
                {"name": "Target Dashboard", "action": "target_dashboard"}
            ]),
            ("RECON", self.get_recon_tools()),
            ("SCANNING", self.get_scanning_tools()),
            ("WEB SECURITY", self.get_web_tools()),
            ("EXPLOITS", self.get_exploit_tools()),
            ("UTILITIES", self.get_utilities()),
            ("ADVANCED", self.get_advanced_tools()),
            ("SECURITY", self.get_security_tools()),
            ("SETTINGS", [
                {"name": "Change Theme", "action": "change_theme"},
                {"name": "Theme List", "action": "theme_list"},
                {"name": "Change Font", "action": "change_font"},
                {"name": "Font Guide", "action": "font_guide"},
                {"name": "Waterfall Mode", "action": "toggle_waterfall"},
                {"name": "Mouse Support", "action": "toggle_mouse"},
                {"name": "Help", "action": "help"},
                {"name": "About", "action": "about"}
            ]),
            ("EXIT", [
                {"name": "Quit", "action": "exit"}
            ])
        ]

        self.section_index = 0
        self.item_index = 0
        self.in_section = False

    def import_modules(self):
        module_list = [
            'dns_enum', 'reverse_ip', 'asn', 'crawler', 'tech', 'headers',
            'ports', 'ssl_scan', 'rate_limit', 'waf', 'cors', 'cookies',
            'robots', 'xss_passive', 'sqli_passive', 'backup_finder',
            'backup_exploit', 'dirs', 'iptracker'
        ]
        
        advanced_modules = [
            'jwt_analyzer', 'graphql_analyzer', 'cache_poisoning',
            'rate_limit_bypass', 'cors_advanced', 'subdomain_takeover'
        ]
        
        security_modules = [
            'security_checker', 'ip_hider', 'dns_leak_test'
        ]
        
        module_list.extend(advanced_modules)
        module_list.extend(security_modules)
        
        if self.env in ("windows", "linux"):
            module_list.append('screenshot')
        
        for module_name in module_list:
            try:
                self.modules[module_name] = __import__(f'modules.{module_name}', fromlist=['run'])
            except ImportError:
                pass

    def get_recon_tools(self):
        tools = []
        recon_modules = [
            ("DNS Enumeration", "dns_enum"),
            ("Reverse IP", "reverse_ip"),
            ("ASN Lookup", "asn"),
            ("Crawler", "crawler"),
            ("Tech Fingerprinting", "tech"),
            ("HTTP Headers", "headers"),
            ("IP Tracker", "iptracker"),
        ]
        for name, mod in recon_modules:
            if self.modules.get(mod):
                tools.append({"name": name, "action": self.modules[mod].run})
        return tools

    def get_scanning_tools(self):
        tools = []
        scanning_modules = [
            ("Port Scan", "ports"),
            ("SSL Scan", "ssl_scan"),
            ("Rate Limit", "rate_limit"),
        ]
        for name, mod in scanning_modules:
            if self.modules.get(mod):
                tools.append({"name": name, "action": self.modules[mod].run})
        return tools

    def get_web_tools(self):
        tools = []
        web_modules = [
            ("WAF Detection", "waf"),
            ("CORS Analyzer", "cors"),
            ("Cookie Security", "cookies"),
            ("Robots Recon", "robots"),
            ("Passive XSS", "xss_passive"),
            ("Passive SQLi", "sqli_passive"),
        ]
        for name, mod in web_modules:
            if self.modules.get(mod):
                tools.append({"name": name, "action": self.modules[mod].run})
        return tools

    def get_exploit_tools(self):
        tools = []
        exploit_modules = [
            ("Backup Finder", "backup_finder"),
            ("Backup Exploit", "backup_exploit"),
        ]
        for name, mod in exploit_modules:
            if self.modules.get(mod):
                tools.append({"name": name, "action": self.modules[mod].run})
        return tools

    def get_utilities(self):
        tools = []
        if self.modules.get('dirs'):
            tools.append({"name": "Directory Scan", "action": self.modules['dirs'].run})
        if self.modules.get('screenshot'):
            tools.append({"name": "Screenshot", "action": self.modules['screenshot'].run})
        return tools

    def get_advanced_tools(self):
        tools = []
        advanced_modules = [
            ("JWT Analyzer", "jwt_analyzer"),
            ("GraphQL Scanner", "graphql_analyzer"),
            ("Cache Poisoning", "cache_poisoning"),
            ("Rate Limit Bypass", "rate_limit_bypass"),
            ("CORS Advanced", "cors_advanced"),
            ("Subdomain Takeover", "subdomain_takeover"),
        ]
        for name, mod in advanced_modules:
            if self.modules.get(mod):
                tools.append({"name": name, "action": self.modules[mod].run})
        return tools

    def get_security_tools(self):
        tools = []
        security_modules = [
            ("Security Checker", "security_checker"),
            ("IP Hider", "ip_hider"),
            ("DNS Leak Test", "dns_leak_test"),
        ]
        for name, mod in security_modules:
            if self.modules.get(mod):
                tools.append({"name": name, "action": self.modules[mod].run})
        return tools

    def get_theme_name(self, theme):
        for name, th in THEMES.items():
            if th == theme:
                return name
        return "Unknown"

    def get_security_status(self):
        """Get security status for minimap - MULTI-PLATFORM"""
        try:
            from core.security_checker import SecurityChecker
            checker = SecurityChecker()
            results = checker.run_check(silent=True)
            
            vpn_status = results.get('vpn', False)
            vpn_name = results.get('vpn_name', '')
            
            location = results.get('location', 'Unknown')
            if location == 'Unknown' and results.get('city') != 'Unknown':
                location = f"{results.get('city', '')}, {results.get('country', '')}"
                location = location.strip(', ')
            
            ip = results.get('ip', 'Unknown')
            dns = results.get('dns', 'Unknown')
            
            return {
                'vpn': vpn_status,
                'vpn_name': vpn_name,
                'location': location,
                'ip': ip,
                'dns': dns
            }
        except Exception as e:
            try:
                from core.security_advisor import SecurityAdvisor
                advisor = SecurityAdvisor()
                status = advisor.run_full_check()
                
                return {
                    'vpn': status.get('vpn', {}).get('status', False),
                    'vpn_name': status.get('vpn', {}).get('name', ''),
                    'location': status.get('ip', {}).get('location', 'Unknown'),
                    'ip': status.get('ip', {}).get('public', 'Unknown'),
                    'dns': status.get('dns', {}).get('status', 'Unknown')
                }
            except:
                return {
                    'vpn': False,
                    'vpn_name': '',
                    'location': 'Unknown',
                    'ip': 'Unknown',
                    'dns': 'Unknown'
                }

    # ==================================================================
    # UI METHODS
    # ==================================================================

    def draw_header(self, scr):
        try:
            scr.addstr(0, 2, "╔════════════════════════════════════════════════════╗", curses.color_pair(1))
            scr.addstr(1, 2, "             CYBER HUD - Marijuana1999                            ", curses.color_pair(2))
            scr.addstr(2, 2, "  GitHub: https://github.com/Marijuana1999                        ", curses.color_pair(3))
            scr.addstr(3, 2, "  Version: 3.0                                                    ", curses.color_pair(2))
            scr.addstr(4, 2, "╚════════════════════════════════════════════════════╝", curses.color_pair(1))
        except:
            pass

    def matrix_rain(self, scr):
        try:
            max_y, max_x = scr.getmaxyx()
            columns = [0] * max_x
            for _ in range(35):
                for x in range(0, max_x, 2):
                    char = chr(random.randint(33, 126))
                    y = columns[x]
                    if y < max_y:
                        try:
                            scr.addstr(y, x, char, curses.color_pair(4))
                        except:
                            pass
                    columns[x] = (y + 1) % max_y
                scr.refresh()
                time.sleep(0.03)
        except:
            pass

    def crt_effect(self, scr):
        try:
            for _ in range(3):
                scr.attron(curses.A_DIM)
                scr.refresh()
                time.sleep(0.04)
                scr.attroff(curses.A_DIM)
                scr.refresh()
                time.sleep(0.04)
        except:
            pass

    def glow(self, scr, y, x, text):
        try:
            scr.attron(curses.color_pair(3))
            scr.addstr(y, x, text)
            scr.attroff(curses.color_pair(3))
        except:
            pass

    def draw_sections(self, scr):
        try:
            y_offset = 6
            target = self.get_target()
            if target:
                scr.addstr(y_offset, 3, f"TARGET: {target}", curses.color_pair(2))
                y_offset += 2
            
            scr.addstr(y_offset, 3, "MODULE GROUPS", curses.color_pair(1))
            y_offset += 1
            
            for i, sec in enumerate(self.sections):
                name = sec[0]
                if i == self.section_index:
                    self.glow(scr, y_offset + i + 1, 5, f">> {name}")
                else:
                    scr.addstr(y_offset + i + 1, 7, name, curses.color_pair(2))
        except:
            pass




    def draw_items(self, scr):
        try:
            y_offset = 6
            target = self.get_target()
            if target:
                scr.addstr(y_offset, 3, f"TARGET: {target}", curses.color_pair(2))
                y_offset += 2
            
            sec_name, items = self.sections[self.section_index]
            scr.addstr(y_offset, 3, f"[ {sec_name} ]", curses.color_pair(1))
            y_offset += 1
            
            for i, item in enumerate(items):
                if i == self.item_index:
                    self.glow(scr, y_offset + i + 1, 5, f">> {item['name']}")
                else:
                    scr.addstr(y_offset + i + 1, 7, item['name'], curses.color_pair(2))
        except:
            pass

    def draw_minimap(self, scr):
        try:
            if self.env == "termux":
                return
            max_y, max_x = scr.getmaxyx()
            x = max_x - 40 
            if x < 5:
                return

            y = 2
            status = self.get_security_status()
            now = datetime.now()
            
            # ===== DATE & TIME =====
            time_str = now.strftime("%H:%M:%S")
            date_str = now.strftime("%Y-%m-%d")
            scr.addstr(y, x, "+--------------------------------+", curses.color_pair(1))
            y += 1
            scr.addstr(y, x, f"  {date_str}  {time_str}           ", curses.color_pair(3))
            y += 1
            scr.addstr(y, x, "+--------------------------------+", curses.color_pair(1))
            y += 1
            
            # ===== TARGET =====
            target = self.get_target()
            if target:
                scr.addstr(y, x, "+--------------------------------+", curses.color_pair(1))
                y += 1
                scr.addstr(y, x, f"  TARGET: {target[:24]:<24}  ", curses.color_pair(2))
                y += 1
                scr.addstr(y, x, "+--------------------------------+", curses.color_pair(1))
                y += 1
            else:
                scr.addstr(y, x, "+--------------------------------+", curses.color_pair(1))
                y += 1
                scr.addstr(y, x, "  TARGET: Not Set                ", curses.color_pair(4))
                y += 1
                scr.addstr(y, x, "+--------------------------------+", curses.color_pair(1))
                y += 1
            
            # ===== SECURITY INFO =====
            scr.addstr(y, x, "+--------------------------------+", curses.color_pair(1))
            y += 1
            
            # VPN
            vpn_color = curses.color_pair(2) if status['vpn'] else curses.color_pair(4)
            vpn_text = f"VPN: {'ACTIVE' if status['vpn'] else 'INACTIVE'}"
            if status['vpn'] and status['vpn_name']:
                vpn_text += f" ({status['vpn_name'][:8]})"
            scr.addstr(y, x, f"  {vpn_text:<28}  ", vpn_color)
            y += 1
            
            # Location
            loc_text = status['location'][:20] if status['location'] != 'Unknown' else 'Unknown'
            scr.addstr(y, x, f"  LOC: {loc_text:<20}  ", curses.color_pair(2))
            y += 1
            
            # IP
            ip_text = status['ip'] if status['ip'] != 'Unknown' else 'Unknown'
            scr.addstr(y, x, f"  IP:  {ip_text:<15}      ", curses.color_pair(2))
            y += 1
            
            # DNS
            dns_color = curses.color_pair(2) if 'Secure' in status['dns'] or 'secure' in status['dns'].lower() else curses.color_pair(4)
            dns_text = status['dns'] if status['dns'] != 'Unknown' else 'Unknown'
            scr.addstr(y, x, f"  DNS: {dns_text:<22}  ", dns_color)
            y += 1
            
            scr.addstr(y, x, "+--------------------------------+", curses.color_pair(1))
            y += 1
            
            # ===== NAVIGATION =====
            scr.addstr(y, x, "+--------------------------------+", curses.color_pair(1))
            y += 1
            
            mode_text = "ITEMS" if self.in_section else "MENU"
            scr.addstr(y, x, f"  Mode: {mode_text:<6}                    ", curses.color_pair(2))
            y += 1
            
            section_name = self.sections[self.section_index][0]
            scr.addstr(y, x, f"  Section: {section_name[:12]:<12}            ", curses.color_pair(2))
            y += 1
            
            scr.addstr(y, x, f"  Theme: {self.theme_name:<8}                ", curses.color_pair(2))
            y += 1
            
            waterfall_text = self.settings['waterfall'][:3].upper()
            scr.addstr(y, x, f"  Waterfall: {waterfall_text:<3}               ", curses.color_pair(2))
            y += 1
            
            scr.addstr(y, x, "+--------------------------------+", curses.color_pair(1))
            y += 2
            
            # ===== AUTHOR =====
            scr.addstr(y, x+8, "Marijuana1999", curses.color_pair(3))
            
        except Exception as e:
            pass
    # ==================================================================
    # FONT AND THEME HANDLERS
    # ==================================================================

    def change_font(self, scr):
        fonts = list(CMD_FONTS.keys())
        index = 0

        while True:
            scr.clear()
            self.draw_header(scr)
            
            scr.addstr(6, 3, "[ SELECT FONT ]", curses.color_pair(1))
            scr.addstr(7, 3, "═" * 40, curses.color_pair(1))
            
            y = 9
            for i, font_key in enumerate(fonts):
                font = CMD_FONTS[font_key]
                if i == index:
                    self.glow(scr, y + i, 5, f">> {font['name']}")
                    scr.addstr(y + i, 25, f"[{font['family']} - {font['size']}px]", curses.color_pair(3))
                else:
                    scr.addstr(y + i, 7, font['name'], curses.color_pair(2))
                    scr.addstr(y + i, 25, f"[{font['family']} - {font['size']}px]", curses.color_pair(2))
            
            scr.addstr(y + len(fonts) + 3, 3, "UP/DOWN: Navigate | ENTER: Select | BACKSPACE: Back", curses.color_pair(1))
            
            scr.refresh()
            key = scr.getch()

            if key == curses.KEY_UP:
                index = (index - 1) % len(fonts)
            elif key == curses.KEY_DOWN:
                index = (index + 1) % len(fonts)
            elif key in (8, 127, curses.KEY_BACKSPACE):
                return
            elif key in (10, 13):
                chosen = fonts[index]
                self.apply_font_settings(chosen)
                return

    def apply_font_settings(self, font_key):
        font = CMD_FONTS.get(font_key, CMD_FONTS["default"])
        
        self.settings["font"] = font_key
        save_settings(self.settings)
        
        curses.endwin()
        clear_screen()
        
        if platform.system() == "Windows":
            print("╔══════════════════════════════════════════════════════════╗")
            print("║                    FONT SETTINGS                         ║")
            print("╠══════════════════════════════════════════════════════════╣")
            print(f"║  Selected: {font['name']:<30}              ║")
            print(f"║  Family: {font['family']:<20}                         ║")
            print(f"║  Size: {font['size']}px                                          ║")
            print(f"║  Weight: {font['weight']:<20}                         ║")
            print("╠══════════════════════════════════════════════════════════╣")
            print("║  To apply:                                               ║")
            print("║  1. Right-click CMD title bar                            ║")
            print("║  2. Select 'Properties'                                  ║")
            print("║  3. Go to 'Font' tab                                     ║")
            print("║  4. Choose settings above                                ║")
            print("╚══════════════════════════════════════════════════════════╝")
        else:
            print("╔══════════════════════════════════════════════════════════╗")
            print("║                 FONT SETTINGS (Linux/macOS)              ║")
            print("╠══════════════════════════════════════════════════════════╣")
            print(f"║  Selected: {font['name']:<30}              ║")
            print(f"║  Family: {font['family']:<20}                         ║")
            print(f"║  Size: {font['size']}px                                          ║")
            print("╠══════════════════════════════════════════════════════════╣")
            print("║  To change terminal font:                                 ║")
            print("║  • Linux: Edit → Preferences → Custom font               ║")
            print("║  • macOS: Terminal → Preferences → Profiles → Text       ║")
            print("╚══════════════════════════════════════════════════════════╝")
        
        input("\nPress ENTER to continue...")

    def theme_list(self, scr):
        themes = get_theme_list()
        index = 0
        page = 0
        per_page = 8

        while True:
            scr.clear()
            self.draw_header(scr)
            
            scr.addstr(6, 3, "[ AVAILABLE THEMES ]", curses.color_pair(1))
            scr.addstr(7, 3, "═" * 70, curses.color_pair(1))
            
            start = page * per_page
            end = start + per_page
            current_themes = themes[start:end]
            
            y = 9
            for i, theme in enumerate(current_themes):
                theme_id = theme["id"]
                theme_name = theme["name"]
                desc = theme.get("description", "")
                
                color = curses.color_pair(2)
                if "red" in theme_id or "blood" in theme_id:
                    color = curses.color_pair(4)
                elif "green" in theme_id or "matrix" in theme_id:
                    color = curses.color_pair(2)
                elif "blue" in theme_id or "ocean" in theme_id:
                    color = curses.color_pair(1)
                
                if (page * per_page + i) == index:
                    self.glow(scr, y + i, 5, f">> {theme_name}")
                    if desc:
                        scr.addstr(y + i, 30, desc, curses.color_pair(3))
                else:
                    scr.addstr(y + i, 7, theme_name, color)
                    if desc:
                        scr.addstr(y + i, 30, desc[:40], curses.color_pair(2))
            
            total_pages = (len(themes) + per_page - 1) // per_page
            page_info = f"Page {page + 1}/{total_pages}"
            scr.addstr(y + per_page + 2, 3, "═" * 70, curses.color_pair(1))
            scr.addstr(y + per_page + 3, 30, page_info, curses.color_pair(1))
            
            help_text = "UP/DOWN: Navigate | LEFT/RIGHT: Change Page | BACKSPACE: Back"
            scr.addstr(y + per_page + 5, 3, help_text, curses.color_pair(1))
            
            scr.refresh()
            key = scr.getch()

            if key == curses.KEY_UP and index > 0:
                index -= 1
                if index < start:
                    page -= 1
            elif key == curses.KEY_DOWN and index < len(themes) - 1:
                index += 1
                if index >= end:
                    page += 1
            elif key == curses.KEY_LEFT and page > 0:
                page -= 1
                index = page * per_page
            elif key == curses.KEY_RIGHT and page < total_pages - 1:
                page += 1
                index = page * per_page
            elif key in (8, 127, curses.KEY_BACKSPACE):
                return

    def font_guide(self, scr):
        lines = [
            "FONT SETUP GUIDE",
            "",
            "Windows Terminal:",
            "  • Right-click title bar → Properties → Font",
            "",
            "Windows 11 Terminal:",
            "  • Click dropdown → Settings → Defaults → Appearance",
            "",
            "Linux Terminal:",
            "  • Edit → Preferences → Custom font",
            "",
            "macOS Terminal:",
            "  • Terminal → Preferences → Profiles → Text",
            "",
            "Best Fonts for Hacking:",
            "  • Consolas - Clean and sharp",
            "  • Lucida Console - Retro feel",
            "  • Courier New - Classic",
            "  • Cascadia Code - Modern",
            "",
            "Font Sizes:",
            "  • 12px - Small (more lines)",
            "  • 16px - Default (balanced)",
            "  • 20px - Large (easier to read)",
            "",
            "CMD Color Codes:",
            "  • 0A - Light Green (Matrix)",
            "  • 0C - Light Red (Blood)",
            "  • 0D - Light Magenta (Purple)",
            "  • 0E - Light Yellow (Amber)",
            "",
            "Press BACKSPACE to return"
        ]

        top = 0
        height, width = scr.getmaxyx()

        while True:
            scr.clear()
            self.draw_header(scr)
            
            visible = lines[top: top + height - 9]
            y = 7
            for line in visible:
                if line.startswith("  •"):
                    scr.addstr(y, 5, line, curses.color_pair(2))
                elif ":" in line and not line.startswith(" "):
                    scr.addstr(y, 3, line, curses.color_pair(1) | curses.A_BOLD)
                else:
                    scr.addstr(y, 3, line, curses.color_pair(2))
                y += 1
            
            scr.addstr(height - 2, 3, "↑ ↓ to scroll | BACKSPACE to exit", curses.color_pair(1))
            scr.refresh()

            key = scr.getch()
            if key in (8, 127, curses.KEY_BACKSPACE):
                return
            if key == curses.KEY_UP and top > 0:
                top -= 1
            if key == curses.KEY_DOWN and (top + height - 9) < len(lines):
                top += 1

    # ==================================================================
    # SETTINGS HANDLERS
    # ==================================================================

    def toggle_waterfall(self):
        if self.settings["waterfall"] == "intro":
            self.settings["waterfall"] = "always"
        elif self.settings["waterfall"] == "always":
            self.settings["waterfall"] = "off"
        else:
            self.settings["waterfall"] = "intro"
        save_settings(self.settings)

    def toggle_mouse(self):
        self.settings["mouse"] = not self.settings["mouse"]
        save_settings(self.settings)

    def change_theme(self, scr):
        themes = list(THEMES.keys())
        index = themes.index(self.theme_name) if self.theme_name in themes else 0

        while True:
            scr.clear()
            self.draw_header(scr)
            scr.addstr(7, 3, "[ SELECT THEME ]", curses.color_pair(1))

            for i, th in enumerate(themes):
                if i == index:
                    self.glow(scr, 9 + i, 5, f">> {th}")
                else:
                    scr.addstr(9 + i, 7, th, curses.color_pair(2))

            scr.refresh()
            key = scr.getch()

            if key == curses.KEY_UP:
                index = (index - 1) % len(themes)
            elif key == curses.KEY_DOWN:
                index = (index + 1) % len(themes)
            elif key in (8, 127, curses.KEY_BACKSPACE):
                return
            elif key in (10, 13):
                chosen = themes[index]
                save_theme(chosen)
                curses.endwin()
                clear_screen()
                print(f"\nTheme '{chosen}' selected. Restarting...")
                print("Cyber HUD - Marijuana1999")
                print("GitHub: https://github.com/Marijuana1999")
                time.sleep(2)
                os.execv(sys.executable, [sys.executable] + sys.argv)

    def about(self, scr):
        lines = [
            "ABOUT CYBER HUD",
            "",
            "Author: Marijuana1999",
            "GitHub: https://github.com/Marijuana1999",
            "Version: 3.0",
            "",
            "Advanced Security Testing Framework",
            "for Bug Bounty Hunters",
            "",
            "Features:",
            "  • Passive reconnaissance modules",
            "  • Security headers analysis",
            "  • Cookie security checker",
            "  • WAF detection",
            "  • CORS misconfiguration scanner",
            "  • User security checker (VPN, DNS, Proxy)",
            "  • HTML/PDF report generation",
            "  • And much more...",
            "",
            "Legal Notice:",
            "This tool is for educational purposes only.",
            "Always get proper authorization before testing.",
            "",
            "Press BACKSPACE to return"
        ]

        top = 0
        height, width = scr.getmaxyx()

        while True:
            scr.clear()
            self.draw_header(scr)
            visible = lines[top: top + height - 9]
            y = 7
            for line in visible:
                scr.addstr(y, 3, line[:width-6], curses.color_pair(2))
                y += 1
            scr.addstr(height - 2, 3, "↑ ↓ to scroll, BACKSPACE to exit", curses.color_pair(1))
            scr.refresh()

            key = scr.getch()
            if key in (8, 127, curses.KEY_BACKSPACE):
                return
            if key == curses.KEY_UP and top > 0:
                top -= 1
            if key == curses.KEY_DOWN and (top + height - 9) < len(lines):
                top += 1

    def help(self, scr):
        lines = [
            "CYBER OPS MANUAL",
            "",
            "← BACKSPACE : Return",
            "↑ ↓ : Scroll",
            "",
            "1) TARGET",
            "   • Set Target: Enter your target domain",
            "   • Show Target: Display current target",
            "   • Target Dashboard: Manage multiple targets",
            "",
            "2) RECON",
            "   • DNS Enumeration: Find subdomains",
            "   • Reverse IP: Domains on same server",
            "   • ASN Lookup: Organization info",
            "   • Crawler: Extract URLs & endpoints",
            "   • Tech Fingerprinting: Detect backend",
            "   • HTTP Headers: Security headers check",
            "   • IP Tracker: Track IP location",
            "",
            "3) SCANNING",
            "   • Port Scan: Find open ports",
            "   • SSL Scan: Check TLS versions",
            "   • Rate Limit: Test brute-force protection",
            "",
            "4) WEB SECURITY",
            "   • WAF Detection: Identify firewall",
            "   • CORS Analyzer: Check misconfigurations",
            "   • Cookie Security: Check flags",
            "   • Robots Recon: Find hidden paths",
            "   • Passive XSS: Detect XSS reflections",
            "   • Passive SQLi: Find SQL errors",
            "",
            "5) EXPLOITS",
            "   • Backup Finder: Find exposed backups",
            "   • Backup Exploit: Verify backup files",
            "",
            "6) UTILITIES",
            "   • Directory Scan: Find admin panels",
            "   • Screenshot: Take webpage screenshot",
            "",
            "7) ADVANCED",
            "   • JWT Analyzer: Check JSON Web Tokens",
            "   • GraphQL Scanner: Find GraphQL endpoints",
            "   • Cache Poisoning: Test cache vulnerabilities",
            "   • Rate Limit Bypass: Bypass rate limiting",
            "   • CORS Advanced: Deep CORS testing",
            "   • Subdomain Takeover: Check for takeovers",
            "",
            "8) SECURITY (Your Protection)",
            "   • Security Checker: Check VPN/DNS/Proxy",
            "   • IP Hider: Hide your real IP",
            "   • DNS Leak Test: Check for DNS leaks",
            "",
            "9) SETTINGS",
            "   • Change Theme: Change color theme",
            "   • Waterfall Mode: Toggle matrix effect",
            "   • Mouse Support: Enable/disable mouse",
            "   • Help / Manual: This help page",
            "   • About: About CyberHUD",
            "",
            "10) EXIT",
            "    • Quit Framework: Exit CyberHUD",
            "",
            "Author: Marijuana1999",
            "GitHub: https://github.com/Marijuana1999"
        ]

        top = 0
        height, width = scr.getmaxyx()

        while True:
            scr.clear()
            self.draw_header(scr)
            visible = lines[top: top + height - 9]
            y = 7
            for line in visible:
                scr.addstr(y, 3, line[:width-6], curses.color_pair(2))
                y += 1
            scr.addstr(height - 2, 3, "↑ ↓ to scroll, BACKSPACE to exit", curses.color_pair(1))
            scr.refresh()

            key = scr.getch()
            if key in (8, 127, curses.KEY_BACKSPACE):
                return
            if key == curses.KEY_UP and top > 0:
                top -= 1
            if key == curses.KEY_DOWN and (top + height - 9) < len(lines):
                top += 1

    def show_target(self):
        target = self.get_target()
        clear_screen()
        print("+------------------------+")
        print(f"  Target: {target or 'Not Set':<14} ")
        print("+------------------------+")
        input("\nPress ENTER...")

    def target_dashboard(self):
        clear_screen()
        print("+------------------------+")
        print("    Target Dashboard     ")
        print("+------------------------+")
        print(f"  Current: {self.get_target() or 'None':<14} ")
        print("  Feature coming soon    ")
        print("+------------------------+")
        input("\nPress ENTER...")

    def execute_action(self, action, scr):
        if action in ["toggle_waterfall", "toggle_mouse"]:
            getattr(self, action)()
            return
        if action == "help":
            self.help(scr)
            return
        if action == "about":
            self.about(scr)
            return
        if action == "change_theme":
            self.change_theme(scr)
            return
        if action == "change_font":
            self.change_font(scr)
            return
        if action == "theme_list":
            self.theme_list(scr)
            return
        if action == "font_guide":
            self.font_guide(scr)
            return
        if action == "set_target":
            curses.endwin()
            clear_screen()
            print("+------------------------+")
            print("        SET TARGET       ")
            print("+------------------------+")
            print()
            value = input("Enter target (example.com): ").strip()
            if value:
                self.set_target(value)
                print(f"\n[✓] Target set to: {value}")
            input("\nPress ENTER...")
            return
        
        if action == "show_target":
            curses.endwin()
            clear_screen()
            self.show_target()
            return
        
        if action == "target_dashboard":
            curses.endwin()
            clear_screen()
            self.target_dashboard()
            return
        
        # Security actions
        if action == "security_checker":
            curses.endwin()
            clear_screen()
            try:
                from core.security_checker import run
                run(None)
            except Exception as e:
                print(f"\n[!] Error: {e}")
                input("\nPress ENTER...")
            return
        
        if action == "ip_hider":
            curses.endwin()
            clear_screen()
            try:
                from core.ip_hider import IPHider
                IPHider().hide_ip_menu()
            except Exception as e:
                print(f"\n[!] Error: {e}")
                input("\nPress ENTER...")
            return
        
        if action == "dns_leak_test":
            curses.endwin()
            clear_screen()
            try:
                from core.dns_leak_test import run
                run(None)
            except Exception as e:
                print(f"\n[!] Error: {e}")
                input("\nPress ENTER...")
            return
        
        if action == "exit":
            curses.endwin()
            clear_screen()
            print("+------------------------+")
            print("   CYBER HUD - Goodbye!  ")
            print("+------------------------+")
            print("\nExiting CyberHUD...")
            sys.exit(0)

        target = self.get_target()
        if not target:
            curses.endwin()
            clear_screen()
            print("+------------------------+")
            print("        CYBER HUD        ")
            print("+------------------------+")
            print()
            print("[!] No target set.")
            input("\nPress ENTER...")
            return

        curses.endwin()
        clear_screen()
        print(f"[+] Running module...")
        print(f"    Target: {target}")
        print("-" * 40)

        try:
            action(target)
        except Exception as e:
            print(f"\n[!] Error: {e}")

        input("\nPress ENTER to return...")

    def loop(self, scr):
        curses.curs_set(0)
        scr.keypad(True)

        if self.settings["waterfall"] in ("intro", "always"):
            self.matrix_rain(scr)
        self.crt_effect(scr)

        while True:
            scr.clear()
            self.draw_header(scr)
            
            if not self.in_section:
                self.draw_sections(scr)
            else:
                self.draw_items(scr)
            
            self.draw_minimap(scr)
            scr.refresh()

            key = scr.getch()

            if key in (8, 127, curses.KEY_BACKSPACE):
                self.in_section = False
                continue

            if key == curses.KEY_UP:
                if not self.in_section:
                    self.section_index = (self.section_index - 1) % len(self.sections)
                else:
                    items = self.sections[self.section_index][1]
                    self.item_index = (self.item_index - 1) % len(items)
                continue

            if key == curses.KEY_DOWN:
                if not self.in_section:
                    self.section_index = (self.section_index + 1) % len(self.sections)
                else:
                    items = self.sections[self.section_index][1]
                    self.item_index = (self.item_index + 1) % len(items)
                continue

            if key in (10, 13):
                if not self.in_section:
                    self.in_section = True
                else:
                    action = self.sections[self.section_index][1][self.item_index]["action"]
                    self.execute_action(action, scr)
                continue

            if self.settings["waterfall"] == "always":
                self.matrix_rain(scr)


# ======================================================================
# MAIN
# ======================================================================

def setup(scr):
    env = detect_environment()
    print(f"[ Environment detected: {env.upper()} ]")
    time.sleep(0.5)

    theme = load_theme()
    settings = load_settings()

    curses.start_color()
    curses.init_pair(1, theme["label"], curses.COLOR_BLACK)
    curses.init_pair(2, theme["text"], curses.COLOR_BLACK)
    curses.init_pair(3, theme["highlight"], curses.COLOR_BLACK)
    curses.init_pair(4, theme["glow"], curses.COLOR_BLACK)

    hud = CyberHUD(theme, settings)
    hud.loop(scr)


if __name__ == "__main__":
    try:
        curses.wrapper(setup)
    except KeyboardInterrupt:
        clear_screen()
        print("\n+------------------------+")
        print("   CYBER HUD - Goodbye!  ")
        print("+------------------------+")
        print("\nExiting CyberHUD...")
        sys.exit(0)
    except Exception as e:
        clear_screen()
        print(f"\n[!] Error: {e}")
        sys.exit(1)