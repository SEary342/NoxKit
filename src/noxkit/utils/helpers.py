from collections.abc import Iterable


def normalize_versions(versions: Iterable[str]) -> list[str]:
    """Return non-empty version strings with duplicates removed in order."""
    return list(dict.fromkeys(version for version in versions if version))