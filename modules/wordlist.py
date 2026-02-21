# core/wordlist.py
import os
import requests

class WordlistManager:
    def __init__(self):
        self.wordlists_dir = "wordlists"
        os.makedirs(self.wordlists_dir, exist_ok=True)
        
        self.default_wordlists = {
            "directories": "https://raw.githubusercontent.com/danielmiessler/SecLists/master/Discovery/Web-Content/common.txt",
            "admin": "https://raw.githubusercontent.com/danielmiessler/SecLists/master/Discovery/Web-Content/admin-panels.txt",
            "backup": "https://raw.githubusercontent.com/danielmiessler/SecLists/master/Discovery/Web-Content/backup-files.txt",
            "params": "https://raw.githubusercontent.com/s0md3v/Arjun/master/arjun/db/params.txt"
        }
    
    def download_wordlist(self, name, url):
        filename = os.path.join(self.wordlists_dir, f"{name}.txt")
        
        if os.path.exists(filename):
            print(f"[✓] Wordlist {name} already exists")
            return filename
        
        print(f"[*] Downloading {name} wordlist...")
        try:
            response = requests.get(url, timeout=10)
            with open(filename, 'w') as f:
                f.write(response.text)
            print(f"[✓] Downloaded {name} wordlist ({len(response.text.splitlines())} entries)")
            return filename
        except Exception as e:
            print(f"[!] Failed to download {name}: {e}")
            return None
    
    def get_wordlist(self, name):
        filename = os.path.join(self.wordlists_dir, f"{name}.txt")
        if os.path.exists(filename):
            with open(filename, 'r') as f:
                return [line.strip() for line in f if line.strip()]
        return []
    
    def download_all(self):
        for name, url in self.default_wordlists.items():
            self.download_wordlist(name, url)