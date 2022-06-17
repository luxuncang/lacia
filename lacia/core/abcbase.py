from abc import ABC
from enum import Enum

from ..typing import Dict, Callable, Any, Union, TYPE_CHECKING

if TYPE_CHECKING:
    from ..network.client.aioclient import AioClient, BaseClient
    from ..network.server.aioserver import AioServer, BaseServer

    Server = Union[AioServer, BaseServer]
    Client = Union[AioClient, BaseClient]


class JsonRpcMode(str, Enum):
    JsonRpc2 = "2.0"
    JsonRpcX = "X"
    Auto = "Auto"


class ListenEvent(str, Enum):
    Exception = "Exception"


class BaseJsonRpc(ABC):
    _server: "Server"
    _client: "Client"
    _PATH: str
    _HOST: str
    _PORT: int
    _Execer: bool = False
    _JsonRpcMode: JsonRpcMode = JsonRpcMode.Auto
    _Events: Dict[ListenEvent, Callable] = {}
    _namespace: Dict[str, Any] = {}

    def on(self, event: ListenEvent, callback) -> None:
        self._Events[event] = callback

    async def __aenter__(self) -> "BaseJsonRpc":
        return self

    async def __aexit__(self, exc_type: Any, exc_value: Any, traceback: Any) -> None:
        ...
