# 🚀 CyberHUD - Advanced Security Testing Framework

**Version 3.4**  
GitHub Repository: https://github.com/Marijuana1999/CyberHUD  
Report Bug: https://github.com/Marijuana1999/CyberHUD/issues  

<div align="center">
  <img src="https://img.shields.io/badge/Python-3.6%2B-blue?style=for-the-badge&logo=python"/>
  <img src="https://img.shields.io/badge/Platform-Windows%20%7C%20Linux%20%7C%20macOS%20%7C%20Termux-green?style=for-the-badge"/>
  <img src="https://img.shields.io/github/v/release/Marijuana1999/CyberHUD?style=for-the-badge&color=red"/>
  <img src="https://img.shields.io/github/downloads/Marijuana1999/CyberHUD/total?style=for-the-badge&color=yellow"/>
</div>

---

## 📋 Table of Contents
- Overview
- What's New in v3.4
- Features
- Multi-Platform Support
- Quick Installation
- Usage Guide
- Modules Description
- Release History
- Auto-Update System
- Themes & Customization
- Security Features
- Troubleshooting
- Contributing
- License
- Contact

---

# 🎯 Overview

CyberHUD is an advanced, **passive** security testing framework designed for **Bug Bounty Hunters** and **Security Researchers**.

It performs safe reconnaissance and vulnerability discovery without sending destructive payloads, making it suitable for authorized security assessments.

---

# ✨ What's New in v3.4

## 🛡 Advanced WAF Detection Engine
- 30+ WAF Signatures (Cloudflare, AWS WAF, Akamai, Imperva, F5, ModSecurity, etc.)
- Multi-layer detection (Headers, Cookies, HTML patterns, Challenge pages)
- 200+ payload effectiveness testing
- 15+ evasion technique detection
- Confidence scoring (CRITICAL / HIGH / MEDIUM / LOW)

## 🔍 InfoLeak Detector
- WordPress REST API discovery
- User enumeration detection
- Sensitive file scanner (.env, backups, configs, debug logs)
- Plugin & theme detection
- Automatic risk assessment

## 📊 Professional Logging System
- JSON structured logging
- Human-readable text logs
- Module-based directories (`logs/waf/`, `logs/infoleak/`)
- Timestamped filenames
- Colorized console output
- Cross-platform compatibility

---

# ⚡ Features

## 🔍 Reconnaissance
- DNS Enumeration (A, AAAA, MX, NS, TXT, SOA)
- Reverse IP Lookup
- ASN & WHOIS
- Web Crawler
- Technology Fingerprinting
- HTTP Header Analysis
- IP Geolocation

## 🔬 Scanning
- Port Scanner
- SSL/TLS Security Check
- Rate Limit Testing

## 🌐 Web Security
- WAF Detection
- InfoLeak Detector
- CORS Misconfiguration Scanner
- Cookie Security Analyzer
- Robots.txt Recon
- Passive XSS Detection
- Passive SQLi Detection

## 💣 Exploits
- Backup File Finder
- Backup Content Verification

## 🛠 Utilities
- Directory Scanner
- Screenshot Capture (Selenium)

## ⚙ Advanced
- JWT Analyzer
- GraphQL Endpoint Scanner
- Cache Poisoning Tester
- Rate Limit Bypass
- Subdomain Takeover Checker

## 🛡 User Security
- VPN Detection
- DNS Leak Test
- IP Hider (DNS Changer)
- Proxy Detection
- Firewall Status Check
- Security Score

---

# 💻 Multi-Platform Support

| Platform | Status |
|----------|--------|
| Windows 10/11 | ✅ Full |
| Linux (Ubuntu, Kali, Debian) | ✅ Full |
| macOS | ✅ Full |
| Termux (Android) | ✅ Full |

---

# 🚀 Quick Installation

## Windows
```
run.bat
```

## Linux / macOS
```
chmod +x run.sh
./run.sh
```

## Termux
```
pkg update && pkg install python -y
chmod +x run.sh
./run.sh
```

## Manual Installation
```
git clone https://github.com/Marijuana1999/CyberHUD.git
cd CyberHUD
pip install -r requirements.txt
python menu.py
```

---

# 📖 Usage Guide

## Navigation

| Key | Function |
|-----|----------|
| ↑ ↓ | Navigate |
| ENTER | Select |
| BACKSPACE | Go Back |
| ESC | Main Menu |

## Basic Workflow

1. Set Target
2. Run Recon Modules
3. Run Security Scanners
4. Review Logs in `logs/` directory

---

# 📦 Modules Description

