"""Configuration package for OpenPCB."""

from .loader import load_agent_settings
from .settings import AgentSettings

__all__ = ["AgentSettings", "load_agent_settings"]
