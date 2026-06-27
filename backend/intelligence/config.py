import yaml
import os
from typing import Dict, Any

class IntelligenceConfig:
    """Loads and parses the intelligence.yaml configuration file."""
    
    def __init__(self, config_path: str = "intelligence.yaml"):
        self.config_path = config_path
        self._config: Dict[str, Any] = {}
        self.reload()

    def reload(self) -> None:
        """Reloads the YAML file from disk."""
        if os.path.exists(self.config_path):
            with open(self.config_path, "r") as f:
                self._config = yaml.safe_load(f) or {}
        else:
            self._config = {"modules": {}}

    def get_module_config(self, module_name: str) -> Dict[str, Any]:
        """Returns the specific configuration for a given module."""
        modules = self._config.get("modules", {})
        return modules.get(module_name.lower(), {})

    def is_enabled(self, module_name: str, default: bool = True) -> bool:
        """Checks if a module is enabled in the YAML configuration."""
        mod_conf = self.get_module_config(module_name)
        return mod_conf.get("enabled", default)

    def get_priority(self, module_name: str, default: int) -> int:
        """Gets the configured priority, falling back to default."""
        mod_conf = self.get_module_config(module_name)
        return mod_conf.get("priority", default)
