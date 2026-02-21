# modules/cors_advanced.py
import requests
from core.core import Color, save_log, safe_request

class CORSAdvancedTester:
    def __init__(self, target):
        self.target = target
        self.test_origins = [
            'https://evil.com',
            'null',
            'https://attacker.com',
            'http://localhost',
            'http://127.0.0.1',
            'https://target.com.evil.com',
            'https://evil-target.com',
            'https://target.com@evil.com',
            'file://',
            'https://192.168.1.1',
            'https://10.0.0.1'
        ]
        
        self.test_methods = ['GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'OPTIONS']
    
    def test_origin(self, url, origin):
        """Test single origin"""
        headers = {'Origin': origin}
        resp, error = safe_request(url, headers=headers, timeout=5)
        
        if error or not resp:
            return None
        
        acao = resp.headers.get('Access-Control-Allow-Origin')
        acc = resp.headers.get('Access-Control-Allow-Credentials')
        
        return {
            'origin': origin,
            'acao': acao,
            'credentials': acc,
            'status': resp.status_code,
            'vulnerable': acao == origin or (acao == '*' and acc == 'true')
        }
    
    def test_preflight(self, url, origin, method):
        """Test preflight request"""
        headers = {
            'Origin': origin,
            'Access-Control-Request-Method': method,
            'Access-Control-Request-Headers': 'X-Custom-Header'
        }
        
        resp, error = safe_request(url, method='OPTIONS', headers=headers, timeout=5)
        
        if error or not resp:
            return None
        
        acam = resp.headers.get('Access-Control-Allow-Methods', '')
        acah = resp.headers.get('Access-Control-Allow-Headers', '')
        
        return {
            'origin': origin,
            'method': method,
            'allow_methods': acam,
            'allow_headers': acah,
            'status': resp.status_code,
            'vulnerable': method in acam if acam else False
        }
    
    def run_tests(self, url):
        results = {
            'origin_tests': [],
            'preflight_tests': [],
            'vulnerabilities': []
        }
        
        # Test origins
        for origin in self.test_origins:
            result = self.test_origin(url, origin)
            if result:
                results['origin_tests'].append(result)
                if result.get('vulnerable'):
                    results['vulnerabilities'].append({
                        'type': 'origin_reflection',
                        'origin': origin,
                        'acao': result['acao']
                    })
        
        # Test preflight for vulnerable origins
        for origin in ['https://evil.com', 'null']:
            for method in ['PUT', 'DELETE']:
                result = self.test_preflight(url, origin, method)
                if result and result.get('vulnerable'):
                    results['preflight_tests'].append(result)
                    results['vulnerabilities'].append({
                        'type': 'preflight_bypass',
                        'origin': origin,
                        'method': method
                    })
        
        return results

def run(target):
    print(Color.C + "\n[+] Advanced CORS Misconfiguration Tester" + Color.N)
    
    url = f"https://{target}"
    tester = CORSAdvancedTester(target)
    
    results = tester.run_tests(url)
    
    if results['vulnerabilities']:
        print(Color.R + f"\n[!] Found {len(results['vulnerabilities'])} CORS vulnerabilities!" + Color.N)
        for vuln in results['vulnerabilities']:
            if vuln['type'] == 'origin_reflection':
                print(Color.R + f"  • Origin reflection: {vuln['origin']} → {vuln['acao']}" + Color.N)
            else:
                print(Color.R + f"  • Preflight bypass: {vuln['origin']} with {vuln['method']}" + Color.N)
    else:
        print(Color.G + "\n[✓] No CORS vulnerabilities found" + Color.N)
    
    save_log(target, "cors_advanced", results)