# modules/security_headers.py
import requests
from core.core import Color, save_log


REQUIRED_HEADERS = {
    "Strict-Transport-Security": "Prevents MITM downgrade attacks",
    "Content-Security-Policy": "Prevents XSS & data injection",
    "X-Frame-Options": "Prevents clickjacking",
    "X-Content-Type-Options": "Prevents MIME sniffing",
    "Referrer-Policy": "Prevents info leakage",
    "Permissions-Policy": "Controls sensitive browser APIs",
    "Cross-Origin-Embedder-Policy": "Isolation security",
    "Cross-Origin-Opener-Policy": "Tab hijacking protection"
}


def run(target):
    print(Color.C + "\n[+] Security Headers Scanner\n" + Color.N)

    url = f"http://{target}"
    result = {"headers": {}, "missing": [], "issues": []}

    try:
        r = requests.get(url, timeout=6)
    except:
        print(Color.R + "Failed to connect." + Color.N)
        return

    headers = {k.lower(): v for k, v in r.headers.items()}
    result["headers"] = headers

    print(Color.Y + "[•] Analyzing security headers...\n" + Color.N)

    for header, description in REQUIRED_HEADERS.items():
        h = header.lower()
        if h in headers:
            print(Color.G + f"[OK] {header}: {headers[h]}" + Color.N)
        else:
            print(Color.R + f"[MISSING] {header} → {description}" + Color.N)
            result["missing"].append(header)
            result["issues"].append(f"{header} missing → {description}")

    filename = save_log(target, "security_headers", result)
    print(Color.Y + f"\nSaved → {filename}\n" + Color.N)
