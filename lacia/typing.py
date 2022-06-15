from __future__ import annotations

import sys
from enum import Enum
from typing import (
    List,
    Tuple,
    Union,
    Dict,
    Optional,
    Literal,
    Callable,
    TYPE_CHECKING,
    TypeVar,
    Any,
    Iterator,
    Iterable,
    AsyncIterator,
    MutableMapping,
    Sequence,
    Generator,
    AsyncGenerator,
    TypedDict,
    Type,
    Generic,
    Annotated,
    get_args,
    get_origin,
    get_type_hints,
    overload,
)
from xmlrpc.client import Server

if sys.version_info >= (3, 10):
    from typing import ParamSpec
else:
    from typing_extensions import ParamSpec

Message = Dict[str, Any]
PyMode = Literal["REPL", "SCRIPT"]
Param = Union[str, float, bool, None, Sequence[Any], MutableMapping[str, Any]]


class JsonRpcCode(int, Enum):
    ParseError = -32700
    InvalidRequest = -32600
    MethodNotFound = -32601
    InvalidParams = -32602
    InternalError = -32603
    ServerError = -32000
    StopAsyncIterationError = -32099
