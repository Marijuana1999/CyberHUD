# modules/dns_enum.py
import dns.resolver
import dns.query
import dns.zone
from core.core import Color, save_log

def safe_query(domain, record_type):
    try:
        answers = dns.resolver.resolve(domain, record_type)
        return [str(r) for r in answers]
    except:
        return []


def run(target):
    print(Color.C + "\n[+] DNS Enumeration (Passive Mode)\n" + Color.N)

    result = {
        "A": [],
        "AAAA": [],
        "CNAME": [],
        "MX": [],
        "NS": [],
        "TXT": [],
        "SOA": [],
        "ZoneTransfer": {},
        "Issues": []
    }

    # ----------------------------------------
    # BASIC RECORDS
    # ----------------------------------------
    print(Color.Y + f"Resolving DNS records for: {target}\n" + Color.N)

    for rtype in ["A", "AAAA", "CNAME", "MX", "NS", "TXT", "SOA"]:
        data = safe_query(target, rtype)
        result[rtype] = data

        if data:
            print(Color.G + f"[{rtype}] {data}" + Color.N)
        else:
            print(Color.R + f"[{rtype}] No Record Found" + Color.N)

    # ----------------------------------------
    # ANALYZE TXT (SPF / DKIM / DMARC)
    # ----------------------------------------
    txt_records = result["TXT"]

    spf = [t for t in txt_records if "v=spf1" in t]
    dmarc = safe_query(f"_dmarc.{target}", "TXT")
    dkim = safe_query(f"default._domainkey.{target}", "TXT")

    if spf:
        print(Color.G + "\n[SPF] OK → " + spf[0] + Color.N)
        result["SPF"] = spf[0]
    else:
        print(Color.R + "\n[SPF] Missing" + Color.N)
        result["Issues"].append("SPF Missing")

    if dmarc:
        print(Color.G + "[DMARC] OK → " + dmarc[0] + Color.N)
        result["DMARC"] = dmarc[0]
    else:
        print(Color.R + "[DMARC] Missing" + Color.N)
        result["Issues"].append("DMARC Missing")

    if dkim:
        print(Color.G + "[DKIM] OK" + Color.N)
        result["DKIM"] = dkim
    else:
        print(Color.R + "[DKIM] Missing" + Color.N)
        result["Issues"].append("DKIM Missing")

    # ----------------------------------------
    # ZONE TRANSFER TEST (Legal Passive Attempt)
    # ----------------------------------------
    print(Color.C + "\n[+] Testing Zone Transfer (AXFR)\n" + Color.N)

    ns_servers = result["NS"]

    for ns in ns_servers:
        ns_clean = ns.split()[-1]
        print(Color.Y + f"Trying AXFR → {ns_clean} ..." + Color.N)

        try:
            zone = dns.zone.from_xfr(dns.query.xfr(ns_clean, target, timeout=4))
            names = zone.nodes.keys()
            print(Color.R + f"[VULNERABLE] ZONE TRANSFER ENABLED on {ns_clean}" + Color.N)

            result["ZoneTransfer"][ns_clean] = [str(n) for n in names]
            result["Issues"].append("Zone Transfer Vulnerability")

        except Exception:
            print(Color.G + f"[SECURE] AXFR blocked on {ns_clean}" + Color.N)
            result["ZoneTransfer"][ns_clean] = "Blocked"

    # ----------------------------------------
    # SAVE LOG
    # ----------------------------------------
    filename = save_log(target, "dns_enum", result)
    print(Color.Y + f"\nSaved → {filename}\n" + Color.N)
