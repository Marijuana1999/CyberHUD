# core/config.py
import json
import os

class Config:
    def __init__(self):
        self.config_file = "config.json"
        self.default_config = {
            "general": {
                "timeout": 10,
                "max_threads": 30,
                "user_agent": "Mozilla/5.0 (CyberHUD/3.0)",
                "save_logs": True,
                "log_format": "json"
            },
            "scanning": {
                "ports": [21,22,23,25,53,80,110,143,443,993,995,3306,3389,5432,8080,8443],
                "dir_depth": 3,
                "follow_redirects": True,
                "rate_limit": 0.5
            },
            "reporting": {
                "auto_open": False,
                "include_screenshots": True,
                "report_format": "html"
            },
            "proxy": {
                "enabled": False,
                "http": "",
                "https": ""
            }
        }
    
    def load(self):
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r') as f:
                    return json.load(f)
            except:
                return self.default_config
        return self.default_config
    
    def save(self, config):
        with open(self.config_file, 'w') as f:
            json.dump(config, f, indent=4)

config = Config().load()