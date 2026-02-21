# modules/subdomain_takeover.py
import dns.resolver
import requests
from core.core import Color, save_log, safe_request

class SubdomainTakeoverChecker:
    def __init__(self, domain):
        self.domain = domain
        self.fingerprints = [
            # AWS
            {'service': 'AWS S3', 'cname': ['s3.amazonaws.com'], 'fingerprint': 'NoSuchBucket'},
            {'service': 'AWS CloudFront', 'cname': ['cloudfront.net'], 'fingerprint': 'BadRequest'},
            
            # GitHub
            {'service': 'GitHub Pages', 'cname': ['github.io'], 'fingerprint': 'There isn\'t a GitHub Pages site here'},
            
            # Heroku
            {'service': 'Heroku', 'cname': ['herokuapp.com'], 'fingerprint': 'No such app'},
            
            # Shopify
            {'service': 'Shopify', 'cname': ['myshopify.com'], 'fingerprint': 'Sorry, this shop is currently unavailable'},
            
            # Tumblr
            {'service': 'Tumblr', 'cname': ['tumblr.com'], 'fingerprint': 'Whatever you were looking for doesn\'t currently exist'},
            
            # WordPress
            {'service': 'WordPress', 'cname': ['wordpress.com'], 'fingerprint': 'Do you want to register'},
            
            # Google
            {'service': 'Google Cloud', 'cname': ['cloud.goog'], 'fingerprint': '404 Not Found'},
            
            # Azure
            {'service': 'Azure', 'cname': ['azurewebsites.net', 'cloudapp.net'], 'fingerprint': '404 Not Found'},
            
            # Fastly
            {'service': 'Fastly', 'cname': ['fastly.net'], 'fingerprint': 'Fastly error: unknown domain'},
            
            # Bitbucket
            {'service': 'Bitbucket', 'cname': ['bitbucket.io'], 'fingerprint': 'The page you have requested does not exist'},
            
            # Readme.io
            {'service': 'Readme.io', 'cname': ['readme.io'], 'fingerprint': 'Project doesnt exist... yet!'}
        ]
    
    def get_cname(self, subdomain):
        """Get CNAME record"""
        try:
            answers = dns.resolver.resolve(subdomain, 'CNAME')
            return [str(r) for r in answers]
        except:
            return []
    
    def check_takeover(self, subdomain):
        """Check if subdomain is vulnerable to takeover"""
        cnames = self.get_cname(subdomain)
        
        if not cnames:
            return None
        
        for cname in cnames:
            for fp in self.fingerprints:
                for pattern in fp['cname']:
                    if pattern in cname:
                        # Try to fetch the page
                        for protocol in ['https://', 'http://']:
                            url = f"{protocol}{subdomain}"
                            resp, error = safe_request(url, timeout=5)
                            
                            if not error and resp:
                                if fp['fingerprint'].lower() in resp.text.lower():
                                    return {
                                        'subdomain': subdomain,
                                        'cname': cname,
                                        'service': fp['service'],
                                        'url': url,
                                        'status': resp.status_code
                                    }
        return None

def run(target):
    print(Color.C + "\n[+] Subdomain Takeover Checker" + Color.N)
    
    # اینجا باید لیست subdomainها رو از فایل بخونی
    # برای نمونه:
    subdomains = ['test', 'dev', 'staging', 'blog', 'shop']
    
    checker = SubdomainTakeoverChecker(target)
    results = {'vulnerable': [], 'checked': []}
    
    for sub in subdomains:
        subdomain = f"{sub}.{target}"
        print(Color.Y + f"[*] Checking {subdomain}..." + Color.N)
        
        result = checker.check_takeover(subdomain)
        if result:
            print(Color.R + f"[!] VULNERABLE: {subdomain} → {result['service']}" + Color.N)
            results['vulnerable'].append(result)
        
        results['checked'].append(subdomain)
    
    if results['vulnerable']:
        print(Color.R + f"\n[!] Found {len(results['vulnerable'])} vulnerable subdomains!" + Color.N)
    
    save_log(target, "subdomain_takeover", results)