from pydantic import BaseModel

from ...typing import Param, Optional, Literal
from ..basestandard import JsonRpcError, ProxyObj


class JsonRpc2Request(BaseModel):
    """
    JSON-RPC 2.0
    """

    jsonrpc: Literal["2.0"] = "2.0"
    id: str
    method: str
    params: Optional[Param] = None


class JsonRpc2Response(BaseModel):
    """
    JSON-RPC 2.0
    """

    jsonrpc: Literal["2.0"] = "2.0"
    id: Optional[str] = None
    result: Optional[Param] = None
    error: Optional[JsonRpcError] = None


def analysis_jsonrpc2_message(message: JsonRpc2Request):
    for i in message.method.split("."):
        yield {"method": "__getattr__", "args": (i,), "kwargs": {}}
    if isinstance(message.params, dict):
        kw = message.params
        args = ()
    elif isinstance(message.params, list):
        args = tuple(message.params)
        kw = {}
    elif message.params == None:
        return
    else:
        raise TypeError("Invalid JSON-RPC 2.0 request")
    yield {"method": "__call__", "args": args, "kwargs": kw}


def proxy_to_jsonrpc2(proxy: ProxyObj):
    """
    JSON-RPC 2.0
    """
    method = []
    params = None
    state = False
    for i in proxy:
        if state:
            raise TypeError("Invalid JSON-RPC 2.0 request")
        if isinstance(i, str):
            method.append(i)
        else:
            state = True
            params = i
    
    method = ".".join(method)

    if params == None:
        if state:
            return method, {}
        else:
            return method, params

    if params[0] and params[1]:
        raise TypeError("Invalid JSON-RPC 2.0 request")
    elif params[1]:
        params = params[1]
    elif params[0]:
        params = params[0]
    else:
        params = {}

    return method, params
