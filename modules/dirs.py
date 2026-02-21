#!/usr/bin/env python3

# modules/dirs.py -  Multiprocessing
import os
import time
import random
from concurrent.futures import ThreadPoolExecutor, as_completed
from urllib.parse import urlparse
from core.core import Color, save_log, safe_request

# ============================================================
# CONFIGURATION
# ============================================================

# 
COMMON_DIRS = [
    # Admin panels
    "admin", "administrator", "adm", "admincp", "adminpanel",
    "cpanel", "cp", "controlpanel", "panel", "manager",
    "dashboard", "portal", "user", "users", "member", "members",
    "login", "signin", "auth", "authenticate",
    
    # Backend directories
    "api", "api/v1", "api/v2", "api/v3", "rest", "rest-api",
    "graphql", "graphiql", "swagger", "docs", "documentation",
    "phpmyadmin", "phpPgAdmin", "adminer", "mysql", "pma",
    "db", "database", "mongodb", "redis",
    
    # Configuration
    "config", "configuration", "conf", "cfg", "settings",
    ".git", ".svn", ".env", ".aws", ".azure", ".gcp",
    "backup", "backups", "old", "archive", "temp", "tmp",
    "logs", "log", "debug", "error_log", "access_log",
    
    # Development
    "dev", "development", "test", "testing", "stage", "staging",
    "demo", "sandbox", "playground", "beta", "alpha",
    
    # Uploads
    "upload", "uploads", "files", "media", "static", "assets",
    "images", "img", "css", "js", "javascript", "styles",
    
    # Common web directories
    "wp-admin", "wp-content", "wp-includes", "wp-json",
    "wordpress", "joomla", "drupal", "magento", "laravel",
    "vendor", "node_modules", "bower_components",
    
    # Sensitive
    "private", "secret", "hidden", "internal", "secure",
    "download", "downloads", "ftp", "sftp", "ssh",
    "server-status", "server-info", "info", "phpinfo",
    "webmail", "mail", "email", "roundcube", "squirrelmail",
    
    # API endpoints
    "api/user", "api/users", "api/admin", "api/auth",
    "api/login", "api/logout", "api/register", "api/signup",
    "api/upload", "api/download", "api/file", "api/files",
    
    # Common files
    "robots.txt", "sitemap.xml", "sitemap", "crossdomain.xml",
    "clientaccesspolicy.xml", ".well-known", "humans.txt",
    "security.txt", "keybase.txt", "apple-app-site-association",
    "assetlinks.json", ".well-known/security.txt",
    
    # Additional directories
    "cgi-bin", "cgi", "scripts", "cgi-sys",
    "error", "errors", "error_docs",
    "icons", "images", "img", "css", "js", "fonts",
    "tmp", "temp", "cache", "sessions",
    "doc", "documentation", "docs", "help",
    "examples", "demo", "sample", "samples",
    "install", "setup", "configure", "config",
    "license", "readme", "README", "CHANGELOG",
    "src", "source", "sources", "lib", "libs", "include",
    "inc", "includes", "classes", "class", "functions",
    "models", "views", "controllers", "templates", "themes",
    "uploads", "uploaded", "files", "download", "downloads",
    "data", "database", "db", "sql", "mysql", "postgres",
    "xml", "json", "rss", "feed", "feeds",
    "proxy", "proxy.php", "curl", "curl.php",
    "shell", "shell.php", "cmd", "cmd.php", "exec", "exec.php",
    "phpinfo", "phpinfo.php", "info.php", "test.php",
    "phpmyadmin", "pma", "adminer", "mysql-admin",
    "webmail", "mail", "email", "roundcube", "squirrelmail",
    "phpPgAdmin", "pgadmin", "postgresql-admin",
    "redis", "redis-admin", "redis-commander",
    "mongodb", "mongo-express", "rockmongo",
    "elasticsearch", "elastic", "kibana",
    "jenkins", "jenkins-ci", "hudson",
    "sonar", "sonarqube", "sonar-scanner",
    "gitlab", "gitlab-ci", "github",
    "travis", "travis-ci", "circleci",
    "docker", "dockerfile", "docker-compose",
    "kubernetes", "k8s", "helm",
    "aws", "amazon", "azure", "google-cloud",
    "firebase", "firebase.json", "firebaserc",
    "heroku", "heroku.yml", "Procfile",
    "netlify", "netlify.toml", "_redirects",
    "vercel", "vercel.json", "now.json",
]

