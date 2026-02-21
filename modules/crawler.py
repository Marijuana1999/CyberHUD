#!/usr/bin/env python3

# modules/crawler.py
import re
import json
import time
from urllib.parse import urljoin, urlparse, parse_qs
from collections import deque
from bs4 import BeautifulSoup
from core.core import Color, save_log, safe_request

# ============================================================
# CONFIGURATION
# ============================================================

HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; CyberSec-Crawler/4.0; +https://github.com/cybersec/framework)",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
    "Accept-Encoding": "gzip, deflate",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1"
}

# Maximum pages to crawl
MAX_PAGES = 100
MAX_DEPTH = 3
REQUEST_DELAY = 0.5  # Delay between requests to be polite

# ============================================================
# RISK ANALYSIS PATTERNS
# ============================================================

SENSITIVE_PARAMS = {
    # Parameter patterns and their risks
    'id': 'IDOR / SQL Injection',
    'uid': 'IDOR / SQL Injection',
    'user_id': 'IDOR / SQL Injection',
    'account': 'IDOR / SQL Injection',
    'order': 'IDOR / SQL Injection',
    'pid': 'IDOR / SQL Injection',
    
    'file': 'LFI/RFI',
    'path': 'LFI/RFI',
    'dir': 'LFI/RFI',
    'page': 'LFI/RFI',
    'document': 'LFI/RFI',
    
    'redirect': 'Open Redirect',
    'url': 'Open Redirect',
    'next': 'Open Redirect',
    'goto': 'Open Redirect',
    'return': 'Open Redirect',
    'dest': 'Open Redirect',
    
    'token': 'Token Leakage',
    'auth': 'Auth Leakage',
    'key': 'API Key Leakage',
    'apikey': 'API Key Leakage',
    'secret': 'Secret Leakage',
    
    'q': 'XSS / SQL Injection',
    'query': 'XSS / SQL Injection',
    'search': 'XSS / SQL Injection',
    
    'debug': 'Debug Mode',
    'test': 'Test Mode',
    'dev': 'Development Mode',
    
    'password': 'Password Exposure',
    'pass': 'Password Exposure',
    'pwd': 'Password Exposure',
    
    'email': 'Email Exposure',
    'phone': 'Phone Exposure',
    
    'callback': 'JSONP / XSS',
    'jsonp': 'JSONP / XSS'
}

SENSITIVE_PATHS = {
    # Path patterns and their risk levels
    'admin': 'HIGH',
    'administrator': 'HIGH',
    'login': 'MEDIUM',
    'signin': 'MEDIUM',
    'register': 'LOW',
    'signup': 'LOW',
    
    'api': 'HIGH',
    'rest': 'HIGH',
    'graphql': 'CRITICAL',
    'v1': 'MEDIUM',
    'v2': 'MEDIUM',
    
    'backup': 'CRITICAL',
    'backups': 'CRITICAL',
    'dump': 'CRITICAL',
    'sql': 'CRITICAL',
    'db': 'CRITICAL',
    
    'config': 'CRITICAL',
    'configuration': 'CRITICAL',
    'settings': 'HIGH',
    '.env': 'CRITICAL',
    '.git': 'CRITICAL',
    
    'phpmyadmin': 'CRITICAL',
    'adminer': 'CRITICAL',
    'mysql': 'HIGH',
    
    'debug': 'HIGH',
    'test': 'MEDIUM',
    'dev': 'MEDIUM',
    'staging': 'MEDIUM'
}

# ============================================================
# CRAWLER CLASS
# ============================================================

