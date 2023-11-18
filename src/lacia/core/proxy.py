from typing import Generic, TypeVar, cast, Type, Optional, Any, TYPE_CHECKING

from lacia.standard import JsonAst
from lacia.types import RpcMessage, JsonRpcCode
from lacia.standard.abcbase import BaseDataTrans
from lacia.exception import JsonRpcRuntimeException

if TYPE_CHECKING:
    from lacia.core.core import JsonRpc

T = TypeVar("T", bound=BaseDataTrans)

Schema = TypeVar("Schema")

def with_schema(obj, schema: Type[Schema]) -> Schema:
    return cast(schema, obj)

class BaseProxy(Generic[T]):
    _jsonrpc: str
    _obj: T

    def __await__(self):
        ...

class ProxyObj(BaseProxy):
    _jsonrpc: str = "jsonast"

    def __init__(self, core: Optional["JsonRpc[JsonAst]"] = None, name: Optional[str] = None):
        self._aiter: Optional["ResultProxy"] = None
        self._obj = None # type: ignore
        self._core = core
        self._name = name

    def __getattr__(self, name: str) -> "ProxyObj":
        self = self._newobj()

        obj = JsonAst( 
            obj=self._obj,
            method="__getattr__",
            args=(name,),
            kwargs={},
        )
        self._obj = obj
        return self

    def __call__(self, *args, **kwargs) -> "ProxyObj":

        self = self._newobj()

        n_args = []
        n_kwargs = {}
        for i in args:
            n_args.append(self._expand(i))
        
        for k,v in kwargs.items():
            n_kwargs[k] = self._expand(v)

        obj = JsonAst(
            obj=self._obj,
            method="__call__",
            args=tuple(n_args),
            kwargs=n_kwargs,
        )
        self._obj = obj
        return self

    def _expand(self, obj: Any):
        if isinstance(obj, ProxyObj):
            return obj._obj
        elif isinstance(obj, list):
            return [self._expand(i) for i in obj]
        elif isinstance(obj, dict):
            return {k: self._expand(v) for k, v in obj.items()}
        elif isinstance(obj, tuple):
            return tuple(self._expand(i) for i in obj)
        elif isinstance(obj, set):
            return {self._expand(i) for i in obj}
        else:
            return obj

    def _newobj(self):
        new = ProxyObj(self._core, self._name)
        setattr(new, "_obj", self._obj)
        setattr(new, "_aiter", self._aiter)
        return new

    def __aiter__(self):
        self = self._newobj()

        obj = JsonAst(
            obj=self._obj,
            method="__aiter__",
            args=(),
            kwargs={}
        )
        self._obj = obj

        return self
    
    def __anext_proxy__(self):
        self = self._newobj()

        obj = JsonAst(
            obj=self._obj,
            method="__anext__",
            args=(),
            kwargs={}
        )
        self._obj = obj

        return self

    async def __anext__(self):
        if self._core is None:
            raise TypeError("ProxyObj is not bind to JsonRpc")
        if not self._aiter:
            data = await self._core.run(self)
            self._aiter = data
            r = await data.__anext__()
            return r
        else:
            r = await self._aiter.__anext__()
            return r

    def __await__(self):
        if self._core is None:
            raise TypeError("ProxyObj is not bind to JsonRpc")
        if not self._core._client is None:
            data = yield from self._core.run(self).__await__()
        elif not self._core._server is None:
            if self._name is None:
                raise JsonRpcRuntimeException("client name is None")
            data = yield from self._core.reverse_run(self._name, self).__await__()
        else:
            raise JsonRpcRuntimeException("server and client are None")
        self._obj = None
        return data.visions

class ResultProxy(BaseProxy):

    def __init__(self, result: RpcMessage, core: Optional["JsonRpc[JsonAst]"] = None):
        self._core = core
        self._result = result
        self._obj = None

    @property
    def visions(self):
        if self._result.error:
            if self._result.error_code == JsonRpcCode.StopAsyncIterationError:
                raise StopAsyncIteration
            raise JsonRpcRuntimeException(self._result.error)
        return self._result.result

    def __getattr__(self, name: str) -> "ProxyObj":
        return getattr(getattr(ProxyObj(self._core), self._result.id), name) # type: ignore

    async def __aiter__(self):
        return self

    async def __anext__(self):
        if self._core is None:
            raise TypeError("ProxyObj is not bind to JsonRpc")
        obj = getattr(ProxyObj(self._core), self._result.id).__anext_proxy__()

        data = await self._core.run(obj)
        return data.visions