| Category | Modules |
|----------|---------|
| Recon | DNS, Reverse IP, ASN, Crawler, Headers |
| Scanning | Ports, SSL, Rate Limit |
| Web Security | WAF, InfoLeak, CORS, Cookies, XSS, SQLi |
| Exploits | Backup Finder |
| Utilities | Directory Scan, Screenshot |
| Advanced | JWT, GraphQL, Cache Poisoning |
| Security | Security Checker, IP Hider |

---

# 📜 Release History

## v3.4 (Current)
- Advanced WAF Detection Engine
- InfoLeak Detector
- Professional Logging System
- Payload Effectiveness Testing
- Evasion Detection
- Risk Scoring System

## v3.3
- Auto-Update System
- Linux/macOS improvements
- API caching system
- Performance optimizations

## v3.2
- User Security Checker
- IP Hider
- 17 Themes
- Security Score System

## v3.1
- Performance optimization
- SSL scan fixes
- Better timeout handling

## v3.0
- Full framework redesign
- Modular architecture
- Multi-threading support
- HTML/PDF reports

## v2.0
- Logging system
- Target management
- Improved menu interface

## v1.0
- Initial release
- Basic scanning modules

---

# 🔄 Auto-Update System

- Checks GitHub API for latest release
- Displays changelog
- Downloads update package
- File replacement confirmation
- Automatic restart
- Smart API caching (1 hour)

---

# 🎨 Themes & Customization

17 Built-in themes including:
- Hacker Green
- Matrix Reloaded
- Cyber Punk
- Neon Pink
- Retro Terminal
- Midnight Blue
- Ocean Deep
- Arctic Ice
- Blood Red
- And more...

Windows users can customize fonts via CMD Properties.

---

# 🔐 Security Features

## Security Checker Includes:
- VPN Detection
- DNS Server Analysis
- IP Geolocation
- Proxy Detection
- Tor Detection
- Firewall Status
- Overall Security Score

## IP Hider:
- Change DNS (1.1.1.1 / 8.8.8.8)
- DNS Leak Testing
- Proxy Detection

---

# 🐛 Troubleshooting

| Problem | Solution |
|----------|----------|
| Arrow keys not working | Update to v3.3+ |
| Update permission error | Run as Administrator / sudo |
| API rate limit exceeded | Wait 1 hour |
| RAR extraction fails | Install 7-Zip or unrar |
| Python not found | Install Python 3.6+ |

Logs available inside `logs/`

---

# 🤝 Contributing

```
git clone https://github.com/Marijuana1999/CyberHUD.git
cd CyberHUD
pip install -r requirements-dev.txt
python menu.py
```

1. Fork repository  
2. Create feature branch  
3. Commit changes  
4. Push branch  
5. Open Pull Request  

---

# 📄 License

MIT License  

Disclaimer:  
This tool is for educational purposes and authorized security testing only.  
Users are responsible for complying with applicable laws.

---

# ⚠️🚫 LEGAL & LIABILITY DISCLAIMER 🚫⚠️

## ❗ IMPORTANT NOTICE — READ CAREFULLY ❗

CyberHUD is an open-source cybersecurity framework developed strictly for:

- 🎓 Educational purposes  
- 🔬 Security research  
- 🛡 Authorized penetration testing  

---

## 🚫 STRICTLY PROHIBITED

🚫 **DO NOT use this tool for illegal activities.**  
🚫 **DO NOT test systems without explicit written authorization.**  
🚫 **DO NOT attempt unauthorized access, disruption, or exploitation.**

Any form of illegal, malicious, or unethical usage is strictly forbidden.

---

## 🔒 USER RESPONSIBILITY

By downloading, accessing, or using this software, you agree that:

- You are **fully and solely responsible** for your actions.
- You will only use this tool on systems you own or have explicit permission to test.
- You understand and comply with all applicable local, national, and international laws.

---

## ⚖️ NO LIABILITY

The developer and contributors:

❗ Assume **NO responsibility** for misuse.  
❗ Are **NOT liable** for any damages, data loss, legal consequences, or criminal charges resulting from improper use.  
❗ Provide this software **"AS IS"**, without any warranty, express or implied.

If you choose to misuse this software, you do so entirely at your own risk.

---

## 🌍 Open-Source Purpose

This project is made open-source to promote:

- Transparency  
- Learning  
- Skill development  
- Collaboration within the cybersecurity community  

It is **NOT** intended to facilitate malicious activity.

---

### 🔥 If you do not agree with these terms — DO NOT USE THIS SOFTWARE.

Use responsibly. Use ethically.
---
# 🌟 Star History

https://api.star-history.com/svg?repos=Marijuana1999/CyberHUD&type=Date

---

# 📞 Contact

Author: Marijuana1999  
GitHub: https://github.com/Marijuana1999  
Issues: https://github.com/Marijuana1999/CyberHUD/issues  

---

**Made with ❤️ for the Bug Bounty Community**
