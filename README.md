# 🚀 CyberHUD - Advanced Security Testing Framework

**Version 3.2** | [GitHub Repository](https://github.com/Marijuana1999/CyberHUD) | [Report Bug](https://github.com/Marijuana1999/CyberHUD/issues)

<div align="center">
  <img src="https://img.shields.io/badge/Python-3.6%2B-blue?style=for-the-badge&logo=python"/>
  <img src="https://img.shields.io/badge/Platform-Windows%20%7C%20Linux%20%7C%20macOS%20%7C%20Termux-green?style=for-the-badge"/>
  <img src="https://img.shields.io/github/v/release/Marijuana1999/CyberHUD?style=for-the-badge&color=red"/>
  <img src="https://img.shields.io/github/downloads/Marijuana1999/CyberHUD/total?style=for-the-badge&color=yellow"/>
</div>

---

## 📋 **Table of Contents**
- [Overview](#-overview)
- [Features](#-features)
- [Multi-Platform Support](#-multi-platform-support)
- [Quick Installation](#-quick-installation)
- [Usage Guide](#-usage-guide)
- [Modules Description](#-modules-description)
- [Auto-Update System](#-auto-update-system)
- [Themes & Customization](#-themes--customization)
- [Security Features](#-security-features)
- [Troubleshooting](#-troubleshooting)
- [Contributing](#-contributing)
- [License](#-license)

---

## 🎯 **Overview**

**CyberHUD** is an advanced, **passive** security testing framework designed for **Bug Bounty Hunters** and **Security Researchers**. It operates without sending malicious requests, making it safe for authorized security assessments.

### ✨ **What's New in v3.3**
- ✅ **Auto-Update System** - One-click updates from GitHub
- ✅ **Improved Linux/macOS Support** - Fixed arrow keys and terminal issues
- ✅ **Multi-Platform UI** - Consistent experience across Windows, Linux, macOS, Termux
- ✅ **Better Error Handling** - Permission prompts for file replacements
- ✅ **Optimized Performance** - No more lag in menus
- ✅ **Enhanced Security Checker** - Better VPN, DNS, and IP detection
- ✅ **Fixed API Rate Limiting** - Smart caching reduces GitHub API calls

---

## ⚡ **Features**

### 🔍 **Reconnaissance**
- DNS Enumeration (A, AAAA, MX, NS, TXT, SOA)
- Reverse IP Lookup (find domains on same server)
- ASN & WHOIS Information
- Web Crawler (extract URLs, forms, parameters)
- Technology Fingerprinting (WordPress, Laravel, React, etc.)
- HTTP Headers Analysis
- IP Geolocation Tracker

### 🔬 **Scanning**
- Port Scanner (common ports)
- SSL/TLS Security Check
- Rate Limit Testing

### 🌐 **Web Security**
- WAF Detection (Cloudflare, F5, ModSecurity, etc.)
- CORS Misconfiguration Scanner
- Cookie Security Analyzer
- Robots.txt Recon
- Passive XSS Detection
- Passive SQLi Detection

### 💣 **Exploits**
- Backup File Finder (zip, sql, bak, old)
- Backup Content Verification

### 🛠️ **Utilities**
- Directory Scanner
- Screenshot Capture (Selenium)

### ⚙️ **Advanced**
- JWT Analyzer
- GraphQL Endpoint Scanner
- Cache Poisoning Tester
- Rate Limit Bypass
- Subdomain Takeover Checker

### 🛡️ **User Security**
- VPN Detection
- DNS Leak Test
- IP Hider (DNS Changer)
- Proxy Detection
- Firewall Status Check

---

## 💻 **Multi-Platform Support**

| Platform | Support | Status |
|----------|---------|--------|
| **Windows 10/11** | ✅ Full | CMD, PowerShell, Git Bash |
| **Linux** (Ubuntu, Debian, Kali) | ✅ Full | Terminal |
| **macOS** | ✅ Full | Terminal |
| **Termux** (Android) | ✅ Full | pkg install |

### **Tested On:**
- ✅ Windows 10/11
- ✅ Ubuntu 20.04/22.04
- ✅ Kali Linux
- ✅ macOS Ventura/Sonoma
- ✅ Termux (Android 10+)

---

## 🚀 **Quick Installation**

### **Windows**
```batch
# Just double-click
run.bat
```

### **Linux / macOS**
```bash
# Make executable and run
chmod +x run.sh
./run.sh
```

### **Termux (Android)**
```bash
pkg update && pkg install python -y
chmod +x run.sh
./run.sh
```

### **Manual Installation**
```bash
git clone https://github.com/Marijuana1999/CyberHUD.git
cd CyberHUD
pip install -r requirements.txt
python menu.py
```

---

## 📖 **Usage Guide**

### **Navigation**
| Key | Function |
|-----|----------|
| ↑ ↓ | Navigate menu |
| ENTER | Select item |
| BACKSPACE | Go back |
| ESC | Back to menu |

### **Basic Workflow**
1. **Set Target** - Enter your target domain
2. **Recon** - Gather information
3. **Scan** - Find vulnerabilities
4. **Report** - Save results

### **First Run**
- Auto-checks for Python packages
- Asks for update if new version available
- Creates `logs/` directory for results

---

## 🔄 **Auto-Update System**

### **How It Works**
1. Checks GitHub API for latest release
2. Shows changelog and asks for permission
3. Downloads new version (ZIP/RAR)
4. Asks for file replacement confirmation
5. Automatically restarts

### **Features**
- ✅ **One-click update** from menu (Settings → Check for Updates)
- ✅ **Smart caching** (only checks API every hour)
- ✅ **Cross-platform** (works on Windows, Linux, macOS)
- ✅ **Permission prompts** for file replacement
- ✅ **Progress bar** during download
- ✅ **Automatic restart** after update

### **Update Process**
```
🔍 Checking for updates...
  Current version: 3.1
  Latest version:  3.2
  Asset: CyberHUD_v3.2.zip

✨ New version 3.2 available!

📝 Release Notes:
  • Added auto-update system
  • Fixed Linux arrow keys
  • Improved performance

⬇️ Download and install now? (y/n): y
📥 Downloading update...
[██████████████████████████████] 100%

⚠️ 5 file(s) will be replaced.
Do you want to proceed? (y/n): y
  🔄 Replaced: menu.py
  🔄 Replaced: core/auto_update.py
  ➕ Added: new_module.py

✅ Update applied successfully!
🔄 Restarting...
```

---

## 🎨 **Themes & Customization**

### **Available Themes (17)**
| Theme | Description | CMD Color |
|-------|-------------|-----------|
| Dark Neon | Classic dark with neon accents | Light Green |
| Blue Soft | Soft blue theme | Light Blue |
| Hacker Green | Classic green matrix style | Light Green |
| Matrix Reloaded | Matrix with cyan | Light Green |
| Blood Red | Aggressive red theme | Light Red |
| Royal Purple | Elegant purple | Light Magenta |
| Ocean Deep | Deep blue ocean | Light Cyan |
| Sunset Orange | Warm sunset colors | Light Yellow |
| Midnight Blue | Dark blue with cyan | Dark Blue |
| Amber Glow | Retro amber style | Dark Yellow |
| Cyber Punk | Cyberpunk 2077 style | Light Magenta |
| Ghost White | Clean white with blue | Bright White |
| Forest Green | Dark green forest | Dark Green |
| Lava Red | Hot lava red | Light Red |
| Arctic Ice | Cold arctic blue | Light Cyan |
| Retro Terminal | Classic monochrome | Dark Green |
| Neon Pink | Bright neon pink | Light Magenta |

### **Font Settings** (Windows CMD)
- Right-click title bar → Properties → Font
- Choose from: Consolas, Lucida Console, Courier New

---

## 🔐 **Security Features**

### **User Security Checker**
```bash
SECURITY → Security Checker
```
- ✅ VPN Detection (20+ VPN services)
- ✅ DNS Server Detection
- ✅ IP Geolocation
- ✅ Proxy Detection
- ✅ Tor Detection
- ✅ Firewall Status
- ✅ Security Score

### **IP Hider**
```bash
SECURITY → IP Hider
```
- Change DNS to secure servers (1.1.1.1, 8.8.8.8)
- DNS leak testing
- Proxy detection

---

## 🐛 **Troubleshooting**

### **Common Issues**

| Problem | Solution |
|---------|----------|
| Arrow keys don't work in Linux | Update to v3.2 or run `stty sane` |
| Update fails with permission error | Run as administrator (Windows) or with `sudo` (Linux) |
| API rate limit exceeded | Wait 1 hour or use cached data |
| RAR extraction fails | Install 7-Zip (Windows) or `unrar` (Linux) |
| Python not found | Install Python 3.6+ and add to PATH |

### **Debug Mode**
Check `update_log.txt` for update-related errors
Check `logs/` directory for scan results

---

## 🤝 **Contributing**

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing`)
5. Open Pull Request

### **Development Setup**
```bash
git clone https://github.com/Marijuana1999/CyberHUD.git
cd CyberHUD
pip install -r requirements-dev.txt
python menu.py
```

---

## 📄 **License**

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

**Disclaimer:** This tool is for educational purposes and authorized security testing only. Users are responsible for complying with applicable laws.

---

## 🌟 **Star History**

[![Star History Chart](https://api.star-history.com/svg?repos=Marijuana1999/CyberHUD&type=Date)](https://star-history.com/#Marijuana1999/CyberHUD&Date)

---

## 📞 **Contact**

- **Author:** Marijuana1999
- **GitHub:** [https://github.com/Marijuana1999](https://github.com/Marijuana1999)
- **Issues:** [https://github.com/Marijuana1999/CyberHUD/issues](https://github.com/Marijuana1999/CyberHUD/issues)

---

**Made with ❤️ for the Bug Bounty Community**
