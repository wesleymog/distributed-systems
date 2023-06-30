from __future__ import annotations

# Se não funcionar no lab rode:
# $ pip install --user typing_extensions
import sys
IS_NEW_PYTHON: bool = sys.version_info >= (3, 8)
if IS_NEW_PYTHON:
    from typing import TypeAlias
else:
    from typing_extensions import TypeAlias

from typing import Callable, TYPE_CHECKING
from dataclasses import dataclass

UserId: TypeAlias = str
Topic: TypeAlias = str

if IS_NEW_PYTHON:
    @dataclass(frozen=True, kw_only=True, slots=True)
    class Content:
        author: UserId
        topic: Topic
        data: str
elif not TYPE_CHECKING:
    @dataclass(frozen=True)
    class Content:
        author: UserId
        topic: Topic
        data: str

if IS_NEW_PYTHON:
    FnNotify: TypeAlias = Callable[[list[Content]], None]
elif not TYPE_CHECKING:
    FnNotify: TypeAlias = Callable