from dataclasses import dataclass
from typing import Any


@dataclass
class ToolResult:
    success: bool
    data:    Any  = None
    error:   str  = None
