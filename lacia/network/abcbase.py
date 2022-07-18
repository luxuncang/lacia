import asyncio
from abc import ABC, abstractmethod

from ..hook import Hook
from ..typing import Message, Optional, Tuple, TypeVar, List, Generic, Generator

W = TypeVar('W')

class BaseServer(Hook, Generic[W]):
    active_connections: List[Tuple[W, asyncio.Event]]

    @abstractmethod
    async def receive(self, websocket: W) -> Message:
        ...

    async def send(self, message) -> None:
        ...

    @abstractmethod
    async def receive_json(self, websocket: W) -> Message:
        ...

    @abstractmethod
    async def receive_bytes(self, websocket: W) -> bytes:
        ...

    @abstractmethod
    async def iter_bytes(self, websocket: W) -> Generator[bytes, None, None]:
        ...

    @abstractmethod
    async def iter_json(self, websocket: W) -> Generator[Message, None, None]:
        ...

    @abstractmethod
    async def send_bytes(self, websocket: W, message: bytes) -> None:
        ...

    @abstractmethod
    async def send_json(self, websocket: W, message: Message) -> None:
        ...

    @abstractmethod
    async def start(self, *args, **kwargs) -> "BaseServer":
        ...

    @abstractmethod
    async def close(self, code: int, reason: Optional[str] = None) -> None:
        ...

    def closed(self) -> bool:
        ...

    @abstractmethod
    def set_on_ws(self, Callable, *args, **kwargs):
        ...

class BaseClient(Hook):
    @abstractmethod
    async def receive(self) -> Message:
        ...

    @abstractmethod
    async def send(self, message) -> None:
        ...

    @abstractmethod
    async def receive_json(self) -> Message:
        ...

    @abstractmethod
    async def receive_bytes(self) -> bytes:
        ...

    @abstractmethod
    async def iter_bytes(self) -> Generator[bytes, None, None]:
        ...

    @abstractmethod
    async def iter_json(self) -> Generator[Message, None, None]:
        ...

    @abstractmethod
    async def send_bytes(self, message: bytes) -> None:
        ...

    @abstractmethod
    async def send_json(self, message: Message) -> None:
        ...

    @abstractmethod
    async def start(self, *args, **kwargs) -> "BaseClient":
        ...

    @abstractmethod
    async def close(self, code: int, reason: Optional[str] = None) -> None:
        ...

    @abstractmethod
    def closed(self) -> bool:
        ...