#!/usr/bin/env python3

# modules/rate_limit.py
import time
import statistics
from core.core import Color, save_log, safe_request

class RateLimitTester:
    def __init__(self, target):
        self.target = target
        self.base_urls = [f"https://{target}", f"http://{target}"]
        self.results = {
            "responses": [],
            "timings": [],
            "status_codes": [],
            "headers": []
        }
    
    def find_working_url(self):
        """Find a working URL for the target"""
        for url in self.base_urls:
            resp, error = safe_request(url, timeout=5)
            if not error and resp and resp.status_code < 500:
                return url, resp
        return None, None
    
    def test_endpoint(self, url, endpoint="", method="GET", count=10, delay=0.1):
        """Test rate limiting on a specific endpoint"""
        test_url = f"{url.rstrip('/')}/{endpoint.lstrip('/')}" if endpoint else url
        
        print(Color.Y + f"\n[*] Testing: {test_url}" + Color.N)
        print(Color.Y + f"[*] Sending {count} requests with {delay}s delay\n" + Color.N)
        
        responses = []
        timings = []
        status_codes = []
        
        for i in range(count):
            try:
                start = time.time()
                resp, error = safe_request(test_url, method=method, timeout=10)
                elapsed = time.time() - start
                
                if error:
                    print(f"  {Color.R}Request {i+1}: ERROR - {error}{Color.N}")
                    responses.append({"error": error})
                else:
                    status = resp.status_code
                    print(f"  {Color.B}Request {i+1}: {Color.Y if status != 200 else Color.G}{status}{Color.N} ({elapsed:.2f}s)")
                    
                    responses.append({
                        "status": status,
                        "time": elapsed,
                        "headers": dict(resp.headers)
                    })
                    timings.append(elapsed)
                    status_codes.append(status)
                
                if i < count - 1 and delay > 0:
                    time.sleep(delay)
                    
            except Exception as e:
                print(f"  {Color.R}Request {i+1}: EXCEPTION - {e}{Color.N}")
                responses.append({"error": str(e)})
        
        return responses, timings, status_codes
    
    def analyze_results(self, responses, timings, status_codes):
        """Analyze test results for rate limiting patterns"""
        analysis = {
            "rate_limited": False,
            "blocked": False,
            "delayed": False,
            "patterns": [],
            "stats": {}
        }
        
        if not status_codes:
            return analysis
        
        # Check for 429 (Too Many Requests)
        if 429 in status_codes:
            analysis["rate_limited"] = True
            analysis["patterns"].append("HTTP 429 detected - Rate limiting active")
        
        # Check for 403 (Forbidden) after many requests
        if status_codes.count(403) > len(status_codes) // 2:
            analysis["blocked"] = True
            analysis["patterns"].append("HTTP 403 after multiple requests - IP may be blocked")
        
        # Check for 503 (Service Unavailable)
        if 503 in status_codes:
            analysis["patterns"].append("HTTP 503 - Server may be overwhelmed or rate limiting")
        
        # Analyze timing patterns
        if len(timings) > 1:
            first_avg = statistics.mean(timings[:3]) if len(timings) >= 3 else timings[0]
            last_avg = statistics.mean(timings[-3:]) if len(timings) >= 3 else timings[-1]
            
            if last_avg > first_avg * 2:
                analysis["delayed"] = True
                analysis["patterns"].append(f"Response time increased from {first_avg:.2f}s to {last_avg:.2f}s")
            
            # Calculate statistics
            analysis["stats"] = {
                "min_time": min(timings),
                "max_time": max(timings),
                "avg_time": statistics.mean(timings),
                "std_dev": statistics.stdev(timings) if len(timings) > 1 else 0
            }
        
        # Check for CAPTCHA or challenge pages
        for resp in responses[-3:]:  # Check last few responses
            if isinstance(resp, dict) and "headers" in resp:
                headers = resp.get("headers", {})
                content_type = headers.get("content-type", "").lower()
                if "captcha" in str(headers).lower() or "challenge" in str(headers).lower():
                    analysis["patterns"].append("CAPTCHA or challenge page detected")
                    analysis["blocked"] = True
        
        return analysis

