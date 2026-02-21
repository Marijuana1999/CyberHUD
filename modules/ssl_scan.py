#!/usr/bin/env python3

# modules/ssl_scan.py
import ssl
import socket
import datetime
import platform
import subprocess
import sys
from core.core import Color, save_log

# ============================================================
# CONFIGURATION
# ============================================================

WEAK_CIPHERS = [
    "RC4", "MD5", "NULL", "DES", "EXPORT", "aNULL", "eNULL",
    "LOW", "MEDIUM", "CBC", "SHA1"
]

SSL_VERSIONS = {
    "SSLv2": ssl.PROTOCOL_SSLv23 if hasattr(ssl, 'PROTOCOL_SSLv23') else None,
    "SSLv3": ssl.PROTOCOL_SSLv3 if hasattr(ssl, 'PROTOCOL_SSLv3') else None,
    "TLSv1.0": ssl.PROTOCOL_TLSv1 if hasattr(ssl, 'PROTOCOL_TLSv1') else None,
    "TLSv1.1": ssl.PROTOCOL_TLSv1_1 if hasattr(ssl, 'PROTOCOL_TLSv1_1') else None,
    "TLSv1.2": ssl.PROTOCOL_TLSv1_2 if hasattr(ssl, 'PROTOCOL_TLSv1_2') else None,
    "TLSv1.3": ssl.PROTOCOL_TLS_CLIENT if hasattr(ssl, 'PROTOCOL_TLS_CLIENT') else None
}

# ============================================================
# CERTIFICATE FUNCTIONS
# ============================================================

def get_certificate(host, port=443, timeout=5):
    """Retrieve SSL certificate from server"""
    cert = {}
    
    try:
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        
        with socket.create_connection((host, port), timeout=timeout) as sock:
            with ctx.wrap_socket(sock, server_hostname=host) as ssock:
                cert = ssock.getpeercert()
                
                # Get cipher info
                cipher = ssock.cipher()
                if cipher:
                    cert['cipher'] = {
                        'name': cipher[0],
                        'protocol': cipher[1],
                        'bits': cipher[2]
                    }
        
        return cert, None
    
    except socket.timeout:
        return None, "Connection timeout"
    except socket.gaierror:
        return None, "Could not resolve hostname"
    except ConnectionRefusedError:
        return None, "Connection refused"
    except ssl.SSLError as e:
        return None, f"SSL Error: {str(e)}"
    except Exception as e:
        return None, str(e)

def format_certificate_info(cert):
    """Format certificate information for display"""
    info = {}
    
    # Subject
    subject = dict(x[0] for x in cert.get('subject', []))
    info['subject'] = {
        'commonName': subject.get('commonName', 'Unknown'),
        'organization': subject.get('organizationName', 'Unknown'),
        'country': subject.get('countryName', 'Unknown')
    }
    
    # Issuer
    issuer = dict(x[0] for x in cert.get('issuer', []))
    info['issuer'] = {
        'commonName': issuer.get('commonName', 'Unknown'),
        'organization': issuer.get('organizationName', 'Unknown')
    }
    
    # Validity
    info['validity'] = {
        'notBefore': cert.get('notBefore', 'Unknown'),
        'notAfter': cert.get('notAfter', 'Unknown')
    }
    
    # Calculate days left
    try:
        not_after = cert.get('notAfter', '')
        exp_date = datetime.datetime.strptime(not_after, "%b %d %H:%M:%S %Y %Z")
        days_left = (exp_date - datetime.datetime.utcnow()).days
        info['validity']['daysLeft'] = days_left
    except:
        info['validity']['daysLeft'] = 'Unknown'
    
    # Version and serial
    info['version'] = cert.get('version', 'Unknown')
    info['serialNumber'] = cert.get('serialNumber', 'Unknown')
    
    # SAN (Subject Alternative Names)
    san = []
    for ext in cert.get('extensions', []):
        if ext.get('extnID') == 'subjectAltName':
            for name in ext.get('value', []):
                san.append(name)
    info['subjectAltNames'] = san
    
    return info

