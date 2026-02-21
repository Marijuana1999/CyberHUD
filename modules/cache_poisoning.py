# modules/cache_poisoning.py
import requests
import hashlib
from core.core import Color, save_log, safe_request

class CachePoisoningChecker:
    def __init__(self, target):
        self.target = target
        self.headers_to_test = [
            'X-Forwarded-Host',
            'X-Forwarded-Scheme',
            'X-Original-URL',
            'X-Rewrite-URL',
            'X-HTTP-Method-Override',
            'X-Original-Method',
            'X-HTTP-Method',
            'X-Method-Override',
            'X-Forwarded-For',
            'X-Real-IP',
            'X-Originating-IP',
            'X-Remote-IP',
            'X-Remote-Addr',
            'X-Client-IP',
            'X-Host',
            'X-Forwarded-Server',
            'Forwarded'
        ]
    
    def test_header(self, url, header, value):
        """Test if header affects response"""
        headers = {header: value}
        
        # First request
        resp1, error1 = safe_request(url, headers=headers, timeout=5)
        if error1:
            return None
        
        # Second request without header (to check cache)
        resp2, error2 = safe_request(url, timeout=5)
        if error2:
            return None
        
        # Check if responses are different
        if resp1.text != resp2.text:
            return {
                'header': header,
                'value': value,
                'different': True,
                'first_status': resp1.status_code,
                'second_status': resp2.status_code
            }
        
        # Check cache headers
        cache_headers = ['x-cache', 'cf-cache-status', 'x-cache-status', 'age']
        for ch in cache_headers:
            if ch in resp1.headers or ch in resp2.headers:
                return {
                    'header': header,
                    'value': value,
                    'cache_detected': True,
                    'cache_headers': {
                        'first': dict(resp1.headers),
                        'second': dict(resp2.headers)
                    }
                }
        
        return None
    
    def run_tests(self, url):
        results = []
        
        for header in self.headers_to_test[:5]:  # Test first 5 to avoid太多
            for value in ['evil.com', '127.0.0.1', 'localhost', 'https://evil.com']:
                print(Color.Y + f"[*] Testing {header}: {value}" + Color.N)
                result = self.test_header(url, header, value)
                if result:
                    results.append(result)
                    print(Color.R + f"[!] Interesting: {header} affects response" + Color.N)
        
        return results

def run(target):
    print(Color.C + "\n[+] Cache Poisoning Vulnerability Checker" + Color.N)
    
    url = f"https://{target}"
    checker = CachePoisoningChecker(target)
    
    results = checker.run_tests(url)
    
    if results:
        print(Color.R + f"\n[!] Found {len(results)} potential cache poisoning issues" + Color.N)
        for r in results:
            print(Color.Y + f"  • {r['header']}: {r.get('value', '')}" + Color.N)
    else:
        print(Color.G + "\n[✓] No obvious cache poisoning issues found" + Color.N)
    
    save_log(target, "cache_poisoning", {'results': results})