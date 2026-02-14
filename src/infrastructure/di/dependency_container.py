"""IoC container for dependency injection pattern.

Port from hs_deckmanager (scr/views/builder/dependency_container.py)
with simplifications for solitario application.

Key Features:
- Thread-safe dependency resolution
- Circular dependency detection
- Minimal API (no singleton flag, no caching)
- Factory-based resolution

Version: v2.2.0
"""

from threading import Lock
from typing import Callable, Any, Optional


class DependencyContainer:
    """IoC container per gestione centralizzata dipendenze.
    
    Port da hs_deckmanager con semplificazioni:
    - Rimosso singleton flag (non usato in pratica)
    - API minimalista: register(), resolve(), has()
    - Thread-safe con Lock
    - Circular dependency detection
    
    Pattern:
        Factory-based resolution: ogni chiamata a resolve() invoca
        la factory function registrata, creando una nuova istanza.
        
        Per singletons: caller deve gestire caching se necessario,
        oppure la factory può ritornare sempre la stessa istanza.
    
    Example:
        >>> container = DependencyContainer()
        >>> container.register("settings", lambda: GameSettings())
        >>> settings = container.resolve("settings")
    
    Thread Safety:
        Lock acquisito durante resolution per prevenire race conditions
        in registrazione/resolution concorrente.
    
    Circular Dependencies:
        Rilevate tramite resolving_stack: se una dependency richiede
        se stessa durante resolution, ValueError viene sollevato.
    
    Version:
        v2.2.0: Initial implementation (port from hs_deckmanager)
    """
    
    def __init__(self):
        """Initialize empty container.
        
        Attributes:
            _dependencies: Dict mapping keys to factory functions
            _resolving_stack: Set tracking dependencies currently resolving
                              (for circular dependency detection)
            _lock: Thread safety lock
        """
        self._dependencies: dict[str, Callable[[], Any]] = {}
        self._resolving_stack: set[str] = set()
        self._lock = Lock()
    
    def register(self, key: str, factory: Callable[[], Any]) -> None:
        """Register dependency factory function.
        
        Args:
            key: Unique identifier for this dependency
            factory: Zero-argument callable returning instance
        
        Raises:
            ValueError: If key already registered
        
        Example:
            >>> container.register("tts", lambda: create_tts_provider("auto"))
            >>> container.register("settings", GameSettings)  # Class as factory
        """
        if key in self._dependencies:
            raise ValueError(f"Dependency '{key}' already registered")
        self._dependencies[key] = factory
    
    def resolve(self, key: str) -> Any:
        """Resolve dependency, call factory and return instance.
        
        Invokes registered factory function and returns result.
        Thread-safe with circular dependency detection.
        
        Args:
            key: Dependency identifier
        
        Returns:
            Instance created by factory
        
        Raises:
            ValueError: If key not registered or circular dependency detected
        
        Example:
            >>> settings = container.resolve("settings")
            >>> tts = container.resolve("tts")
        """
        with self._lock:
            if key not in self._dependencies:
                raise ValueError(f"Dependency '{key}' not registered")
            
            # Check circular dependency
            if key in self._resolving_stack:
                raise ValueError(
                    f"Circular dependency detected: {key} "
                    f"(stack: {self._resolving_stack})"
                )
            
            # Add to resolving stack
            self._resolving_stack.add(key)
            try:
                # Invoke factory and return result
                return self._dependencies[key]()
            finally:
                # Always remove from stack (even if exception)
                self._resolving_stack.discard(key)
    
    def resolve_optional(self, key: str) -> Optional[Any]:
        """Resolve dependency, return None if not registered.
        
        Convenience method for optional dependencies.
        Swallows ValueError and returns None instead.
        
        Args:
            key: Dependency identifier
        
        Returns:
            Instance created by factory, or None if not registered
        
        Example:
            >>> controller = container.resolve_optional("main_controller")
            >>> if controller:
            ...     controller.initialize()
        """
        try:
            return self.resolve(key)
        except ValueError:
            return None
    
    def has(self, key: str) -> bool:
        """Check if dependency registered.
        
        Args:
            key: Dependency identifier
        
        Returns:
            True if key registered, False otherwise
        
        Example:
            >>> if container.has("database"):
            ...     db = container.resolve("database")
        """
        return key in self._dependencies
