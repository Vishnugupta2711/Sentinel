import structlog
from typing import Dict, List, Optional
from intelligence.interfaces.module import BaseIntelligenceModule
from intelligence.config import IntelligenceConfig

logger = structlog.get_logger(__name__)

class ModuleRegistry:
    """Maintains the registry of available and enabled intelligence modules."""
    
    def __init__(self, config: IntelligenceConfig):
        self._config = config
        self._modules: Dict[str, BaseIntelligenceModule] = {}
        self._disabled: set[str] = set()

    def register(self, module: BaseIntelligenceModule) -> None:
        """Registers a module and evaluates its config state."""
        name = module.name()
        self._modules[name] = module
        
        # Check YAML configuration
        if not self._config.is_enabled(name, default=True):
            self._disabled.add(name)
            logger.info(f"Module '{name}' registered but DISABLED via config.")
        else:
            logger.info(f"Module '{name}' registered and ENABLED.")

    def unregister(self, module_name: str) -> None:
        """Removes a module from the registry."""
        if module_name in self._modules:
            del self._modules[module_name]
        self._disabled.discard(module_name)

    def enable(self, module_name: str) -> bool:
        """Manually enables a module at runtime."""
        if module_name in self._modules:
            self._disabled.discard(module_name)
            logger.info(f"Module '{module_name}' enabled manually.")
            return True
        return False

    def is_enabled(self, module_name: str) -> bool:
        """Check if a module is registered and enabled."""
        if module_name not in self._modules:
            return False
        return module_name not in self._disabled

    def disable(self, module_name: str) -> bool:
        """Manually disables a module at runtime."""
        if module_name in self._modules:
            self._disabled.add(module_name)
            logger.info(f"Module '{module_name}' disabled manually.")
            return True
        return False

    def get_module(self, module_name: str) -> Optional[BaseIntelligenceModule]:
        """Returns a specific module if it exists."""
        return self._modules.get(module_name)

    def list_modules(self) -> List[Dict[str, str]]:
        """Lists all registered modules and their current state."""
        result = []
        for name, module in self._modules.items():
            result.append({
                "name": name,
                "version": module.version(),
                "health": module.health(),
                "state": "DISABLED" if name in self._disabled else "ENABLED",
                "priority": self._config.get_priority(name, module.priority())
            })
        return result

    def get_execution_pipeline(self) -> List[BaseIntelligenceModule]:
        """
        Returns an ordered list of enabled modules sorted by priority.
        (Lower number = higher priority = executes first).
        """
        active_modules = [m for name, m in self._modules.items() if name not in self._disabled]
        
        # Sort by YAML priority first, fallback to hardcoded priority
        active_modules.sort(key=lambda m: self._config.get_priority(m.name(), m.priority()))
        return active_modules
