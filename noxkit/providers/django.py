from noxkit.providers.base import BaseProvider


class DjangoProvider(BaseProvider):
    """Provides Django version metadata and compatibility rules."""

    def discover_versions(self, selector: str) -> list[str]:
        raise NotImplementedError("Django version discovery is not implemented yet")

    def get_compatibility_rules(self) -> list[dict[str, str]]:
        raise NotImplementedError("Django compatibility rules are not implemented yet")