class SmartCrawler:
    def __init__(self, target, max_pages=MAX_PAGES, max_depth=MAX_DEPTH):
        self.target = target
        self.base_url = self.normalize_url(target)
        self.base_domain = urlparse(self.base_url).netloc
        self.max_pages = max_pages
        self.max_depth = max_depth
        
        # Data structures
        self.visited = set()
        self.to_visit = deque()
        self.depth_map = {}
        
        # Results
        self.results = {
            "target": target,
            "base_url": self.base_url,
            "pages_crawled": 0,
            "internal_links": [],
            "external_links": [],
            "forms": [],
            "parameters": {},
            "sensitive_params": [],
            "sensitive_paths": [],
            "js_files": [],
            "api_endpoints": [],
            "interesting_files": [],
            "emails": [],
            "comments": [],
            "findings": {
                "CRITICAL": [],
                "HIGH": [],
                "MEDIUM": [],
                "LOW": []
            }
        }
    
    def normalize_url(self, target):
        """Normalize target URL"""
        if not target.startswith(('http://', 'https://')):
            # Try HTTPS first, then HTTP
            for proto in ['https://', 'http://']:
                url = proto + target
                resp, error = safe_request(url, timeout=5, headers=HEADERS)
                if not error and resp and resp.status_code < 500:
                    return url
            return 'https://' + target
        return target
    
    def is_same_domain(self, url):
        """Check if URL is from same domain"""
        try:
            domain = urlparse(url).netloc
            return domain == self.base_domain or domain.endswith('.' + self.base_domain)
        except:
            return False
    
    def clean_url(self, url):
        """Clean and normalize URL"""
        try:
            parsed = urlparse(url)
            # Remove fragments
            parsed = parsed._replace(fragment='')
            # Normalize path
            path = parsed.path.rstrip('/')
            if not path:
                path = '/'
            parsed = parsed._replace(path=path)
            return parsed.geturl()
        except:
            return url
    
    def extract_links(self, soup, current_url):
        """Extract all links from page"""
        links = []
        
        for link in soup.find_all('a', href=True):
            href = link['href'].strip()
            if not href or href.startswith('#') or href.startswith('javascript:'):
                continue
            
            try:
                full_url = urljoin(current_url, href)
                full_url = self.clean_url(full_url)
                
                if self.is_same_domain(full_url):
                    links.append(full_url)
                    
                    if full_url not in self.results["internal_links"]:
                        self.results["internal_links"].append(full_url)
                else:
                    if full_url not in self.results["external_links"]:
                        self.results["external_links"].append(full_url)
            
            except Exception:
                continue
        
        return links
    
    def extract_forms(self, soup, current_url):
        """Extract and analyze forms"""
        forms = []
        
        for form in soup.find_all('form'):
            action = form.get('action', '')
            method = form.get('method', 'GET').upper()
            
            if action:
                action_url = urljoin(current_url, action)
            else:
                action_url = current_url
            
            form_data = {
                "page": current_url,
                "action": action_url,
                "method": method,
                "inputs": [],
                "risk": "LOW"
            }
            
            # Extract inputs
            for inp in form.find_all(['input', 'textarea', 'select']):
                inp_name = inp.get('name')
                inp_type = inp.get('type', 'text')
                inp_value = inp.get('value', '')
                
                if inp_name:
                    input_info = {
                        "name": inp_name,
                        "type": inp_type,
                        "value": inp_value[:50] if inp_value else ''
                    }
                    
                    # Check for sensitive inputs
                    if inp_type in ['password', 'file']:
                        form_data["risk"] = "HIGH"
                        self.add_finding("HIGH", f"Form with {inp_type} input at {current_url}")
                    
                    if inp_name.lower() in ['cc', 'creditcard', 'card']:
                        form_data["risk"] = "CRITICAL"
                        self.add_finding("CRITICAL", f"Payment form at {current_url}")
                    
                    form_data["inputs"].append(input_info)
            
            if form_data["inputs"]:
                forms.append(form_data)
                self.results["forms"].append(form_data)
        
        return forms
    
    def extract_js_files(self, soup, current_url):
        """Extract JavaScript files"""
        js_files = []
        
        for script in soup.find_all('script', src=True):
            src = script['src']
            if src:
                full_url = urljoin(current_url, src)
                if full_url not in self.results["js_files"]:
                    self.results["js_files"].append(full_url)
                    js_files.append(full_url)
                    
                    # Check for minified JS (potential secrets)
                    if '.min.js' in src:
                        self.add_finding("MEDIUM", f"Minified JS file (may contain secrets): {src}")
        
        return js_files
    
    def extract_parameters(self, url):
        """Extract URL parameters and analyze risks"""
        parsed = urlparse(url)
        params = parse_qs(parsed.query)
        
        for param, values in params.items():
            param_lower = param.lower()
            
            if param not in self.results["parameters"]:
                self.results["parameters"][param] = {
                    "values": values,
                    "pages": [url]
                }
                
                # Check for sensitive parameters
                for pattern, risk in SENSITIVE_PARAMS.items():
                    if pattern in param_lower:
                        finding = f"Sensitive parameter '{param}' found: {risk}"
                        if risk in ['CRITICAL', 'IDOR', 'LFI']:
                            self.add_finding("CRITICAL", finding)
                        elif risk in ['HIGH', 'XSS', 'Open Redirect']:
                            self.add_finding("HIGH", finding)
                        else:
                            self.add_finding("MEDIUM", finding)
                        
                        self.results["sensitive_params"].append({
                            "parameter": param,
                            "risk": risk,
                            "url": url
                        })
                        break
            else:
                if url not in self.results["parameters"][param]["pages"]:
                    self.results["parameters"][param]["pages"].append(url)
    
    def extract_emails(self, text):
        """Extract email addresses"""
        email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
        emails = re.findall(email_pattern, text)
        
        for email in emails:
            if email not in self.results["emails"]:
                self.results["emails"].append(email)
                
                # Check for potential disclosure
                if any(domain in email for domain in ['gmail', 'yahoo', 'hotmail']):
                    self.add_finding("LOW", f"Personal email disclosed: {email}")
                else:
                    self.add_finding("MEDIUM", f"Corporate email disclosed: {email}")
    
    def extract_comments(self, soup):
        """Extract HTML comments"""
        comments = soup.find_all(string=lambda text: isinstance(text, str) and '<!--' in text)
        
        for comment in comments:
            comment_text = comment.strip()
            if comment_text and len(comment_text) > 10:
                if comment_text not in self.results["comments"]:
                    self.results["comments"].append(comment_text[:200])
                    
                    # Check for sensitive info in comments
                    if any(word in comment_text.lower() for word in ['todo', 'fixme', 'hack', 'bug', 'secret', 'password']):
                        self.add_finding("HIGH", f"Sensitive comment: {comment_text[:100]}")
    
    def check_sensitive_path(self, url):
        """Check if URL path contains sensitive patterns"""
        path = urlparse(url).path.lower()
        
        for pattern, risk in SENSITIVE_PATHS.items():
            if pattern in path:
                if pattern not in [p['pattern'] for p in self.results["sensitive_paths"]]:
                    self.results["sensitive_paths"].append({
                        "pattern": pattern,
                        "risk": risk,
                        "url": url
                    })
                    
                    finding = f"Sensitive path found: {pattern} at {url}"
                    self.add_finding(risk, finding)
                return True
        
        return False
    
    def detect_api_endpoint(self, url):
        """Detect potential API endpoints"""
        path = urlparse(url).path.lower()
        
        api_patterns = ['/api/', '/v1/', '/v2/', '/v3/', '/rest/', '/graphql', '/swagger']
        
        for pattern in api_patterns:
            if pattern in path:
                if url not in self.results["api_endpoints"]:
                    self.results["api_endpoints"].append(url)
                    
                    if 'graphql' in pattern:
                        self.add_finding("CRITICAL", f"GraphQL endpoint found: {url}")
                    else:
                        self.add_finding("HIGH", f"API endpoint found: {url}")
                return True
        
        return False
    
    def check_interesting_files(self, url):
        """Check for interesting files"""
        interesting_extensions = [
            '.sql', '.bak', '.backup', '.old', '.txt', '.pdf', '.doc', '.xls',
            '.git', '.svn', '.env', '.config', '.json', '.xml', '.yaml', '.yml',
            '.tar', '.gz', '.zip', '.rar', '.7z', '.log'
        ]
        
        path = urlparse(url).path.lower()
        
        for ext in interesting_extensions:
            if path.endswith(ext):
                if url not in self.results["interesting_files"]:
                    self.results["interesting_files"].append(url)
                    
                    if ext in ['.sql', '.git', '.env']:
                        self.add_finding("CRITICAL", f"Critical file found: {url}")
                    elif ext in ['.bak', '.backup', '.old', '.zip', '.tar']:
                        self.add_finding("HIGH", f"Backup file found: {url}")
                    else:
                        self.add_finding("MEDIUM", f"Interesting file found: {url}")
                return True
        
        return False
    
    def add_finding(self, severity, message):
        """Add a finding with severity level"""
        if message not in self.results["findings"][severity]:
            self.results["findings"][severity].append(message)
    
    def crawl_page(self, url, depth):
        """Crawl a single page"""
        if url in self.visited or depth > self.max_depth:
            return []
        
        print(Color.C + f"[CRAWL] {url} (depth: {depth})" + Color.N)
        
        # Respect robots.txt (simplified)
        time.sleep(REQUEST_DELAY)
        
        # Fetch page
        resp, error = safe_request(url, headers=HEADERS, timeout=8)
        
        if error or not resp or resp.status_code >= 400:
            print(Color.R + f"  [!] Failed: {error or resp.status_code}" + Color.N)
            return []
        
        self.visited.add(url)
        self.results["pages_crawled"] += 1
        
        # Parse HTML
        try:
            soup = BeautifulSoup(resp.text, 'html.parser')
        except:
            print(Color.R + "  [!] Failed to parse HTML" + Color.N)
            return []
        
        # Check for sensitive paths
        self.check_sensitive_path(url)
        
        # Check for API endpoints
        self.detect_api_endpoint(url)
        
        # Check for interesting files
        self.check_interesting_files(url)
        
        # Extract parameters
        self.extract_parameters(url)
        
        # Extract emails
        self.extract_emails(resp.text)
        
        # Extract comments
        self.extract_comments(soup)
        
        # Extract forms
        forms = self.extract_forms(soup, url)
        if forms:
            print(Color.Y + f"  [i] Found {len(forms)} form(s)" + Color.N)
        
        # Extract JS files
        js_files = self.extract_js_files(soup, url)
        if js_files:
            print(Color.Y + f"  [i] Found {len(js_files)} JS file(s)" + Color.N)
        
        # Extract and return links
        links = self.extract_links(soup, url)
        print(Color.G + f"  [✓] Found {len(links)} internal link(s)" + Color.N)
        
        return links
    
    def run(self):
        """Main crawling function"""
        print(Color.Y + f"\n[*] Starting crawl of {self.base_url}" + Color.N)
        print(Color.Y + f"[*] Max pages: {self.max_pages}, Max depth: {self.max_depth}\n" + Color.N)
        
        # Start with base URL
        self.to_visit.append((self.base_url, 0))
        
        while self.to_visit and len(self.visited) < self.max_pages:
            url, depth = self.to_visit.popleft()
            
            if url in self.visited:
                continue
            
            # Crawl page
            new_links = self.crawl_page(url, depth)
            
            # Add new links to queue
            for link in new_links:
                if link not in self.visited and link not in [u for u, _ in self.to_visit]:
                    self.to_visit.append((link, depth + 1))
        
        # Final summary
        print(Color.C + "\n┌─ CRAWLER SUMMARY ─────────────────────┐" + Color.N)
        print(f"  {Color.Y}Pages Crawled:{Color.N} {self.results['pages_crawled']}")
        print(f"  {Color.Y}Internal Links:{Color.N} {len(self.results['internal_links'])}")
        print(f"  {Color.Y}External Links:{Color.N} {len(self.results['external_links'])}")
        print(f"  {Color.Y}Forms Found:{Color.N} {len(self.results['forms'])}")
        print(f"  {Color.Y}Parameters:{Color.N} {len(self.results['parameters'])}")
        print(f"  {Color.Y}JS Files:{Color.N} {len(self.results['js_files'])}")
        print(f"  {Color.Y}API Endpoints:{Color.N} {len(self.results['api_endpoints'])}")
        print(f"  {Color.Y}Emails Found:{Color.N} {len(self.results['emails'])}")
        print(f"  {Color.Y}Interesting Files:{Color.N} {len(self.results['interesting_files'])}")
        print(Color.C + "└────────────────────────────────────┘" + Color.N)
        
        # Findings by severity
        print(Color.C + "\n┌─ FINDINGS BY SEVERITY ────────────────┐" + Color.N)
        
        for severity in ['CRITICAL', 'HIGH', 'MEDIUM', 'LOW']:
            count = len(self.results['findings'][severity])
            if count > 0:
                color = Color.R if severity in ['CRITICAL', 'HIGH'] else Color.Y
                print(f"  {color}{severity}: {count}{Color.N}")
        
        print(Color.C + "└────────────────────────────────────┘" + Color.N)
        
        # Show critical findings
        if self.results['findings']['CRITICAL']:
            print(Color.R + "\n[!] CRITICAL FINDINGS:" + Color.N)
            for finding in self.results['findings']['CRITICAL'][:10]:
                print(f"  {Color.R}• {finding}{Color.N}")
        
        # Show high findings
        if self.results['findings']['HIGH']:
            print(Color.Y + "\n[!] HIGH FINDINGS:" + Color.N)
            for finding in self.results['findings']['HIGH'][:10]:
                print(f"  {Color.Y}• {finding}{Color.N}")
        
        return self.results

# ============================================================
# MAIN FUNCTION
# ============================================================

def run(target):
    """Main crawler function"""
    print(Color.C + "\n[+] Web Crawler — Smart Hybrid Mode\n" + Color.N)
    
    if not target:
        print(Color.R + "[!] No target set" + Color.N)
        return
    
    # Ask for crawl options
    print("Crawl options:")
    print("1) Quick scan (50 pages, depth 2)")
    print("2) Deep scan (100 pages, depth 3)")
    print("3) Custom")
    
    choice = input(Color.Y + "\nSelect (1/2/3): " + Color.N).strip()
    
    if choice == '1':
        max_pages = 50
        max_depth = 2
    elif choice == '2':
        max_pages = 100
        max_depth = 3
    else:
        try:
            max_pages = int(input("Max pages (default 100): ").strip() or "100")
            max_depth = int(input("Max depth (default 3): ").strip() or "3")
        except:
            max_pages = 100
            max_depth = 3
    
    # Create and run crawler
    crawler = SmartCrawler(target, max_pages=max_pages, max_depth=max_depth)
    results = crawler.run()
    
    # Save results
    filename = save_log(target, "crawler", results)
    print(Color.Y + f"\nSaved → {filename}\n" + Color.N)