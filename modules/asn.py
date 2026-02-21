# modules/asn.py
import socket
import requests
from core.core import Color, save_log


def is_private_ip(ip):
    parts = ip.split(".")
    p1 = int(parts[0])
    p2 = int(parts[1])

    if p1 == 10:
        return True
    if p1 == 172 and 16 <= p2 <= 31:
        return True
    if p1 == 192 and p2 == 168:
        return True
    return False


def run(target):
    print(Color.C + "\n[+] ASN & WHOIS Enumeration\n" + Color.N)
    result = {}

    try:
        # ---------------------------------------
        # Check if target is IP or domain
        # ---------------------------------------
        try:
            socket.inet_aton(target)
            ip = target
        except:
            ip = socket.gethostbyname(target)

        print(Color.G + f"Using IP: {ip}\n" + Color.N)
        result["ip"] = ip

        # ---------------------------------------
        # Reject private IP
        # ---------------------------------------
        if is_private_ip(ip):
            print(Color.R + "Private IP detected — No ASN or Location exists for private networks." + Color.N)
            return

        # ---------------------------------------
        # Get info from ipinfo.io
        # ---------------------------------------
        url = f"https://ipinfo.io/{ip}/json"
        r = requests.get(url, timeout=5)

        if r.status_code != 200:
            print(Color.R + "Failed to fetch IP info." + Color.N)
            return

        data = r.json()
        result["info"] = data

        org = data.get("org", "Unknown")
        city = data.get("city", "Unknown")
        region = data.get("region", "Unknown")
        country = data.get("country", "Unknown")
        loc = data.get("loc", "Unknown")
        asn = org.split()[0] if org != "Unknown" else "Unknown"

        print(Color.Y + "Organization: " + Color.G + org + Color.N)
        print(Color.Y + "ASN:          " + Color.G + asn + Color.N)
        print(Color.Y + "City:         " + Color.G + city + Color.N)
        print(Color.Y + "Region:       " + Color.G + region + Color.N)
        print(Color.Y + "Country:      " + Color.G + country + Color.N)
        print(Color.Y + "Location:     " + Color.G + loc + Color.N)
        print()

        cloud = "Unknown"
        org_l = org.lower()

        if "cloudflare" in org_l: cloud = "Cloudflare"
        elif "google" in org_l: cloud = "Google Cloud"
        elif "amazon" in org_l or "aws" in org_l: cloud = "Amazon AWS"
        elif "microsoft" in org_l or "azure" in org_l: cloud = "Microsoft Azure"
        elif "ovh" in org_l: cloud = "OVH"
        elif "digitalocean" in org_l: cloud = "DigitalOcean"
        elif "hetzner" in org_l: cloud = "Hetzner"

        result["cloud"] = cloud
        print(Color.C + "Cloud Provider: " + Color.G + cloud + Color.N)

        filename = save_log(target, "asn", result)
        print(Color.Y + f"\nSaved → {filename}\n" + Color.N)

    except Exception as e:
        print(Color.R + f"Error: {str(e)}" + Color.N)
        result["error"] = str(e)
        save_log(target, "asn", result)
