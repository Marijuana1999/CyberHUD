# modules/graphql_analyzer.py
import requests
import json
from core.core import Color, save_log, safe_request

class GraphQLAnalyzer:
    def __init__(self, target):
        self.target = target
        self.endpoints = [
            '/graphql',
            '/graphiql',
            '/v1/graphql',
            '/v2/graphql',
            '/api/graphql',
            '/query',
            '/gql'
        ]
    
    def check_introspection(self, url):
        """Check if GraphQL introspection is enabled"""
        query = """
        {
            __schema {
                types {
                    name
                    fields {
                        name
                        type {
                            name
                            kind
                        }
                    }
                }
            }
        }
        """
        
        try:
            response, error = safe_request(
                url, 
                method="POST",
                headers={'Content-Type': 'application/json'},
                data=json.dumps({'query': query}),
                timeout=5
            )
            
            if not error and response.status_code == 200:
                data = response.json()
                if 'data' in data and data['data']:
                    return True, data['data']
            return False, None
        except:
            return False, None
    
    def find_endpoints(self, base_url):
        """Find GraphQL endpoints"""
        found = []
        
        for endpoint in self.endpoints:
            url = base_url.rstrip('/') + endpoint
            response, error = safe_request(url, timeout=3)
            
            if not error and response.status_code != 404:
                # Check if it's GraphQL
                if 'graphql' in response.text.lower() or response.status_code == 400:
                    found.append({
                        'url': url,
                        'status': response.status_code,
                        'type': 'GraphQL endpoint'
                    })
        
        return found

def run(target):
    print(Color.C + "\n[+] GraphQL Security Analyzer" + Color.N)
    
    base_url = f"https://{target}"
    analyzer = GraphQLAnalyzer(target)
    
    results = {
        'target': target,
        'endpoints': [],
        'introspection': {}
    }
    
    # Find endpoints
    print(Color.Y + "[*] Searching for GraphQL endpoints..." + Color.N)
    endpoints = analyzer.find_endpoints(base_url)
    
    if not endpoints:
        print(Color.R + "[-] No GraphQL endpoints found" + Color.N)
        return
    
    results['endpoints'] = endpoints
    
    for endpoint in endpoints:
        url = endpoint['url']
        print(Color.G + f"[+] Found: {url}" + Color.N)
        
        # Check introspection
        enabled, schema = analyzer.check_introspection(url)
        if enabled:
            print(Color.R + f"[!] CRITICAL: Introspection enabled at {url}" + Color.N)
            results['introspection'][url] = {
                'enabled': True,
                'risk': 'CRITICAL',
                'note': 'Attacker can dump entire API schema'
            }
    
    save_log(target, "graphql", results)