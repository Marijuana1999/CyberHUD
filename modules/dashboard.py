# core/dashboard.py
import os
import json
from datetime import datetime
from collections import defaultdict

class TargetManager:
    def __init__(self):
        self.targets_file = "targets.json"
        self.targets = self.load_targets()
    
    def load_targets(self):
        if os.path.exists(self.targets_file):
            with open(self.targets_file, 'r') as f:
                return json.load(f)
        return {}
    
    def save_targets(self):
        with open(self.targets_file, 'w') as f:
            json.dump(self.targets, f, indent=4)
    
    def add_target(self, name, url):
        self.targets[name] = {
            "url": url,
            "added": datetime.now().isoformat(),
            "last_scan": None,
            "findings": defaultdict(list),
            "notes": ""
        }
        self.save_targets()
    
    def update_findings(self, target, module, findings):
        if target in self.targets:
            if "findings" not in self.targets[target]:
                self.targets[target]["findings"] = {}
            self.targets[target]["findings"][module] = findings
            self.targets[target]["last_scan"] = datetime.now().isoformat()
            self.save_targets()
    
    def get_stats(self, target):
        if target not in self.targets:
            return None
        
        stats = {
            "critical": 0,
            "high": 0,
            "medium": 0,
            "low": 0
        }
        
        for module, findings in self.targets[target].get("findings", {}).items():
            for f in findings:
                severity = f.get("severity", "low").lower()
                stats[severity] = stats.get(severity, 0) + 1
        
        return stats