#!/usr/bin/env python3

# modules/ports.py
import socket
import sys
import platform
from core.core import Color, save_log

# Common ports for Web + Mail + DB + SSH
COMMON_PORTS = {
    21:  "FTP",
    22:  "SSH",
    23:  "Telnet",
    25:  "SMTP",
    53:  "DNS",
    80:  "HTTP",
    110: "POP3",
    143: "IMAP",
    443: "HTTPS",
    993: "IMAPS",
    995: "POP3S",
    3306: "MySQL",
    3389: "RDP",
    5432: "PostgreSQL",
    27017: "MongoDB",
    8080: "HTTP-Alt",
    8443: "HTTPS-Alt"
}

def port_status(code):
    """Convert socket error code to status"""
    if code == 0:
        return Color.G + "OPEN" + Color.N
    elif code == 111 or code == 10061:  # connection refused
        return Color.R + "CLOSED" + Color.N
    elif code == 110 or code == 10060:  # timeout
        return Color.Y + "TIMEOUT" + Color.N
    else:
        return Color.Y + "FILTERED" + Color.N

def can_connect(host, port, timeout=2):
    """Check if port is open (cross-platform)"""
    try:
        # Handle IPv6 addresses
        try:
            # Try IPv4 first
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        except:
            # Fallback to IPv6
            sock = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
        
        sock.settimeout(timeout)
        result = sock.connect_ex((host, port))
        sock.close()
        return result == 0
    except:
        return False

def run(target):
    """Main port scanner function"""
    print(Color.C + f"\n[+] Port Scanner – Safe Mode\n" + Color.N)
    
    # Check if target is valid
    if not target:
        print(Color.R + "[!] No target set" + Color.N)
        return
    
    result = {}
    open_ports = []
    
    print(Color.Y + f"Scanning {target} for common ports...\n" + Color.N)
    
    for port, name in COMMON_PORTS.items():
        try:
            # Create socket (IPv4/IPv6 agnostic)
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            except:
                s = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
            
            s.settimeout(1.5)
            
            try:
                code = s.connect_ex((target, port))
                state = port_status(code)
                
                # Store result without colors
                clean_state = state.replace(Color.G, "").replace(Color.R, "").replace(Color.Y, "").replace(Color.N, "")
                result[str(port)] = {
                    "service": name,
                    "state": clean_state
                }
                
                if code == 0:
                    open_ports.append(port)
                    print(f"{Color.B}{port:<6}{Color.N} ({name:<8}) → {Color.G}OPEN{Color.N}")
                elif code in [111, 10061]:
                    print(f"{Color.B}{port:<6}{Color.N} ({name:<8}) → {Color.R}CLOSED{Color.N}")
                else:
                    print(f"{Color.B}{port:<6}{Color.N} ({name:<8}) → {Color.Y}FILTERED/TIMEOUT{Color.N}")
            
            except socket.gaierror:
                print(f"{Color.R}[!] Invalid hostname{Color.N}")
                return
            except Exception as e:
                print(f"{Color.Y}{port:<6} ({name:<8}) → ERROR: {str(e)[:30]}{Color.N}")
                result[str(port)] = {
                    "service": name,
                    "error": str(e)
                }
            finally:
                s.close()
                
        except Exception as e:
            print(f"{Color.R}[!] Error on port {port}: {e}{Color.N}")
    
    # Summary
    if open_ports:
        print(f"\n{Color.G}[✓] Open ports: {', '.join(map(str, open_ports))}{Color.N}")
    else:
        print(f"\n{Color.Y}[!] No open ports found{Color.N}")
    
    # Save results
    filename = save_log(target, "ports", result)
    print(Color.Y + f"\nSaved → {filename}\n" + Color.N)