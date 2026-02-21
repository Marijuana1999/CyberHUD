# modules/jwt_analyzer.py
import jwt
import json
import base64
from core.core import Color, save_log, safe_request

class JWTAnalyzer:
    def __init__(self):
        self.weak_secrets = ['secret', 'password', '123456', 'key', 'token', 'jwt', 'changeit', 'admin']
    
    def decode_jwt(self, token):
        """Decode JWT without verification"""
        try:
            parts = token.split('.')
            if len(parts) != 3:
                return None, "Not a valid JWT"
            
            header = json.loads(base64.b64decode(parts[0] + '==').decode('utf-8'))
            payload = json.loads(base64.b64decode(parts[1] + '==').decode('utf-8'))
            
            return {
                'header': header,
                'payload': payload,
                'signature': parts[2]
            }, None
        except Exception as e:
            return None, str(e)
    
    def check_none_algorithm(self, token):
        """Check if server accepts 'none' algorithm"""
        try:
            parts = token.split('.')
            header = json.loads(base64.b64decode(parts[0] + '==').decode('utf-8'))
            
            # Create modified token with 'none' algorithm
            modified_header = header.copy()
            modified_header['alg'] = 'none'
            modified_header_str = json.dumps(modified_header)
            modified_header_b64 = base64.urlsafe_b64encode(modified_header_str.encode()).decode().rstrip('=')
            
            modified_token = f"{modified_header_b64}.{parts[1]}."
            
            return modified_token
        except:
            return None
    
    def check_weak_secret(self, token):
        """Try to crack JWT with weak secrets"""
        for secret in self.weak_secrets:
            try:
                decoded = jwt.decode(token, secret, algorithms=['HS256'])
                return secret, decoded
            except:
                pass
        return None, None
    
    def analyze(self, token):
        results = {
            'token': token[:30] + '...' if len(token) > 30 else token,
            'issues': [],
            'risk': 'LOW'
        }
        
        # Decode token
        decoded, error = self.decode_jwt(token)
        if error:
            results['issues'].append(f"Invalid JWT: {error}")
            return results
        
        results['decoded'] = decoded
        
        # Check for sensitive data in payload
        sensitive_keys = ['password', 'secret', 'key', 'token', 'auth', 'admin']
        for key in sensitive_keys:
            if key in decoded['payload']:
                results['issues'].append(f"Sensitive data in payload: {key}")
                results['risk'] = 'HIGH'
        
        # Check for 'none' algorithm vulnerability
        if decoded['header'].get('alg') == 'none':
            results['issues'].append("Algorithm set to 'none' - CRITICAL vulnerability")
            results['risk'] = 'CRITICAL'
        
        # Check for weak secrets
        secret, cracked = self.check_weak_secret(token)
        if secret:
            results['issues'].append(f"Weak secret found: '{secret}' - JWT can be forged")
            results['risk'] = 'CRITICAL'
            results['cracked'] = cracked
        
        return results

def run(target):
    print(Color.C + "\n[+] JWT Security Analyzer" + Color.N)
    print(Color.Y + "[*] Looking for JWT tokens in requests..." + Color.N)
    
    # اینجا باید tokenها رو از localStorage یا cookies پیدا کنی
    # اما فعلاً نمونه:
    analyzer = JWTAnalyzer()
    result = analyzer.analyze("eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c")
    
    print(json.dumps(result, indent=2))
    save_log(target, "jwt_analyzer", result)