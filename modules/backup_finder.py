#!/usr/bin/env python3

# modules/backup_finder.py
import os
from core.core import Color, save_log, safe_request

COMMON_BACKUP_PATHS = [
    # Archives
    "backup.zip", "backup.tar", "backup.tar.gz", "backup.tgz", "backup.7z",
    "backup.rar", "backup.bak", "backup.old", "backup.sql", "backup.db",
    "site.zip", "site.tar.gz", "site.rar", "site.7z",
    "www.zip", "www.tar.gz", "www.rar",
    "web.zip", "web.tar.gz", "web.rar",
    
    # Database dumps
    "db.sql", "database.sql", "dump.sql", "db.sql.gz", "db.sql.bz2",
    "mysql.sql", "mysqldump.sql", "data.sql", "db_backup.sql",
    "backup_mysql.sql", "sql_backup.sql", "db_dump.sql",
    
    # Common backup names
    "backup", "backups", "backup.zip", "backup.tar", "backup.rar",
    "site_backup", "site-backup", "site_backup.zip", "site-backup.zip",
    "www_backup", "www-backup", "www_backup.zip", "www-backup.zip",
    "old", "old.zip", "old.tar.gz", "old.rar",
    "archive", "archive.zip", "archive.tar.gz",
    
    # WordPress specific
    "wp-content.zip", "wp-content.tar.gz", "wp-content.rar",
    "wp-config.php.bak", "wp-config.php.old", "wp-config.php~",
    "wp-config.bak", "wp-config.old", "wp-config.save",
    
    # Config files
    "config.php.bak", "config.php.old", "config.php~", "config.php.save",
    "config.inc.php.bak", "config.inc.php.old", "config.inc.php~",
    ".env.bak", ".env.old", ".env.local", ".env.backup",
    ".htaccess.bak", ".htaccess.old", ".htaccess~",
    
    # Version control
    ".git/config", ".git/index", ".git/HEAD", ".gitignore",
    ".svn/entries", ".svn/wc.db",
    
    # Temp files
    "index.php~", "index.html~", "index.php.bak", "index.html.bak",
    "*.swp", "*.swo", "*.tmp", "*.temp",
    
    # Other
    "phpinfo.php", "info.php", "test.php", "php.php",
    "shell.php", "cmd.php", "exec.php", "system.php",
    "debug.php", "dev.php", "development.php",
    
    # Directories
    "backup/", "backups/", "old/", "archive/", "bak/",
    "temp/", "tmp/", "test/", "dev/", "private/"
]

COMMON_EXTENSIONS = ['.zip', '.tar', '.gz', '.tgz', '.bz2', '.7z', '.rar', '.bak', '.old', '.sql']

def check_file_type(content, headers, url):
    """Try to determine file type"""
    file_info = {
        "type": "Unknown",
        "size": len(content) if content else 0,
        "headers": headers
    }
    
    # Check by content-type header
    content_type = headers.get('content-type', '').lower()
    if 'zip' in content_type:
        file_info["type"] = "ZIP Archive"
    elif 'gzip' in content_type or 'x-gzip' in content_type:
        file_info["type"] = "GZIP Archive"
    elif 'tar' in content_type:
        file_info["type"] = "TAR Archive"
    elif 'sql' in content_type or 'mysql' in content_type:
        file_info["type"] = "SQL Dump"
    elif 'php' in content_type:
        file_info["type"] = "PHP File"
    elif 'text/plain' in content_type:
        file_info["type"] = "Text File"
    
    # Check by content (magic bytes)
    if content and len(content) > 4:
        if content.startswith(b'PK\x03\x04'):
            file_info["type"] = "ZIP Archive"
        elif content.startswith(b'\x1F\x8B'):
            file_info["type"] = "GZIP Archive"
        elif content.startswith(b'BZh'):
            file_info["type"] = "BZIP2 Archive"
        elif content.startswith(b'Rar!'):
            file_info["type"] = "RAR Archive"
        elif content.startswith(b'ustar'):
            file_info["type"] = "TAR Archive"
        elif b'CREATE TABLE' in content[:500] or b'INSERT INTO' in content[:500]:
            file_info["type"] = "SQL Dump"
        elif b'<?php' in content[:100]:
            file_info["type"] = "PHP Source"
    
    # Check by extension
    ext = os.path.splitext(url)[1].lower()
    if ext in ['.php', '.php3', '.php4', '.php5', '.php7', '.phtml']:
        file_info["type"] = "PHP File"
    elif ext in ['.sql', '.mysql', '.psql']:
        file_info["type"] = "SQL File"
    elif ext in ['.zip', '.tar', '.gz', '.tgz', '.bz2', '.7z', '.rar']:
        file_info["type"] = f"{ext.upper()[1:]} Archive"
    
    return file_info

