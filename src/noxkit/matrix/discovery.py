from typing import Protocol


class VersionDiscovery(Protocol):
    """Interface for discovering versions from metadata or providers."""

    def discover(self, package: str, selector: str) -> list[str]: ...


def discover_versions(package: str, selector: str = "supported") -> list[str]:
    """Discover versions using project metadata or a registered provider."""
    raise NotImplementedError("Version discovery is not implemented yet")