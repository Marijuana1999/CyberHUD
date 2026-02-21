# core/plugin_manager.py
import os
import importlib.util
import inspect

class PluginManager:
    def __init__(self):
        self.plugins_dir = "plugins"
        os.makedirs(self.plugins_dir, exist_ok=True)
        self.plugins = {}
    
    def discover_plugins(self):
        for filename in os.listdir(self.plugins_dir):
            if filename.endswith(".py") and not filename.startswith("__"):
                self.load_plugin(filename[:-3])
    
    def load_plugin(self, plugin_name):
        try:
            spec = importlib.util.spec_from_file_location(
                plugin_name, 
                os.path.join(self.plugins_dir, f"{plugin_name}.py")
            )
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            # Check if plugin has required functions
            if hasattr(module, 'run') and hasattr(module, 'info'):
                self.plugins[plugin_name] = module
                print(f"[✓] Loaded plugin: {module.info().get('name', plugin_name)}")
            else:
                print(f"[!] Plugin {plugin_name} missing required functions")
                
        except Exception as e:
            print(f"[!] Failed to load plugin {plugin_name}: {e}")
    
    def get_plugin_info(self):
        info = {}
        for name, module in self.plugins.items():
            info[name] = module.info()
        return info
    
    def run_plugin(self, name, target):
        if name in self.plugins:
            return self.plugins[name].run(target)
        return None