# ============================================================
# TLS VERSION TESTING
# ============================================================

def test_tls_version(host, version_name, port=443, timeout=3):
    """Test if a specific TLS version is supported"""
    if version_name not in SSL_VERSIONS or not SSL_VERSIONS[version_name]:
        return False, "Not available in this Python version"
    
    try:
        context = ssl.SSLContext(SSL_VERSIONS[version_name])
        context.check_hostname = False
        context.verify_mode = ssl.CERT_NONE
        
        with socket.create_connection((host, port), timeout=timeout) as sock:
            with context.wrap_socket(sock, server_hostname=host) as ssock:
                return True, ssock.cipher()[0] if ssock.cipher() else "Supported"
    
    except ssl.SSLError as e:
        if "unsupported protocol" in str(e).lower():
            return False, "Not supported"
        return False, str(e)
    except Exception as e:
        return False, str(e)

def check_all_tls_versions(host):
    """Check all TLS versions for support"""
    results = {}
    
    for version in SSL_VERSIONS:
        supported, info = test_tls_version(host, version)
        results[version] = {
            'supported': supported,
            'info': info
        }
    
    return results

# ============================================================
# CIPHER ANALYSIS
# ============================================================

def analyze_cipher_strength(cipher_name):
    """Analyze cipher strength and detect weaknesses"""
    analysis = {
        'weak': False,
        'reasons': []
    }
    
    cipher_upper = cipher_name.upper()
    
    for weak in WEAK_CIPHERS:
        if weak.upper() in cipher_upper:
            analysis['weak'] = True
            analysis['reasons'].append(f"Contains {weak}")
    
    # Check key size
    if "128" in cipher_upper and "AES" not in cipher_upper:
        analysis['reasons'].append("128-bit key may be weak")
    
    if "56" in cipher_upper or "40" in cipher_upper:
        analysis['weak'] = True
        analysis['reasons'].append("Short key size")
    
    return analysis

# ============================================================
# MAIN FUNCTION
# ============================================================