def run(target):
    """Main backup finder function"""
    print(Color.C + "\n[+] Backup File Finder\n" + Color.N)
    
    if not target:
        print(Color.R + "[!] No target set" + Color.N)
        return
    
    # Try both HTTP and HTTPS
    base_urls = [f"https://{target}", f"http://{target}"]
    
    result = {
        "target": target,
        "url_used": None,
        "found_files": [],
        "tested_paths": [],
        "summary": {
            "total_tested": 0,
            "found_count": 0,
            "file_types": {}
        }
    }
    
    base_used = None
    
    # Determine which base URL works
    for base in base_urls:
        resp, error = safe_request(base, timeout=5)
        if not error and resp and resp.status_code < 500:
            base_used = base
            result["url_used"] = base
            print(Color.G + f"[✓] Using base: {base}" + Color.N)
            break
    
    if not base_used:
        base_used = base_urls[0]
        result["url_used"] = base_used
        print(Color.Y + f"[!] Using base: {base_used} (may not respond)" + Color.N)
    
    print(Color.Y + f"\n[*] Testing {len(COMMON_BACKUP_PATHS)} common backup paths..." + Color.N)
    
    # Test each path
    for i, path in enumerate(COMMON_BACKUP_PATHS, 1):
        # Construct URL
        if path.endswith('/'):
            url = f"{base_used.rstrip('/')}/{path}"
        else:
            url = f"{base_used.rstrip('/')}/{path}"
        
        result["tested_paths"].append(url)
        result["summary"]["total_tested"] += 1
        
        # Progress indicator
        if i % 20 == 0:
            print(f"  {Color.Y}Progress: {i}/{len(COMMON_BACKUP_PATHS)}{Color.N}")
        
        # Make request
        resp, error = safe_request(url, timeout=5, allow_redirects=False)
        
        if not error and resp:
            # Check if file exists (200 OK and has content)
            if resp.status_code == 200 and len(resp.content) > 20:
                # Analyze file type
                file_info = check_file_type(resp.content, dict(resp.headers), url)
                
                # Check if it's a real file (not HTML)
                is_real = True
                if 'text/html' in resp.headers.get('content-type', '').lower():
                    # Could be HTML error page
                    if b'<html' in resp.content[:500] or b'<!doctype' in resp.content[:500]:
                        is_real = False
                
                if is_real:
                    print(Color.R + f"\n[FOUND] {url}" + Color.N)
                    print(f"  Type: {Color.C}{file_info['type']}{Color.N}")
                    print(f"  Size: {Color.Y}{file_info['size']:,} bytes{Color.N}")
                    
                    file_entry = {
                        "url": url,
                        "status": resp.status_code,
                        "size": file_info['size'],
                        "type": file_info['type'],
                        "content_type": resp.headers.get('content-type', 'unknown')
                    }
                    
                    result["found_files"].append(file_entry)
                    result["summary"]["found_count"] += 1
                    
                    # Count by type
                    ftype = file_info['type']
                    if ftype not in result["summary"]["file_types"]:
                        result["summary"]["file_types"][ftype] = 0
                    result["summary"]["file_types"][ftype] += 1
            
            elif resp.status_code in [301, 302]:
                # Redirect - might be worth noting
                location = resp.headers.get('location', 'unknown')
                print(Color.Y + f"[REDIRECT] {url} → {location}" + Color.N)
    
    # Summary
    print(Color.C + "\n┌─ BACKUP SCAN SUMMARY ─────────────────┐" + Color.N)
    print(f"  {Color.Y}Paths Tested:{Color.N} {result['summary']['total_tested']}")
    print(f"  {Color.Y}Files Found:{Color.N} {Color.R if result['summary']['found_count'] > 0 else Color.G}{result['summary']['found_count']}{Color.N}")
    
    if result["summary"]["file_types"]:
        print(f"\n  {Color.Y}File Types:{Color.N}")
        for ftype, count in result["summary"]["file_types"].items():
            print(f"    • {ftype}: {count}")
    
    print(Color.C + "└────────────────────────────────────┘" + Color.N)
    
    if result["found_files"]:
        print(Color.R + f"\n[!] Found {result['summary']['found_count']} backup files!" + Color.N)
        print(Color.Y + "    These files may contain sensitive information." + Color.N)
        print(Color.Y + "    Check them manually or use backup_exploit module." + Color.N)
    else:
        print(Color.G + "\n[✓] No backup files found." + Color.N)
    
    # Save results
    filename = save_log(target, "backup_finder", result)
    print(Color.Y + f"\nSaved → {filename}\n" + Color.N)