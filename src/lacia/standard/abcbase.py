from abc import ABC, abstractmethod, abstractclassmethod

from typing import TypeVar, Generic, Type, Any, Dict, NamedTuple, Hashable
from typing_extensions import Self

T = TypeVar("T")
S = TypeVar("S")

class Namespace(NamedTuple):

    builtins: Dict[str, Any] = {}
    globals: Dict[str, Any] = {}
    locals: Dict[Hashable, Dict[str, Any]] = {}

    def __getitem__(self, key: T) -> Dict[str, Any]:

        return {
            **self.builtins,
            **self.globals,
            **self.locals.get(key, {})
        }      

class BaseDataTrans(ABC, Generic[T]):

    @abstractclassmethod # type: ignore
    def loads(cls, obj: T) -> Self:
        ...
    
    @abstractmethod
    def dumps(self) -> T:
        ...

class BaseRunTime(ABC, Generic[S]):

    def __init__(self, namespace: Dict[str, Any], proxy, proxyresult):
        self.namespace = namespace
        self.proxy = proxy
        self.proxyresult = proxyresult

    @abstractmethod
    async def run(self, obj: S) -> Any:
        ...

class BaseStandard(ABC, Generic[T, S]):
    
    datatrans: Type[BaseDataTrans[T]]
    runtime: Type[BaseRunTime[S]]
