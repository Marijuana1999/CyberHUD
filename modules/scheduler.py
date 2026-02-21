# core/scheduler.py
import time
import threading
from datetime import datetime, timedelta
from queue import Queue

class ScanScheduler:
    def __init__(self):
        self.tasks = Queue()
        self.results = {}
        self.running = False
        self.threads = []
    
    def add_task(self, target, module, priority=1):
        self.tasks.put({
            "target": target,
            "module": module,
            "priority": priority,
            "added": datetime.now()
        })
    
    def worker(self):
        while self.running:
            try:
                task = self.tasks.get(timeout=1)
                
                # Run the scan
                print(f"[*] Running {task['module']} on {task['target']}")
                
                # Import module dynamically
                module = __import__(f"modules.{task['module']}", fromlist=['run'])
                
                # Run with timeout
                result = module.run(task['target'])
                
                # Store result
                key = f"{task['target']}_{task['module']}"
                self.results[key] = {
                    "result": result,
                    "completed": datetime.now()
                }
                
                self.tasks.task_done()
                
            except:
                pass
    
    def start(self, num_threads=3):
        self.running = True
        for i in range(num_threads):
            t = threading.Thread(target=self.worker)
            t.daemon = True
            t.start()
            self.threads.append(t)
    
    def stop(self):
        self.running = False
    
    def get_results(self, target=None, module=None):
        if target and module:
            return self.results.get(f"{target}_{module}")
        return self.results