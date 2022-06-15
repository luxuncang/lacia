import asyncio

from pydantic import BaseModel

from ..exception import JsonRpcException
from ..typing import Union, Tuple, List, Iterator, Dict, Optional, Iterable, Param, JsonRpcCode, TYPE_CHECKING, TypeVar, Generic, Any

if TYPE_CHECKING:
    from ..core.core import JsonRpc
    from .jsonrpc2 import JsonRpc2Request, JsonRpc2Response
    from .jsonrpcX import JsonRpcXRequest, JsonRpcXResponse

Code = Union[int, JsonRpcCode]

T_Res = TypeVar("T_Res", "JsonRpcXResponse", "JsonRpc2Response")
T_Req = TypeVar("T_Req", "JsonRpcXRequest", "JsonRpc2Request")

class JsonRpcError(BaseModel):
    code: Code
    message: str
    data: Optional[Param] = None


class Assign(Generic[T_Res, T_Req]): # TODO 与其他Json-RPC实现进行交互时可能存在ID冲突

    future: Dict[str, asyncio.Event] = {}
    result: Dict[str, Any] = {}

    @classmethod
    async def receiver(cls, uid: str, pop: bool = True):
        event = asyncio.Event()
        cls.future[uid] = event
        await event.wait()
        if pop:
            data = cls.result.pop(uid)
        else:
            data = cls.result[uid]
            return data
        if 'error' in data.dict(exclude_unset = True) and data.error != None:
            if data.error.code == JsonRpcCode.StopAsyncIterationError:
                cls.future.pop(uid, None)
                return JsonRpcCode.StopAsyncIterationError
            raise JsonRpcException(data.error.code, data.error.message, data.error.data)
        elif 'result' in data.dict(exclude_unset = True) and data.result != None:
            return data.result
        raise TypeError("JsonRpc Response Obj Error")

    @classmethod
    def post_data(cls, data: Any, pop: bool = True):
        uid = data.id
        cls.future[uid].set() 
        if pop:
            cls.future.pop(uid, None)
        cls.result[uid] = data



class ProxyObj:
    def __init__(self, _self: "JsonRpc"):
        self.__self = _self
        self.__methods: List[Union[str, Tuple[tuple, dict]]] = []

    def __getattr__(self, name) -> "ProxyObj":
        self.__methods.append(name)
        return self

    def __call__(self, *args, **kwargs) -> "ProxyObj":
        self.__methods.append((args, kwargs))
        return self

    def __iter__(self) -> Iterator[Union[str, Tuple[tuple, dict]]]:
        return iter(self.__methods)

    def __aiter__(self):
        self.__methods.append('__aiter__')
        self.__aiter_request = False
        return self

    async def __anext__(self):
        if hasattr(self.__self, "_client"):
            if not self.__self._client.closed():
                if not self.__aiter_request:
                    request = self.__self.auto_standard(self)
                    self.__aiter_request = request
                else:
                    request = self.__aiter_request
                if TYPE_CHECKING:
                    assert isinstance(request, (JsonRpcXRequest, JsonRpc2Request))
                try:
                    await self.__self._client.send_json(request.dict())
                    data = await Assign.receiver(request.id)
                except JsonRpcException as e:
                    raise e
                if isinstance(data, JsonRpcCode) and data == JsonRpcCode.StopAsyncIterationError:
                    raise StopAsyncIteration
                return data
        raise AttributeError("client is not running")

    def __await__(self):
        if hasattr(self.__self, "_client"):
            if not self.__self._client.closed():
                request = self.__self.auto_standard(self)
                yield from self.__self._client.send_json(request.dict()).__await__()
                try:
                    data = yield from Assign.receiver(request.id).__await__()
                except JsonRpcException as e:
                    raise e
                return data
        raise AttributeError("client is not running")

def analysis_proxy(
    proxy: Union[ProxyObj, Iterable[Union[str, Tuple[tuple, dict]]]]
) -> Iterator:
    for i in proxy:
        if isinstance(i, str):
            yield {"method": "__getattr__", "args": (i,), "kwargs": {}}
        else:
            yield {"method": "__call__", "args": i[0], "kwargs": i[1]}


class Proxy:
    def __getattr__(self, name) -> ProxyObj:
        proxy = getattr(ProxyObj(self), name) # type: ignore
        return proxy
    