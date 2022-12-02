"""
    Declared types.
"""

from typing import Callable, Awaitable, Any, MutableMapping

Message = MutableMapping[str, Any]

# ASGI call params.
Scope = MutableMapping[str, Any]
Receive = Callable[[], Awaitable[Message]]
Send = Callable[[Message], Awaitable[None]]