EXTENSIONS = ['', '/', '.html', '.php', '.asp', '.aspx', '.jsp', '.do', '.action', '.cgi']

# ============================================================
# USER AGENT ROTATION ()
# ============================================================

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/121.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/119.0.0.0 Safari/537.36",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_1 like Mac OS X) AppleWebKit/605.1.15",
    "Mozilla/5.0 (iPad; CPU OS 17_1 like Mac OS X) AppleWebKit/605.1.15",
    "Mozilla/5.0 (Android 13; Mobile; rv:109.0) Gecko/121.0 Firefox/121.0",
    "Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)",
    "Mozilla/5.0 (compatible; Bingbot/2.0; +http://www.bing.com/bingbot.htm)",
    "Mozilla/5.0 (compatible; Baiduspider/2.0; +http://www.baidu.com/search/spider.html)",
]

# ============================================================
# RATE LIMITING CONFIG
# ============================================================

class RateLimiter:
    def __init__(self, max_requests_per_second=10):
        self.max_requests = max_requests_per_second
        self.requests = []
    
    def wait_if_needed(self):
        """Wait if we're sending too many requests"""
        now = time.time()
        # Remove requests older than 1 second
        self.requests = [r for r in self.requests if r > now - 1]
        
        if len(self.requests) >= self.max_requests:
            sleep_time = 1 - (now - self.requests[0])
            if sleep_time > 0:
                time.sleep(sleep_time)
        
        self.requests.append(now)

# ============================================================
# DIRECTORY SCANNER CLASS
# ============================================================

