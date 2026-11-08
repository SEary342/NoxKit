from abc import ABC, abstractmethod
from typing import Any


class BaseProvider(ABC):
    """Abstract base class for framework-specific compatibility providers."""
    
    @abstractmethod
    def discover_versions(self, selector: str) -> list[str]:
        """Discover versions based on Trove classifiers or other metadata."""
        raise NotImplementedError

    @abstractmethod
    def get_compatibility_rules(self) -> list[Any]:
        """Return rules for incompatible combinations."""
        raise NotImplementedError