def run(target):
    """Main rate limit tester"""
    print(Color.C + "\n[+] Rate-Limit Sensitivity Test\n" + Color.N)
    
    if not target:
        print(Color.R + "[!] No target set" + Color.N)
        return
    
    tester = RateLimitTester(target)
    
    # Find working URL
    print(Color.Y + "[*] Finding working endpoint..." + Color.N)
    url, response = tester.find_working_url()
    
    if not url:
        print(Color.R + "[!] Could not connect to target" + Color.N)
        return
    
    print(Color.G + f"[✓] Using: {url}\n" + Color.N)
    
    result = {
        "target": target,
        "url_used": url,
        "tests": {},
        "summary": {}
    }
    
    # Test 1: Rapid requests (no delay)
    print(Color.C + "┌─ TEST 1: Rapid Requests (No Delay) ───┐" + Color.N)
    resp1, time1, status1 = tester.test_endpoint(url, count=10, delay=0)
    result["tests"]["rapid"] = {
        "responses": resp1,
        "timings": time1,
        "status_codes": status1
    }
    
    # Test 2: Slow requests (with delay)
    print(Color.C + "\n┌─ TEST 2: Slow Requests (1s Delay) ────┐" + Color.N)
    resp2, time2, status2 = tester.test_endpoint(url, count=5, delay=1)
    result["tests"]["slow"] = {
        "responses": resp2,
        "timings": time2,
        "status_codes": status2
    }
    
    # Test 3: Test login page if exists
    login_endpoints = ["login", "wp-login.php", "admin", "user/login"]
    for endpoint in login_endpoints:
        test_url = f"{url.rstrip('/')}/{endpoint}"
        resp, error = safe_request(test_url, timeout=5)
        if not error and resp and resp.status_code < 500:
            print(Color.C + f"\n┌─ TEST 3: Login Page ({endpoint}) ───────┐" + Color.N)
            resp3, time3, status3 = tester.test_endpoint(url, endpoint=endpoint, count=5, delay=0.2)
            result["tests"]["login"] = {
                "endpoint": endpoint,
                "responses": resp3,
                "timings": time3,
                "status_codes": status3
            }
            break
    
    # Analyze results
    print(Color.C + "\n┌─ RATE LIMIT ANALYSIS ─────────────────┐" + Color.N)
    
    for test_name, test_data in result["tests"].items():
        if "status_codes" in test_data:
            analysis = tester.analyze_results(
                test_data.get("responses", []),
                test_data.get("timings", []),
                test_data.get("status_codes", [])
            )
            test_data["analysis"] = analysis
    
    # Combine analysis for summary
    all_status = []
    all_timings = []
    all_patterns = []
    
    for test in result["tests"].values():
        if "status_codes" in test:
            all_status.extend(test["status_codes"])
        if "timings" in test:
            all_timings.extend(test["timings"])
        if "analysis" in test and "patterns" in test["analysis"]:
            all_patterns.extend(test["analysis"]["patterns"])
    
    # Determine overall rate limiting status
    if 429 in all_status:
        result["summary"]["rate_limited"] = True
        result["summary"]["severity"] = "LOW"
        result["summary"]["message"] = "Rate limiting is active (429)"
    elif 403 in all_status:
        result["summary"]["rate_limited"] = True
        result["summary"]["severity"] = "MEDIUM"
        result["summary"]["message"] = "IP may be blocked after multiple requests"
    elif any(p for p in all_patterns if "increased" in p):
        result["summary"]["rate_limited"] = True
        result["summary"]["severity"] = "LOW"
        result["summary"]["message"] = "Response time increased - possible throttling"
    else:
        result["summary"]["rate_limited"] = False
        result["summary"]["severity"] = "HIGH"
        result["summary"]["message"] = "No rate limiting detected - possible brute force"
    
    # Display summary
    risk_color = Color.G
    if result["summary"]["severity"] == "HIGH":
        risk_color = Color.R
    elif result["summary"]["severity"] == "MEDIUM":
        risk_color = Color.Y
    
    print(f"  {Color.Y}Status:{Color.N} {risk_color}{result['summary']['message']}{Color.N}")
    print(f"  {Color.Y}Rate Limited:{Color.N} {result['summary']['rate_limited']}")
    print(f"  {Color.Y}Severity:{Color.N} {risk_color}{result['summary']['severity']}{Color.N}")
    
    if all_timings:
        print(f"  {Color.Y}Avg Response Time:{Color.N} {statistics.mean(all_timings):.2f}s")
        print(f"  {Color.Y}Min/Max:{Color.N} {min(all_timings):.2f}s / {max(all_timings):.2f}s")
    
    if all_patterns:
        print(f"\n  {Color.Y}Patterns Detected:{Color.N}")
        for pattern in list(set(all_patterns))[:5]:
            print(f"    • {pattern}")
    
    print(Color.C + "└────────────────────────────────────┘" + Color.N)
    
    if not result["summary"]["rate_limited"]:
        print(Color.R + f"\n[!] No rate limiting detected!" + Color.N)
        print(Color.Y + "    This could allow brute force attacks." + Color.N)
        print(Color.Y + "    Consider implementing rate limiting." + Color.N)
    
    # Save results
    filename = save_log(target, "rate_limit", result)
    print(Color.Y + f"\nSaved → {filename}\n" + Color.N)