class FastDirectoryScanner:
    def __init__(self, target, threads=30, delay=0.1):
        self.target = target
        self.base_urls = [f"https://{target}", f"http://{target}"]
        self.threads = threads
        self.delay = delay
        self.base_used = None
        self.rate_limiter = RateLimiter(max_requests_per_second=threads)
        
        self.results = {
            "target": target,
            "url_used": None,
            "directories": {},
            "found": [],
            "not_found": [],
            "errors": [],
            "stats": {
                "total_tests": 0,
                "found_count": 0,
                "speed": 0,
                "time_elapsed": 0
            }
        }
        
        # Generate all URLs to test
        self.urls_to_test = []
    
    def find_working_base(self):
        """Find a working base URL"""
        for base in self.base_urls:
            headers = {"User-Agent": random.choice(USER_AGENTS)}
            resp, error = safe_request(base, headers=headers, timeout=5)
            if not error and resp and resp.status_code < 500:
                self.base_used = base
                self.results["url_used"] = base
                print(Color.G + f"[✓] Using base: {base}" + Color.N)
                return True
        
        self.base_used = self.base_urls[0]
        self.results["url_used"] = self.base_used
        print(Color.Y + f"[!] Using base: {self.base_used} (may not respond)" + Color.N)
        return True
    
    def generate_urls(self):
        """Generate all URLs to test"""
        total = len(COMMON_DIRS) * len(EXTENSIONS)
        print(Color.Y + f"\n[*] Generating {total} URLs to test..." + Color.N)
        
        for dir_path in COMMON_DIRS:
            for ext in EXTENSIONS:
                url = f"{self.base_used.rstrip('/')}/{dir_path}{ext}"
                self.urls_to_test.append({
                    "url": url,
                    "path": dir_path,
                    "ext": ext
                })
        
        # Shuffle URLs to avoid pattern detection
        random.shuffle(self.urls_to_test)
        return len(self.urls_to_test)
    
    def check_single_url(self, item):
        """Check a single URL (for threading)"""
        url = item["url"]
        path = item["path"]
        ext = item["ext"]
        
        # Rate limiting
        self.rate_limiter.wait_if_needed()
        
        # Random user agent
        headers = {"User-Agent": random.choice(USER_AGENTS)}
        
        # Make request
        resp, error = safe_request(url, headers=headers, timeout=5, allow_redirects=False)
        
        result = {
            "url": url,
            "path": path,
            "ext": ext,
            "status": None,
            "error": None,
            "found": False,
            "size": 0,
            "redirect": None
        }
        
        if error:
            result["error"] = error
            return result
        
        if resp:
            result["status"] = resp.status_code
            
            # Check if exists (not 404)
            if resp.status_code not in [404, 410]:
                result["found"] = True
                result["size"] = len(resp.content) if hasattr(resp, 'content') else 0
                
                if resp.status_code in [301, 302, 307, 308]:
                    result["redirect"] = resp.headers.get('location', 'unknown')
        
        return result
    
    def run_scan(self):
        """Run the directory scan with multiple threads"""
        print(Color.C + f"\n[+] Starting FAST Directory Scan with {self.threads} threads" + Color.N)
        
        start_time = time.time()
        tested = 0
        total = len(self.urls_to_test)
        
        # Progress tracking
        last_percent = 0
        found_in_this_batch = 0
        
        with ThreadPoolExecutor(max_workers=self.threads) as executor:
            # Submit all tasks
            future_to_url = {executor.submit(self.check_single_url, item): item for item in self.urls_to_test}
            
            # Process results as they complete
            for future in as_completed(future_to_url):
                tested += 1
                result = future.result()
                
                # Update stats
                self.results["stats"]["total_tests"] += 1
                
                # Calculate percentage
                percent = (tested / total) * 100
                if percent - last_percent >= 1:  # Update every 1%
                    elapsed = time.time() - start_time
                    speed = tested / elapsed if elapsed > 0 else 0
                    
                    # Progress bar
                    bar_length = 30
                    filled = int(bar_length * tested // total)
                    bar = '█' * filled + '░' * (bar_length - filled)
                    
                    print(f"\r{Color.C}[{bar}] {percent:.1f}% | {tested}/{total} | {speed:.1f} req/s | Found: {self.results['stats']['found_count']}{Color.N}", end='')
                    
                    last_percent = percent
                
                if result["error"]:
                    self.results["errors"].append({
                        "url": result["url"],
                        "error": result["error"]
                    })
                    continue
                
                if result["found"]:
                    # Found something
                    self.results["stats"]["found_count"] += 1
                    found_in_this_batch += 1
                    
                    dir_info = {
                        "url": result["url"],
                        "status": result["status"],
                        "size": result["size"],
                        "path": result["path"]
                    }
                    
                    if result["redirect"]:
                        dir_info["redirect"] = result["redirect"]
                    
                    self.results["directories"][result["url"]] = dir_info
                    self.results["found"].append(result["url"])
                    
                    # Print immediately when found (with newline to break progress bar)
                    if found_in_this_batch % 5 == 0:
                        status_color = Color.G if result["status"] == 200 else Color.Y
                        print(f"\n  {Color.G}[FOUND]{Color.N} {result['url']} → {status_color}{result['status']}{Color.N}")
        
        # Final newline after progress bar
        print()
        
        # Calculate stats
        elapsed = time.time() - start_time
        self.results["stats"]["time_elapsed"] = round(elapsed, 2)
        self.results["stats"]["speed"] = round(tested / elapsed, 2)
        
        return self.results
    
    def analyze_results(self):
        """Analyze found directories"""
        if not self.results["found"]:
            return
        
        # Group by status code
        by_status = {}
        admin_panels = []
        sensitive_files = []
        
        for url in self.results["found"]:
            status = self.results["directories"][url]["status"]
            if status not in by_status:
                by_status[status] = []
            by_status[status].append(url)
            
            # Check for admin panels
            if any(x in url.lower() for x in ['admin', 'login', 'dashboard', 'cpanel', 'manager']):
                admin_panels.append(url)
            
            # Check for sensitive files
            if any(x in url.lower() for x in ['.git', '.env', 'backup', 'sql', 'db']):
                sensitive_files.append(url)
        
        return {
            "by_status": by_status,
            "admin_panels": admin_panels,
            "sensitive_files": sensitive_files
        }

# ============================================================
# MAIN FUNCTION
# ============================================================

def run(target):
    """Main directory scanner with ultra-fast mode"""
    print(Color.C + "\n" + "="*60)
    print("🔥 DIRECTORY SCANNER ULTRA -  Multiprocessing")
    print("="*60 + Color.N + "\n")
    
    if not target:
        print(Color.R + "[!] No target set" + Color.N)
        return
    
    # Ask for scan mode
    print(Color.Y + "Scan Modes:" + Color.N)
    print("1) 🐢 Slow & Safe (5 threads) - For sensitive sites")
    print("2) 🚀 Balanced (15 threads) - default")
    print("3) ⚡ Ultra Fast (30 threads) - Moderate risk")
    print("4) 💥 Insane (50 threads) - High risk (may crash the site)")
    print("5) 🎯 Custom")
    
    choice = input(Color.Y + "\nSelect mode (1-5): " + Color.N).strip()
    
    threads = 15  # default
    delay = 0.1   # default delay between requests
    
    if choice == '1':
        threads = 5
        delay = 0.3
    elif choice == '2':
        threads = 15
        delay = 0.1
    elif choice == '3':
        threads = 30
        delay = 0.05
    elif choice == '4':
        threads = 50
        delay = 0.01
        print(Color.R + "\n⚠️  WARNING: Insane mode may crash the server or get you banned!" + Color.N)
        confirm = input("Are you sure? (y/N): ").strip().lower()
        if confirm != 'y':
            threads = 15
            delay = 0.1
            print(Color.Y + "Switching to Balanced mode." + Color.N)
    elif choice == '5':
        try:
            threads = int(input("Number of threads (1-100): ").strip() or "15")
            delay = float(input("Delay between requests (seconds, 0-1): ").strip() or "0.1")
            if threads > 100:
                threads = 100
                print(Color.Y + "Max threads limited to 100" + Color.N)
        except:
            threads = 15
            delay = 0.1
    
    # Create scanner
    scanner = FastDirectoryScanner(target, threads=threads, delay=delay)
    
    # Find working base
    if not scanner.find_working_base():
        print(Color.R + "[!] Could not connect to target" + Color.N)
        return
    
    # Generate URLs
    total_urls = scanner.generate_urls()
    
    print(Color.Y + f"\n[*] Starting scan with {threads} concurrent threads" + Color.N)
    print(Color.Y + f"[*] Total URLs to check: {total_urls:,}" + Color.N)
    print(Color.Y + f"[*] Estimated time: {total_urls/(threads*2):.1f} seconds\n" + Color.N)
    
    # Run scan
    results = scanner.run_scan()
    
    # Analyze results
    analysis = scanner.analyze_results()
    
    # Print summary
    print(Color.C + "\n┌─ SCAN SUMMARY ─────────────────────────┐" + Color.N)
    print(f"  {Color.Y}Total Requests:{Color.N} {results['stats']['total_tests']:,}")
    print(f"  {Color.Y}Found:{Color.N} {Color.G}{results['stats']['found_count']}{Color.N}")
    print(f"  {Color.Y}Speed:{Color.N} {results['stats']['speed']:.1f} req/s")
    print(f"  {Color.Y}Time:{Color.N} {results['stats']['time_elapsed']:.1f}s")
    print(f"  {Color.Y}Threads:{Color.N} {threads}")
    print(Color.C + "└────────────────────────────────────┘" + Color.N)
    
    if analysis:
        # Show by status
        for status, urls in analysis["by_status"].items():
            status_color = Color.G if status == 200 else Color.Y
            print(f"\n{status_color}HTTP {status}: {len(urls)} URLs{Color.N}")
            for url in urls[:10]:
                print(f"  • {url}")
            if len(urls) > 10:
                print(f"  ... and {len(urls)-10} more")
        
        # Show admin panels
        if analysis["admin_panels"]:
            print(Color.R + f"\n[!] Potential Admin Panels Found: {len(analysis['admin_panels'])}" + Color.N)
            for url in analysis["admin_panels"][:10]:
                print(f"  {Color.R}• {url}{Color.N}")
        
        # Show sensitive files
        if analysis["sensitive_files"]:
            print(Color.R + f"\n[🔥] CRITICAL: Sensitive Files Found: {len(analysis['sensitive_files'])}" + Color.N)
            for url in analysis["sensitive_files"][:10]:
                print(f"  {Color.R}• {url}{Color.N}")
    
    # Save results
    filename = save_log(target, "dirs_ultra", results)
    print(Color.Y + f"\nSaved → {filename}\n" + Color.N)
    
    # Recommendations
    if results['stats']['found_count'] > 0:
        print(Color.G + "\n[✓] Next steps:" + Color.N)
        print("  1. Check admin panels for login pages")
        print("  2. Download sensitive files and examine them")
        print("  3. Run backup_exploit module on found files")