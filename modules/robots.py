# modules/robots.py
import requests
from core.core import Color, save_log

def run(target):
    print(Color.C + "\n[+] Robots.txt & Sitemap Recon\n" + Color.N)

    base = f"http://{target}"
    result = {"robots": None, "disallow": [], "sitemap": None, "issues": []}

    # ---------------------------
    # robots.txt
    # ---------------------------
    try:
        r = requests.get(f"{base}/robots.txt", timeout=6)
        if r.status_code == 200:
            print(Color.G + "[OK] robots.txt found" + Color.N)
            result["robots"] = r.text

            for line in r.text.split("\n"):
                if line.lower().startswith("disallow"):
                    result["disallow"].append(line)
                    print(Color.R + f"[!] Hidden Path: {line}" + Color.N)
        else:
            print(Color.Y + "robots.txt not found." + Color.N)

    except:
        print(Color.R + "robots fetch error" + Color.N)

    # ---------------------------
    # sitemap.xml
    # ---------------------------
    try:
        s = requests.get(f"{base}/sitemap.xml", timeout=6)
        if s.status_code == 200:
            print(Color.G + "[OK] sitemap.xml found" + Color.N)
            result["sitemap"] = s.text
        else:
            print(Color.Y + "sitemap.xml not found." + Color.N)
    except:
        print(Color.R + "sitemap fetch error" + Color.N)

    filename = save_log(target, "robots", result)
    print(Color.Y + f"\nSaved → {filename}\n" + Color.N)