def run(target):
    """Main SSL/TLS scanner"""
    print(Color.C + "\n[+] SSL/TLS Security Scanner\n" + Color.N)
    
    if not target:
        print(Color.R + "[!] No target set" + Color.N)
        return
    
    # Remove port if present
    if ':' in target:
        host, port_str = target.split(':', 1)
        try:
            port = int(port_str)
        except:
            port = 443
    else:
        host = target
        port = 443
    
    print(Color.Y + f"[*] Target: {host}:{port}\n" + Color.N)
    
    result = {
        "target": host,
        "port": port,
        "certificate": None,
        "tls_versions": {},
        "cipher": None,
        "issues": [],
        "grade": "Unknown"
    }
    
    # Get certificate
    print(Color.Y + "[•] Fetching SSL certificate..." + Color.N)
    cert, error = get_certificate(host, port)
    
    if error:
        print(Color.R + f"[ERROR] {error}" + Color.N)
        result["error"] = error
        filename = save_log(target, "ssl_scan", result)
        print(Color.Y + f"\nSaved → {filename}\n" + Color.N)
        return
    
    if cert:
        result["certificate"] = cert
        cert_info = format_certificate_info(cert)
        
        print(Color.G + "[✓] Certificate retrieved successfully\n" + Color.N)
        
        # Display certificate info
        print(Color.C + "┌─ CERTIFICATE INFORMATION ────────────┐" + Color.N)
        print(f"  {Color.Y}Subject CN:{Color.N} {cert_info['subject']['commonName']}")
        print(f"  {Color.Y}Organization:{Color.N} {cert_info['subject']['organization']}")
        print(f"  {Color.Y}Issuer:{Color.N} {cert_info['issuer']['commonName']}")
        print(f"  {Color.Y}Valid From:{Color.N} {cert_info['validity']['notBefore']}")
        print(f"  {Color.Y}Valid Until:{Color.N} {cert_info['validity']['notAfter']}")
        
        days = cert_info['validity']['daysLeft']
        if isinstance(days, int):
            if days < 0:
                print(f"  {Color.Y}Days Left:{Color.N} {Color.R}EXPIRED ({abs(days)} days ago){Color.N}")
                result["issues"].append("Certificate expired")
            elif days < 30:
                print(f"  {Color.Y}Days Left:{Color.N} {Color.R}{days} days (expiring soon){Color.N}")
                result["issues"].append("Certificate expiring soon")
            else:
                print(f"  {Color.Y}Days Left:{Color.N} {Color.G}{days} days{Color.N}")
        
        if cert_info['subjectAltNames']:
            print(f"  {Color.Y}Alt Names:{Color.N} {len(cert_info['subjectAltNames'])} domains")
        
        print(Color.C + "└────────────────────────────────────┘" + Color.N)
    
    # Test TLS versions
    print(Color.C + "\n┌─ TLS VERSION SUPPORT ─────────────────┐" + Color.N)
    
    tls_results = check_all_tls_versions(host)
    result["tls_versions"] = tls_results
    
    weak_tls = []
    for version, data in tls_results.items():
        if data['supported']:
            if version in ["SSLv2", "SSLv3", "TLSv1.0", "TLSv1.1"]:
                print(f"  {Color.Y}{version}:{Color.N} {Color.R}SUPPORTED (WEAK){Color.N}")
                weak_tls.append(version)
            else:
                print(f"  {Color.Y}{version}:{Color.N} {Color.G}SUPPORTED{Color.N}")
        else:
            print(f"  {Color.Y}{version}:{Color.N} {Color.R}Not supported{Color.N}")
    
    if weak_tls:
        result["issues"].append(f"Weak TLS versions supported: {', '.join(weak_tls)}")
    
    print(Color.C + "└────────────────────────────────────┘" + Color.N)
    
    # Get cipher info
    if cert and 'cipher' in cert:
        cipher = cert['cipher']
        result["cipher"] = cipher
        
        print(Color.C + "\n┌─ CURRENT CIPHER ──────────────────────┐" + Color.N)
        print(f"  {Color.Y}Cipher:{Color.N} {cipher['name']}")
        print(f"  {Color.Y}Protocol:{Color.N} {cipher['protocol']}")
        print(f"  {Color.Y}Bits:{Color.N} {cipher['bits']}")
        
        # Analyze cipher strength
        analysis = analyze_cipher_strength(cipher['name'])
        if analysis['weak']:
            print(f"  {Color.R}WEAK: {', '.join(analysis['reasons'])}{Color.N}")
            result["issues"].append(f"Weak cipher: {cipher['name']}")
        else:
            print(f"  {Color.G}✓ Cipher strength appears adequate{Color.N}")
        
        print(Color.C + "└────────────────────────────────────┘" + Color.N)
    
    # Determine grade
    if result["issues"]:
        if any("expired" in i for i in result["issues"]):
            result["grade"] = "F"
        elif any("weak TLS" in i for i in result["issues"]):
            result["grade"] = "C"
        elif any("expiring" in i for i in result["issues"]):
            result["grade"] = "B"
        else:
            result["grade"] = "B-"
    else:
        result["grade"] = "A"
    
    print(Color.C + "\n┌─ SSL SCAN SUMMARY ────────────────────┐" + Color.N)
    grade_color = Color.G if result["grade"] in ["A", "B"] else Color.Y if result["grade"] in ["B-", "C"] else Color.R
    print(f"  {Color.Y}Grade:{Color.N} {grade_color}{result['grade']}{Color.N}")
    print(f"  {Color.Y}Issues:{Color.N} {Color.R if result['issues'] else Color.G}{len(result['issues'])}{Color.N}")
    print(Color.C + "└────────────────────────────────────┘" + Color.N)
    
    if result["issues"]:
        print(Color.R + "\n[!] SSL/TLS Issues Found:" + Color.N)
        for issue in result["issues"]:
            print(f"  {Color.R}• {issue}{Color.N}")
    
    # Save results
    filename = save_log(target, "ssl_scan", result)
    print(Color.Y + f"\nSaved → {filename}\n" + Color.N)