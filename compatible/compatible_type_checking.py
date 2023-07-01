from __future__ import annotations
from typing import Callable, TYPE_CHECKING
from dataclasses import dataclass

@dataclass(frozen=True)
class Content:
    author: str
    topic: str
    data: str