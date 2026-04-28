"""
PiDog MCP - Model Context Protocol server for Sunfounder PiDog robot API
"""

__version__ = "0.1.0"
__author__ = "PiDog MCP Contributors"

from .server import app, main, VALID_ACTIONS

__all__ = ["app", "main", "VALID_ACTIONS"]
