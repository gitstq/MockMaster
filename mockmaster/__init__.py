"""
MockMaster - API Mock Server Intelligent Manager

A lightweight CLI tool for rapid API mock server creation, management, and switching.
Zero dependencies, pure Python 3.8+ implementation.

Author: MockMaster Team
Version: 1.0.0
License: MIT
"""

__version__ = "1.0.0"
__author__ = "MockMaster Team"
__license__ = "MIT"
__title__ = "MockMaster"
__description__ = "API Mock Server Intelligent Manager - Zero-dependency CLI tool"

from .server import MockServer
from .config import ConfigParser
from .storage import ProjectStorage

__all__ = ["MockServer", "ConfigParser", "ProjectStorage"]