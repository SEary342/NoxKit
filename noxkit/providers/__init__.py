"""Framework-specific compatibility metadata providers."""

from .base import BaseProvider
from .django import DjangoProvider

__all__ = ["BaseProvider", "DjangoProvider"]